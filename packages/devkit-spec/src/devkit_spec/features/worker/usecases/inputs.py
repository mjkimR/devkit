"""Derive inspection inputs from Git records, never from uncommitted documents."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any

from devkit_agt.features.workflow.services.envelope import Envelopes, collect_envelopes, is_envelope_name
from devkit_agt.features.worktree.usecases.lifecycle import locate
from devkit_core.base.errors import ArgumentError
from devkit_core.core import GitError, run_git, run_git_text
from devkit_core.core.frontmatter import parse

from devkit_spec.base.axes import PROPOSAL_WORKFLOW, SPEC_WORKFLOW_PREFIX
from devkit_spec.base.errors import (
    SpecError,
    WorkerBaseUnresolvedError,
    WorkerHeadUnresolvedError,
    WorkerScopeUnresolvedError,
    WorkerUnitUnresolvedError,
)
from devkit_spec.base.units import PROPOSAL_FILE, PROPOSAL_UNIT, SPEC_UNIT
from devkit_spec.features.delivery.usecases.attach import attach_check
from devkit_spec.features.entrypoints.repositories.bundle import parse_boundaries, parse_targets


def files(root: Path, revision: str, prefix: str = "") -> list[str]:
    return [
        p
        for p in run_git(root, "ls-tree", "-rz", "--name-only", revision, "--", prefix or ".")
        .decode("utf-8", errors="surrogateescape")
        .split("\0")
        if p
    ]


def read(root: Path, revision: str, path: str) -> str:
    return run_git(root, "show", f"{revision}:{path}").decode("utf-8")


def marker(root: Path, branch: str, key: str) -> str:
    try:
        return run_git_text(root, "config", "--get", f"branch.{branch}.{key}")
    except GitError as exc:
        if exc.returncode == 1:
            return ""
        raise


def records(root: Path, revision: str, unit: str) -> Envelopes:
    prefix = f"{unit}/envelopes/"
    return collect_envelopes(
        (Path(p).name, lambda p=p: read(root, revision, p))
        for p in files(root, revision, prefix)
        if "/" not in p.removeprefix(prefix) and is_envelope_name(Path(p).name)
    )


def added(root: Path, revision: str, path: str, error: type[SpecError]) -> str:
    commits = run_git_text(root, "log", "--format=%H", "--diff-filter=A", revision, "--", path).splitlines()
    if len(commits) != 1:
        raise error(f"{path} has {len(commits)} adding commits")
    return commits[0]


def prefix(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or any(c in value for c in "*?[]\\\x00"):
        raise WorkerScopeUnresolvedError(f"Scope entry is not a literal repository-relative path: {value!r}")
    return path.as_posix().rstrip("/")


NOT_APPLICABLE = ("n/a", "none")


def unit_path(root: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        try:
            value = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise WorkerUnitUnresolvedError("Unit is outside the worktree") from exc
    if ".." in PurePosixPath(value).parts or value in ("", "."):
        raise WorkerUnitUnresolvedError("Unit must name a directory within the worktree")
    return PurePosixPath(value).as_posix()


def derive_unit(root: Path, tip: str, branch: str | None) -> tuple[str, str]:
    if not branch:
        raise WorkerUnitUnresolvedError("Detached HEAD has no activity unit")
    marked = marker(root, branch, "devkitUnit")
    if marked:
        unit = unit_path(root, marked)
        if not files(root, tip, unit):
            raise WorkerUnitUnresolvedError(f"Marked unit {unit} is absent at HEAD")
        return unit, "branch.devkitUnit"
    if not branch.startswith(("dev-", "plan-")):
        raise WorkerUnitUnresolvedError(f"{branch} is not an activity branch")
    candidates = []
    for path in files(root, tip):
        directory, _, name = path.rpartition("/")
        if name not in ("spec.md", PROPOSAL_FILE):
            continue
        match = SPEC_UNIT.fullmatch(directory) or PROPOSAL_UNIT.fullmatch(directory)
        if match and match["slug"] == branch.split("-", 1)[1] and not attach_check(root, branch, directory, tip):
            candidates.append(directory)
    # A handed-off spec supersedes its carried proposal directory.
    specs = [p for p in candidates if SPEC_UNIT.fullmatch(p)]
    candidates = specs or candidates
    if len(candidates) != 1:
        raise WorkerUnitUnresolvedError(f"{branch} corresponds to {len(candidates)} committed units")
    return candidates[0], "activity-branch"


def derive_base(
    root: Path, tip: str, unit: str, workers: list[str], branch: str | None, base_checkout: Path | None
) -> tuple[str, str]:
    if len(workers) > 1:
        previous = added(root, tip, workers[-2], WorkerBaseUnresolvedError)
        loaded = records(root, previous, unit)
        if loaded.errors:
            raise WorkerBaseUnresolvedError("Previous committed envelopes are malformed")
        problems = loaded.unresolved_problems()
        if problems:
            bases = {e.diff_base for e in problems}
            if "" in bases or len(bases) != 1:
                raise WorkerBaseUnresolvedError("Unresolved problems have missing or conflicting range bases")
            return bases.pop(), "previous-blocked-range"
        return previous, "previous-worker-commit"
    base_branch = marker(root, branch, "devkitBase") if branch else ""
    if not base_branch and base_checkout:
        base_branch = run_git_text(base_checkout, "symbolic-ref", "--quiet", "--short", "HEAD")
    if not base_branch or base_branch == branch:
        raise WorkerBaseUnresolvedError("No distinct base branch is recorded")
    bases = run_git_text(root, "merge-base", "--all", tip, base_branch).splitlines()
    if len(bases) != 1:
        raise WorkerBaseUnresolvedError("The base branch has no single merge base")
    return bases[0], "branch-merge-base"


def derive_scope(root: Path, tip: str, unit: str) -> list[dict[str, Any]]:
    paths = files(root, tip)
    anchor = f"{unit}/spec.md" if f"{unit}/spec.md" in paths else f"{unit}/{PROPOSAL_FILE}"
    text = read(root, tip, anchor)
    workflow = (parse(text).data or {}).get("workflow", "")
    entries: list[dict[str, Any]] = [{"path": unit, "source": "unit"}]
    if workflow == PROPOSAL_WORKFLOW:
        return entries
    if not isinstance(workflow, str) or not workflow.startswith(SPEC_WORKFLOW_PREFIX):
        raise WorkerScopeUnresolvedError(f"Unsupported workflow: {workflow}")
    for task in parse_boundaries(read(root, tip, f"{unit}/tasks.md")):
        entries.extend(
            {"path": prefix(p), "source": "boundary", "task": task.index}
            for p in task.values
            if p.strip().lower() not in NOT_APPLICABLE
        )
    parts = PurePosixPath(unit).parts
    entries.append({"path": str(PurePosixPath(*parts[:-3], "docs", "materials", *parts[-2:])), "source": "materials"})
    for target in parse_targets(read(root, tip, f"{unit}/reconcile.md"), f"{unit}/reconcile.md"):
        if target.file.strip():
            entries.append({"path": prefix(target.file.strip()), "source": "reconcile"})
    section = re.search(r"(?im)^## [^\n]*Source feedback[^\n]*\n(.*?)(?=^## |\Z)", text, re.DOTALL)
    for identifier in sorted(set(re.findall(r"\bFB-[a-z0-9-]+", section[1] if section else ""))):
        matches = []
        for path in paths:
            if (
                "/feedback/" in path
                and path.endswith(".md")
                and Path(path).stem == identifier.removeprefix("FB-")
                and (parse(read(root, tip, path)).data or {}).get("id") == identifier
            ):
                matches.append(path)
        if len(matches) != 1:
            raise WorkerScopeUnresolvedError(f"{identifier} resolves to {len(matches)} feedback files")
        if (parse(read(root, tip, matches[0])).data or {}).get("status") == "open":
            entries.append({"path": matches[0], "source": "source-feedback", "id": identifier})
    return entries


def inputs(
    root: Path, unit: str | None, base: str | None, head: str | None, base_checkout: str | None
) -> tuple[Path, str, dict[str, Any]]:
    position = locate(root)
    root = position.root
    tip = run_git_text(root, "rev-parse", "HEAD")
    checkout = Path(base_checkout).resolve() if base_checkout else position.base if position.linked else None
    chosen_unit, unit_source = (unit_path(root, unit), "argument") if unit else derive_unit(root, tip, position.branch)
    if not files(root, tip, chosen_unit):
        raise WorkerUnitUnresolvedError(f"{chosen_unit} does not exist in committed HEAD")
    workers = sorted(
        (p for p in files(root, tip, f"{chosen_unit}/envelopes/") if re.fullmatch(r"worker-\d+\.yaml", Path(p).name)),
        key=lambda p: int(Path(p).stem.split("-")[-1]),
    )
    if head:
        chosen_head, head_source = head, "argument"
    elif workers:
        chosen_head, head_source = added(root, tip, workers[-1], WorkerHeadUnresolvedError), "latest-worker-commit"
    else:
        raise WorkerHeadUnresolvedError("No committed worker envelope")
    try:
        chosen_base, base_source = (
            (base, "argument") if base else derive_base(root, tip, chosen_unit, workers, position.branch, checkout)
        )
    except GitError as exc:
        raise WorkerBaseUnresolvedError(exc.message) from exc
    resolved = {}
    for name, value, source in (
        ("unit", chosen_unit, unit_source),
        ("base", chosen_base, base_source),
        ("head", chosen_head, head_source),
    ):
        if name != "unit":
            try:
                value = run_git_text(root, "rev-parse", "--verify", "--end-of-options", f"{value}^{{commit}}")
            except GitError as exc:
                raise ArgumentError(
                    f"Unknown {name} commit: {value}", fix=f"Pass --{name} with a valid commit"
                ) from exc
        resolved[name] = {"value": value, "source": source}
    resolved["base_checkout"] = {
        "value": str(checkout) if checkout else None,
        "source": "argument" if base_checkout else "registered-worktree" if checkout else "base-checkout",
    }
    return root, tip, resolved
