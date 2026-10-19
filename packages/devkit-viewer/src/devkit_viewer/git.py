"""Read one repository's committed content through Git at any local ref.

Every read names a commit and a repository-relative path; Git resolves the path inside that commit's tree, so no
file outside the repository, and no uncommitted file, is ever reachable. Nothing here fetches, checks out or
writes: the working tree and ``HEAD`` are never touched.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit.core.errors import GitError
from devkit.core.git import run_git

from devkit_viewer.errors import git_failed, path_invalid, path_not_found, ref_unknown


@dataclass(frozen=True)
class TreeItem:
    """One entry of a directory at a ref: ``type`` is ``tree`` or ``blob``; ``size`` is in bytes, blobs only."""

    name: str
    path: str
    type: str
    size: int | None = None

    def as_json(self) -> dict[str, object]:
        data: dict[str, object] = {"name": self.name, "path": self.path, "type": self.type}
        if self.size is not None:
            data["size"] = self.size
        return data


def _decode(data: bytes) -> str:
    return data.decode("utf-8", errors="surrogateescape")


def check_path(path: str) -> str:
    """``path`` when it is repository-relative (empty for the root); ``VIEWER_PATH_INVALID`` otherwise."""
    if path == "":
        return path
    if path.startswith("/") or "\\" in path or "\0" in path:
        raise path_invalid(path)
    if any(part in ("", ".", "..") for part in path.split("/")):
        raise path_invalid(path)
    return path


class GitReader:
    """Reads of the Git repository whose work tree top level is ``root``."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _git(self, *args: str) -> bytes:
        try:
            return run_git(self.root, *args)
        except GitError as exc:
            raise git_failed(exc.stderr or str(exc)) from exc

    # Branch names are always full (``refs/heads/`` stripped, never Git's ``--short`` form): a branch a tag of the same
    # name shadows would be abbreviated to ``heads/<name>``, which ``commit`` would not find.
    def default_branch(self) -> str:
        """The branch checked out in this work tree; ``HEAD`` when it is detached."""
        try:
            ref = _decode(run_git(self.root, "symbolic-ref", "--quiet", "HEAD")).strip()
        except GitError:
            return "HEAD"
        return ref.removeprefix("refs/heads/")

    def branches(self) -> list[str]:
        """Every local branch, sorted; remote-tracking branches are not listed."""
        out = self._git("for-each-ref", "--format=%(refname:lstrip=2)", "refs/heads")
        return sorted(line for line in _decode(out).splitlines() if line)

    def commit(self, ref: str) -> str:
        """The full commit ID of the local branch named exactly ``ref``, or of ``HEAD``; ``VIEWER_REF_UNKNOWN``
        otherwise.

        A remote-tracking branch, a tag, a commit ID or a revision expression (``main~1``) is unknown, and a ref that
        looks like an option never reaches Git as one.
        """
        if not ref or ref.startswith("-") or "\0" in ref:
            raise ref_unknown(ref)
        try:
            if ref == "HEAD":
                out = run_git(self.root, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
            else:
                out = run_git(self.root, "show-ref", "--verify", "--hash", f"refs/heads/{ref}")
        except GitError as exc:
            raise ref_unknown(ref) from exc
        return _decode(out).strip()

    def _type(self, commit: str, path: str) -> str | None:
        if path == "":
            return "tree"
        try:
            return _decode(run_git(self.root, "cat-file", "-t", f"{commit}:{path}")).strip()
        except GitError:
            return None

    def tree(self, ref: str, path: str) -> list[TreeItem]:
        """The entries of the directory ``path`` at ``ref``, directories first, then by name."""
        path = check_path(path)
        commit = self.commit(ref)
        if self._type(commit, path) != "tree":
            raise path_not_found(path, "directory")
        args = ["ls-tree", "-l", "-z", commit]
        if path:
            args += ["--", f"{path}/"]
        items: list[TreeItem] = []
        for record in _decode(self._git(*args)).split("\0"):
            if not record:
                continue
            meta, _, entry = record.partition("\t")
            _mode, kind, _object, size = meta.split(maxsplit=3)
            if kind not in ("tree", "blob"):
                continue  # a submodule (``commit``) has no content in this repository
            items.append(
                TreeItem(
                    name=entry.rsplit("/", 1)[-1],
                    path=entry,
                    type=kind,
                    size=int(size) if kind == "blob" else None,
                )
            )
        return sorted(items, key=lambda item: (item.type != "tree", item.name))

    def blob(self, ref: str, path: str) -> bytes:
        """The bytes of the file ``path`` at ``ref``."""
        path = check_path(path)
        commit = self.commit(ref)
        if not path or self._type(commit, path) != "blob":
            raise path_not_found(path, "file")
        return self._git("cat-file", "blob", f"{commit}:{path}")
