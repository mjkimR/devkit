"""Errors of the ``devkit.workflow`` library: one ``AdvisoryError`` class per stable code.

A library caller branches on ``error.code`` (or the class) and the CLI renders
the same object as an Agent Advisory Protocol block. Every class derives from
``WorkflowError``, which sets the actor and retry defaults once; a class sets
only what differs (input error, exit code, interaction). Errors of
``devkit.core`` (``RECEIPT_INVALID``, ``CONFIG_INVALID``, ``GIT_FAILED``, ...)
and of ``devkit.rules`` (the ``lint-clean`` binding) pass through unchanged.

Problems that are collected rather than raised (a malformed decision record or
envelope, a definition that cannot be loaded or does not validate, a plugin
check file that fails, a shared stage that differs) are instances of these
same classes; ``to_dict()`` is their JSON form.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Unpack

from devkit.advisory import Actor, Advisory, AdvisoryError, AdvisoryFields, ExitCode, Level, Retry
from devkit.core import errors as core_errors

ENVELOPE_CONTRACT = "docs/workflow/definition-and-checks.md section 3"


class WorkflowError(AdvisoryError):
    """Base class of every workflow error: a developer corrects something before retrying."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class _FileProblem(WorkflowError):
    """A problem in one unit-relative file (``file``, the advisory target unless one is given)."""

    def __init__(self, message: str, *details: object, file: str = "", **fields: Unpack[AdvisoryFields]) -> None:
        super().__init__(message, *details, **fields)
        self.file = file

    @property
    def advisory(self) -> Advisory:
        advisory = super().advisory
        return replace(advisory, target_files=(self.file,)) if self.file and not advisory.target_files else advisory

    def to_dict(self, *, include_advisory: bool = True) -> dict[str, Any]:
        data = super().to_dict(include_advisory=include_advisory)
        data["file"] = self.file or None
        return data


# -- configuration, layout and definitions -------------------------------------


class WorkflowConfigError(core_errors.ConfigError, WorkflowError):
    """The ``[workflow]``, ``[workflow.approvals]`` or ``[workflow.stages]`` table is malformed.

    A ``.devkit/config.toml`` that cannot be read or parsed at all is the core
    ``ConfigError`` (``CONFIG_INVALID``), raised unchanged.
    """

    code = "WORKFLOW_CONFIG_INVALID"
    fix = "Correct the [workflow], [workflow.approvals] and [workflow.stages] tables of .devkit/config.toml"


class LayoutError(WorkflowError):
    """A layout template, directory or anchor file name is malformed."""

    code = "LAYOUT_INVALID"
    input_error = True


class SlugError(WorkflowError):
    """A unit slug does not match ``[a-z0-9][a-z0-9-]*``."""

    code = "SLUG_INVALID"
    input_error = True
    fix = "Use lowercase letters, digits and hyphens"


class DefinitionError(WorkflowError):
    """A workflow definition cannot be read or represented, or an id names several definitions."""

    code = "WORKFLOW_DEFINITION_INVALID"
    input_error = True


class DefinitionProblem(DefinitionError):
    """One validation problem of a loaded definition, collected rather than raised.

    ``where`` names the field (``<stage>.<field>``, ``next[0].workflow``, ...).
    A definition with problems is a finding (exit 1), unlike one that cannot be
    loaded at all.
    """

    exit_code = ExitCode.FINDINGS

    def __init__(self, message: str, *details: object, where: str = "", **fields: Unpack[AdvisoryFields]) -> None:
        super().__init__(message, *details, **fields)
        self.where = where

    def __str__(self) -> str:
        return f"{self.where}: {self.message}" if self.where else self.message

    def to_dict(self, *, include_advisory: bool = True) -> dict[str, Any]:
        data = super().to_dict(include_advisory=include_advisory)
        data["where"] = self.where
        return data


class RoleUnknownProblem(DefinitionProblem):
    """A stage role outside the project's subagent vocabulary."""

    code = "ROLE_UNKNOWN"


