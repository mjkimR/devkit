"""Stage evaluation: which stage a unit is in, what is unmet and what comes next.

``evaluate_definition`` is pure: it reads the unit's files and returns a
``UnitEvaluation``. The drift policy belongs to ``Workspace.evaluate_unit``;
nothing here writes a file.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from devkit.advisory import AdvisoryError, as_advisory_error
from devkit.core.errors import UnsafePathError
from devkit.workflow.definition.checks import (
    GATE_PREFIX,
    Check,
    CheckClass,
    CheckError,
    CheckResult,
    Invocation,
    Registry,
)
from devkit.workflow.definition.definition import HANDOFF_GATE, StageDefinition, WorkflowDocument, schema_hash
from devkit.workflow.errors import GatePolicyError, UnitNotFoundError
from devkit.workflow.evaluation.primitives import AncestorFunc, PrimitiveContext, evaluate_primitive
from devkit.workflow.evaluation.requests import handoff_request, question_requests, stage_requests
from devkit.workflow.evaluation.results import Delegate, Drift, GateStatus, Skipped, UnitEvaluation, Waiting
from devkit.workflow.handoff import evaluate_handoff
from devkit.workflow.project.roles import is_builtin_role
from devkit.workflow.unit.binding import AnchorState, Binding, read_anchor
from devkit.workflow.unit.decisions import (
    CHECK_PREFIX,
    HANDOFF_REQUEST,
    RETURN_PREFIX,
    Decision,
    Decisions,
    Instant,
    load_decisions,
    record_instant,
)
from devkit.workflow.unit.envelope import Envelope, Envelopes, Hold, load_envelopes
from devkit.workflow.unit.records import is_temporary

__all__ = ["LintFunc", "Options", "evaluate_definition"]

# Returns one description per blocking violation, or raises (an ``AdvisoryError``) when the rules cannot run.
LintFunc = Callable[[Path, list[str]], list[str]]
# Violations a ``lint-clean`` detail quotes; the rest are counted, with the command that lists them all.
LINT_DETAIL_SHOWN = 3
# The unmet check a gate stage reports while unresolved problems or unanswered questions hold its gate.
HOLD_CHECK = "envelope-hold"


@dataclass(frozen=True)
class Options:
    workspace_root: Path
    unit_dir: Path  # absolute
    anchor: str
    approvals: dict[str, str] = field(default_factory=dict)
    stages: dict[str, str] = field(default_factory=dict)  # stage id -> on|off ([workflow.stages])
    given: tuple[str, ...] = ()
    lint: LintFunc | None = None
    skip_lint: bool = False
    ancestor: AncestorFunc | None = None
    roles: dict[str, str] = field(default_factory=dict)  # role -> contract path, for [DELEGATE]


class _Evaluator:
    def __init__(self, doc: WorkflowDocument, registry: Registry, opts: Options, binding: Binding) -> None:
        self.doc = doc
        self.registry = registry
        self.opts = opts
        self.unit_dir = opts.unit_dir
        self.all_decisions: Decisions = load_decisions(self.unit_dir)
        # Only records of this workflow written after the last handoff count.
        self.decisions = self.all_decisions.segment(doc.id, binding.segment_start)
        returns = [r for r in self.decisions.records if r.kind == "return" and r.action == "accept"]
        self.returns = [(r.seq, doc.stage_index(r.request[len(RETURN_PREFIX) :])) for r in returns]
        # Problems and questions hold the unit whatever their segment, and a return does not clear them.
        loaded = load_envelopes(self.unit_dir)
        self.hold: Hold = loaded.hold()
        self.held_from = _held_from(self.hold, doc)
        # Envelopes scoped to another workflow or segment do not count either; unscoped ones count everywhere.
        self.envelopes: Envelopes = _after_returns(
            loaded.scoped(doc.id, binding.segment),
            [(record_instant(r.at), doc.stage_index(r.request[len(RETURN_PREFIX) :])) for r in returns],
            doc,
        )
        self.primitives = PrimitiveContext(opts.workspace_root, self.unit_dir, self.envelopes, opts.ancestor)
        self.given = set(opts.given)
        self.cache: dict[tuple[str, str], CheckResult] = {}
        self.lint_done = False
        self.lint_violations: list[str] = []
        self.lint_error: AdvisoryError | None = None

    # -- decisions -----------------------------------------------------------

    def voided(self, record: Decision) -> bool:
        """An approval is void once a later return re-entered its stage or an earlier one."""
        if record.kind != "approve":
            return False
        index = self.doc.stage_index(record.stage)
        return index >= 0 and any(seq > record.seq and 0 <= target <= index for seq, target in self.returns)

    def effective(self, request_id: str, stage: str = "") -> Decision | None:
        """The latest record answering ``request_id`` for ``stage`` (``""``: the handoff, which has none).

        A gate or human check used by several stages is answered for each of them separately.
        """
        for record in reversed(self.decisions.records):
            if (
                record.request == request_id
                and record.stage == stage
                and record.action != "cancel"
                and not self.voided(record)
            ):
                return record
        return None

    def accepted(self, request_id: str, stage: str = "") -> Decision | None:
        decision = self.effective(request_id, stage)
        return decision if decision is not None and decision.action == "accept" else None

    def declined(self, request_id: str, stage: str = "") -> Decision | None:
        decision = self.effective(request_id, stage)
        return decision if decision is not None and decision.action == "decline" else None

    def approvals_after(self, index: int) -> list[Decision]:
        """Accepted, still valid approvals for stages after position ``index``."""
        stale: list[Decision] = []
        for record in self.decisions.records:
            if (
                record.kind == "approve"
                and record.action == "accept"
                and self.doc.stage_index(record.stage) > index
                and self.effective(record.request, record.stage) is record
            ):
                stale.append(record)
        return stale

    # -- check evaluation ------------------------------------------------------

    def eval_ref(self, ref: str, stage: str = "") -> CheckResult:
        """Evaluate ``ref`` as a check of ``stage``; a human check's answer belongs to its stage."""
        try:
            inv, check = self.registry.resolve_name(ref)
        except CheckError as exc:
            return CheckResult(ref, CheckClass.DISK, False, False, str(exc))
        key = (ref, stage if check.class_ == CheckClass.HUMAN else "")
        if key not in self.cache:
            self.cache[key] = self._eval(ref, inv, check, stage)
        return self.cache[key]

    def _eval(self, ref: str, inv: Invocation, check: Check, stage: str) -> CheckResult:
        if check.class_ == CheckClass.DISK:
            outcome = evaluate_primitive(self.primitives, inv.name, inv.args)
            return CheckResult(ref, check.class_, outcome.satisfied, outcome.evaluated, outcome.detail)
        if check.class_ == CheckClass.LINT:
            evaluated, ok, detail = self.lint()
            return CheckResult(ref, check.class_, ok, evaluated, detail)
        if ref in self.given:
            return CheckResult(ref, check.class_, True, False, "given by executor")
        if check.class_ == CheckClass.HUMAN:
            accepted = self.accepted(CHECK_PREFIX + ref, stage)
            if accepted is not None:
                return CheckResult(ref, check.class_, True, False, f"accepted by {accepted.file}")
        return CheckResult(ref, check.class_, False, False, f"declared for {check.class_.value}; not evaluated")

    def gate(self, gate: str, policy: str, stage: str) -> GateStatus:
        if policy == "auto":
            return GateStatus(gate, policy, True, "policy")
        if gate in self.given:
            return GateStatus(gate, policy, True, "given")
        accepted = self.accepted(GATE_PREFIX + gate, stage)
        if accepted is not None:
            return GateStatus(gate, policy, True, "decision", accepted.file)
        return GateStatus(gate, policy, False)

    def lint(self) -> tuple[bool, bool, str]:
        if self.opts.skip_lint:
            return False, True, "skipped (--no-lint)"
        if self.opts.lint is None:
            return False, True, "no lint function configured"
        if not self.lint_done:
            self.lint_done = True
            root = self.opts.workspace_root
            try:
                if not self.unit_dir.is_relative_to(root):
                    raise UnsafePathError(
                        f"unit {self.unit_dir.as_posix()} resolves outside the workspace root {root.as_posix()}; "
                        "lint-clean lints only files of the workspace",
                        target_files=[self.unit_dir.as_posix()],
                        fix=(
                            "Pass a unit directory inside the workspace (replace a symbolic link that leads out of it), "
                            "or run the command with -w <the unit's project root>"
                        ),
                    )
                files = _unit_files(self.unit_dir, root)
                self.lint_violations = self.opts.lint(root, files)
            except Exception as exc:
                self.lint_error = as_advisory_error(exc)
        if self.lint_error is not None:
            return True, False, f"lint failed: {self.lint_error.message}"
        if self.lint_violations:
            shown = "; ".join(self.lint_violations[:LINT_DETAIL_SHOWN])
            more = len(self.lint_violations) - LINT_DETAIL_SHOWN
            if more > 0:
                unit = _rel(self.unit_dir, self.opts.workspace_root)
                shown += f"; {more} more (devkit rules check {unit})"
            return True, False, f"{len(self.lint_violations)} violation(s): {shown}"
        return True, True, ""


