"""Workflow definition documents: the model, parsing and the schema hash.

Validation lives in ``validation`` and discovery (definitions directory plus
synchronized workflow assets) in ``discovery``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.core import frontmatter as core_frontmatter
from devkit.core.errors import FrontmatterError
from devkit.workflow.definition.checks import DECLARABLE, Check, CheckClass
from devkit.workflow.definition.ids import IDENT_HINT, is_ident
from devkit.workflow.errors import DefinitionError, LayoutError
from devkit.workflow.project.layout import LayoutSpec, parse_layout_spec

SCHEMA_VERSION = 1
ISOLATIONS = ("none", "preferred", "required")
HANDOFF_GATE = "handoff"
DOCUMENT_KEYS = frozenset({"id", "title", "status", "schema_version", "checks", "stages", "next", "layout", "gates"})
# How a person's gate answer reaches the engine: a decision record, or `next --given <gate>` with nothing written.
GATE_ANSWERS = ("record", "given")
# The gate policies of `[workflow.approvals]`; a definition may narrow a gate to some of them (`gates.<gate>.policies`).
GATE_POLICIES = ("ask", "auto", "off")
STAGE_KEYS = frozenset(
    {
        "id",
        "name",
        "human_gate",
        "optional",
        "exception",
        "entry",
        "exit",
        "artifacts",
        "skills",
        "role",
        "isolation",
        "returns",
    }
)
# Display-only stage fields; changing them never causes drift.
DISPLAY_FIELDS = frozenset({"name"})


@dataclass(frozen=True)
class Return:
    to: str
    when: str

    def to_dict(self) -> dict[str, str]:
        return {"to": self.to, "when": self.when}


@dataclass(frozen=True)
class Candidate:
    """A workflow this one may hand the unit to once it is complete."""

    workflow: str
    when: tuple[str, ...] = ()  # check references that must hold for the candidate to be eligible
    recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"workflow": self.workflow, "when": list(self.when), "recommended": self.recommended}


@dataclass(frozen=True)
class StageDefinition:
    id: str
    name: str = ""
    gate: str | None = None  # normalized human_gate: None, or the gate name
    optional: bool = False
    exception: bool = False
    entry: tuple[str, ...] = ()
    exit: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    role: str = "developer"
    isolation: str = "none"
    returns: tuple[Return, ...] = ()
    unknown_keys: tuple[str, ...] = field(default=(), compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "human_gate": self.gate,
            "optional": self.optional,
            "exception": self.exception,
            "entry": list(self.entry),
            "exit": list(self.exit),
            "artifacts": list(self.artifacts),
            "skills": list(self.skills),
            "role": self.role,
            "isolation": self.isolation,
            "returns": [r.to_dict() for r in self.returns],
        }


@dataclass(frozen=True)
class WorkflowDocument:
    id: str
    title: str = ""
    status: str = ""
    schema_version: int = SCHEMA_VERSION
    declared_checks: tuple[Check, ...] = ()
    stages: tuple[StageDefinition, ...] = ()
    next: tuple[Candidate, ...] = ()
    layout: LayoutSpec | None = None  # keys the definition overrides in the project layout
    gate_answers: tuple[tuple[str, str], ...] = ()  # (gate, answer) for gates whose answer is not the default
    gate_policies: tuple[tuple[str, tuple[str, ...]], ...] = ()  # (gate, allowed policies) for narrowed gates
    path: Path | None = None
    unknown_keys: tuple[str, ...] = field(default=(), compare=False)  # unknown top-level keys

    def stage(self, stage_id: str) -> StageDefinition | None:
        return next((s for s in self.stages if s.id == stage_id), None)

    def stage_index(self, stage_id: str) -> int:
        """Position of the stage in ``stages``; ``-1`` when absent."""
        return next((i for i, s in enumerate(self.stages) if s.id == stage_id), -1)

    @property
    def gates(self) -> set[str]:
        return {s.gate for s in self.stages if s.gate}

    def gate_answer(self, gate: str) -> str:
        """``record`` (the default) or ``given``: how the executor passes a person's answer to ``gate``."""
        return dict(self.gate_answers).get(gate, "record")

    def gate_policies_for(self, gate: str) -> tuple[str, ...]:
        """The ``[workflow.approvals]`` policies ``gate`` accepts: those the definition narrows it to, else all."""
        return dict(self.gate_policies).get(gate, GATE_POLICIES)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "schema_version": self.schema_version,
            "path": self.path.as_posix() if self.path else None,
            "checks": [c.to_dict() for c in self.declared_checks],
            "stages": [s.to_dict() for s in self.stages],
            "next": [c.to_dict() for c in self.next],
            "layout": self.layout.to_dict() if self.layout else None,
            "gates": self._gates_dict(),
            "hash": schema_hash(self),
        }

    def _gates_dict(self) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {gate: {"answer": answer} for gate, answer in self.gate_answers}
        for gate, policies in self.gate_policies:
            out.setdefault(gate, {})["policies"] = list(policies)
        return dict(sorted(out.items()))

    def anchor(self, default: str) -> str:
        """The anchor file name for this workflow's units: declared, or the project default."""
        return self.layout.anchor if self.layout and self.layout.anchor else default


