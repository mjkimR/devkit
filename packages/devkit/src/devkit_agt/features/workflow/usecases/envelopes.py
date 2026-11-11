"""Author and inspect unit envelopes independently of a transport."""

from __future__ import annotations

import shlex
from dataclasses import replace
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import GitError, run_git

from devkit_agt.features.workflow.models.definition import WorkflowDocument
from devkit_agt.features.workflow.models.envelope import WORKER, EnvelopeFlags, Envelopes
from devkit_agt.features.workflow.models.errors import EnvelopeFlagError, locate_envelope_errors, workflow_command
from devkit_agt.features.workflow.repositories.unit.decisions import load_decisions
from devkit_agt.features.workflow.services.envelope import (
    FROM_LATEST,
    check_head,
    compose_envelope,
    envelope_timestamp,
    load_envelopes,
    render_envelope,
    skeleton,
    write_envelope,
)
from devkit_agt.features.workflow.usecases.evaluate import current_envelopes
from devkit_agt.features.workflow.usecases.workspace import UnitScope, Workspace


def _resolve_scope(root: Path, base: str, head: str) -> tuple[str, str]:
    """Resolve supplied scope revisions before writing; retain lexical-only authoring outside Git.

    ``--head`` is checked before Git resolves it, so a symbolic name (``HEAD``, a branch) is refused, not resolved.
    """
    check_head(head)
    if not (base or head):
        return base, head
    # Workspace.root is normalized to the Git top level inside a repository (including linked worktrees).
    # Detect metadata rather than interpreting Git's human-readable error messages as a not-a-repository signal.
    if not (root / ".git").exists():
        return base, head
    resolved = []
    for flag, revision in (("--base", base), ("--head", head)):
        if not revision:
            resolved.append("")
            continue
        try:
            sha = run_git(root, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}")
        except GitError as exc:
            if exc.returncode is None:
                raise
            raise EnvelopeFlagError(
                f"{flag} {revision!r} does not resolve to a commit",
                target_files=[flag],
                fix=f"Pass {flag} an existing commit of this repository (`git rev-parse --verify {revision}^{{commit}}`"
                " shows why this one is not)",
            ) from exc
        resolved.append(sha.decode("ascii").strip())
    return resolved[0], resolved[1]


def _scope_definition(ws: Workspace, scope: UnitScope) -> WorkflowDocument | None:
    """The definition of the workflow the unit's envelopes record; ``None`` when it cannot be loaded or is another
    workflow, so authoring never needs a valid definition."""
    try:
        doc = ws.load_definition(scope.binding.workflow or ws.config.default or "")
    except AdvisoryError:
        return None
    return doc if doc.id == scope.workflow else None


def _carried_from(ws: Workspace, scope: UnitScope, loaded: Envelopes) -> Envelopes:
    """The envelopes ``--from latest`` reads: the segment's, without those a later ``return`` re-opened.

    Evaluation reads the same set (``current_envelopes``), so a reverify never closes a round that no longer counts.
    The definition gives the stage order a return voids by; when it cannot be loaded, nothing is voided, as the
    authoring commands do not need a valid definition.
    """
    scoped = loaded.scoped(scope.workflow, scope.binding.segment)
    doc = _scope_definition(ws, scope)
    if doc is None:
        return scoped
    decisions = load_decisions(scope.dir).segment(scope.workflow, scope.binding.segment_start)
    return current_envelopes(loaded, decisions, doc, scope.binding.segment)


def _require_declared_stage(ws: Workspace, scope: UnitScope, stage: str) -> None:
    """Refuse a worker ``--stage`` the unit's workflow does not declare, before anything is written.

    An envelope with an undeclared stage would hold every gate of the unit. The definition is loaded as ``--from
    latest`` loads it: when it cannot be loaded, or is not the workflow the envelope records, the check is skipped,
    so a run can still be recorded on a missing or broken definition.
    """
    doc = _scope_definition(ws, scope)
    if doc is None:
        return
    declared = [s.id for s in doc.stages]
    if stage in declared:
        return
    next_command = workflow_command(f"next --unit {shlex.quote(scope.rel)}")
    raise EnvelopeFlagError(
        f"--stage {stage!r} is not a stage of workflow {doc.id}",
        target_files=["--stage"],
        fix=f"Pass --stage the stage `{next_command}` names; when it names none (complete=yes), pass the declared stage"
        f" the run worked in. Workflow {doc.id} declares: {', '.join(declared)}",
    )


class WriteEnvelopeUseCase(BaseUseCase):
    """Execute the write envelope request operation."""

    def execute(
        self,
        kind: str,
        *,
        workspace: Workspace,
        unit: str,
        anchor: str | None,
        flags: EnvelopeFlags,
    ) -> dict[str, Any]:
        """Write the next <kind>-NN.yaml: a skeleton when no authoring flag is given, else the complete envelope."""
        ws = workspace
        scope = ws.unit_scope(unit, anchor=anchor)
        unit_dir, workflow, segment = scope.dir, scope.workflow, scope.binding.segment
        if kind == WORKER:
            _require_declared_stage(ws, scope, flags.stage)
        created = envelope_timestamp(unit_dir, workflow, scope.binding.segment_start)
        authoring = flags.authoring
        if authoring:
            base, head = _resolve_scope(ws.root, flags.base, flags.head)
            loaded = load_envelopes(unit_dir)
            draft = compose_envelope(
                unit_dir=unit_dir,
                unit=scope.rel,
                envelopes=_carried_from(ws, scope, loaded)
                if flags.source == FROM_LATEST
                else loaded.scoped(workflow, segment),
                loaded=loaded,
                kind=kind,
                workflow=workflow,
                segment=segment,
                flags=replace(flags, base=base, head=head),
            )
            body = render_envelope(draft, created)
            written_status, open_findings = draft.status, draft.open_findings()
        else:
            body = skeleton(kind, flags.stage, created, workflow, segment)
            written_status, open_findings = "needs_input", 0
        path, seq = write_envelope(unit_dir, kind, body)
        return {
            "unit": scope.rel,
            "file": path.relative_to(unit_dir).as_posix(),
            "kind": kind,
            "seq": seq,
            "status": written_status,
            "skeleton": not authoring,
            "open_findings": open_findings,
        }


class CheckEnvelopesUseCase(BaseUseCase):
    """Execute the check envelopes operation."""

    def execute(self, workspace: Workspace, unit: str) -> Envelopes:
        """Load a unit's envelopes and resolve malformed-file targets relative to the project."""
        unit_dir = workspace.unit_path(unit)
        workspace.present_anchors(unit_dir)
        envelopes = load_envelopes(unit_dir)
        locate_envelope_errors(envelopes.errors, workspace.rel(unit_dir))
        return envelopes
