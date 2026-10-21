"""Identity and Git worktree root of a served repository."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Repository:
    id: str
    root: Path
