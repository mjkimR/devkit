"""Planning sources: the ``plan-<slug>`` worktrees and refs whose proposal directory overlays the checkout's.

A source is a worktree on ``plan-<slug>`` (read from its files), else the local branch ``plan-<slug>``, else the
remote-tracking ``<remote>/plan-<slug>`` whose remote sorts first. Each contributes only
``docs/proposals/PROP-<slug>/``. One scan starts ``git worktree list``, ``git for-each-ref`` and one
``git cat-file --batch``; nothing fetches or writes.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.git import run_git

from devkit_viewer.features.browse.models.errors import (
    ReadError,
    path_invalid,
    path_not_found,
    source_path_refused,
    source_unknown,
)
from devkit_viewer.features.browse.repositories.worktree import TreeItem, WorkingTreeReader, check_path

_SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_LOCAL = re.compile(r"refs/heads/plan-(?P<slug>[^/]+)")
_REMOTE = re.compile(r"refs/remotes/(?P<remote>[^/]+)/plan-(?P<slug>[^/]+)")
_SKIPPED_MODES = (b"120000", b"160000")  # symlinks and submodules are never served


@dataclass(frozen=True)
class PlanningSource:
    """One Planning source; ``commit`` is empty for a worktree, whose files are read instead."""

    id: str
    kind: str
    label: str
    slug: str
    commit: str = ""
    worktree: Path | None = None

    @property
    def directory(self) -> str:
        return f"docs/proposals/PROP-{self.slug}"

    @property
    def proposal(self) -> str:
        return f"{self.directory}/proposal.md"

    def as_json(self) -> dict[str, str]:
        return {"id": self.id, "kind": self.kind, "label": self.label, "slug": self.slug}


def _slug(value: str) -> str | None:
    return value if _SLUG.fullmatch(value) and ".." not in value else None


def _worktrees(root: Path) -> tuple[list[tuple[Path, str]], str | None]:
    """``(directory, slug)`` of every other existing worktree on a ``plan-*`` branch, and the checkout's own slug."""
    output = run_git(root, "worktree", "list", "--porcelain").decode("utf-8", errors="surrogateescape")
    found: list[tuple[Path, str]] = []
    own: str | None = None
    for block in output.split("\n\n"):
        path = branch = ""
        for line in block.splitlines():
            if line.startswith("worktree "):
                path = line.removeprefix("worktree ")
            elif line.startswith("branch "):
                branch = line.removeprefix("branch ")
        match = _LOCAL.fullmatch(branch)
        slug = _slug(match["slug"]) if match else None
        if not path or slug is None:
            continue
        directory = Path(path)
        try:
            if directory.resolve() == root:
                own = slug
                continue
            if not directory.is_dir():
                continue
        except OSError:
            continue
        found.append((directory, slug))
    return found, own


def planning_sources(root: Path) -> tuple[dict[str, PlanningSource], list[str]]:
    """The winning source of each slug by ID, and the enumeration failures.

    The checkout's own ``plan-<slug>``, known from the worktree list, has no source: the checkout already shows it.
    A branch or remote-tracking ref merged into the checkout's ``HEAD`` holds nothing newer and is skipped; a worktree
    stays a source, because it can hold saved, uncommitted edits.
    """
    root = root.resolve()
    errors: list[str] = []
    own: str | None = None
    by_slug: dict[str, PlanningSource] = {}
    try:
        worktrees, own = _worktrees(root)
        for directory, slug in sorted(worktrees, key=lambda item: (item[1], str(item[0]))):
            by_slug.setdefault(
                slug, PlanningSource(f"worktree:plan-{slug}", "worktree", f"worktree plan-{slug}", slug, "", directory)
            )
    except GitError as exc:
        errors.append(f"git worktree list: {exc}")
    try:
        output = run_git(
            root,
            "for-each-ref",
            "--no-merged=HEAD",
            "--format=%(refname)%00%(objectname)",
            "refs/heads/plan-*",
            "refs/remotes/*/plan-*",
        ).decode("utf-8", errors="surrogateescape")
    except GitError as exc:
        errors.append(f"git for-each-ref: {exc}")
        output = ""
    local: list[PlanningSource] = []
    remote: list[tuple[str, PlanningSource]] = []
    for line in output.splitlines():
        refname, _, commit = line.partition("\0")
        if (match := _LOCAL.fullmatch(refname)) and (slug := _slug(match["slug"])):
            local.append(PlanningSource(f"branch:plan-{slug}", "branch", f"plan-{slug}", slug, commit))
        elif (match := _REMOTE.fullmatch(refname)) and (slug := _slug(match["slug"])):
            name = f"{match['remote']}/plan-{slug}"
            remote.append((match["remote"], PlanningSource(f"remote:{name}", "remote", name, slug, commit)))
    for source in local:
        by_slug.setdefault(source.slug, source)
    for _, source in sorted(remote, key=lambda item: (item[1].slug, item[0])):
        by_slug.setdefault(source.slug, source)
    by_slug.pop(own or "", None)
    return {source.id: source for source in sorted(by_slug.values(), key=lambda s: s.slug)}, errors


def _batch(root: Path, names: list[str]) -> list[tuple[str, bytes] | None]:
    """Read ``<commit>:<path>`` objects through one ``git cat-file --batch``: ``(type, content)`` or ``None``."""
    if not names:
        return []
    output = run_git(root, "cat-file", "--batch", input="".join(f"{name}\n" for name in names).encode())
    results: list[tuple[str, bytes] | None] = []
    position = 0
    for _ in names:
        end = output.index(b"\n", position)
        header = output[position:end]
        position = end + 1
        fields = header.split(b" ")
        if header.endswith((b" missing", b" ambiguous")) or len(fields) != 3 or not fields[2].isdigit():
            results.append(None)
            continue
        size = int(fields[2])
        results.append((fields[1].decode(), output[position : position + size]))
        position += size + 1
    return results