class RolesUncheckedNotice(WorkflowError):
    """Neither a receipt nor ``[workflow] roles_dir`` exists, so stage roles were not checked (``NOTICE``, never raised)."""

    code = "WORKFLOW_ROLES_UNCHECKED"
    level = Level.NOTICE
    brief = True


class SharedStageMismatchError(WorkflowError):
    """Two definitions give the same stage id different ``exit``, gate, role, isolation, skills or artifacts."""

    code = "SHARED_STAGE_MISMATCH"
    input_error = True
    exit_code = ExitCode.FINDINGS


class WorkflowAssetMissingError(WorkflowError):
    """A workflow definition recorded in the installation receipt is missing from the working tree."""

    code = "WORKFLOW_ASSET_MISSING"
    actor = Actor.TOOL
    fix = "devkit sync"


class CheckError(WorkflowError):
    """A malformed, colliding or unregistered check reference."""

    code = "WORKFLOW_CHECK_INVALID"
    input_error = True


class CheckReferenceProblem(CheckError, DefinitionProblem):
    """A check reference in a definition that does not resolve: the collected form of ``CheckError``."""


class PluginError(WorkflowError):
    """A plugin check file cannot be loaded or declares an invalid check."""

    code = "WORKFLOW_CHECK_LOAD_FAILED"


# -- selecting a workflow ----------------------------------------------------------


class WorkflowNotFoundError(WorkflowError):
    """No definition has the requested id, or the named definition file does not exist."""

    code = "WORKFLOW_NOT_FOUND"
    input_error = True


class WorkflowNotSelectedError(WorkflowError):
    """Neither a workflow reference, a binding nor ``[workflow].default`` selects a workflow."""

    code = "WORKFLOW_NOT_SELECTED"
    input_error = True
    fix = "Pass --workflow <id>, bind the unit, or set [workflow].default in .devkit/config.toml"


class WorkflowInvalidError(WorkflowError):
    """The selected workflow definition has validation problems."""

    code = "WORKFLOW_INVALID"
    input_error = True


# -- units ---------------------------------------------------------------------------


class UnitNotFoundError(WorkflowError):
    """The unit directory has no anchor file."""

    code = "UNIT_NOT_FOUND"
    input_error = True
    fix = "Pass an existing unit directory (`devkit workflow list`) or create one with `devkit workflow new <slug>`"


class UnitExistsError(WorkflowError):
    """``new`` would create a unit whose anchor already exists."""

    code = "UNIT_EXISTS"
    input_error = True


class AnchorInvalidError(WorkflowError):
    """The anchor file's frontmatter cannot be read."""

    code = "ANCHOR_INVALID"
    input_error = True
    fix = "Repair the anchor's YAML frontmatter"


class AnchorAmbiguousError(WorkflowError):
    """A unit directory contains the anchor files of several workflows."""

    code = "ANCHOR_AMBIGUOUS"
    input_error = True
    fix = "Pass --workflow <id> to name the workflow (and so the anchor) to evaluate against"


class AnchorMismatchError(WorkflowError):
    """The unit's anchor is not the anchor its workflow declares."""

    code = "ANCHOR_MISMATCH"
    input_error = True


class GivenInvalidError(WorkflowError):
    """A ``--given`` name is neither a gate of the workflow nor a registered runner or human check."""

    code = "GIVEN_INVALID"
    input_error = True


class DriftError(WorkflowError):
    """The bound stage schema changed under in-flight work (a guardrail).

    A refusal of ``next`` that reports the unit's state, so the CLI exits
    ``FINDINGS`` (1) like a refused commit, not ``ERROR``.
    """

    code = "WORKFLOW_DRIFT"
    guardrail = True
    exit_code = ExitCode.FINDINGS


# -- decisions and answers -----------------------------------------------------------


