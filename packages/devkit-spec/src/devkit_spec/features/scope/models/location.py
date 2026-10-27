"""A registry location and its owner token path."""

import os
from dataclasses import dataclass
from pathlib import Path

TOKEN_FILE = "devkit-spec-scope-token"


@dataclass(frozen=True)
class Location:
    """``root`` is the workspace root (a directory of a Git work tree); the other paths are absolute."""

    root: Path
    common_dir: Path
    git_dir: Path
    shared_path: Path
    namespace: str

    @property
    def token_path(self) -> Path:
        return self.git_dir / TOKEN_FILE

    def shown(self, path: Path | str) -> str:
        """``path`` as output names it: relative to the workspace root, so it is openable and not absolute."""
        return os.path.relpath(path, self.root)

    @property
    def linked(self) -> bool:
        """Whether the workspace is in a linked worktree (its Git directory is not the common one)."""
        return self.git_dir != self.common_dir
