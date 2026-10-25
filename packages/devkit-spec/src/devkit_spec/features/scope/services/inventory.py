"""Token-free candidate inventory; physical accessibility is not task liveness."""

from __future__ import annotations

import re
from pathlib import Path

from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.observation import Candidate
from devkit_spec.features.scope.repositories.collection_git import git

ACTIVITY = re.compile(r"^(?:plan|dev)-([a-z0-9][a-z0-9_-]*)$")
MAX_SOURCES = 256


def refs(root: Path, deadline: Deadline) -> list[Candidate]:
    remotes = git(root, "remote", deadline=deadline).decode().splitlines()
    arguments = (
        "refs/heads/plan-*",
        "refs/heads/dev-*",
        *(f"refs/remotes/{r}/plan-*" for r in remotes),
        *(f"refs/remotes/{r}/dev-*" for r in remotes),
    )
    raw = git(root, "for-each-ref", "--format=%(refname)%00%(objectname)%00%(symref)", *arguments, deadline=deadline)
    result = []
    for line in raw.decode("utf-8", errors="surrogateescape").splitlines():
        deadline.check("scope ref inventory")
        ref, sha, symbolic = line.split("\0")
        if not symbolic:
            result.append(Candidate(source_id=ref, ref=ref, sha=sha, branch=ref.rsplit("/", 1)[-1]))
    return result


def worktrees(root: Path, deadline: Deadline) -> list[Candidate]:
    raw = git(root, "worktree", "list", "--porcelain", "-z", deadline=deadline)
    prefix = git(root, "rev-parse", "--show-prefix", deadline=deadline).decode().removesuffix("\n")
    result = []
    for block in raw.split(b"\0\0"):
        deadline.check("scope worktree inventory")
        fields: dict[str, str] = {}
        for item in block.split(b"\0"):
            if item:
                key, _, value = item.decode("utf-8", errors="surrogateescape").partition(" ")
                fields[key] = value
        if "worktree" not in fields or "bare" in fields:
            continue
        path, ref = str(Path(fields["worktree"]) / prefix), fields.get("branch", "")
        result.append(
            Candidate(
                source_id=f"worktree:{path}",
                ref=ref,
                sha=fields.get("HEAD", ""),
                worktree=path,
                branch=ref.removeprefix("refs/heads/"),
            )
        )
    return result
