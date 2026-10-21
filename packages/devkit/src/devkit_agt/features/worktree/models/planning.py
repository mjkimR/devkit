"""Immutable approved worktree finish scope."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class FinishPlan:
    base: str
    common_dir: str
    common_identity: tuple[int, int]
    branch: str
    source_sha: str
    target_branch: str
    target_sha: str
    path: str
    worktree_identity: tuple[int, int] | None
    source_upstream: str
    markers: tuple[str, str, str]
    delete_branch: bool
    merge_method: str = "no-ff"
    already_merged: bool = False  # the target already contains the source: a cleanup-only plan builds nothing

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
