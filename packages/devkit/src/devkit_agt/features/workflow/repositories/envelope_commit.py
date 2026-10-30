"""Git and filesystem boundary for single-envelope commits; never resets or retries."""

from __future__ import annotations

import os
from pathlib import Path

from devkit_core.core import GitError, run_git

from devkit_agt.features.workflow.models.errors import (
    EnvelopeCommitFailedError,
    EnvelopeCommitInvalidError,
    EnvelopeCommitStateError,
    EnvelopeCommitUncertainError,
)


class EnvelopeCommitRepository:
    """Use the normal index and ordinary hooks/signing in one attached Git worktree."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def git(self, *args: str, input: bytes | None = None) -> bytes:
        return run_git(self.root, "--literal-pathspecs", *args, input=input)

    def head(self) -> str:
        return self.git("rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()

    def state(self) -> str:
        """Refuse alternate indices, detached/unborn HEAD and operation markers before staging."""
        if "GIT_INDEX_FILE" in os.environ:
            raise EnvelopeCommitStateError("GIT_INDEX_FILE is supplied; use the normal worktree index")
        try:
            root = Path(self.git("rev-parse", "--show-toplevel").decode().strip()).resolve()
            if root != self.root:
                raise EnvelopeCommitStateError("Git repository identity differs from the requested workspace")
            self.git("symbolic-ref", "--quiet", "HEAD")
            head = self.head()
            git_dir = Path(self.git("rev-parse", "--absolute-git-dir").decode().strip())
            markers = (
                "MERGE_HEAD",
                "rebase-merge",
                "rebase-apply",
                "CHERRY_PICK_HEAD",
                "REVERT_HEAD",
                "sequencer",
                "index.lock",
            )
            present = [name for name in markers if (git_dir / name).exists()]
            if present or self.git("ls-files", "--unmerged", "-z"):
                raise EnvelopeCommitStateError(f"in-progress operation or locked/unmerged index: {present}")
            return head
        except GitError as exc:
            raise EnvelopeCommitStateError(str(exc)) from exc

    def regular_path(self, path: Path) -> None:
        """Refuse symlinks in every component and resolved paths outside this worktree."""
        try:
            rel = path.relative_to(self.root)
        except ValueError as exc:
            raise EnvelopeCommitInvalidError("Unit/file is outside this Git worktree") from exc
        current = self.root
        for part in rel.parts:
            current /= part
            if current.is_symlink():
                raise EnvelopeCommitInvalidError(f"symlink is unsupported: {current}")
        if not path.is_file():
            raise EnvelopeCommitInvalidError(f"not an existing regular file: {path}")

    def tree_entry(self, revision: str, path: str) -> tuple[str, str] | None:
        data = self.git("ls-tree", "-z", revision, "--", path)
        if not data:
            return None
        metadata, name = data.removesuffix(b"\0").split(b"\t", 1)
        mode, kind, blob = metadata.decode("ascii").split()
        if name.decode("utf-8", "surrogateescape") != path or kind != "blob" or mode not in {"100644", "100755"}:
            raise EnvelopeCommitInvalidError(f"not a tracked regular file: {path}")
        return mode, blob

    def blob(self, oid: str) -> bytes:
        return self.git("cat-file", "blob", oid)

    def dirty(self) -> dict[str, str]:
        data = self.git(
            "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignore-submodules=none", "--no-renames"
        )
        return {
            item[3:].decode("utf-8", "surrogateescape"): item[:2].decode("ascii") for item in data.split(b"\0") if item
        }

    def index_blob(self, path: str) -> bytes | None:
        data = self.git("ls-files", "--stage", "-z", "--", path)
        if not data:
            return None
        entries = data.removesuffix(b"\0").split(b"\0")
        if len(entries) != 1:
            raise EnvelopeCommitInvalidError("selected envelope has unmerged index entries")
        mode, oid, stage = entries[0].split(b"\t", 1)[0].decode("ascii").split()
        if stage != "0" or mode not in {"100644", "100755"}:
            raise EnvelopeCommitInvalidError("selected envelope must be a regular stage-0 file")
        return self.blob(oid)

    def preflight(self, path: str, content: bytes, head: str) -> bool:
        """Return True only for an unchanged committed record; allow identical staged additions."""
        dirty = self.dirty()
        unrelated = sorted(set(dirty) - {path})
        if unrelated:
            raise EnvelopeCommitStateError(f"other dirty paths: {unrelated}", target_files=unrelated)
        try:
            run_git(
                self.root,
                "check-ignore",
                "--quiet",
                "--no-index",
                "--stdin",
                "-z",
                input=path.encode("utf-8", "surrogateescape") + b"\0",
            )
        except GitError as exc:
            if exc.returncode != 1:
                raise
        else:
            raise EnvelopeCommitInvalidError("selected envelope is ignored by Git")
        entry = self.tree_entry(head, path)
        if entry:
            if not dirty and self.blob(entry[1]) == content:
                return True
            raise EnvelopeCommitInvalidError("modified historical envelopes cannot be committed")
        if dirty.get(path) not in {"??", "A "}:
            raise EnvelopeCommitInvalidError("selected envelope must be new, with no partial staging")
        indexed = self.index_blob(path)
        if indexed is not None and indexed != content:
            raise EnvelopeCommitInvalidError("partially staged envelope; index bytes differ from worktree bytes")
        return False

    def commit(self, path: str, content: bytes, before: str, subject: str, body: str) -> str:
        """Recheck preconditions; preserve every observed resource after a mutation attempt."""
        target = self.root / path
        if self.state() != before or target.read_bytes() != content:
            raise EnvelopeCommitStateError("HEAD or selected bytes changed before staging")
        self.preflight(path, content, before)
        staging = False
        try:
            self.git("add", "--", path)
            staging = True
            if (
                self.state() != before
                or self.dirty() != {path: "A "}
                or self.index_blob(path) != content
                or target.read_bytes() != content
            ):
                raise EnvelopeCommitUncertainError("preconditions changed after staging")
            self.git("commit", "-m", subject, "-m", body)
            after = self.head()
            parents = self.git("rev-list", "--parents", "-n", "1", after).decode("ascii").split()
            changes = self.git(
                "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", "-z", before, after
            )
            expected = b"A\0" + path.encode("utf-8", "surrogateescape") + b"\0"
            entry = self.tree_entry(after, path)
            if (
                parents != [after, before]
                or changes != expected
                or entry is None
                or self.blob(entry[1]) != content
                or self.dirty()
                or target.read_bytes() != content
                or self.state() != after
            ):
                raise EnvelopeCommitUncertainError(
                    "postconditions failed: parent, added path/blob or clean state differs"
                )
            return after
        except (
            GitError,
            KeyboardInterrupt,
            OSError,
            EnvelopeCommitStateError,
            EnvelopeCommitInvalidError,
            EnvelopeCommitUncertainError,
        ) as exc:
            try:
                after = self.head()
                dirty = self.dirty()
                retained = target.read_bytes() == content
                index = self.index_blob(path)
                known = after == before and retained and set(dirty) <= {path} and (index is None or index == content)
            except (GitError, OSError, EnvelopeCommitInvalidError):
                after, dirty, known = "unknown", {}, False
            detail = f"staging={'yes' if staging else 'attempted'} before={before} after={after} retained={path} dirty={dirty}"
            uncertain = (
                isinstance(exc, (EnvelopeCommitUncertainError, KeyboardInterrupt))
                or not known
                or (isinstance(exc, GitError) and exc.returncode is None)
            )
            error = EnvelopeCommitUncertainError if uncertain else EnvelopeCommitFailedError
            fix = (
                f"Inspect `git status --short`, `git log -2 --oneline` and `git diff HEAD -- {path}` before any retry"
                if uncertain
                else f"Fix the reported Git/hook/signing cause; retry this same envelope commit command for {path}, without authoring another record"
            )
            raise error(str(exc), detail, target_files=[path], fix=fix) from exc
