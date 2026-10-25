"""Checkout declaration operations and Git scope observations."""

from __future__ import annotations

from pathlib import Path

from devkit_core.core import GitError, run_git

from devkit_spec.base.errors import EntrypointsPathError
from devkit_spec.features.entrypoints import normalize
from devkit_spec.features.proposals.usecases.scaffold import clean_slug
from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import ScopePath, ScopeSet, Source, Stage, Unresolved
from devkit_spec.features.scope.repositories.git import git_lines
from devkit_spec.features.scope.services.declarations import from_proposal as declared_proposal
from devkit_spec.features.scope.services.declarations import from_spec as declared_spec
from devkit_spec.features.scope.services.declarations import kind_of


def from_proposal(root: Path, slug: str) -> ScopeSet:
    return declared_proposal(root, clean_slug(slug))


def _fork_point(root: Path, base_ref: str, deadline: Deadline) -> str:
    """``git merge-base <base_ref> HEAD``; ``""`` when the ref does not resolve or shares no history with HEAD."""
    try:
        return run_git(root, "merge-base", base_ref, "HEAD", deadline=deadline).decode().strip()
    except GitError as exc:
        if exc.returncode is None:
            raise
        return ""


def _is_ancestor(root: Path, ancestor: str, descendant: str, deadline: Deadline) -> bool:
    """``git merge-base --is-ancestor``; ``False`` also when Git does not know either commit."""
    try:
        run_git(root, "merge-base", "--is-ancestor", ancestor, descendant, deadline=deadline)
    except GitError as exc:
        if exc.returncode is None:
            raise
        return False
    return True


def observe_git(
    root: Path, base_revision: str, deadline: Deadline, first_seen: str, *, base_ref: str = ""
) -> tuple[list[ScopePath], list[Unresolved]]:
    """The paths changed in the worktree at ``root``: the committed range, staged, unstaged and untracked.

    The committed range starts where ``HEAD`` forks from the branch ``base_ref`` (``git merge-base``), so what the
    task merged or rebased in from that branch is not observed while its own changes and conflict resolutions are. It
    is never wider than ``base_revision..HEAD``, so a ``base_ref`` that is not the branch the task forked from (the
    base checkout was on another branch at registration) cannot pull another branch's commits in: the range is
    ``<fork point>..HEAD`` when ``base_revision`` is the fork point or its ancestor, ``base_revision..HEAD`` when the
    fork point predates ``base_revision``, and only the paths both ranges change when neither is the other's
    ancestor (the task registered after its own commits, then merged its base branch). Without ``base_ref`` it is
    ``base_revision..HEAD``; a ``base_ref`` that does not resolve or shares no history with ``HEAD`` (a shallow clone)
    falls back to ``base_revision`` and is unresolved (``missing-base-ref``). An empty or unknown ``base_revision``
    skips the committed range and is unresolved, unless an empty one has a fork point to start from. Paths are
    relative to ``root`` and limited to it. Renames are not detected, so a moved file contributes both its old and its
    new path. A path outside the entrypoint path contract (a glob character or a colon in its name) is left out.
    Raises ``ScopeTimeoutError`` when the deadline passes and ``GitError`` when Git fails otherwise.
    """
    seen: set[str] = set()
    observed: list[ScopePath] = []
    unresolved: list[Unresolved] = []

    def add(paths: list[str]) -> None:
        for raw in paths:
            try:
                path = normalize(raw)
            except EntrypointsPathError:
                continue
            if path not in seen:
                seen.add(path)
                observed.append(ScopePath(path, kind_of(root, path), Source.OBSERVED, Stage.BUILD, first_seen))

    start, diverged = base_revision, ""
    if base_ref:
        fork = _fork_point(root, base_ref, deadline)
        if not fork:
            unresolved.append(Unresolved(base_ref, "missing-base-ref", Source.OBSERVED))
        elif not base_revision or _is_ancestor(root, base_revision, fork, deadline):
            start = fork  # no wider than base_revision..HEAD: the fork point is base_revision or descends from it
        elif not _is_ancestor(root, fork, base_revision, deadline):
            diverged = fork  # base_revision is a task-side commit and the task merged base_ref in since
    changed = ("diff", "--name-only", "--no-renames", "-z", "--relative")
    if not start:
        unresolved.append(Unresolved("", "missing-base-revision", Source.OBSERVED))
    else:
        try:
            committed = git_lines(root, *changed, f"{start}..HEAD", deadline=deadline)
        except GitError as exc:
            if exc.returncode is None:
                raise
            unresolved.append(Unresolved(start, "unknown-base-revision", Source.OBSERVED))
        else:
            if diverged:  # what HEAD no longer differs in from the fork point came in from base_ref
                since_fork = set(git_lines(root, *changed, f"{diverged}..HEAD", deadline=deadline))
                committed = [path for path in committed if path in since_fork]
            add(committed)
    add(git_lines(root, *changed, "--cached", deadline=deadline))
    add(git_lines(root, *changed, deadline=deadline))
    add(git_lines(root, "ls-files", "-z", "--others", "--exclude-standard", deadline=deadline))
    observed.sort(key=lambda path: path.path)
    return observed, unresolved


def from_spec(root: Path, spec_dir: str) -> ScopeSet:
    return declared_spec(root, spec_dir)
