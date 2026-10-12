"""Errors raised by the ``devkit.workflow`` library.

Every error is an ``AdvisoryError`` with a stable ``code`` (``UNIT_NOT_FOUND``,
``WORKFLOW_DRIFT``, ...), so a library caller can branch on ``error.code`` and
the CLI renders the same object as an Agent Advisory Protocol block. Errors of
``devkit.core`` (``RECEIPT_INVALID``, ``FRONTMATTER_INVALID``, ...) pass through
unchanged where the workflow layer has nothing to add.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from devkit.advisory import Actor, AdvisoryError, ExitCode, Retry


class WorkflowError(AdvisoryError):
    """An error of the workflow engine; ``code`` names the condition."""


@dataclass(frozen=True)
class WorkflowProblem:
    """A problem collected rather than raised: a definition or plugin check file that could not be
    loaded, or definitions that disagree on a shared stage.

    ``target`` is the file concerned when known; ``fix`` the remediation when one is specific.
    """

    message: str
    code: str
    target: str = ""
    fix: str = ""

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict[str, str | None]:
        return {"code": self.code, "message": self.message, "target": self.target or None, "fix": self.fix or None}


def input_error(
    message: str,
    *details: str,
    code: str,
    fix: str | None = None,
    target_files: Sequence[str] = (),
    exit_code: ExitCode = ExitCode.ERROR,
) -> WorkflowError:
    """Malformed input or state the caller corrects before retrying (``INPUT_ERROR``).

    ``exit_code`` is ``FINDINGS`` when the error reports a negative result of a check that did run.
    """
    error = WorkflowError.invalid_input(message, *details, code=code, fix=fix, target_files=target_files)
    error.exit_code = exit_code
    return error


def maintenance_error(
    message: str, *details: str, code: str, fix: str | None = None, target_files: Sequence[str] = ()
) -> WorkflowError:
    """Something a developer must repair, such as a failing plugin or rule (``MAINTENANCE``)."""
    return WorkflowError(
        message,
        *details,
        code=code,
        actor=Actor.DEVELOPER,
        retry=Retry.AFTER_FIX,
        fix=fix,
        target_files=target_files or None,
    )


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
    """The bound stage schema changed under in-flight work (a guardrail).

    A refusal of ``next`` that reports the unit's state, so the CLI exits
    ``FINDINGS`` (1) like a refused commit, not ``ERROR``.
    """

    code = "WORKFLOW_DRIFT"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    guardrail = True
    exit_code = ExitCode.FINDINGS


class LayoutError(WorkflowError):
    """A layout template, slug, directory or anchor file name is malformed."""

    code = "LAYOUT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class DefinitionError(WorkflowError):
    """A workflow definition cannot be read or represented, or a reference names none."""

    code = "DEFINITION_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class CheckError(WorkflowError):
    """A malformed, colliding or unregistered check reference."""

    code = "CHECK_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class PluginError(WorkflowError):
    """A plugin check file declares an invalid check."""

    code = "CHECK_LOAD_FAILED"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
