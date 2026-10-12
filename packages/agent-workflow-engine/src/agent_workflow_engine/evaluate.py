"""Stage evaluation: which stage a unit is in, what is unmet, and what comes next."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent_workflow_engine import frontmatter
from agent_workflow_engine.binding import Binding, read_binding
from agent_workflow_engine.checks import (
    ENVELOPE_CHECK_PASS,
    ENVELOPE_COMPLETED,
    FILE_EXISTS,
    FRONTMATTER,
    GATE_PREFIX,
    NOT_SKELETON,
    REVISION_ANCESTOR,
    SKELETON_MARKER,
    TASKS_CHECKED,
    Check,
    CheckClass,
    CheckError,
    CheckResult,
    Invocation,
    Registry,
    count_tasks,
)
from agent_workflow_engine.decisions import Decision, DecisionError, Decisions, load_decisions
from agent_workflow_engine.definition import HANDOFF_GATE, Stage, WorkflowDocument, schema_hash
from agent_workflow_engine.envelope import Envelopes, load_envelopes
from agent_workflow_engine.git import REVISION
from agent_workflow_engine.plugins import BaseCheck, CheckContext

# Returns one description per violation, or raises on a rule execution failure.
LintFunc = Callable[[Path, list[str]], list[str]]
AncestorFunc = Callable[[Path, str, str], bool]

COMPLETED_STATUS = "completed"


class UnitNotFoundError(FileNotFoundError):
    def __init__(self, unit_dir: Path, anchor: str) -> None:
        super().__init__(f"{anchor} not found in {unit_dir.as_posix()}")
        self.unit_dir = unit_dir


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
    plugins: tuple[BaseCheck, ...] = ()  # loaded plugin checks definitions may reference
    roles: dict[str, str] = field(default_factory=dict)  # role -> contract path, for [DELEGATE]


@dataclass(frozen=True)
class Skipped:
    id: str
    reason: str  # the policy entry that skipped the stage, e.g. approvals.<gate>=off or stages.<id>=off

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "reason": self.reason}


@dataclass(frozen=True)
class Gate:
    name: str
    policy: str
    given: bool

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "policy": self.policy, "given": self.given}


@dataclass(frozen=True)
class Delegate:
    role: str
    isolation: str
    contract: str | None = None  # workspace-relative path of the role's contract, when known

    def to_dict(self) -> dict[str, str | None]:
        return {"role": self.role, "isolation": self.isolation, "contract": self.contract}


@dataclass(frozen=True)
class Waiting:
    class_: CheckClass
    checks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"class": self.class_.value, "checks": list(self.checks)}


@dataclass(frozen=True)
class Drift:
    recorded: str
    current: str

    def to_dict(self) -> dict[str, str]:
        return {"recorded": self.recorded, "current": self.current}


@dataclass(frozen=True)
class Option:
    id: str
    label: str
    description: str = ""
    recommended: bool = False
    eligible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "recommended": self.recommended,
            "eligible": self.eligible,
        }


@dataclass(frozen=True)
class Target:
    type: str  # gate | check | handoff
    name: str
    stage: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "name": self.name, "stage": self.stage}


@dataclass(frozen=True)
class Request:
    """An open question for a person; see docs/workflow/human-interaction.md."""

    id: str
    kind: str  # approve | choose
    title: str
    prompt: str
    target: Target
    options: tuple[Option, ...] = ()
    multi: bool = False
    allow_other: bool = False
    allow_note: bool = True
    declined: Decision | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "prompt": self.prompt,
            "target": self.target.to_dict(),
            "options": [o.to_dict() for o in self.options],
            "multi": self.multi,
            "allow_other": self.allow_other,
            "allow_note": self.allow_note,
            "declined": (
                {"file": self.declined.file, "note": self.declined.note, "at": self.declined.at}
                if self.declined
                else None
            ),
        }


GATE_REQUEST = "gate:"
CHECK_REQUEST = "check:"
HANDOFF_REQUEST = "handoff"


@dataclass(frozen=True)
class CandidateResult:
    workflow: str
    recommended: bool
    eligible: bool
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "recommended": self.recommended,
            "eligible": self.eligible,
            "checks": [c.to_dict() for c in self.checks],
        }


@dataclass(frozen=True)
class Handoff:
    """The handoff decision once the bound workflow is complete.

    ``chosen`` is set only under ``policy=auto`` when an eligible candidate
    exists; under ``ask`` a person picks, and with no eligible candidate the
    engine falls back to asking.
    """

    policy: str
    candidates: tuple[CandidateResult, ...]
    chosen: str | None = None
    decision: Decision | None = None  # recorded choice that produced ``chosen``, if any

    @property
    def eligible(self) -> tuple[str, ...]:
        return tuple(c.workflow for c in self.candidates if c.eligible)

    @property
    def recommended(self) -> tuple[str, ...]:
        return tuple(c.workflow for c in self.candidates if c.recommended and c.eligible)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "candidates": [c.to_dict() for c in self.candidates],
            "eligible": list(self.eligible),
            "recommended": list(self.recommended),
            "chosen": self.chosen,
            "decision": self.decision.file if self.decision else None,
        }


@dataclass
class Result:
    workflow: str
    unit: str
    status: str
    binding: Binding
    done: list[str] = field(default_factory=list)
    skipped: list[Skipped] = field(default_factory=list)
    stage: Stage | None = None
    unmet: list[CheckResult] = field(default_factory=list)
    next_skill: str = ""
    delegate: Delegate | None = None
    gate: Gate | None = None
    waiting: Waiting | None = None
    envelope_errors: list[Any] = field(default_factory=list)
    drift: Drift | None = None
    lint_error: str | None = None
    handoff: Handoff | None = None
    requests: list[Request] = field(default_factory=list)
    decision_errors: list[DecisionError] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return self.stage is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "unit": self.unit,
            "status": self.status,
            "bound": self.binding.bound,
            "done": list(self.done),
            "skipped": [s.to_dict() for s in self.skipped],
            "stage": self.stage.to_dict() if self.stage else None,
            "unmet": [u.to_dict() for u in self.unmet],
            "next_skill": self.next_skill or None,
            "delegate": self.delegate.to_dict() if self.delegate else None,
            "gate": self.gate.to_dict() if self.gate else None,
            "waiting": self.waiting.to_dict() if self.waiting else None,
            "complete": self.complete,
            "envelope_errors": [e.to_dict() for e in self.envelope_errors],
            "drift": self.drift.to_dict() if self.drift else None,
            "lint_error": self.lint_error,
            "handoff": self.handoff.to_dict() if self.handoff else None,
            "requests": [r.to_dict() for r in self.requests],
            "decision_errors": [e.to_dict() for e in self.decision_errors],
        }


class _Evaluator:
    def __init__(self, doc: WorkflowDocument, registry: Registry, opts: Options) -> None:
        self.doc = doc
        self.registry = registry
        self.opts = opts
        self.unit_dir = opts.unit_dir
        self.envelopes: Envelopes = load_envelopes(self.unit_dir)
        self.decisions: Decisions = load_decisions(self.unit_dir)
        self.given = set(opts.given)
        self.cache: dict[str, CheckResult] = {}
        self.lint_done = False
        self.lint_violations: list[str] = []
        self.lint_error: str | None = None

    # -- check evaluation --------------------------------------------------

    def eval_ref(self, ref: str) -> CheckResult:
        if ref in self.cache:
            return self.cache[ref]
        try:
            inv, check = self.registry.resolve_name(ref)
        except CheckError as exc:
            result = CheckResult(ref, CheckClass.DISK, False, False, str(exc))
        else:
            result = self._eval(ref, inv, check)
        self.cache[ref] = result
        return result

    def _eval(self, ref: str, inv: Invocation, check: Check) -> CheckResult:
        if check.class_ == CheckClass.DISK:
            ok, detail = self.disk(inv)
            return CheckResult(ref, check.class_, ok, True, detail)
        if check.class_ == CheckClass.LINT:
            evaluated, ok, detail = self.lint()
            return CheckResult(ref, check.class_, ok, evaluated, detail)
        if check.class_ == CheckClass.PLUGIN:
            return self.plugin(ref, inv)
        if ref in self.given:
            return CheckResult(ref, check.class_, True, False, "given by executor")
        if check.class_ == CheckClass.HUMAN:
            accepted = self.accepted(CHECK_REQUEST + ref)
            if accepted is not None:
                return CheckResult(ref, check.class_, True, False, f"accepted by {accepted.file}")
        return CheckResult(ref, check.class_, False, False, f"declared for {check.class_.value}; not evaluated")

    def plugin(self, ref: str, inv: Invocation) -> CheckResult:
        """Run a loaded plugin check; a raising plugin is an unsatisfied, evaluated result."""
        plugin = self.registry.plugins[inv.name]
        ctx = CheckContext(
            workspace_root=self.opts.workspace_root,
            unit_dir=self.unit_dir,
            anchor=self.opts.anchor,
            ref=ref,
            name=inv.name,
            args=inv.args,
            envelopes=self.envelopes,
        )
        try:
            result = plugin.evaluate(ctx)
        except Exception as exc:
            return CheckResult(ref, CheckClass.PLUGIN, False, True, f"check failed: {exc}")
        if not isinstance(result, CheckResult):
            return CheckResult(ref, CheckClass.PLUGIN, False, True, "check returned no CheckResult")
        return CheckResult(ref, CheckClass.PLUGIN, result.satisfied, result.evaluated, result.detail)

    def accepted(self, request_id: str) -> Decision | None:
        decision = self.decisions.effective(request_id)
        return decision if decision is not None and decision.action == "accept" else None

    def declined(self, request_id: str) -> Decision | None:
        decision = self.decisions.effective(request_id)
        return decision if decision is not None and decision.action == "decline" else None

    def gate_check(self, gate: str, policy: str) -> CheckResult:
        name = GATE_PREFIX + gate
        if policy == "auto":
            return CheckResult(name, CheckClass.HUMAN, True, False, "policy=auto")
        if gate in self.given:
            return CheckResult(name, CheckClass.HUMAN, True, False, "given by executor")
        accepted = self.accepted(GATE_REQUEST + gate)
        if accepted is not None:
            return CheckResult(name, CheckClass.HUMAN, True, False, f"accepted by {accepted.file}")
        return CheckResult(name, CheckClass.HUMAN, False, False, f"approval for gate {gate!r} not given")

    def _read(self, name: str) -> str | None:
        path = self.unit_dir / name
        try:
            return path.read_text("utf-8")
        except (OSError, UnicodeError):
            return None

    def disk(self, inv: Invocation) -> tuple[bool, str]:
        args = inv.args
        if inv.name == FILE_EXISTS:
            return (self.unit_dir / args[0]).exists(), ""
        if inv.name == FRONTMATTER:
            file, fld, want = args
            text = self._read(file)
            if text is None:
                return False, f"{file} missing"
            try:
                got = frontmatter.field(frontmatter.parse(text), fld)
            except frontmatter.FrontmatterError as exc:
                return False, f"{file}: {exc}"
            return got == want, f"{fld}={got or '-'}"
        if inv.name == NOT_SKELETON:
            text = self._read(args[0])
            if text is None:
                return True, f"{args[0]} missing"
            if any(line.strip() == SKELETON_MARKER for line in text.splitlines()):
                return False, f"{args[0]} is a handoff skeleton"
            return True, ""
        if inv.name == TASKS_CHECKED:
            text = self._read(args[0])
            if text is None:
                return False, f"{args[0]} missing"
            checked, total = count_tasks(text)
            if total == 0:
                return False, "no tasks"
            return checked == total, f"{checked}/{total} checked"
        if inv.name == ENVELOPE_COMPLETED:
            env = self.envelopes.deciding(args[0])
            if env is None:
                return False, f"no {args[0]} envelope"
            open_count = env.open_findings()
            return (
                env.status == "completed" and open_count == 0,
                f"{env.file} status={env.status} open_findings={open_count}",
            )
        if inv.name == ENVELOPE_CHECK_PASS:
            kind, key = args
            env = self.envelopes.deciding(kind)
            if env is None:
                return False, f"no {kind} envelope"
            return env.status == "completed" and env.check_pass(
                key
            ), f"{env.file} status={env.status} {key}={env.checks.get(key, '')!r}"
        if inv.name == REVISION_ANCESTOR:
            return self.revision_ancestor(args[0], args[1])
        return False, "no evaluator"

    def revision_ancestor(self, ancestor_kind: str, descendant_kind: str) -> tuple[bool, str]:
        heads: list[str] = []
        for kind in (ancestor_kind, descendant_kind):
            env = self.envelopes.latest(kind)
            if env is None:
                return False, f"no {kind} envelope"
            if not env.diff_head:
                return False, f"{env.file} has no diff_scope.head"
            if not REVISION.match(env.diff_head):
                return False, f"{env.file} head {env.diff_head!r} is not a revision"
            heads.append(env.diff_head)
        if self.opts.ancestor is None:
            return False, "no git function configured"
        try:
            ok = self.opts.ancestor(self.opts.workspace_root, heads[0], heads[1])
        except Exception as exc:
            return False, f"git: {exc}"
        return ok, f"{heads[0]}..{heads[1]} ancestor={str(ok).lower()}"

    def lint(self) -> tuple[bool, bool, str]:
        if self.opts.skip_lint:
            return False, True, "skipped (--no-lint)"
        if self.opts.lint is None:
            return False, True, "no lint function configured"
        if not self.lint_done:
            self.lint_done = True
            files = sorted(
                p.relative_to(self.opts.workspace_root).as_posix() for p in self.unit_dir.rglob("*") if p.is_file()
            )
            try:
                self.lint_violations = self.opts.lint(self.opts.workspace_root, files)
            except Exception as exc:
                self.lint_error = str(exc)
        if self.lint_error:
            return True, False, f"lint failed: {self.lint_error}"
        if self.lint_violations:
            return True, False, f"{len(self.lint_violations)} violation(s): {'; '.join(self.lint_violations)}"
        return True, True, ""


def _waiting_for(stage: Stage, unmet: list[CheckResult]) -> Waiting | None:
    if stage.gate is not None and any(u.name == GATE_PREFIX + stage.gate for u in unmet):
        return Waiting(CheckClass.HUMAN, tuple(u.name for u in unmet))
    class_: CheckClass | None = None
    names: list[str] = []
    for u in unmet:
        if u.class_ not in (CheckClass.RUNNER, CheckClass.HUMAN):
            return None
        class_ = u.class_ if class_ is None else (class_ if class_ == u.class_ else CheckClass.HUMAN)
        names.append(u.name)
    if not names or class_ is None:
        return None
    return Waiting(class_, tuple(names))


def _handoff(doc: WorkflowDocument, ev: _Evaluator, policy: str) -> Handoff | None:
    """Evaluate every ``next`` candidate's preconditions and apply the handoff policy.

    A recorded, still-eligible choice wins under either policy; ``auto`` then
    falls back to the first eligible candidate.
    """
    if not doc.next or policy == "off":
        return None
    results: list[CandidateResult] = []
    for cand in doc.next:
        checks = tuple(ev.eval_ref(ref) for ref in cand.when)
        results.append(CandidateResult(cand.workflow, cand.recommended, all(c.satisfied for c in checks), checks))
    eligible = {c.workflow for c in results if c.eligible}
    chosen = None
    decision = ev.accepted(HANDOFF_REQUEST)
    if decision is not None and isinstance(decision.value, str) and decision.value in eligible:
        chosen = decision.value
    else:
        decision = None
        if policy == "auto":
            chosen = next((c.workflow for c in results if c.eligible), None)
    return Handoff(policy, tuple(results), chosen, decision)


def _stage_requests(doc: WorkflowDocument, stage: Stage, unmet: list[CheckResult], ev: _Evaluator) -> list[Request]:
    requests: list[Request] = []
    for u in unmet:
        if stage.gate and u.name == GATE_PREFIX + stage.gate:
            rid = GATE_REQUEST + stage.gate
            requests.append(
                Request(
                    id=rid,
                    kind="approve",
                    title=f"Approve {stage.gate}"[:40],
                    prompt=f"Approve gate {stage.gate!r} to finish stage {stage.id!r} of {doc.id}.",
                    target=Target("gate", stage.gate, stage.id),
                    declined=ev.declined(rid),
                )
            )
        elif u.class_ == CheckClass.HUMAN and u.satisfied is False:
            rid = CHECK_REQUEST + u.name
            requests.append(
                Request(
                    id=rid,
                    kind="approve",
                    title=f"Confirm {u.name}"[:40],
                    prompt=f"Confirm human check {u.name!r} for stage {stage.id!r} of {doc.id}.",
                    target=Target("check", u.name, stage.id),
                    declined=ev.declined(rid),
                )
            )
    return requests


def _handoff_request(doc: WorkflowDocument, handoff: Handoff, ev: _Evaluator) -> Request:
    options = tuple(
        Option(
            c.workflow,
            c.workflow,
            " ".join(f"{k.name}={str(k.satisfied).lower()}" for k in c.checks),
            c.recommended,
            c.eligible,
        )
        for c in handoff.candidates
    )
    return Request(
        id=HANDOFF_REQUEST,
        kind="choose",
        title="Choose next workflow",
        prompt=f"Workflow {doc.id} is complete; choose the workflow that continues this unit.",
        target=Target("handoff", doc.id, None),
        options=options,
        declined=ev.declined(HANDOFF_REQUEST),
    )


def evaluate(doc: WorkflowDocument, opts: Options) -> Result:
    """Compute the current stage of a unit against a workflow document."""
    anchor_path = opts.unit_dir / opts.anchor
    if not anchor_path.is_file():
        raise UnitNotFoundError(opts.unit_dir, opts.anchor)
    try:
        anchor_data = frontmatter.read(anchor_path)
    except frontmatter.FrontmatterError:
        anchor_data = {}
    status = frontmatter.field(anchor_data, "status")
    binding = read_binding(anchor_path) if anchor_data else Binding()

    registry = Registry.build(opts.anchor, doc.declared_checks, opts.plugins)
    ev = _Evaluator(doc, registry, opts)
    try:
        unit_rel = opts.unit_dir.relative_to(opts.workspace_root).as_posix()
    except ValueError:
        unit_rel = opts.unit_dir.as_posix()

    res = Result(workflow=doc.id, unit=unit_rel, status=status, binding=binding)
    res.envelope_errors = list(ev.envelopes.errors)

    current = schema_hash(doc)
    if binding.bound and binding.hash != current:
        res.drift = Drift(recorded=binding.hash, current=current)

    for stage in doc.stages:
        if stage.exception:
            continue
        if opts.stages.get(stage.id) == "off":
            res.skipped.append(Skipped(stage.id, f"stages.{stage.id}=off"))
            continue
        policy = opts.approvals.get(stage.gate, "ask") if stage.gate else None
        if stage.gate and policy == "off":
            res.skipped.append(Skipped(stage.id, f"approvals.{stage.gate}=off"))
            continue
        results = [ev.eval_ref(ref) for ref in stage.exit]
        if stage.gate and policy:
            results.append(ev.gate_check(stage.gate, policy))
        unmet = [r for r in results if not r.satisfied]
        if not unmet:
            res.done.append(stage.id)
            continue
        if stage.optional:
            continue
        res.stage = stage
        res.unmet = unmet
        res.next_skill = stage.skills[0] if stage.skills else ""
        if stage.isolation != "none" and stage.role not in ("developer", "-", ""):
            res.delegate = Delegate(stage.role, stage.isolation, opts.roles.get(stage.role))
        if stage.gate and policy:
            res.gate = Gate(stage.gate, policy, stage.gate in ev.given)
        res.waiting = _waiting_for(stage, unmet)
        res.requests = _stage_requests(doc, stage, unmet, ev)
        break

    if res.stage is None:
        res.handoff = _handoff(doc, ev, opts.approvals.get(HANDOFF_GATE, "ask"))
        if res.handoff is not None and res.handoff.chosen is None:
            res.waiting = Waiting(CheckClass.HUMAN, (HANDOFF_GATE,))
            res.requests = [_handoff_request(doc, res.handoff, ev)]

    res.decision_errors = list(ev.decisions.errors)
    res.lint_error = ev.lint_error
    return res


def is_completed(result: Result) -> bool:
    return result.status == COMPLETED_STATUS
