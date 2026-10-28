"""``devkit_agt.features.integration.readiness`` provider (``spec``): SDD completion readiness at ``source_sha``.

``devkit_agt.features.integration`` calls ``check(context)`` during ``prepare(branch, task)`` (no result commit yet) and again at
each build of an approved ``IntegrationRequest`` with the execution context: ``context.finish.target_sha`` is then the
build target and ``context.result_sha`` the commit that would land. The build's evidence must equal the approved
evidence except the codes declared target-bound (``TARGET_SHA``, ``RESULT_SHA``), so verification reads only
committed Git trees (never uncommitted working-tree files or wall-clock timestamps) and always returns a non-empty
tuple of deterministic ``Evidence`` items, with any unmet conditions listed in ``Readiness.reasons``.

The unit (or session) is evaluated from the source tree; the CI rules run on the result tree with the diff from the
build target once a result exists (before it, on the source tree with the diff from the merge base). ``SPEC_POLICY``
binds the parsed ``[tool.spec]`` of the target and of the result (the source before a build). Tests are not re-run on
the result; ``DISCLOSURE`` is included in the report the Host presents before conversational approval.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_agt.features.integration import Evidence, IntegrationContext, Readiness
from devkit_agt.features.integration import (
    build_snapshot as _build_snapshot,
)
from devkit_agt.features.integration import (
    populate_managed_files as _populate_managed_files,
)
from devkit_agt.features.integration import (
    snapshot_root as _snapshot_root,
)
from devkit_agt.features.rules import Phase, Snapshot, materialize_snapshot, run_project_rules
from devkit_agt.features.workflow import Workspace, is_ancestor, load_decisions, load_envelopes, load_workflow_config
from devkit_core.core import FrontmatterError, run_git
from devkit_core.core.frontmatter import parse
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION as DEVKIT
from devkit_dist.features.project.repositories.project import commit_config

from devkit_spec.base.axes import EFFORTS, PROPOSAL_WORKFLOW, SPEC_WORKFLOWS, TASK_KINDS
from devkit_spec.base.units import PROPOSAL_UNIT, SPEC_UNIT, is_spec_dir
from devkit_spec.features.delivery.usecases.attach import attach_check
from devkit_spec.features.policy.services.config import check_approvals, read_spec_config

REGULAR_MODES = {"100644", "100755"}
SYMLINK_MODE = "120000"
GITLINK_MODE = "160000"
SESSION_KINDS = frozenset({*TASK_KINDS, "overall-refactor"})
SESSION_EFFORTS = frozenset(EFFORTS)
TARGET_BOUND = ("TARGET_SHA", "RESULT_SHA")
DISCLOSURE = "CI rules only on the merged result; tests and review ran on the source only"


def _check_project_policies(base: Path, workspace: Path) -> list[str]:
    reasons: list[str] = []
    for label, root in (("base", base), ("source", workspace)):
        try:
            read_spec_config(root)
        except AdvisoryError as exc:
            reasons.append(f"{label} [tool.spec] policy invalid ({exc.code}): {exc.message}")
        try:
            wf_config = load_workflow_config(root)
            check_approvals(wf_config.approvals)
        except AdvisoryError as exc:
            reasons.append(f"{label} workflow policy invalid ({exc.code}): {exc.message}")
    return reasons


def _check_ci_rules(snapshot: Snapshot) -> tuple[str, list[str]]:
    reasons: list[str] = []
    try:
        run = run_project_rules(snapshot.root, snapshot=snapshot, phase=Phase.LINTER)
    except AdvisoryError as exc:
        return f"error:{exc.code}", [f"CI rules failed to run ({exc.code}): {exc.message}"]
    for err in run.errors:
        reasons.append(f"CI rule problem ({err.code}): {err.message}")
    for violation in run.blocking_violations:
        reasons.append(
            f"CI rule violation {violation.rule_id} at {violation.file}:{violation.line}: {violation.message}"
        )
    if reasons:
        return f"fail:errors={len(run.errors)},violations={len(run.blocking_violations)}", reasons
    return "pass", []


def _read_frontmatter(path: Path) -> tuple[dict[str, object], str | None]:
    if not path.is_file():
        return {}, f"missing {path.name}"
    try:
        doc = parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, FrontmatterError) as exc:
        return {}, f"{path.name} frontmatter is unreadable: {exc}"
    return dict(doc.data or {}), None


def _check_unit_task(
    context: IntegrationContext,
    base: Path,
    workspace: Path,
) -> tuple[list[Evidence], list[str]]:
    branch = context.finish.branch
    activity, _, slug = branch.partition("-")
    unit_rel = (context.task.unit or "").strip("/")
    reasons: list[str] = []

    reasons.extend(attach_check(base, branch, unit_rel, context.finish.source_sha))
    if activity == "dev" and SPEC_UNIT.fullmatch(unit_rel) is None:
        reasons.append(
            f"{unit_rel} is not a handed-off spec bundle specs/<YYYY-MM>/<YYYYMMDD>-{slug}; "
            f"hand off the proposal before integrating {branch}"
        )

    ws = Workspace(workspace, ancestor=lambda _root, anc, desc: is_ancestor(base, anc, desc))
    if ws.discovery_errors:
        for err in ws.discovery_errors:
            reasons.append(f"workflow discovery error ({err.code}): {err.message}")

    workflow_id = "unknown"
    stage_status = "unresolved"
    hold_status = "unknown"

    try:
        ref = ws.resolve_unit(unit_rel)
        workflow_id = ref.doc.id
    except AdvisoryError as exc:
        reasons.append(f"unit {unit_rel} could not be resolved ({exc.code}): {exc.message}")
        return (
            [
                Evidence("TASK_KIND", "unit"),
                Evidence("WORKFLOW", workflow_id),
                Evidence("UNIT", unit_rel or "none"),
                Evidence("SOURCE_SHA", context.finish.source_sha),
                Evidence("TARGET_SHA", context.finish.target_sha),
                Evidence("STAGE_STATUS", stage_status),
                Evidence("HOLD_STATUS", hold_status),
            ],
            reasons,
        )

    if not ref.binding.bound:
        reasons.append(f"unit {unit_rel} is not bound to workflow {workflow_id}")

    anchor_data, anchor_err = _read_frontmatter(ref.anchor_path)
    if anchor_err:
        reasons.append(f"{unit_rel}/{ref.anchor}: {anchor_err}")
    doc_id = anchor_data.get("id")
    expected_ids = {slug, f"SPEC-{slug}" if activity == "dev" else f"PROP-{slug}"}
    if isinstance(doc_id, str) and doc_id:
        expected_ids.add(doc_id)
    if context.task.id not in expected_ids:
        reasons.append(f"task.id {context.task.id!r} does not match unit {unit_rel} ({sorted(expected_ids)})")

    given = ("dev-integration", "lint-ci-clean") if workflow_id in SPEC_WORKFLOWS else ()
    try:
        evaluation = ws.evaluate_unit(ref, given=given)
    except AdvisoryError as exc:
        reasons.append(f"workflow evaluation failed ({exc.code}): {exc.message}")
        return (
            [
                Evidence("TASK_KIND", "unit"),
                Evidence("WORKFLOW", workflow_id),
                Evidence("UNIT", unit_rel),
                Evidence("SOURCE_SHA", context.finish.source_sha),
                Evidence("TARGET_SHA", context.finish.target_sha),
                Evidence("STAGE_STATUS", f"error:{exc.code}"),
                Evidence("HOLD_STATUS", hold_status),
            ],
            reasons,
        )

    for err in evaluation.errors:
        reasons.append(f"workflow error ({err.code}): {err.message}")
    if evaluation.stale_approvals:
        stale = ", ".join(decision.file for decision in evaluation.stale_approvals)
        reasons.append(f"unit {unit_rel} has stale approvals: {stale}")

    problems = len(evaluation.hold.problems)
    questions = len(evaluation.hold.questions)
    if problems or questions:
        hold_status = f"held:problems={problems},questions={questions}"
        reasons.append(f"unit {unit_rel} is held (problems={problems}, pending_questions={questions})")
    else:
        hold_status = "clear"

    if activity == "dev":
        if workflow_id not in SPEC_WORKFLOWS:
            reasons.append(f"dev branch {branch} requires workflow in {sorted(SPEC_WORKFLOWS)}, got {workflow_id}")
        decisions = load_decisions(ref.dir)
        for decision in decisions.records:
            if decision.request == "gate:plan-accept" and decision.action != "accept":
                reasons.append(f"carried gate:plan-accept in {decision.file} is {decision.action!r}, not 'accept'")
        if evaluation.stage is not None and evaluation.stage.id == "merge" and "integrate" in evaluation.done:
            stage_status = f"ready:{','.join(evaluation.done)}"
        else:
            current = evaluation.stage.id if evaluation.stage is not None else "complete"
            stage_status = f"incomplete:{current}"
            unmet = ", ".join(check.name for check in evaluation.unmet)
            if evaluation.gate is not None and not evaluation.gate.satisfied:
                reasons.append(f"stage {current} is waiting on gate:{evaluation.gate.name}")
            if unmet:
                reasons.append(f"stage {current} has unmet checks: {unmet}")
            elif evaluation.stage is None or evaluation.stage.id != "merge":
                reasons.append(f"unit {unit_rel} is at stage {current!r}, not ready for merge")
    elif activity == "plan":
        if workflow_id != PROPOSAL_WORKFLOW:
            reasons.append(f"plan branch {branch} requires workflow {PROPOSAL_WORKFLOW}, got {workflow_id}")
        status = anchor_data.get("status")
        if status != "accepted":
            reasons.append(f"{unit_rel}/proposal.md status must be 'accepted' for integration, got {status!r}")
        if anchor_data.get("needs_decompose") is True:
            reasons.append(f"{unit_rel}/proposal.md has needs_decompose=true")
        passed_gates = {gate.name for _stage, gate in evaluation.passed_gates if gate.satisfied}
        for required_gate in ("plan-intent", "plan-accept"):
            if required_gate not in passed_gates:
                reasons.append(f"{unit_rel} has not passed gate:{required_gate}")
        if evaluation.complete and "direction-handoff" in evaluation.done:
            stage_status = f"ready:{','.join(evaluation.done)}"
        else:
            current = evaluation.stage.id if evaluation.stage is not None else "incomplete"
            stage_status = f"incomplete:{current}"
            unmet = ", ".join(check.name for check in evaluation.unmet)
            if evaluation.gate is not None and not evaluation.gate.satisfied:
                reasons.append(f"stage {current} is waiting on gate:{evaluation.gate.name}")
            if unmet:
                reasons.append(f"stage {current} has unmet checks: {unmet}")

    evidence = [
        Evidence("TASK_KIND", "unit"),
        Evidence("WORKFLOW", workflow_id),
        Evidence("UNIT", unit_rel),
        Evidence("SOURCE_SHA", context.finish.source_sha),
        Evidence("TARGET_SHA", context.finish.target_sha),
        Evidence("STAGE_STATUS", stage_status),
        Evidence("HOLD_STATUS", hold_status),
    ]
    for code, key in (("TASK_TITLE", "title"), ("TASK_SUMMARY", "summary")):
        value = anchor_data.get(key)
        if isinstance(value, str) and value.strip():
            evidence.append(Evidence(code, value.strip()))
    reports = load_envelopes(ref.dir).scoped(workflow_id, ref.binding.segment)
    report = reports.latest("final-report")
    if report is not None and report.status == "completed" and report.summary.strip():
        evidence.append(Evidence("RESULT_SUMMARY", report.summary.strip()))
    return evidence, reasons


def _claim_passed(value: object) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        normalized = value.strip().upper()
        return normalized == "PASSED" or normalized == "PASS" or normalized.startswith("PASS ")
    return False


def _touched_units(snapshot: Snapshot, workspace: Path) -> set[str]:
    units: set[str] = set()
    for rel in (*snapshot.changed, *snapshot.deleted):
        parts = Path(rel).parts
        if len(parts) >= 3 and parts[0] == "specs":
            candidate = f"{parts[0]}/{parts[1]}/{parts[2]}"
            if SPEC_UNIT.fullmatch(candidate) and (workspace / candidate).is_dir():
                units.add(candidate)
        elif len(parts) >= 3 and parts[0] == "docs" and parts[1] == "proposals":
            candidate = f"{parts[0]}/{parts[1]}/{parts[2]}"
            if PROPOSAL_UNIT.fullmatch(candidate) and (workspace / candidate).is_dir():
                units.add(candidate)
    return units


def _session_workflow(task_kind: object) -> str:
    if task_kind == "overall-refactor":
        return "sdd-overall-refactor"
    return f"sdd-session-{task_kind}" if isinstance(task_kind, str) and task_kind in SESSION_KINDS else "unknown"


def _check_session_task(
    context: IntegrationContext,
    snapshot: Snapshot,
    workspace: Path,
) -> tuple[list[Evidence], list[str]]:
    branch = context.finish.branch
    activity, _, slug = branch.partition("-")
    reasons: list[str] = []
    if activity != "dev":
        reasons.append(f"session tasks must run on a dev-<slug> branch, not {branch}")

    # Verify the branch does not carry a spec/proposal unit for this slug or leave a touched unit held/incomplete.
    for spec_dir in sorted((workspace / "specs").glob(f"*/*-{slug}")) if (workspace / "specs").is_dir() else ():
        rel = spec_dir.relative_to(workspace).as_posix()
        if SPEC_UNIT.fullmatch(rel) and is_spec_dir(spec_dir.name, slug):
            reasons.append(f"branch {branch} has spec unit {rel}; integrate it as a unit task, not a session task")
    for unit_rel in sorted(_touched_units(snapshot, workspace)):
        unit_dir = workspace / unit_rel
        envelopes = load_envelopes(unit_dir)
        if envelopes.errors:
            reasons.append(f"touched unit {unit_rel} has malformed envelopes")
        hold = envelopes.hold()
        if hold.problems or hold.questions:
            reasons.append(f"touched unit {unit_rel} has an unresolved problem or pending question hold")
        if SPEC_UNIT.fullmatch(unit_rel):
            data, err = _read_frontmatter(unit_dir / "spec.md")
            if err or data.get("status") != "completed":
                reasons.append(f"touched spec unit {unit_rel} is not completed")
        elif PROPOSAL_UNIT.fullmatch(unit_rel):
            data, err = _read_frontmatter(unit_dir / "proposal.md")
            if err or data.get("status") != "accepted":
                reasons.append(f"touched proposal unit {unit_rel} is not accepted")

    try:
        claims = json.loads(context.task.claims_json)
    except ValueError:
        claims = {}
    if not isinstance(claims, dict):
        claims = {}

    source_reason_count = len(reasons)
    task_kind = claims.get("task_kind")
    effort = claims.get("effort")
    if task_kind not in SESSION_KINDS:
        reasons.append("session claims require task_kind in 'feature', 'bugfix' or 'overall-refactor'")
    if effort not in SESSION_EFFORTS:
        reasons.append("session claims require effort in 'low', 'medium' or 'high'")
    for field in ("review", "tests", "lint"):
        if not _claim_passed(claims.get(field)):
            reasons.append(f"session claims require passing {field} verification")
    if task_kind == "bugfix":
        for field in ("reproduced", "resolved"):
            if not _claim_passed(claims.get(field)):
                reasons.append(f"bugfix session claims require passing {field} verification")
    if claims.get("blocked") is True or claims.get("pending_questions") is True:
        reasons.append("session claims report a blocked problem or pending question")

    workflow_id = _session_workflow(task_kind)
    claims_summary = (
        f"kind={task_kind or 'invalid'},effort={effort or 'invalid'},"
        f"review={'pass' if _claim_passed(claims.get('review')) else 'fail'},"
        f"tests={'pass' if _claim_passed(claims.get('tests')) else 'fail'},"
        f"lint={'pass' if _claim_passed(claims.get('lint')) else 'fail'}"
    )
    if task_kind == "bugfix":
        claims_summary += (
            f",reproduced={'pass' if _claim_passed(claims.get('reproduced')) else 'fail'},"
            f"resolved={'pass' if _claim_passed(claims.get('resolved')) else 'fail'}"
        )
    evidence = [
        Evidence("TASK_KIND", "session"),
        Evidence("WORKFLOW", workflow_id),
        Evidence("SOURCE_SHA", context.finish.source_sha),
        Evidence("TARGET_SHA", context.finish.target_sha),
        Evidence("SESSION_CLAIMS", claims_summary),
    ]
    if len(reasons) > source_reason_count:
        evidence.append(Evidence("SESSION_CLAIMS_INVALID", "--claims"))
    return evidence, reasons


def _spec_policy(root: Path, commit: str) -> object:
    """The parsed ``[tool.spec]`` table committed at ``commit``; ``None`` without one, ``"invalid"`` when unreadable."""
    try:
        data = commit_config(root, commit)
    except ConfigError:
        return "invalid"
    if data is None:
        return None
    tool = data.get("tool")
    return tool.get("spec") if isinstance(tool, dict) else None


def _policy_evidence(root: Path, context: IntegrationContext) -> Evidence:
    """``SPEC_POLICY``: the target's and the result's (or source's) ``[tool.spec]``, so a change refuses the build."""
    result = context.result_sha or context.finish.source_sha
    value = [_spec_policy(root, context.finish.target_sha), _spec_policy(root, result)]
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return Evidence("SPEC_POLICY", hashlib.sha256(encoded).hexdigest())


def _unit_advance(root: Path, context: IntegrationContext) -> list[str]:
    """A reason when the build target changed the unit directory since the merge base (the unit is read from the
    source tree, which would not show it)."""
    unit = (context.task.unit or "").strip("/")
    if context.result_sha is None or context.task.kind != "unit" or not unit:
        return []
    plan = context.finish
    prior = run_git(root, "merge-base", "--", plan.target_sha, plan.source_sha).decode().strip()
    if prior == plan.target_sha:
        return []
    if run_git(root, "diff", "--name-only", prior, plan.target_sha, "--", unit).strip():
        return [f"the target changed {unit} since the task branch's merge base; merge the target into the branch"]
    return []


def check(context: IntegrationContext) -> Readiness:
    """Verify SDD completion readiness for ``context`` from committed Git state."""
    from devkit_agt.features.integration import check_project_readiness as project_check
    from devkit_dist.features.project import development_approach

    target_config = commit_config(Path(context.finish.base), context.finish.target_sha) or {}
    if development_approach(target_config).approach == "incubation" and context.task.kind == "session":
        # The independent provider refuses touched retained Units; callers use their Unit validator explicitly.
        return project_check(context)
    base = Path(context.finish.base).resolve()
    worktree = Path(context.finish.path)
    snap_root = _snapshot_root(base, worktree)
    plan = context.finish
    # The unit is read from the source tree; with a result commit, the CI rules check the tree that would land.
    snapshot = _build_snapshot(snap_root, plan.source_sha, plan.target_sha)
    landing = (
        _build_snapshot(snap_root, plan.source_sha, plan.target_sha, context.result_sha)
        if context.result_sha
        else snapshot
    )
    sources = (worktree.resolve(), base) if worktree.is_dir() else (base,)

    with tempfile.TemporaryDirectory(prefix="devkit-spec-readiness-") as temp_dir:
        workspace = Path(temp_dir).resolve()
        materialize_snapshot(snapshot, workspace)
        _populate_managed_files(workspace, sources)

        reasons = _check_project_policies(base, workspace)
        if context.task.kind == "unit":
            evidence, task_reasons = _check_unit_task(context, base, workspace)
        else:
            evidence, task_reasons = _check_session_task(context, snapshot, workspace)
        reasons.extend(task_reasons)

    reasons.extend(_unit_advance(snap_root, context))
    ci_status, ci_reasons = _check_ci_rules(landing)
    evidence.append(Evidence("CI_RULES", ci_status))
    reasons.extend(ci_reasons)
    evidence.append(_policy_evidence(snap_root, context))
    if context.result_sha:
        evidence.append(Evidence("RESULT_SHA", context.result_sha))

    return Readiness(
        source_sha=context.finish.source_sha,
        target_sha=context.finish.target_sha,
        evidence=tuple(evidence),
        reasons=tuple(reasons),
        result_sha=context.result_sha,
        target_bound=TARGET_BOUND,
        disclosure=DISCLOSURE,
        landed_check=f"{DEVKIT} rules check",
    )
