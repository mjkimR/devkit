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
from devkit_dist.features.project.models.invocation import devkit_command
from devkit_dist.features.project.usecases.configuration import approval_language

from devkit_spec.base.errors import (
    ProposalNotFoundError,
    ReportArgumentError,
    ReportSourceDirtyError,
    ReportSourceInvalidError,
    ReportSourceNotHeadError,
    ReportWrongCheckoutError,
)

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


def _command(slug: str) -> str:
    return devkit_command(f"spec proposal report {slug}")


def check_arguments(slug: str, sha: str | None) -> None:
    """Refuse a malformed slug or source SHA before any checkout is read (``ReportArgumentError``)."""
    if not SLUG.fullmatch(slug) or len(slug) > 59:
        raise ReportArgumentError(
            f"{slug!r} is not a proposal slug",
            target_files=["SLUG"],
            fix="Pass the slug of an existing proposal: lowercase letters, digits and single hyphens, at most 59 "
            f"characters ({devkit_command('spec list proposal')} shows them)",
        )
    if sha is not None and not SHA.fullmatch(sha):
        raise ReportArgumentError(
            f"--source-sha {sha!r} is not a full lowercase commit SHA",
            target_files=["--source-sha"],
            fix=f"Pass the full 40-character commit SHA, or omit --source-sha for HEAD: `{_command(slug)}`",
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


def _read(path: str, unit: str) -> bool:
    """Whether ``source`` reads ``path`` of the proposal ``unit``: its proposal, PADRs and envelopes, never materials."""
    return (
        path == unit + "proposal.md"
        or (path.startswith(unit + "decisions/PADR-") and path.endswith(".md"))
        or (path.startswith(unit + "envelopes/") and path.endswith((".yaml", ".yml")))
    )


def source(root: Path, slug: str, sha: str) -> Source:
    check_arguments(slug, sha)
    unit = f"docs/proposals/PROP-{slug}/"
    anchor = unit + "proposal.md"
    try:
        if run_git(root, "rev-parse", "HEAD").decode().strip() != sha:
            raise ReportSourceNotHeadError(
                f"--source-sha {sha[:12]} is not the current commit of this checkout",
                fix=f"Pass the current committed SHA, or omit --source-sha: `{_command(slug)}`",
            )
        entries = run_git(root, "ls-tree", "-r", "-z", sha, "--", unit).split(b"\0")
        if not any(entries):
            raise ProposalNotFoundError(
                f"proposal PROP-{slug} is not in commit {sha[:12]}",
                target_files=[anchor],
                fix=f"Pass the slug of a committed proposal ({devkit_command('spec list proposal')} shows them)",
            )
        dirty = run_git(root, "status", "--porcelain", "--untracked-files=normal").decode().splitlines()
        if any(line.strip() for line in dirty):
            raise ReportSourceDirtyError(
                "the source checkout has uncommitted changes; the report reads committed records only",
                target_files=[line[3:] for line in dirty if line.strip()][:20],
                fix=f"Once the user has decided what happens to the changes in [TARGET] and the checkout is clean, run "
                f"`{_command(slug)}`",
            )
        files = {}
        for entry in filter(None, entries):
            header, _tab, raw_path = entry.partition(b"\t")
            mode = header.split(None, 1)[0].decode()
            path = raw_path.decode("utf-8", "surrogateescape")
            if mode not in {"100644", "100755"}:
                raise _invalid(slug, path, "is not a committed regular file")
            if _read(path, unit):
                files[path] = run_git(root, "show", f"{sha}:{path}").decode()
        meta = parse(files.get(anchor, "")).data or {}
        if meta.get("id") != f"PROP-{slug}":
            raise _invalid(slug, anchor, f"does not declare id: PROP-{slug}")
        position = locate(root)
        planning = position.branch == f"plan-{slug}" and meta.get("status") in {"reviewing", "accepted"}
        accepted = (
            not position.linked
            and bool(position.branch)
            and not position.branch.startswith(("dev-", "plan-"))
            and meta.get("status") == "accepted"
        )
        if not (planning or accepted):
            raise ReportWrongCheckoutError(
                f"PROP-{slug} (status {meta.get('status') or '-'}) is reported from plan-{slug} or, once accepted, "
                f"from the retained base, not from {position.branch or '- (detached HEAD)'}",
                target_files=[f"plan-{slug}"],
                fix=f"Run `{_command(slug)}` in the plan-{slug} worktree",
            )
        padrs, coverage = [], []
        for path, text in files.items():
            if path.startswith(unit + "decisions/PADR-") and path.endswith(".md"):
                identifier = (parse(text).data or {}).get("id")
                if not isinstance(identifier, str) or identifier != Path(path).stem:
                    raise _invalid(slug, path, f"declares id {identifier!r}, not its file name {Path(path).stem}")
                padrs.append(identifier)
            if path.startswith(unit + "envelopes/") and path.endswith((".yaml", ".yml")):
                record = safe_load(text, source=path)
                if not isinstance(record, dict):
                    raise _invalid(slug, path, "is not a YAML mapping")
                coverage.append(Path(path).name)
                effort = record.get("activity_effort", record.get("effort"))
                if effort is not None:
                    coverage.append(str(effort))
        effort, dev_effort = meta.get("planning_effort", "medium"), meta.get("dev_effort", "medium")
        if effort not in {"low", "medium", "high"} or dev_effort not in {"low", "medium", "high"}:
            raise _invalid(slug, anchor, "has a planning_effort or dev_effort other than low, medium or high")
        return Source(
            sha,
            approval_language(root),
            str(meta.get("title", f"PROP-{slug}")),
            tuple(padrs),
            tuple(coverage),
            effort,
            dev_effort,
        )
    except (
        ReportSourceNotHeadError,
        ReportSourceDirtyError,
        ReportSourceInvalidError,
        ReportWrongCheckoutError,
        ProposalNotFoundError,
        YamlBindingUnavailableError,
    ):
        raise
    except (AdvisoryError, ValueError, UnicodeError, yaml.YAMLError) as exc:
        raise ReportSourceInvalidError(
            f"the committed records of PROP-{slug} cannot be read: {exc}",
            target_files=[unit.rstrip("/")],
            fix=f"Correct the record named in the message, commit it, then run `{_command(slug)}`",
        ) from exc


def _invalid(slug: str, path: str, reason: str) -> ReportSourceInvalidError:
    return ReportSourceInvalidError(
        f"{path} {reason}",
        target_files=[path],
        fix=f"Correct {path}, commit it, then run `{_command(slug)}`",
    )


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
        try:
            return find(position, f"plan-{slug}")
        except AdvisoryError as exc:
            if exc.code != "WORKTREE_NOT_FOUND":
                raise
            raise ReportSourceNotHeadError(
                f"--source-sha {source_sha[:12]} is not the current commit, and PROP-{slug} has no plan-{slug} "
                "worktree to read it from",
                fix=f"Pass the current committed SHA of the base or of plan-{slug}, or omit --source-sha: "
                f"`{_command(slug)}`",
            ) from exc
    return root


class ReportTemplateUseCase(BaseUseCase):
    """Application entrypoint for the report template/briefing; read-only."""

    def execute(self, root: Path, slug: str, source_sha: str | None = None) -> str:
        """The template to complete for ``source_sha``, read from the matching Planning source."""
        check_arguments(slug, source_sha)
        if source_sha is None:
            source_sha = run_git(root, "rev-parse", "HEAD").decode().strip()
        return template(_workspace_source(root, slug, source_sha), slug, source_sha)
