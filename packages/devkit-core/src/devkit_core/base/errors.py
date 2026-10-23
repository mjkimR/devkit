"""Transport-independent foundation errors with stable advisory codes."""

from __future__ import annotations

from typing import Unpack

from devkit.advisory import Actor, AdvisoryError, AdvisoryFields, Retry
from devkit.advisory import ArgumentError as AdvisoryArgumentError


class DevkitCoreError(AdvisoryError):
    """Base class of shared foundation and distribution errors."""


class FrontmatterError(DevkitCoreError):
    """A document opens a YAML frontmatter block that cannot be used."""

    code = "FRONTMATTER_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class YamlBindingUnavailableError(DevkitCoreError):
    """The current PyYAML installation does not expose its LibYAML safe parser."""

    code = "YAML_BINDING_UNAVAILABLE"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    fix = "Install PyYAML from a compatible binary wheel in the active environment, then rerun the command"

    def __init__(self, source: str = "YAML input") -> None:
        super().__init__(f"LibYAML's PyYAML binding is unavailable while reading {source}")


class ArgumentError(DevkitCoreError, AdvisoryArgumentError):
    """A command argument or library parameter is malformed or names something that does not exist.

    Command lines raise it for every semantic argument check (click only parses
    syntax), so a JSON caller still receives one ``{"error": ...}`` document. The
    code and its fields come from ``devkit.advisory.ArgumentError``, which owns
    ``ARGUMENT_INVALID``; this class keeps it a ``DevkitCoreError`` too.
    """


class UnsafePathError(DevkitCoreError):
    """A workspace-relative path is absolute, escapes its root, or is otherwise unusable."""

    code = "PATH_UNSAFE"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


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


class DeadlineExceededError(DevkitCoreError):
    """An operation bounded by a ``Deadline`` ran out of time (``DEFER``): something else kept it busy.

    ``what`` names the step that ran out (``git fetch``, ``waiting for the lock on <path>``) and
    ``seconds`` the deadline's length. A caller with a code of its own catches it and re-raises, or gives
    its ``Deadline`` an ``error`` factory so the deadline raises the caller's error directly.
    """

    code = "DEADLINE_EXCEEDED"
    actor = Actor.NONE
    retry = Retry.SAFE

    def __init__(
        self,
        message: str,
        *details: object,
        what: str = "",
        seconds: float = 0.0,
        **fields: Unpack[AdvisoryFields],
    ) -> None:
        super().__init__(message, *details, **fields)
        self.what = what
        self.seconds = seconds


class LockHeldError(DeadlineExceededError):
    """Another process held a file lock past the wait the caller allowed (``DEFER``); ``seconds`` is that wait."""

    code = "LOCK_HELD"


class LockUnsupportedError(DevkitCoreError):
    """The platform has no ``fcntl.flock``, which every devkit file lock uses (``BLOCKED``)."""

    code = "LOCK_UNSUPPORTED"
    guardrail = True
    fix = "Run the command on Linux or macOS"
