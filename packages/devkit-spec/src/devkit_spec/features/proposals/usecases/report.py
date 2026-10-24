"""Source-bound proposal briefings; authors supply meaning, the domain checks coverage."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from devkit.advisory import AdvisoryError
from devkit_agt.features.worktree import find, locate
from devkit_core.base.errors import YamlBindingUnavailableError
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import run_git
from devkit_core.core.frontmatter import parse
from devkit_core.core.yaml import safe_load
from devkit_dist.features.project.usecases.configuration import approval_language

from devkit_spec.base.errors import SpecError

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")

SECTIONS = {
    "en": (
        "Outcome",
        "Decisions",
        "Proposed approval effects",
    ),
    "ko": (
        "결론",
        "결정",
        "제안된 승인 효과",
    ),
}
DECISION_FIELDS = {
    "en": ("Problem", "Choice"),
    "ko": ("문제", "선택"),
}


class ReportInvalidError(SpecError):
    code = "PROPOSAL_REVIEW_INVALID"
    input_error = True
    fix = (
        "Fill the report template of the current clean committed proposal: "
        "`devkit spec proposal report <slug> [--source-sha <sha>]`"
    )


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
            raise ReportInvalidError("source: commit or resolve worktree changes before generating report")
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
                record = safe_load(text, source=path)
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
    except YamlBindingUnavailableError:
        raise
    except (AdvisoryError, ValueError, UnicodeError, yaml.YAMLError) as exc:
        raise ReportInvalidError("source: cannot read the exact committed proposal records") from exc


def template(root: Path, slug: str, sha: str) -> str:
    """Return the report structure for this proposal source."""
    selected = source(root, slug, sha)
    header = yaml.safe_dump(
        {
            "proposal": f"PROP-{slug}",
            "source_sha": sha,
            "language": selected.language,
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
        elif index == 2:
            lines.append(selected.dev_effort)
    return "\n".join(lines) + "\n"


def _workspace_source(root: Path, slug: str, source_sha: str) -> Path:
    """The checkout holding ``source_sha``: ``root``, or the ``plan-<slug>`` worktree of a retained base."""
    position = locate(root)
    if not position.linked and run_git(root, "rev-parse", "HEAD").decode().strip() != source_sha:
        return find(position, f"plan-{slug}")
    return root


class ReportTemplateUseCase(BaseUseCase):
    """Application entrypoint for the report template/briefing; read-only."""

    def execute(self, root: Path, slug: str, source_sha: str | None = None) -> str:
        """The template to complete for ``source_sha``, read from the matching Planning source."""
        if source_sha is None:
            source_sha = run_git(root, "rev-parse", "HEAD").decode().strip()
        return template(_workspace_source(root, slug, source_sha), slug, source_sha)