def _tree_modes(data: bytes, hash_size: int) -> dict[bytes, bytes]:
    """Entry name to mode of one raw tree object."""
    modes: dict[bytes, bytes] = {}
    position = 0
    while position < len(data):
        space = data.index(b" ", position)
        nul = data.index(b"\0", space)
        modes[data[space + 1 : nul]] = data[position:space]
        position = nul + 1 + hash_size
    return modes


def _blob_in_tree(
    tree: tuple[str, bytes] | None, blob: tuple[str, bytes] | None, commit: str, name: bytes
) -> tuple[bytes, bytes | None] | None:
    """A batched ``(parent tree, blob)`` pair as ``(content, mode of name in the tree)``, or ``None`` when not both."""
    if tree is None or blob is None or tree[0] != "tree" or blob[0] != "blob":
        return None
    return blob[1], _tree_modes(tree[1], len(commit) // 2).get(name)


def _committed_blob(root: Path, commit: str, path: str) -> bytes | None:
    """A regular file at ``commit:path``, or ``None``; the parent tree in the same batch excludes symlinks."""
    parent, _, name = path.rpartition("/")
    tree, blob = _batch(root, [f"{commit}:{parent}", f"{commit}:{path}"])
    found = _blob_in_tree(tree, blob, commit, name.encode())
    if found is None:
        return None
    content, mode = found
    return content if mode is not None and mode not in _SKIPPED_MODES else None


def planning_proposals(root: Path) -> dict[str, object]:
    """``{"sources", "items", "errors"}``: each source's ``proposal.md``, branch sources read in one batch."""
    root = root.resolve()
    sources, errors = planning_sources(root)
    items: list[dict[str, str]] = []
    batched = [source for source in sources.values() if source.worktree is None]
    for source in sources.values():
        if source.worktree is None:
            continue
        if not os.path.lexists(source.worktree / source.proposal):
            continue
        try:
            content = WorkingTreeReader(source.worktree).blob(source.proposal).decode("utf-8")
        except (ReadError, UnicodeDecodeError) as exc:
            errors.append(f"{source.label}: {source.proposal}: {exc}")
            continue
        items.append({"source": source.id, "path": source.proposal, "content": content, "encoding": "utf-8"})
    names = [
        name
        for source in batched
        for name in (f"{source.commit}:{source.directory}", f"{source.commit}:{source.proposal}")
    ]
    try:
        objects = _batch(root, names)
    except (GitError, ValueError) as exc:
        errors.append(f"git cat-file: {exc}")
        objects = [None] * len(names)
    for index, source in enumerate(batched):
        found = _blob_in_tree(objects[2 * index], objects[2 * index + 1], source.commit, b"proposal.md")
        if found is None:
            continue
        raw, mode = found
        try:
            if mode in _SKIPPED_MODES:
                raise ValueError("not a regular file")
            content = raw.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            errors.append(f"{source.label}: {source.proposal}: {exc}")
            continue
        items.append({"source": source.id, "path": source.proposal, "content": content, "encoding": "utf-8"})
    items.sort(key=lambda item: item["path"])
    return {"sources": [source.as_json() for source in sources.values()], "items": items, "errors": errors}


def _scoped(root: Path, source_id: str, path: str) -> tuple[PlanningSource, str]:
    """The source named by ``source_id`` and ``path`` inside its proposal directory, or the request's error."""
    path = check_path(path)
    if "\n" in path or "\r" in path:
        raise path_invalid(path)
    source = planning_sources(root)[0].get(source_id)
    if source is None:
        raise source_unknown(source_id)
    if path != source.directory and not path.startswith(f"{source.directory}/"):
        raise source_path_refused(path, source_id)
    return source, path


def source_tree(root: Path, source_id: str, path: str, *, recursive: bool = False) -> list[TreeItem]:
    """List a directory of one source's proposal directory, in the order and shape of the checkout listing."""
    source, path = _scoped(root.resolve(), source_id, path)
    if source.worktree is not None:
        return WorkingTreeReader(source.worktree).tree(path, recursive=recursive)
    flags = ("-r", "-t") if recursive else ()
    try:
        output = run_git(root, "--literal-pathspecs", "ls-tree", "-z", "-l", *flags, source.commit, "--", f"{path}/")
    except GitError as exc:
        raise path_not_found(path, "directory") from exc
    items: list[TreeItem] = []
    for entry in output.split(b"\0"):
        meta, _, name = entry.partition(b"\t")
        fields = meta.split()
        relative = name.decode("utf-8", errors="surrogateescape")
        if len(fields) != 4 or fields[0] in _SKIPPED_MODES or not relative.startswith(f"{path}/"):
            continue
        if any(part.casefold() == ".git" for part in relative.split("/")):
            continue
        kind = fields[1].decode()
        if kind == "tree":
            items.append(TreeItem(relative.rsplit("/", 1)[-1], relative, "tree"))
        elif kind == "blob":
            items.append(TreeItem(relative.rsplit("/", 1)[-1], relative, "blob", int(fields[3])))
    if not items:
        raise path_not_found(path, "directory")
    return sorted(items, key=lambda item: (item.type != "tree", item.path))


def source_blob(root: Path, source_id: str, path: str) -> bytes:
    """Read one regular file of one source's proposal directory."""
    source, path = _scoped(root.resolve(), source_id, path)
    if source.worktree is not None:
        return WorkingTreeReader(source.worktree).blob(path)
    try:
        data = _committed_blob(root, source.commit, path)
    except (GitError, ValueError) as exc:
        raise path_not_found(path, "file") from exc
    if data is None:
        raise path_not_found(path, "file")
    return data