def _unit_files(unit_dir: Path, root: Path) -> list[str]:
    """The unit's files for ``lint-clean``, without the temporary files of writes in progress (``is_temporary``).

    A writer removes its temporary file at any moment, so linting one could fail on a file that no longer exists.
    """
    return sorted(_rel(p, root) for p in unit_dir.rglob("*") if not is_temporary(p.name) and p.is_file())


def _rel(path: Path, root: Path) -> str:
    """``path`` relative to ``root`` when inside it, else as given (``Workspace.rel``)."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _after_returns(envelopes: Envelopes, returns: list[tuple[Instant | None, int]], doc: WorkflowDocument) -> Envelopes:
    """The envelopes no later return re-opened.

    A return to a stage voids, besides the approvals, every envelope recorded for that stage or a later one that is
    not certainly after the return: going back means doing that work again, so an earlier review or report no longer
    satisfies the stage. Each time spans what its precision allows (``record_instant``: a whole second for
    ``...:00Z``), and an envelope counts only when its earliest possible time is at or after the latest possible
    time of the return; when the order is unknown, asking for the envelope again is safer than letting stale
    evidence count. ``envelope new`` stamps a new envelope after the segment's latest return, so it always counts.
    An envelope without a stage of the definition or a ``created_at``, or a return without a time, voids nothing.
    """
    timed = [(at.end, target) for at, target in returns if at is not None and target >= 0]
    if not timed:
        return envelopes

    def current(envelope: Envelope) -> bool:
        written, index = record_instant(envelope.created_at), doc.stage_index(envelope.stage)
        if written is None or index < 0:
            return True
        return not any(written.start < end and target <= index for end, target in timed)

    kept = {kind: [e for e in items if current(e)] for kind, items in envelopes.by_kind.items()}
    return Envelopes({kind: items for kind, items in kept.items() if items}, list(envelopes.errors))


def _gate_result(gate: GateStatus) -> CheckResult:
    """The implicit ``gate:<name>`` human check of a gate that is not yet satisfied."""
    return CheckResult(
        GATE_PREFIX + gate.name, CheckClass.HUMAN, False, False, f"approval for gate {gate.name!r} not given"
    )


def _check_gate_policies(doc: WorkflowDocument, opts: Options) -> None:
    """Refuse a ``[workflow.approvals]`` policy the definition does not accept for its gate (``GatePolicyError``)."""
    for gate in sorted(doc.gates):
        policy, allowed = opts.approvals.get(gate, "ask"), doc.gate_policies_for(gate)
        if policy not in allowed:
            raise GatePolicyError(
                f"[workflow.approvals] {gate} = {policy!r}, but workflow {doc.id} accepts only"
                f" {' | '.join(allowed)} for that gate",
                target_files=[".devkit/config.toml"],
                fix=f"Remove {gate} from [workflow.approvals] in .devkit/config.toml, or set it to one of"
                f" {', '.join(allowed)}",
            )


def _held_from(hold: Hold, doc: WorkflowDocument) -> int:
    """The index of the first stage whose gate the hold keeps from passing.

    A problem or question holds the gate of the stage its worker envelope was written in and of every later stage;
    gates passed before it stay passed, so a run that resolves it goes on from where the unit is. A malformed worker
    envelope holds from the stage it still states. An envelope of another workflow or with no stage of this one
    holds every gate.
    """
    scopes = [(e.stage, e.workflow) for e in (*hold.problems, *(e for e, _ in hold.questions))]
    scopes += [(e.stage, e.workflow) for e in hold.malformed]
    if not scopes:
        return 0
    indexes = [doc.stage_index(stage) if workflow in ("", doc.id) else -1 for stage, workflow in scopes]
    return 0 if any(i < 0 for i in indexes) else min(indexes)


def _hold_result(hold: Hold) -> CheckResult:
    """The unmet ``envelope-hold`` check of a gate stage whose gate the unit's envelopes hold."""
    parts = []
    blocking = [e.file for e in hold.problems] + [e.file for e in hold.malformed]
    if blocking:
        parts.append("blocked by " + ", ".join(blocking))
    if hold.questions:
        parts.append(
            f"{len(hold.questions)} unanswered question(s) in " + ", ".join(sorted({e.file for e, _ in hold.questions}))
        )
    return CheckResult(HOLD_CHECK, CheckClass.DISK, False, True, "; ".join(parts))


