"""Exception hierarchy shared by every ``devkit.core`` module.

These are plain exceptions. Packages catch them at their own boundaries and map
them to whatever they report (advisories, CLI exit codes, gate results).
"""

from __future__ import annotations


class DevkitCoreError(Exception):
    """Base class of every error raised by ``devkit.core``."""


class FrontmatterError(DevkitCoreError, ValueError):
    """A document opens a YAML frontmatter block that cannot be used."""


class ReceiptError(DevkitCoreError, ValueError):
    """``.devkit/installation.json`` exists but is unreadable or does not match its schema."""


class ConfigError(DevkitCoreError, ValueError):
    """``.devkit/config.toml`` exists but cannot be read or parsed."""


class UnsafePathError(DevkitCoreError, ValueError):
    """A workspace-relative path is absolute, escapes its root, or is otherwise unusable."""


class GitError(DevkitCoreError):
    """A Git command could not run, timed out, or exited with a nonzero status.

    ``returncode`` is ``None`` when Git never produced an exit status (not
    installed, not executable, or timed out). ``stderr`` is Git's decoded
    diagnostic output, possibly empty.
    """

    def __init__(
        self,
        message: str,
        *,
        command: tuple[str, ...] = (),
        returncode: int | None = None,
        stderr: str = "",
    ) -> None:
        super().__init__(message)
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
