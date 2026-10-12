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
    Invocation,
    Registry,
    count_tasks,
)
from agent_workflow_engine.definition import Stage, WorkflowDocument, schema_hash
from agent_workflow_engine.envelope import Envelopes, load_envelopes
from agent_workflow_engine.git import REVISION

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
    given: tuple[str, ...] = ()
    lint: LintFunc | None = None
    skip_lint: bool = False
    ancestor: AncestorFunc | None = None


@dataclass(frozen=True)
class CheckResult:
    name: str
    class_: CheckClass
    satisfied: bool
    evaluated: bool
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "class": self.class_.value,
            "satisfied": self.satisfied,
            "evaluated": self.evaluated,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class Skipped:
    id: str
    policy: str

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "policy": self.policy}


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

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "isolation": self.isolation}


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
        }


class _Evaluator:
    def __init__(self, doc: WorkflowDocument, registry: Registry, opts: Options) -> None:
        self.doc = doc
        self.registry = registry
        self.opts = opts
        self.unit_dir = opts.unit_dir
        self.envelopes: Envelopes = load_envelopes(self.unit_dir)
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
        if ref in self.given:
            return CheckResult(ref, check.class_, True, False, "given by executor")
        return CheckResult(ref, check.class_, False, False, f"declared for {check.class_.value}; not evaluated")

    def gate_check(self, gate: str, policy: str) -> CheckResult:
        name = GATE_PREFIX + gate
        if policy == "auto":
            return CheckResult(name, CheckClass.HUMAN, True, False, "policy=auto")
        if gate in self.given:
            return CheckResult(name, CheckClass.HUMAN, True, False, "given by executor")
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

    registry = Registry.build(opts.anchor, doc.declared_checks)
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
            res.delegate = Delegate(stage.role, stage.isolation)
        if stage.gate and policy:
            res.gate = Gate(stage.gate, policy, stage.gate in ev.given)
        res.waiting = _waiting_for(stage, unmet)
        break

    res.lint_error = ev.lint_error
    return res


def is_completed(result: Result) -> bool:
    return result.status == COMPLETED_STATUS