class DecisionRecordError(_FileProblem):
    """A decision record file does not match the record format; collected by ``load_decisions``."""

    code = "DECISION_RECORD_INVALID"
    input_error = True


class HandoffChoiceIgnoredError(DecisionRecordError):
    """A recorded handoff choice that is not an eligible candidate; it is ignored, not applied."""

    code = "HANDOFF_CHOICE_IGNORED"


class RequestUnknownError(WorkflowError):
    """An answer names a request id that is malformed, of an unknown form, or not open."""

    code = "REQUEST_UNKNOWN"
    input_error = True


class DecisionInvalidError(WorkflowError):
    """An answer's action or values do not fit the open request."""

    code = "DECISION_INVALID"
    input_error = True


class ReturnInvalidError(WorkflowError):
    """A return names a stage that does not exist or comes after the current one."""

    code = "RETURN_INVALID"
    input_error = True


# -- handoff -------------------------------------------------------------------------


class HandoffNotReadyError(WorkflowError):
    """The unit has not completed its workflow."""

    code = "HANDOFF_NOT_READY"
    input_error = True


class HandoffNoneError(WorkflowError):
    """The workflow declares no ``next`` candidates."""

    code = "HANDOFF_NONE"
    input_error = True


class HandoffOffError(WorkflowError):
    """Handoff is disabled by ``[workflow.approvals].handoff = "off"``."""

    code = "HANDOFF_OFF"
    input_error = True


class HandoffUndecidedError(WorkflowError):
    """Under ``auto`` no candidate is eligible."""

    code = "HANDOFF_UNDECIDED"
    input_error = True


class HandoffChoiceRequiredError(WorkflowError):
    """Under ``ask`` a person must choose the next workflow (``INTERACTION``)."""

    code = "HANDOFF_CHOICE_REQUIRED"
    actor = Actor.USER


class HandoffInvalidError(WorkflowError):
    """The chosen workflow is not a ``next`` candidate."""

    code = "HANDOFF_INVALID"
    input_error = True


class HandoffIneligibleError(WorkflowError):
    """The chosen candidate's ``when`` checks do not hold."""

    code = "HANDOFF_INELIGIBLE"
    input_error = True


class HandoffLayoutMismatchError(WorkflowError):
    """The target workflow declares an anchor other than the unit's."""

    code = "HANDOFF_LAYOUT_MISMATCH"
    input_error = True


# -- envelopes -------------------------------------------------------------------------


class EnvelopeFormatError(_FileProblem):
    """An envelope file does not match the envelope contract; collected by ``load_envelopes``.

    A malformed envelope is a finding of ``envelope check`` (exit 1).
    """

    code = "ENVELOPE_INVALID"
    input_error = True
    exit_code = ExitCode.FINDINGS
    fix = f"Fix or remove the file; the contract is {ENVELOPE_CONTRACT}"


class EnvelopeKindError(WorkflowError):
    """An envelope kind does not match ``[a-z][a-z0-9-]*``."""

    code = "ENVELOPE_KIND_INVALID"
    input_error = True
    fix = "Use a lowercase kind such as review"


class AuthoringError(WorkflowError):
    """Base of the ``envelope new`` authoring errors: flags that cannot produce a valid envelope."""

    input_error = True


class EnvelopeFlagError(AuthoringError):
    """A malformed ``--check``, ``--resolve``, ``--waive`` or ``--head`` value, or an invalid flag combination."""

    code = "ENVELOPE_FLAG_INVALID"


class EnvelopeFindingsError(AuthoringError):
    """The ``--findings-file`` content is not a valid list of findings."""

    code = "ENVELOPE_FINDINGS_INVALID"


class EnvelopeFromError(AuthoringError):
    """``--from`` is missing, or names no usable review or reverify envelope."""

    code = "ENVELOPE_FROM_INVALID"


class EnvelopeStatusError(AuthoringError):
    """``--status`` is not one of the envelope statuses."""

    code = "ENVELOPE_STATUS_INVALID"