def _waiting_for(stage: StageDefinition, unmet: list[CheckResult]) -> Waiting | None:
    """Who the stage waits for: only people or runners, once nothing else is unmet."""
    if not unmet:
        return None
    if stage.gate is not None and any(u.name == GATE_PREFIX + stage.gate for u in unmet):
        return Waiting(CheckClass.HUMAN, tuple(u.name for u in unmet))
    class_: CheckClass | None = None
    for u in unmet:
        if u.class_ not in (CheckClass.RUNNER, CheckClass.HUMAN):
            return None
        class_ = u.class_ if class_ in (None, u.class_) else CheckClass.HUMAN
    assert class_ is not None
    return Waiting(class_, tuple(u.name for u in unmet))


def _read_anchor(opts: Options, unit_rel: str) -> AnchorState:
    anchor_path = opts.unit_dir / opts.anchor
    if not anchor_path.is_file():
        raise UnitNotFoundError(f"{opts.anchor} not found in {unit_rel}")
    return read_anchor(anchor_path, f"{unit_rel}/{opts.anchor}")


def evaluate_definition(doc: WorkflowDocument, opts: Options) -> UnitEvaluation:
    """Compute the current stage of a unit against a workflow document.

    Raises ``UnitNotFoundError`` when the anchor is missing and
    ``AnchorInvalidError`` when its frontmatter cannot be read.
    """
    unit_rel = _rel(opts.unit_dir, opts.workspace_root)
    state = _read_anchor(opts, unit_rel)
    binding = state.binding
    registry = Registry.build(opts.anchor, doc.declared_checks)
    ev = _Evaluator(doc, registry, opts, binding)

    _check_gate_policies(doc, opts)
    res = UnitEvaluation(workflow=doc.id, unit=unit_rel, status=state.status, binding=binding)
    res.envelope_errors = list(ev.envelopes.errors)
    if binding.bound and binding.workflow != doc.id:
        res.bound_elsewhere = binding.workflow
    elif binding.bound and binding.hash != (current := schema_hash(doc)):
        res.drift = Drift(recorded=binding.hash, current=current)

    for index, stage in enumerate(doc.stages):
        if stage.exception:
            continue
        if opts.stages.get(stage.id) == "off":
            res.skipped.append(Skipped(stage.id, f"stages.{stage.id}=off"))
            continue
        policy = opts.approvals.get(stage.gate, "ask") if stage.gate else None
        if stage.gate and policy == "off":
            res.skipped.append(Skipped(stage.id, f"approvals.{stage.gate}=off"))
            continue
        unmet = [r for r in (ev.eval_ref(ref, stage.id) for ref in stage.exit) if not r.satisfied]
        gate = ev.gate(stage.gate, policy, stage.id) if stage.gate and policy else None
        if gate is not None and ev.hold and index >= ev.held_from:
            # No gate at or after the stage that raised the hold passes, by any source; it is not asked.
            gate = GateStatus(gate.name, gate.policy, False, held=True)
            if not unmet:
                unmet.append(_hold_result(ev.hold))
        # The gate is asked only once the stage's own work is done.
        if gate is not None and not gate.satisfied and not unmet:
            unmet.append(_gate_result(gate))
        if not unmet and (gate is None or gate.satisfied):
            res.done.append(stage.id)
            if gate is not None:
                res.passed_gates.append((stage.id, gate))  # what passed it: policy, given or a decision record
            continue
        if stage.optional:
            continue
        res.stage = stage
        res.unmet = unmet
        res.next_skill = stage.skills[0] if stage.skills else ""
        if stage.isolation != "none" and not is_builtin_role(stage.role):
            res.delegate = Delegate(stage.role, stage.isolation, opts.roles.get(stage.role))
        res.gate = gate
        res.waiting = _waiting_for(stage, unmet)
        res.requests = stage_requests(doc, stage, unmet, lambda rid, sid=stage.id: ev.declined(rid, sid))
        res.stale_approvals = ev.approvals_after(index)
        break

    res.decision_errors = list(ev.all_decisions.errors)
    if res.stage is None:
        handoff, ignored = evaluate_handoff(
            doc, ev.eval_ref, ev.accepted(HANDOFF_REQUEST), opts.approvals.get(HANDOFF_GATE, "ask")
        )
        res.handoff = handoff
        if ignored is not None:
            res.decision_errors.append(ignored)
        if handoff is not None and handoff.chosen is None and not ev.hold:
            res.waiting = Waiting(CheckClass.HUMAN, (HANDOFF_GATE,))
            res.requests = [handoff_request(doc, handoff, ev.declined)]

    res.hold = ev.hold
    if ev.hold.questions:
        asked = question_requests(ev.hold.questions)
        res.requests = [*res.requests, *asked]
        # The answers decide how the work goes on: the unit waits for them, not for its other checks.
        res.waiting = Waiting(CheckClass.HUMAN, tuple(r.id for r in asked))
    res.lint_error = ev.lint_error
    return res
