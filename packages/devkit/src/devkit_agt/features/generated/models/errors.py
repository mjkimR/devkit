"""Errors and warnings of ``devkit_agt.features.generated``: ``AdvisoryError`` subclasses, one class per code.

``resolve`` refuses before it changes anything when a conflict it cannot settle would feed a regeneration
(``GENERATED_INPUTS_CONFLICTED``); a command that fails or writes outside its declared paths stops it after the
seeding, and rerunning ``resolve`` starts over from the same conflicts, since nothing is staged until every command
succeeded. ``devkit.core`` errors pass through unchanged: a failed Git command is ``GitError`` (``GIT_FAILED``), an
unreadable ``.devkit/generated.toml`` ``ConfigError`` (``CONFIG_INVALID``).
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry
from devkit_dist.base.errors import ConfigError


class GeneratedError(AdvisoryError):
    """Base class of every error raised by ``devkit_agt.features.generated``; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class GeneratedConfigError(GeneratedError, ConfigError):
    """``.devkit/generated.toml`` is malformed, or two artifacts own one path (``INPUT_ERROR``, as
    ``CONFIG_INVALID``)."""

    code = "GENERATED_CONFIG_INVALID"
    target_files = (".devkit/generated.toml",)
    fix = "Correct .devkit/generated.toml"


class InputsConflictedError(GeneratedError):
    """``resolve`` found a conflict no artifact owns that an artifact to regenerate may read (``BLOCKED``).

    An artifact without ``inputs`` may read anything, so every such conflict blocks it. Nothing was changed.
    """

    code = "GENERATED_INPUTS_CONFLICTED"
    guardrail = True
    fix = "Resolve the listed conflicts by hand and stage them (git add <path>), then rerun `devkit generated resolve`"


class UnmergedError(GeneratedError):
    """``regen`` found unmerged paths: a command would read conflict markers (``BLOCKED``); nothing ran."""

    code = "GENERATED_UNMERGED"
    guardrail = True
    fix = "Run `devkit generated resolve` for the generated conflicts and resolve the others by hand, then rerun"


class CommandFailedError(GeneratedError):
    """An artifact's command failed (``MAINTENANCE``); the details carry its log and last output lines."""

    code = "GENERATED_COMMAND_FAILED"


class OutputUndeclaredError(GeneratedError):
    """An artifact's command changed files outside its ``paths`` and ``updates`` (``MAINTENANCE``).

    The changes are left in the work tree for review; nothing was staged.
    """

    code = "GENERATED_OUTPUT_UNDECLARED"


class StaleError(GeneratedError):
    """``check`` regenerated artifacts that differ from the checked commit (``MAINTENANCE``, exit ``1``)."""

    code = "GENERATED_STALE"
    exit_code = ExitCode.FINDINGS


class ConflictsRemainWarning(GeneratedError):
    """``resolve`` settled the generated conflicts, but conflicts no artifact owns remain (``WARNING``)."""

    code = "GENERATED_CONFLICTS_REMAIN"
    level = Level.WARNING
    fix = "Resolve the remaining conflicts by hand and stage them, then continue the operation"
