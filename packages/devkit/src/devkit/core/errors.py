"""Errors raised by ``devkit.core``: ``AdvisoryError`` subclasses with stable codes.

Each class carries the code and the Agent Advisory Protocol fields that fit
its condition, so a caller can branch on ``error.code`` and a CLI boundary
renders the error as it is. A caller that knows more (the command that
repairs the file, the flag that named the path) re-raises with its own fields.
"""

from __future__ import annotations

from typing import Unpack

from devkit.advisory import Actor, AdvisoryError, AdvisoryFields, Retry


class DevkitCoreError(AdvisoryError):
    """Base class of every error raised by ``devkit.core``."""


class FrontmatterError(DevkitCoreError):
    """A document opens a YAML frontmatter block that cannot be used."""

    code = "FRONTMATTER_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class ReceiptError(DevkitCoreError):
    """``.devkit/installation.json`` exists but is unreadable or does not match its schema."""

    code = "RECEIPT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    target_files = (".devkit/installation.json",)
    fix = "Restore .devkit/installation.json from version control (git checkout -- .devkit/installation.json), then run `devkit sync`"


class ConfigError(DevkitCoreError):
    """A TOML configuration file exists but cannot be read or parsed (``CONFIG_INVALID``).

    The base of every configuration error: an area whose own table is malformed
    raises a subclass with its own code (``RULES_CONFIG_INVALID``,
    ``WORKFLOW_CONFIG_INVALID``, ``GATE_CONFIG_INVALID``).
    """

    code = "CONFIG_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True
    target_files = (".devkit/config.toml",)


class ArgumentError(DevkitCoreError):
    """A command argument or library parameter is malformed or names something that does not exist.

    Command lines raise it for every semantic argument check (click only parses
    syntax), so a JSON caller still receives one ``{"error": ...}`` document.
    """

    code = "ARGUMENT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class UnsafePathError(DevkitCoreError):
    """A workspace-relative path is absolute, escapes its root, or is otherwise unusable."""

    code = "PATH_UNSAFE"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class AssetFileError(DevkitCoreError):
    """A file the receipt lists for a synchronized asset is missing, unsafe, or differs from its recorded hash."""

    code = "ASSET_FILE_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    fix = "Run `devkit sync`"


class GitError(DevkitCoreError):
    """A Git command could not run, timed out, or exited with a nonzero status.

    ``returncode`` is ``None`` when Git never produced an exit status (not
    installed, not executable, or timed out). ``stderr`` is Git's decoded
    diagnostic output, possibly empty.
    """

    code = "GIT_FAILED"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX

    def __init__(
        self,
        message: str,
        *details: object,
        command: tuple[str, ...] = (),
        returncode: int | None = None,
        stderr: str = "",
        **fields: Unpack[AdvisoryFields],
    ) -> None:
        super().__init__(message, *details, **fields)
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
