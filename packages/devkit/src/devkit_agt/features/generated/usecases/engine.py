"""Regenerate, check and settle generated artifacts in a Git checkout.

``resolve`` settles the conflicts of an operation in progress (merge, rebase, cherry-pick, revert, ``am``, or any
command that left unmerged paths) whose paths an artifact owns: each such path gets the artifact's ``seed`` side
(or is removed, when that side deleted it), the artifacts and the artifacts after them run their commands in
order, and the conflicted and changed paths are staged. It never commits and never touches a conflict no artifact
owns. ``regenerate`` runs the commands in place and stages nothing; ``check`` runs them in a temporary detached
worktree of a commit and reports the artifacts whose files differ from it, leaving the checkout as it was.

Every command runs through ``devkit_agt.features.compact.run_command`` (``sh -c``, from the project root, the full output in a
log file); a command that changes a file outside its artifact's ``paths`` and ``updates`` is
``GENERATED_OUTPUT_UNDECLARED``. Paths in results are relative to the top level of the work tree, as Git prints them.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import shutil
import stat
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from devkit.advisory import AdvisoryError, Level
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import ArgumentError, GitError, run_git
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.repositories.project import require_git_toplevel

from devkit_agt.features.compact import CommandRun, run_command
from devkit_agt.features.generated.models.errors import (
    CommandFailedError,
    ConflictsRemainWarning,
    InputsConflictedError,
    OutputUndeclaredError,
    UnmergedError,
)
from devkit_agt.features.generated.repositories.registry import PROJECT_FILE, Artifact, Registry, load_registry

# The command that continues each operation once no unmerged path is left.
CONTINUE = {
    "merge": "git merge --continue",
    "rebase": "git rebase --continue",
    "cherry-pick": "git cherry-pick --continue",
    "revert": "git revert --continue",
    "am": "git am --continue",
}
LISTED = 20  # paths listed in an advisory's details
TAIL_LINES = 10  # last output lines shown for a failed command
WORKTREE_TIMEOUT = 300.0  # seconds for checking out the temporary worktree of `check`


@dataclass(frozen=True)
class Checkout:
    """A devkit project inside a Git work tree: ``prefix`` is ``root`` relative to ``top`` (``""`` when equal)."""

    root: Path
    top: Path
    prefix: str = ""

    def project_path(self, path: str) -> str | None:
        """``path`` (relative to ``top``) relative to the project root; ``None`` outside the project."""
        if not self.prefix:
            return path
        head = f"{self.prefix}/"
        return path.removeprefix(head) if path.startswith(head) else None


def open_checkout(root: Path) -> Checkout:
    top = require_git_toplevel(root)
    root = root.resolve()
    return Checkout(root, top, root.relative_to(top).as_posix() if root != top else "")


@dataclass(frozen=True)
class ArtifactRun:
    """One artifact of a run: the conflicts it settled, the files its command changed, or why it was skipped.

    ``owned`` is the part of ``changed`` the artifact owns (its ``paths``); the rest are files it ``updates``.
    """

    id: str
    command: str
    conflicts: tuple[str, ...] = ()
    changed: tuple[str, ...] = ()
    skipped: bool = False  # optional, and none of its paths is tracked
    owned: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "command": self.command,
            "conflicts": list(self.conflicts),
            "changed": list(self.changed),
            "skipped": self.skipped,
        }


@dataclass
class ResolveResult:
    """``operation`` is the Git operation in progress (``None`` when none is known); ``remaining`` the conflicts
    left after the run, which no artifact owns. A dry run changed nothing and ran no command."""

    operation: str | None
    dry_run: bool = False
    artifacts: list[ArtifactRun] = field(default_factory=list)
    remaining: list[str] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)

    @property
    def next_command(self) -> str | None:
        """The command that continues the operation, once nothing is left to resolve."""
        if self.dry_run or self.remaining or self.operation is None:
            return None
        return CONTINUE.get(self.operation)

    def to_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "dry_run": self.dry_run,
            "artifacts": [item.to_dict() for item in self.artifacts],
            "remaining": list(self.remaining),
            "next_command": self.next_command,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass
class RunResult:
    """What ``regenerate`` or ``check`` ran; ``commit`` is the commit ``check`` checked (``None`` for regenerate)."""

    artifacts: list[ArtifactRun] = field(default_factory=list)
    commit: str | None = None

    @property
    def stale(self) -> list[ArtifactRun]:
        """The artifacts whose command changed a file they own; a change to a file they only update is not stale."""
        return [item for item in self.artifacts if item.owned]

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {"artifacts": [item.to_dict() for item in self.artifacts]}
        if self.commit is not None:
            data["commit"] = self.commit
            data["stale"] = [item.id for item in self.stale]
        return data


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="surrogateescape")


def _literal(paths: Iterable[str]) -> list[str]:
    return [f":(literal){path}" for path in paths]


def _listed(paths: Sequence[str]) -> list[str]:
    extra = len(paths) - LISTED
    return [*paths[:LISTED], *([f"... and {extra} more"] if extra > 0 else [])]


def unmerged(top: Path) -> dict[str, frozenset[int]]:
    """The unmerged paths of the index and the stages each has (``1`` base, ``2`` ours, ``3`` theirs)."""
    stages: dict[str, set[int]] = {}
    for record in run_git(top, "ls-files", "--unmerged", "-z").split(b"\0"):
        if record:
            meta, _, path = record.partition(b"\t")
            stages.setdefault(_decode(path), set()).add(int(meta.split()[2]))
    return {path: frozenset(found) for path, found in stages.items()}


def operation(top: Path) -> str | None:
    """The Git operation in progress in the work tree at ``top``, from its Git directory's state files."""
    git_dir = Path(os.fsdecode(run_git(top, "rev-parse", "--absolute-git-dir").rstrip(b"\n")))
    if (git_dir / "rebase-merge").is_dir():
        return "rebase"
    if (git_dir / "rebase-apply").is_dir():
        return "am" if (git_dir / "rebase-apply" / "applying").exists() else "rebase"
    for name, kind in (("MERGE_HEAD", "merge"), ("CHERRY_PICK_HEAD", "cherry-pick"), ("REVERT_HEAD", "revert")):
        if (git_dir / name).exists():
            return kind
    return None


