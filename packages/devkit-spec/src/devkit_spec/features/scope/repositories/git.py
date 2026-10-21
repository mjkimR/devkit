"""Git observations bounded by the scope operation deadline."""

from pathlib import Path

from devkit_core.core import run_git

from devkit_spec.features.scope.models.deadline import Deadline


def git_lines(cwd: Path, *args: str, deadline: Deadline) -> list[str]:
    """The NUL-separated output of a ``-z`` Git command under ``deadline``, decoded with ``surrogateescape``."""
    output = run_git(cwd, *args, deadline=deadline).decode("utf-8", errors="surrogateescape")
    return [item for item in output.split("\0") if item]
