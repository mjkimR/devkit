"""Author and inspect unit envelopes independently of a transport."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devkit_core.core import GitError, run_git

from devkit_agt.features.workflow.models.envelope import Envelopes
from devkit_agt.features.workflow.models.errors import EnvelopeFlagError
from devkit_agt.features.workflow.repositories.git import is_revision
from devkit_agt.features.workflow.services.envelope import (
    compose_envelope,
    envelope_timestamp,
    load_envelopes,
    render_envelope,
    skeleton,
    write_envelope,
)
from devkit_agt.features.workflow.usecases.workspace import Workspace


def _resolve_scope(root: Path, base: str, head: str) -> tuple[str, str]:
    """Resolve supplied scope revisions before writing; retain lexical-only authoring outside Git."""
    if head and not is_revision(head):
        raise EnvelopeFlagError(
            f"--head {head!r} must be a hexadecimal commit id", fix="Pass --head $(git rev-parse HEAD)"
        )
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
                fix=f"Pass {flag} an existing commit in this repository (inspect `git rev-parse --verify <rev>^{{commit}}`)",
            ) from exc
        resolved.append(sha.decode("ascii").strip())
    return resolved[0], resolved[1]


def write_envelope_request(
    kind: str,
    *,
    workspace: Workspace,
    authoring: bool,
    unit: str,
    anchor: str | None,
    stage: str,
    status: str | None,
    summary: str | None,
    assumptions: tuple[str, ...],
    unverified: tuple[str, ...],
    checks: tuple[str, ...],
    base: str,
    head: str,
    effort: str,
    findings_yaml: str | None = None,
    source: str | None = None,
    resolve: tuple[str, ...] = (),
    waive: tuple[str, ...] = (),
    questions_yaml: str | None = None,
    answers_to: str = "",
    answers_yaml: str | None = None,
    settle: tuple[str, ...] = (),
    problem: str = "",
    attempts: tuple[str, ...] = (),
    recovery: str = "",
    resolves: str = "",
) -> dict[str, Any]:
    """Write the next <kind>-NN.yaml: a skeleton when no authoring flag is given, else the complete envelope."""
    ws = workspace
    scope = ws.unit_scope(unit, anchor=anchor)
    unit_dir, workflow, segment = scope.dir, scope.workflow, scope.binding.segment
    created = envelope_timestamp(unit_dir, workflow, scope.binding.segment_start)
    if authoring:
        base, head = _resolve_scope(ws.root, base, head)
        loaded = load_envelopes(unit_dir)
        draft = compose_envelope(
            unit_dir=unit_dir,
            envelopes=loaded.scoped(workflow, segment),
            loaded=loaded,
            kind=kind,
            stage=stage,
            workflow=workflow,
            segment=segment,
            status=status,
            summary=summary or "",
            assumptions=assumptions,
            unverified=unverified,
            checks=checks,
            base=base,
            head=head,
            findings_yaml=findings_yaml,
            source=source,
            resolve=resolve,
            waive=waive,
            questions_yaml=questions_yaml,
            answers_to=answers_to,
            answers_yaml=answers_yaml,
            settle=settle,
            problem=problem,
            attempts=attempts,
            recovery=recovery,
            resolves=resolves,
            effort=effort,
        )
        body = render_envelope(draft, created)
        written_status, open_findings = draft.status, draft.open_findings()
    else:
        body = skeleton(kind, stage, created, workflow, segment)
        written_status, open_findings = "needs_input", 0
    path, seq = write_envelope(unit_dir, kind, body)
    rel = ws.rel(path)
    return {"file": rel, "kind": kind, "seq": seq, "status": written_status, "open_findings": open_findings}


def check_envelopes(workspace: Workspace, unit: str) -> Envelopes:
    """Load a unit's envelopes and resolve malformed-file targets relative to the project."""
    unit_dir = workspace.unit_path(unit)
    workspace.present_anchors(unit_dir)
    envelopes = load_envelopes(unit_dir)
    unit_rel = workspace.rel(unit_dir)
    for error in envelopes.errors:
        error.target_files = (f"{unit_rel}/{error.file}",)
    return envelopes