def tracked(top: Path) -> set[str]:
    """The paths in the index of the work tree at ``top``."""
    return {_decode(path) for path in run_git(top, "ls-files", "-z").split(b"\0") if path}


def _digest(path: Path) -> str:
    try:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            return f"link:{os.readlink(path)}"
        if stat.S_ISREG(info.st_mode):
            return f"{info.st_mode & 0o111:o}:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        return "other"
    except FileNotFoundError:
        return "-"


def snapshot(top: Path) -> dict[str, tuple[str, str]]:
    """Every path ``git status`` lists (ignored files excepted) with its status and content digest.

    Comparing two snapshots names exactly the paths a command changed, also among files that were already dirty.
    """
    fields = iter(run_git(top, "status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0"))
    found: dict[str, tuple[str, str]] = {}
    for entry in fields:
        if len(entry) < 4:
            continue
        status = entry[:2]
        if b"R" in status or b"C" in status:
            next(fields, None)  # the rename's source path
        path = _decode(entry[3:])
        found[path] = (_decode(status), _digest(top / path))
    return found


def _failure_details(run: CommandRun) -> list[str]:
    found = run.scan
    lines = [f"exit={run.exit_code}  log={run.log}"]
    lines += [f"  summary: {summary}" for summary in found.summaries]
    shown = set(found.summaries)
    tail = [line for line in found.output.splitlines() if line.strip() and line not in shown][-TAIL_LINES:]
    lines += [f"  | {line}" for line in tail]
    lines += [
        f"  > {line}" for item in found.advisories if item.level is Level.ERROR for line in item.text.splitlines()
    ]
    return lines


def _regenerate(checkout: Checkout, artifact: Artifact) -> tuple[str, ...]:
    """Run ``artifact``'s command in ``checkout`` and return the paths it changed, all within its declared files."""
    before = snapshot(checkout.top)
    run = run_command(["sh", "-c", artifact.shell], cwd=checkout.root, slow_after=0)
    if not run.passed:
        raise CommandFailedError(
            f"{artifact.id}: {artifact.command} failed",
            *_failure_details(run),
            fix=f"Fix what the command reports (the log has the full output), then rerun; "
            f"the command is set in [artifacts.{artifact.id}] of .devkit/generated.toml",
        )
    after = snapshot(checkout.top)
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    undeclared = [
        path for path in changed if (rel := checkout.project_path(path)) is None or not artifact.may_write(rel)
    ]
    if undeclared:
        raise OutputUndeclaredError(
            f"{artifact.id}: {artifact.command} changed {len(undeclared)} file(s) outside its paths and updates;"
            " the changes are left in the work tree and nothing was staged",
            *_listed(undeclared),
            fix=f"Review the changes (git status); declare these files under paths or updates of "
            f"[artifacts.{artifact.id}] in .devkit/generated.toml, or change the command so it writes only its files",
        )
    return tuple(changed)


