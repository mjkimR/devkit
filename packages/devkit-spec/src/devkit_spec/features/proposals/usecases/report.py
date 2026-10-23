"""Source-bound proposal briefings; authors supply meaning, the domain checks coverage."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml
from devkit.advisory import AdvisoryError
from devkit_agt.features.worktree import find, locate
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import run_git
from devkit_core.core.frontmatter import parse
from devkit_dist.features.project.usecases.configuration import approval_language
from devkit_dist.features.project.usecases.invocation import guard_execution
from devkit_dist.features.shared import Artifact, PutRequest, adapter
from devkit_dist.features.shared.models.api import MAX_BYTES, SHA, SLUG

from devkit_spec.base.errors import SpecError

SECTIONS = {
    "en": (
        "Outcome",
        "Decisions",
        "Boundary impacts",
        "Planning effort and support",
        "Open decisions and waived findings",
        "Unverified areas",
        "Recommended Development effort",
        "Proposed approval effects",
    ),
    "ko": (
        "결론",
        "결정",
        "범위 영향",
        "Planning 노력 및 지원",
        "열린 결정 및 면제된 지적",
        "미검증 영역",
        "권장 Development 노력",
        "제안된 승인 효과",
    ),
}
DECISION_FIELDS = {
    "en": ("Problem", "Choice", "Rejected alternatives", "Consequences"),
    "ko": ("문제", "선택", "기각한 대안", "결과"),
}


class ReportInvalidError(SpecError):
    code = "PROPOSAL_REVIEW_INVALID"
    input_error = True
    fix = (
        "Fill the report template of the current clean committed proposal and publish it again: "
        "`devkit spec proposal report <slug> --source-sha <sha> --template` (MCP: spec_proposal_report_template)"
    )


class ReviewRefreshRequiredError(SpecError):
    code = "PROPOSAL_REVIEW_REFRESH_REQUIRED"
    fix = "Regenerate the report for the current source, have the Host present it and obtain fresh conversational approval before invoking the CLI"


@dataclass(frozen=True)
class Source:
    sha: str
    language: str
    title: str
    padrs: tuple[str, ...]
    coverage: tuple[str, ...]
    effort: str
    dev_effort: str


def source(root: Path, slug: str, sha: str) -> Source:
    if not SLUG.fullmatch(slug) or len(slug) > 59 or not SHA.fullmatch(sha):
        raise ReportInvalidError("source: expected a proposal slug and full lowercase commit SHA")
    try:
        if (
            run_git(root, "rev-parse", "HEAD").decode().strip() != sha
            or run_git(root, "cat-file", "-t", sha).strip() != b"commit"
        ):
            raise ReportInvalidError("source: source_sha must be the current full commit identity")
        if run_git(root, "status", "--porcelain", "--untracked-files=normal").strip():
            raise ReportInvalidError("source: commit or resolve worktree changes before publishing")
        unit = f"docs/proposals/PROP-{slug}/"
        entries = run_git(root, "ls-tree", "-r", sha, "--", unit).decode().splitlines()
        files = {}
        for entry in entries:
            mode, _kind, _oid, path = entry.split(None, 3)
            if mode not in {"100644", "100755"}:
                raise ReportInvalidError("source: proposal records must be committed regular files")
            files[path] = run_git(root, "show", f"{sha}:{path}").decode()
        meta = parse(files.get(unit + "proposal.md", "")).data or {}
        if meta.get("id") != f"PROP-{slug}":
            raise ReportInvalidError("source: the commit does not contain the expected proposal")
        position = locate(root)
        planning = position.branch == f"plan-{slug}" and meta.get("status") in {"reviewing", "accepted"}
        accepted = (
            not position.linked
            and bool(position.branch)
            and not position.branch.startswith(("dev-", "plan-"))
            and meta.get("status") == "accepted"
        )
        if not (planning or accepted):
            raise ReportInvalidError("source: must be the Planning branch or accepted retained base")
        padrs, coverage = [], []
        for path, text in files.items():
            if path.startswith(unit + "decisions/PADR-") and path.endswith(".md"):
                identifier = (parse(text).data or {}).get("id")
                if not isinstance(identifier, str) or identifier != Path(path).stem:
                    raise ReportInvalidError("source: PADR identity must match its committed filename")
                padrs.append(identifier)
            if path.startswith(unit + "envelopes/") and path.endswith((".yaml", ".yml")):
                record = yaml.safe_load(text)
                if not isinstance(record, dict):
                    raise ReportInvalidError("source: invalid committed envelope")
                coverage.append(Path(path).name)
                effort = record.get("activity_effort", record.get("effort"))
                if effort is not None:
                    coverage.append(str(effort))
        effort, dev_effort = meta.get("planning_effort", "medium"), meta.get("dev_effort", "medium")
        if effort not in {"low", "medium", "high"} or dev_effort not in {"low", "medium", "high"}:
            raise ReportInvalidError("source: proposal effort must be low, medium or high")
        return Source(
            sha,
            approval_language(root),
            str(meta.get("title", f"PROP-{slug}")),
            tuple(padrs),
            tuple(coverage),
            effort,
            dev_effort,
        )
    except ReportInvalidError:
        raise
    except (AdvisoryError, ValueError, UnicodeError, yaml.YAMLError) as exc:
        raise ReportInvalidError("source: cannot read the exact committed proposal records") from exc


def _sections(body: str, level: int) -> dict[str, str]:
    matches = list(re.finditer(rf"(?m)^{'#' * level} ([^\n]+)\n", body))
    result = {}
    for index, match in enumerate(matches):
        name = match[1].strip()
        if name in result:
            raise ReportInvalidError(f"sections: duplicate report section {name!r}")
        result[name] = body[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(body)].strip()
    return result


def planning_support(report: Artifact) -> str:
    """Read the Planning effort/support section from a validated localized report."""
    heading = SECTIONS[report.metadata.language][3]
    return _sections(report.content, 2)[heading]


def _check(body: str, slug: str, selected: Source, namespace: str) -> None:
    """Refuse a briefing that misses part of the template; each message starts with the failed field class."""
    if not isinstance(body, str) or len(body.encode("utf-8")) > MAX_BYTES:
        raise ReportInvalidError("size: report exceeds the 1 MiB envelope limit")
    parsed = parse(body)
    meta = parsed.data or {}
    expected = {
        "proposal": f"PROP-{slug}",
        "source_sha": selected.sha,
        "language": selected.language,
        "repository_namespace": namespace,
    }
    mismatched = [key for key, value in expected.items() if meta.get(key) != value]
    if mismatched:
        raise ReportInvalidError(
            "identity: frontmatter does not match repository, proposal, source or language: " + ", ".join(mismatched)
        )
    if not re.search(r"(?m)^# [^\n]+", body):
        raise ReportInvalidError("title: report needs an H1 title")
    sections = _sections(body, 2)
    headings = SECTIONS[selected.language]
    missing = [heading for heading in headings if not sections.get(heading)]
    if missing:
        raise ReportInvalidError("sections: missing or empty mandatory section: " + ", ".join(missing))
    decisions = _sections(sections[headings[1]], 3)
    if set(decisions) != set(selected.padrs):
        absent = sorted(set(selected.padrs) - set(decisions))
        extra = sorted(set(decisions) - set(selected.padrs))
        raise ReportInvalidError(
            "decisions: report must account for every current PADR exactly once"
            + (f"; missing {', '.join(absent)}" if absent else "")
            + (f"; unknown {', '.join(extra)}" if extra else "")
        )
    for identifier, content in decisions.items():
        fields = _sections(content, 4)
        empty = [field for field in DECISION_FIELDS[selected.language] if not fields.get(field)]
        if empty:
            raise ReportInvalidError(f"decision fields: {identifier} needs {', '.join(empty)}")
    coverage = sections[headings[3]]
    uncovered = [token for token in (*selected.coverage, selected.effort) if token not in coverage]
    if uncovered:
        raise ReportInvalidError(
            f"coverage: section {headings[3]!r} must name every envelope and applied effort; missing "
            + ", ".join(uncovered)
        )
    if selected.dev_effort not in sections[headings[6]]:
        raise ReportInvalidError(
            f"dev_effort: section {headings[6]!r} must identify the recommended dev_effort {selected.dev_effort}"
        )


def template(root: Path, slug: str, sha: str) -> str:
    """Return the structure to complete; placeholders are not a semantic briefing."""
    selected = source(root, slug, sha)
    namespace = adapter(root).repository_namespace
    header = yaml.safe_dump(
        {
            "proposal": f"PROP-{slug}",
            "source_sha": sha,
            "language": selected.language,
            "repository_namespace": namespace,
        },
        sort_keys=False,
    )
    lines = [f"---\n{header}---\n\n# {selected.title}"]
    for index, heading in enumerate(SECTIONS[selected.language]):
        lines.append(f"\n## {heading}\n")
        if index == 1:
            for identifier in selected.padrs:
                lines.append(f"### {identifier}\n")
                lines.extend(f"#### {field}\n\n" for field in DECISION_FIELDS[selected.language])
            if not selected.padrs:
                lines.append("None." if selected.language == "en" else "없음.")
        elif index == 3:
            lines.append("\n".join((selected.effort, *selected.coverage)))
        elif index == 6:
            lines.append(selected.dev_effort)
    return "\n".join(lines) + "\n"


def publish(root: Path, slug: str, sha: str, body: str) -> Artifact:
    """Compose the application entrypoint for internal callers."""
    return PublishProposalReportUseCase().execute(root, slug, sha, body)


def validate_artifact(root: Path, slug: str, sha: str, uri: str) -> Artifact:
    """Check immutable identity and expiry even after an authorized acceptance commit."""
    try:
        store = adapter(root)
        artifact = store.get(uri)
        meta = artifact.metadata
        if (
            not SHA.fullmatch(sha)
            or meta.artifact_uri != uri
            or meta.repository_namespace != store.repository_namespace
            or meta.kind != "proposal-review"
            or meta.slug != slug
            or meta.source_sha != sha
            or meta.language != approval_language(root)
            or meta.content_sha256 != hashlib.sha256(artifact.content.encode()).hexdigest()
            or not meta.live(datetime.now(UTC))
        ):
            raise ReportInvalidError("report metadata is stale or mismatched")
        return artifact
    except (AdvisoryError, ValueError, UnicodeError) as exc:
        raise ReviewRefreshRequiredError("the exact report is unavailable or no longer matches its identity") from exc


def validate(root: Path, slug: str, sha: str, uri: str) -> Artifact:
    """Read an exact live report; never refresh, list, sweep or publish implicitly."""
    try:
        selected = source(root, slug, sha)
        artifact = validate_artifact(root, slug, sha, uri)
        _check(artifact.content, slug, selected, artifact.metadata.repository_namespace)
        return artifact
    except (AdvisoryError, ValueError, UnicodeError) as exc:
        raise ReviewRefreshRequiredError(
            "the exact report is unavailable, incomplete or no longer matches the source"
        ) from exc


def publish_workspace_report(root: Path, slug: str, source_sha: str, body: str) -> Artifact:
    """Compose the application entrypoint for internal callers."""
    return PublishWorkspaceProposalReportUseCase().execute(root, slug, source_sha, body)


class PublishProposalReportUseCase(BaseUseCase):
    """Application entrypoint for publish."""

    def execute(self, root: Path, slug: str, sha: str, body: str) -> Artifact:
        selected = source(root, slug, sha)
        store = adapter(root)
        _check(body, slug, selected, store.repository_namespace)
        return store.put(PutRequest("proposal-review", slug, sha, selected.language, body))


def _workspace_source(root: Path, slug: str, source_sha: str) -> Path:
    """The checkout holding ``source_sha``: ``root``, or the ``plan-<slug>`` worktree of a retained base."""
    position = locate(root)
    if not position.linked and run_git(root, "rev-parse", "HEAD").decode().strip() != source_sha:
        return find(position, f"plan-{slug}")
    return root


class PublishWorkspaceProposalReportUseCase(BaseUseCase):
    """Application entrypoint for publish workspace report."""

    def execute(self, root: Path, slug: str, source_sha: str, body: str) -> Artifact:
        """Publish from the matching Planning source without changing the caller's checkout."""
        guard_execution()
        return publish(_workspace_source(root, slug, source_sha), slug, source_sha, body)


class ReportTemplateUseCase(BaseUseCase):
    """Application entrypoint for the report template; read-only, publishes nothing."""

    def execute(self, root: Path, slug: str, source_sha: str) -> str:
        """The template to complete for ``source_sha``, read from the matching Planning source."""
        return template(_workspace_source(root, slug, source_sha), slug, source_sha)
