"""Errors raised by the ``devkit.workflow`` library.

Every error is an ``AdvisoryError`` with a stable ``code`` (``UNIT_NOT_FOUND``,
``WORKFLOW_DRIFT``, ...), so a library caller can branch on ``error.code`` and
the CLI renders the same object as an Agent Advisory Protocol block.
"""

from __future__ import annotations

from collections.abc import Sequence

from devkit.advisory import Actor, AdvisoryError, Retry


class WorkflowError(AdvisoryError):
    """An error of the workflow engine; ``code`` names the condition."""


def input_error(
    message: str, *details: str, code: str, fix: str | None = None, target_files: Sequence[str] = ()
) -> WorkflowError:
    """Malformed input or state the caller corrects before retrying (``INPUT_ERROR``)."""
    return WorkflowError.invalid_input(message, *details, code=code, fix=fix, target_files=target_files)


def maintenance_error(message: str, *details: str, code: str, fix: str | None = None) -> WorkflowError:
    """Something a developer must repair, such as a failing plugin or rule (``MAINTENANCE``)."""
    return WorkflowError(message, *details, code=code, actor=Actor.DEVELOPER, retry=Retry.AFTER_FIX, fix=fix)


class UnitNotFoundError(WorkflowError):
    """The unit directory has no anchor file."""

    code = "UNIT_NOT_FOUND"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class AnchorInvalidError(WorkflowError):
    """The anchor file's frontmatter cannot be read."""

    code = "ANCHOR_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class DriftError(WorkflowError):
    """The bound stage schema changed under in-flight work (a guardrail)."""

    code = "WORKFLOW_DRIFT"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    guardrail = True