def _skipped(checkout: Checkout, artifact: Artifact, files: set[str]) -> bool:
    """An optional artifact none of whose paths is among ``files`` (the tracked paths) is skipped."""
    if not artifact.optional:
        return False
    return not any((rel := checkout.project_path(path)) is not None and artifact.owns(rel) for path in files)


def _plan(
    registry: Registry, ids: Sequence[str], *, working: Path | None = None, rev: str = ""
) -> tuple[Artifact, ...]:
    """The artifacts ``ids`` name, with the ones they depend on; all of them when ``ids`` is empty.

    ``working`` is the project root of the working tree when ``registry`` was read at ``rev``: an unknown ID that its
    registry declares is named as not committed, so the refusal does not contradict ``devkit generated list``. The
    lookup is best effort: a working-tree registry that cannot be read leaves the plain unknown-ID refusal.
    """
    unknown = [artifact_id for artifact_id in ids if registry.get(artifact_id) is None]
    if unknown and working is not None:
        try:
            pending: Registry | None = load_registry(working)
        except ConfigError:
            pending = None
        uncommitted = [artifact_id for artifact_id in unknown if pending is not None and pending.get(artifact_id)]
        if uncommitted:
            raise ArgumentError(
                f"generated artifacts registered in the working tree but not at {rev}: {', '.join(uncommitted)}",
                target_files=[PROJECT_FILE],
                fix=f"Commit the {PROJECT_FILE} change, or pass --rev with a commit whose registry declares them",
            )
    if unknown:
        known = ", ".join(item.id for item in registry.artifacts) or "none"
        raise ArgumentError(
            f"unknown or disabled generated artifacts: {', '.join(unknown)}",
            target_files=list(unknown),
            fix=f"Pass ids that `devkit generated list` prints (registered: {known})",
        )
    return registry.closure(ids) if ids else registry.artifacts


class ResolveArtifacts(BaseUseCase):
    """Settle the conflicts whose paths a generated artifact owns, regenerate, and stage; see the module docstring."""

    def execute(self, root: Path, *, dry_run: bool = False) -> ResolveResult:
        """Settle the conflicts whose paths a generated artifact owns, regenerate, and stage; see the module docstring.

        Raises ``InputsConflictedError`` before any change when a conflict no artifact owns may be read or updated by
        an artifact to regenerate; ``CommandFailedError`` or ``OutputUndeclaredError`` when a command fails or writes outside its
        files, with nothing staged (rerunning starts over from the same conflicts).
        """
        checkout = open_checkout(root)
        registry = load_registry(checkout.root)
        result = ResolveResult(operation(checkout.top), dry_run=dry_run)
        conflicts = unmerged(checkout.top)
        owned: dict[str, list[str]] = {}
        unowned: list[str] = []
        for path in sorted(conflicts):
            rel = checkout.project_path(path)
            owner = registry.owner(rel) if rel is not None else None
            if owner is None:
                unowned.append(path)
            else:
                owned.setdefault(owner.id, []).append(path)
        plan = registry.closure(owned)
        readers: dict[str, list[str]] = {}
        for path in unowned:
            rel = checkout.project_path(path)
            for artifact in plan:
                # A file the artifact updates is read too: its command rewrites it in place, conflict markers included.
                if not artifact.inputs or (rel is not None and (artifact.may_read(rel) or artifact.may_write(rel))):
                    readers.setdefault(path, []).append(artifact.id)
        if readers:
            raise InputsConflictedError(
                f"{len(readers)} conflict(s) no artifact owns may be read by the artifacts to regenerate; nothing was changed",
                *_listed([f"{path}: read by {', '.join(ids)}" for path, ids in readers.items()]),
                target_files=list(readers)[:LISTED],
            )
        files = tracked(checkout.top) if any(item.optional for item in plan) else set()
        runs = [
            ArtifactRun(
                item.id,
                item.command,
                conflicts=tuple(owned.get(item.id, ())),
                skipped=item.id not in owned and _skipped(checkout, item, files),
            )
            for item in plan
        ]
        if dry_run:
            result.artifacts, result.remaining = runs, unowned
            return result
        _seed(checkout, plan, owned, conflicts)
        staged: set[str] = {path for paths in owned.values() for path in paths}
        for index, (artifact, run) in enumerate(zip(plan, runs, strict=True)):
            if not run.skipped:
                changed = _regenerate(checkout, artifact)
                runs[index] = ArtifactRun(run.id, run.command, run.conflicts, changed)
                staged.update(changed)
        _stage(checkout.top, sorted(staged))
        result.artifacts = runs
        result.remaining = sorted(unmerged(checkout.top))
        if result.remaining:
            result.notices.append(
                ConflictsRemainWarning(
                    f"{len(result.remaining)} conflict(s) no artifact owns remain", *_listed(result.remaining)
                )
            )
        return result