def schema_hash(doc: WorkflowDocument) -> str:
    """``sha256:<hex>`` of the canonical JSON of the stages without display-only fields.

    Nothing outside ``stages`` affects it, and neither does a stage's ``name``.
    """
    stages = [{k: v for k, v in s.to_dict().items() if k not in DISPLAY_FIELDS} for s in doc.stages]
    payload = json.dumps(stages, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _str_list(value: Any, what: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise DefinitionError(f"{what}: expected a list of strings")
    return tuple(value)


def _bool(raw: dict[str, Any], key: str, what: str) -> bool:
    value = raw.get(key, False)
    if value is None:
        return False
    if not isinstance(value, bool):
        raise DefinitionError(f"{what}.{key}: expected true or false")
    return value


def _str(raw: dict[str, Any], key: str, what: str, default: str = "") -> str:
    value = raw.get(key)
    if value is None or value == "":
        return default
    if not isinstance(value, str):
        raise DefinitionError(f"{what}.{key}: expected a string")
    return value


def _returns(raw: Any, stage_id: str) -> tuple[Return, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise DefinitionError(f"{stage_id}.returns: expected a list")
    out: list[Return] = []
    for i, item in enumerate(raw):
        where = f"{stage_id}.returns[{i}]"
        if not isinstance(item, dict):
            raise DefinitionError(f"{where}: expected a mapping with to/when")
        if unknown := set(item) - {"to", "when"}:
            raise DefinitionError(f"{where}: unknown keys {sorted(unknown)}")
        out.append(Return(to=_str(item, "to", where), when=_str(item, "when", where)))
    return tuple(out)


def _stage(raw: Any, index: int) -> StageDefinition:
    if not isinstance(raw, dict):
        raise DefinitionError(f"stages[{index}]: expected a mapping")
    stage_id = raw.get("id")
    if not isinstance(stage_id, str) or not stage_id:
        raise DefinitionError(f"stages[{index}].id: expected a nonempty string")
    gate_raw = raw.get("human_gate", False)
    if gate_raw is True:
        gate: str | None = stage_id
    elif gate_raw is False or gate_raw is None:
        gate = None
    elif isinstance(gate_raw, str) and gate_raw:
        gate = gate_raw
    else:
        raise DefinitionError(f"stages[{index}].human_gate: expected false, true or a gate name")
    return StageDefinition(
        id=stage_id,
        name=_str(raw, "name", stage_id),
        gate=gate,
        optional=_bool(raw, "optional", stage_id),
        exception=_bool(raw, "exception", stage_id),
        entry=_str_list(raw.get("entry"), f"{stage_id}.entry"),
        exit=_str_list(raw.get("exit"), f"{stage_id}.exit"),
        artifacts=_str_list(raw.get("artifacts"), f"{stage_id}.artifacts"),
        skills=_str_list(raw.get("skills"), f"{stage_id}.skills"),
        role=_str(raw, "role", stage_id, "developer"),
        isolation=_str(raw, "isolation", stage_id, "none"),
        returns=_returns(raw.get("returns"), stage_id),
        unknown_keys=tuple(sorted(str(k) for k in set(raw) - STAGE_KEYS)),
    )


def _declared(raw: Any) -> tuple[Check, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise DefinitionError("checks: expected a list")
    out: list[Check] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]:
            raise DefinitionError(f"checks[{i}]: expected a mapping with name, class, description")
        if unknown := set(item) - {"name", "class", "description"}:
            raise DefinitionError(f"checks[{i}]: unknown keys {sorted(unknown)}")
        if not is_ident(item["name"]):
            raise DefinitionError(f"checks[{i}].name: {item['name']!r} must match {IDENT_HINT}")
        try:
            class_ = CheckClass(str(item.get("class") or ""))
        except ValueError as exc:  # not a CheckClass member
            raise DefinitionError(f"checks[{i}].class: expected runner or human") from exc
        if class_ not in DECLARABLE:
            raise DefinitionError(f"checks[{i}].class: expected runner or human")
        out.append(Check(item["name"], class_, _str(item, "description", f"checks[{i}]")))
    return tuple(out)


def _candidates(raw: Any) -> tuple[Candidate, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise DefinitionError("next: expected a list of candidate mappings")
    out: list[Candidate] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise DefinitionError(f"next[{i}]: expected a mapping with workflow, when, recommended")
        if unknown := set(item) - {"workflow", "when", "recommended"}:
            raise DefinitionError(f"next[{i}]: unknown keys {sorted(unknown)}")
        workflow = item.get("workflow")
        if not isinstance(workflow, str) or not workflow:
            raise DefinitionError(f"next[{i}].workflow: expected a nonempty string")
        recommended = item.get("recommended", False)
        if not isinstance(recommended, bool):
            raise DefinitionError(f"next[{i}].recommended: expected true or false")
        out.append(Candidate(workflow, _str_list(item.get("when"), f"next[{i}].when"), recommended))
    return tuple(out)


def _gate_settings(
    raw: Any, gates: set[str]
) -> tuple[tuple[tuple[str, str], ...], tuple[tuple[str, tuple[str, ...]], ...]]:
    """``gates``: per gate, how its answer reaches the engine (``answer``) and the policies it accepts (``policies``)."""
    if raw is None:
        return (), ()
    if not isinstance(raw, dict):
        raise DefinitionError("gates: expected a mapping of gate name to settings")
    answers: list[tuple[str, str]] = []
    narrowed: list[tuple[str, tuple[str, ...]]] = []
    for gate, settings in raw.items():
        if gate not in gates:
            raise DefinitionError(f"gates.{gate}: not the human_gate of any stage")
        if not isinstance(settings, dict):
            raise DefinitionError(f"gates.{gate}: expected a mapping with answer and/or policies")
        if unknown := set(settings) - {"answer", "policies"}:
            raise DefinitionError(f"gates.{gate}: unknown keys {sorted(unknown)}")
        answer = settings.get("answer", "record")
        if answer not in GATE_ANSWERS:
            raise DefinitionError(f"gates.{gate}.answer: expected one of {list(GATE_ANSWERS)}")
        if answer != "record":
            answers.append((gate, answer))
        if "policies" in settings:
            policies = settings["policies"]
            if (
                not isinstance(policies, list)
                or not policies
                or any(p not in GATE_POLICIES for p in policies)
                or len(set(policies)) != len(policies)
            ):
                raise DefinitionError(
                    f"gates.{gate}.policies: expected a non-empty list of distinct values of {list(GATE_POLICIES)}"
                )
            if "ask" not in policies:
                raise DefinitionError(f"gates.{gate}.policies: must include ask, the policy of an unset gate")
            narrowed.append((gate, tuple(p for p in GATE_POLICIES if p in policies)))
    return tuple(sorted(answers)), tuple(sorted(narrowed))


def parse_definition(text: str, path: Path | None = None) -> WorkflowDocument:
    """Parse a definition document; raises ``DefinitionError`` for anything that cannot be represented."""
    try:
        data = core_frontmatter.parse(text).data
    except FrontmatterError as exc:
        raise DefinitionError(str(exc)) from exc
    if data is None:
        raise DefinitionError("no frontmatter block found")
    doc_id = data.get("id")
    if not isinstance(doc_id, str) or not doc_id:
        raise DefinitionError("id: expected a nonempty string")
    stages_raw = data.get("stages")
    if not isinstance(stages_raw, list) or not stages_raw:
        raise DefinitionError("stages: expected a nonempty list")
    stages = tuple(_stage(raw, i) for i, raw in enumerate(stages_raw))
    version = data.get("schema_version")
    layout: LayoutSpec | None = None
    if data.get("layout") is not None:
        try:
            layout = parse_layout_spec(data["layout"])
        except LayoutError as exc:
            raise DefinitionError(str(exc)) from exc
    gate_answers, gate_policies = _gate_settings(data.get("gates"), {s.gate for s in stages if s.gate})
    return WorkflowDocument(
        id=doc_id,
        title=_str(data, "title", "document"),
        status=_str(data, "status", "document"),
        schema_version=version if isinstance(version, int) and not isinstance(version, bool) else 0,
        declared_checks=_declared(data.get("checks")),
        stages=stages,
        next=_candidates(data.get("next")),
        layout=layout,
        gate_answers=gate_answers,
        gate_policies=gate_policies,
        path=path,
        unknown_keys=tuple(sorted(set(data) - DOCUMENT_KEYS)),
    )


def load_definition(path: Path) -> WorkflowDocument:
    """Read and parse the definition file at ``path``; raises ``DefinitionError`` targeting it."""
    try:
        text = path.read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        raise DefinitionError(f"{path}: {exc}", target_files=[path.as_posix()]) from exc
    try:
        return parse_definition(text, path)
    except DefinitionError as exc:
        raise DefinitionError(f"{path}: {exc}", target_files=[path.as_posix()]) from exc
