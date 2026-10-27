"""Bind a new anchor (a spec bundle's ``spec.md``, a proposal's ``proposal.md``) to a devkit workflow.

The workflow is resolved and validated with devkit's own ``Workspace`` (project definitions in
``.devkit/workflows/`` and synchronized ones), before anything is written. A workflow named explicitly must resolve
and validate; a default that is not available leaves the anchor unbound, with a notice.
"""

from __future__ import annotations

from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_agt.features.workflow import Binding, Workspace
from devkit_core.core.logs import get_logger

from devkit_spec.base.errors import DEVKIT, ProposalWorkflowError, SpecError
from devkit_spec.features.proposals.models.axes import DEFAULT_WORKFLOW

_log = get_logger(__name__)


def unbound_guidance(root: Path, unit: str, default: str) -> tuple[str, tuple[str, ...]]:
    """The fix and details of an unbound notice for ``unit``: the exact bind command when one workflow other than
    ``default`` is available, else the available workflow ids as details to choose from."""
    try:
        ids = sorted({doc.id for doc in Workspace(root, lint=None, ancestor=None).definitions() if doc.id != default})
    except AdvisoryError:
        ids = []
    if len(ids) == 1:
        return f"Once it fits the unit, bind it with `{DEVKIT} workflow bind --unit {unit} --workflow {ids[0]}`", ()
    if not ids:
        return (
            f"Make {default} available ({DEVKIT} sync with its bundle selected), then bind it with "
            f"`{DEVKIT} workflow bind --unit {unit} --workflow {default}`",
            (),
        )
    return (
        "Bind it to the workflow that fits the unit: run the matching command in [DETAIL]",
        tuple(f"{DEVKIT} workflow bind --unit {unit} --workflow {workflow}" for workflow in ids),
    )


def resolve_binding(
    root: Path,
    value: object,
    source: str,
    *,
    field: str = "workflow",
    default: str = DEFAULT_WORKFLOW,
    error: type[SpecError] = ProposalWorkflowError,
) -> tuple[Binding | None, AdvisoryError | None]:
    """The binding for ``value`` (a workflow id, or ``None``/empty for ``default``), or ``None`` with the reason.

    ``source`` names where ``value`` came from (a file, or a command option) and ``field`` its key, for messages. An
    explicit ``value`` that is not a string, does not resolve, does not validate or names a definition by a path that
    is not the one discovered for its id (devkit's ``Workspace.require_bindable``, ``WORKFLOW_NOT_BINDABLE``) raises
    ``error``.
    """
    if value is not None and not isinstance(value, str):
        raise error(f"{source}: {field} must be a workflow id", target_files=[source])
    explicit = (value or "").strip()
    workflow = explicit or default
    try:
        workspace = Workspace(root, lint=None, ancestor=None)
        doc = workspace.definition(workflow)
        # A binding records only the id: a definition named by a path must be the one discovered for that id.
        workspace.require_bindable(doc, explicit or None)
    except AdvisoryError as exc:
        if explicit:
            raise error(
                f"{field} {workflow} cannot be bound: {exc.message}",
                f"{exc.code}: {exc.message}",
                *exc.details,
                target_files=[source],
            ) from exc
        _log.info("default workflow %s not bound: %s (%s)", workflow, exc.message, exc.code)
        return None, exc
    return Binding(doc.id), None