def _seed(
    checkout: Checkout, plan: Sequence[Artifact], owned: dict[str, list[str]], conflicts: dict[str, frozenset[int]]
) -> None:
    """Leave each owned conflict at its artifact's ``seed`` side: that side's file, or none where it deleted it."""
    for artifact in plan:
        paths = owned.get(artifact.id, [])
        stage = 2 if artifact.seed == "ours" else 3
        kept = [path for path in paths if stage in conflicts[path]]
        if kept:
            run_git(checkout.top, "checkout", f"--{artifact.seed}", "--", *_literal(kept))
        for path in paths:
            target = checkout.top / path
            if stage not in conflicts[path] and (target.is_symlink() or target.is_file()):
                target.unlink()


def _stage(top: Path, paths: Sequence[str]) -> None:
    present = [path for path in paths if os.path.lexists(top / path)]
    absent = [path for path in paths if not os.path.lexists(top / path)]
    if present:
        run_git(top, "add", "--", *_literal(present))
    if absent:
        run_git(top, "rm", "--cached", "--quiet", "--ignore-unmatch", "--", *_literal(absent))


class RegenerateArtifacts(BaseUseCase):
    """Run the commands of ``ids`` and the artifacts after them (every artifact when empty) in place; stage nothing."""

    def execute(self, root: Path, ids: Sequence[str] = ()) -> RunResult:
        """Run the commands of ``ids`` and the artifacts after them (every artifact when empty) in place; stage nothing.

        Raises ``UnmergedError`` when the index has unmerged paths: a command would read conflict markers.
        """
        checkout = open_checkout(root)
        plan = _plan(load_registry(checkout.root), ids)
        conflicts = sorted(unmerged(checkout.top))
        if conflicts:
            raise UnmergedError(f"{len(conflicts)} unmerged path(s); nothing ran", *_listed(conflicts))
        return RunResult(_run_all(checkout, plan))


def _run_all(checkout: Checkout, plan: Sequence[Artifact]) -> list[ArtifactRun]:
    files = tracked(checkout.top)
    runs: list[ArtifactRun] = []
    for artifact in plan:
        if _skipped(checkout, artifact, files):
            runs.append(ArtifactRun(artifact.id, artifact.command, skipped=True))
        else:
            changed = _regenerate(checkout, artifact)
            owned = tuple(
                path for path in changed if (rel := checkout.project_path(path)) is not None and artifact.owns(rel)
            )
            runs.append(ArtifactRun(artifact.id, artifact.command, changed=changed, owned=owned))
    return runs


class CheckArtifacts(BaseUseCase):
    """Regenerate in a temporary detached worktree of ``rev`` and report the artifacts that differ from it."""

    def execute(self, root: Path, ids: Sequence[str] = (), *, rev: str = "HEAD") -> RunResult:
        """Regenerate in a temporary detached worktree of ``rev`` and report the artifacts that differ from it.

        The registry is read from that commit; the checkout is left as it was. An artifact is stale when its command
        changed one of the files it owns there (``RunResult.stale``); a change to a file it only ``updates`` is
        reported in ``changed`` but is not stale.
        """
        checkout = open_checkout(root)
        try:
            commit = _decode(run_git(checkout.top, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}").strip())
        except GitError as exc:
            raise ArgumentError(
                f"--rev {rev}: not a commit", target_files=["--rev"], fix="Pass a commit, branch or tag"
            ) from exc
        temporary = Path(tempfile.mkdtemp(prefix="devkit-generated-"))
        tree = temporary / checkout.top.name
        try:
            run_git(checkout.top, "worktree", "add", "--detach", "--quiet", str(tree), commit, timeout=WORKTREE_TIMEOUT)
            clone = Checkout(tree / checkout.prefix if checkout.prefix else tree, tree, checkout.prefix)
            plan = _plan(load_registry(clone.root), ids, working=checkout.root, rev=rev)
            return RunResult(_run_all(clone, plan), commit=commit)
        finally:
            with contextlib.suppress(GitError):
                run_git(checkout.top, "worktree", "remove", "--force", str(tree))
            shutil.rmtree(temporary, ignore_errors=True)


class ListArtifacts(BaseUseCase):
    """Return built-in and project artifacts in their effective registration order."""

    def execute(self, root: Path) -> tuple[Artifact, ...]:
        """Return built-in and project artifacts in their effective registration order."""
        return load_registry(root).artifacts
