"""Workflow definition documents: parsing, validation and the schema hash."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent_workflow_engine import frontmatter
from agent_workflow_engine.checks import DECLARABLE, Check, CheckClass, CheckError, Registry

SCHEMA_VERSION = 1
WORKFLOW_ID = re.compile(r"^[a-z][a-z0-9-]*$")
ISOLATIONS = ("none", "preferred", "required")
STAGE_KEYS = {
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


class DefinitionError(ValueError):
    """Structural failure that prevents a document from being represented."""


@dataclass(frozen=True)
class Return:
    to: str
    when: str

    def to_dict(self) -> dict[str, str]:
        return {"to": self.to, "when": self.when}


@dataclass(frozen=True)
class Stage:
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
    stages: tuple[Stage, ...] = ()
    path: Path | None = None
    # Unknown keys per stage, aligned with ``stages`` by index.
    unknown_keys: tuple[tuple[str, ...], ...] = field(default=(), compare=False)

    def stage(self, stage_id: str) -> Stage | None:
        return next((s for s in self.stages if s.id == stage_id), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "schema_version": self.schema_version,
            "path": self.path.as_posix() if self.path else None,
            "checks": [c.to_dict() for c in self.declared_checks],
            "stages": [s.to_dict() for s in self.stages],
            "hash": schema_hash(self),
        }


@dataclass(frozen=True)
class Problem:
    stage: str
    field: str
    message: str

    def __str__(self) -> str:
        where = f"{self.stage}.{self.field}" if self.stage else self.field
        return f"{where}: {self.message}"


def schema_hash(doc: WorkflowDocument) -> str:
    """``sha256:<hex>`` of the canonical JSON of the stages; nothing else affects it."""
    payload = json.dumps([s.to_dict() for s in doc.stages], sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _str_list(value: Any, what: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise DefinitionError(f"{what}: expected a list of strings")
    return tuple(value)


def _stage(raw: Any, index: int) -> Stage:
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
    returns_raw = raw.get("returns") or []
    if not isinstance(returns_raw, list):
        raise DefinitionError(f"{stage_id}.returns: expected a list")
    returns: list[Return] = []
    for r in returns_raw:
        if not isinstance(r, dict):
            raise DefinitionError(f"{stage_id}.returns: expected mappings with to/when")
        returns.append(Return(to=str(r.get("to") or ""), when=str(r.get("when") or "")))
    return Stage(
        id=stage_id,
        name=str(raw.get("name") or ""),
        gate=gate,
        optional=bool(raw.get("optional", False)),
        exception=bool(raw.get("exception", False)),
        entry=_str_list(raw.get("entry"), f"{stage_id}.entry"),
        exit=_str_list(raw.get("exit"), f"{stage_id}.exit"),
        artifacts=_str_list(raw.get("artifacts"), f"{stage_id}.artifacts"),
        skills=_str_list(raw.get("skills"), f"{stage_id}.skills"),
        role=str(raw.get("role") or "developer"),
        isolation=str(raw.get("isolation") or "none"),
        returns=tuple(returns),
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
        try:
            class_ = CheckClass(str(item.get("class") or ""))
        except ValueError as exc:
            raise DefinitionError(f"checks[{i}].class: expected runner or human") from exc
        if class_ not in DECLARABLE:
            raise DefinitionError(f"checks[{i}].class: expected runner or human")
        out.append(Check(item["name"], class_, str(item.get("description") or "")))
    return tuple(out)


def parse(text: str, path: Path | None = None) -> WorkflowDocument:
    front, _ = frontmatter.split(text)
    if front is None:
        raise DefinitionError("no frontmatter block found")
    try:
        data = frontmatter.parse(text)
    except frontmatter.FrontmatterError as exc:
        raise DefinitionError(str(exc)) from exc
    if not data:
        raise DefinitionError("frontmatter is not a mapping")
    doc_id = data.get("id")
    if not isinstance(doc_id, str) or not doc_id:
        raise DefinitionError("id: expected a nonempty string")
    stages_raw = data.get("stages")
    if not isinstance(stages_raw, list) or not stages_raw:
        raise DefinitionError("stages: expected a nonempty list")
    stages = tuple(_stage(raw, i) for i, raw in enumerate(stages_raw))
    unknown_keys = tuple(tuple(sorted(set(raw) - STAGE_KEYS)) for raw in stages_raw)
    version = data.get("schema_version")
    return WorkflowDocument(
        id=doc_id,
        title=str(data.get("title") or ""),
        status=str(data.get("status") or ""),
        schema_version=version if isinstance(version, int) else 0,
        declared_checks=_declared(data.get("checks")),
        stages=stages,
        path=path,
        unknown_keys=unknown_keys,
    )


def load(path: Path) -> WorkflowDocument:
    try:
        text = path.read_text("utf-8")
    except OSError as exc:
        raise DefinitionError(f"{path}: {exc}") from exc
    try:
        return parse(text, path)
    except DefinitionError as exc:
        raise DefinitionError(f"{path}: {exc}") from exc


def validate(doc: WorkflowDocument, anchor: str) -> list[Problem]:
    """Every problem in the document; an empty list means it is usable."""
    problems: list[Problem] = []
    if not WORKFLOW_ID.match(doc.id):
        problems.append(Problem("", "id", f"{doc.id!r} must match [a-z][a-z0-9-]*"))
    if doc.schema_version != SCHEMA_VERSION:
        problems.append(Problem("", "schema_version", f"unsupported schema_version {doc.schema_version} (expected 1)"))
    try:
        registry = Registry.build(anchor, doc.declared_checks)
    except CheckError as exc:
        problems.append(Problem("", "checks", str(exc)))
        registry = Registry.build(anchor)

    ids = [s.id for s in doc.stages]
    seen: set[str] = set()
    for index, s in enumerate(doc.stages):
        if s.id in seen:
            problems.append(Problem(s.id, "id", "duplicate stage id"))
        seen.add(s.id)
        unknown = doc.unknown_keys[index] if index < len(doc.unknown_keys) else ()
        for key in unknown:
            problems.append(Problem(s.id, key, "unknown stage key"))
        if s.isolation not in ISOLATIONS:
            problems.append(Problem(s.id, "isolation", f"{s.isolation!r} not in {'|'.join(ISOLATIONS)}"))
        for fld in ("entry", "exit"):
            for ref in getattr(s, fld):
                try:
                    registry.resolve_name(ref)
                except CheckError as exc:
                    problems.append(Problem(s.id, fld, str(exc)))
        for i, r in enumerate(s.returns):
            if not r.to:
                problems.append(Problem(s.id, f"returns[{i}].to", "missing target stage"))
            elif r.to not in ids:
                problems.append(Problem(s.id, f"returns[{i}].to", f"unknown stage {r.to!r}"))
            if not r.when:
                problems.append(Problem(s.id, f"returns[{i}].when", "missing reason"))
    return problems


RECEIPT_PATH = ".devkit/installation.json"


def _load_paths(paths: Iterable[Path]) -> tuple[list[WorkflowDocument], list[str]]:
    docs: list[WorkflowDocument] = []
    errors: list[str] = []
    for path in paths:
        try:
            docs.append(load(path))
        except DefinitionError as exc:
            errors.append(str(exc))
    return docs, errors


def load_all(definitions_dir: Path) -> tuple[list[WorkflowDocument], list[str]]:
    """Load every ``*.md`` definition in a directory; unreadable files are returned as error strings."""
    if not definitions_dir.is_dir():
        return [], []
    return _load_paths(sorted(definitions_dir.glob("*.md")))


def managed_definition_paths(workspace_root: Path) -> list[Path]:
    """Workflow assets recorded in the devkit installation receipt, if any."""
    receipt = workspace_root / RECEIPT_PATH
    if not receipt.is_file():
        return []
    try:
        data = json.loads(receipt.read_text("utf-8"))
    except (OSError, UnicodeError, ValueError):
        return []
    assets = data.get("assets") if isinstance(data, dict) else None
    paths: list[Path] = []
    for asset in assets or []:
        if not isinstance(asset, dict) or asset.get("kind") != "workflow":
            continue
        for rel in asset.get("entrypoints") or asset.get("paths") or []:
            if isinstance(rel, str) and rel.endswith(".md"):
                paths.append(workspace_root / rel)
    return sorted(set(paths))


def discover(workspace_root: Path, definitions_dir: Path) -> tuple[list[WorkflowDocument], list[str]]:
    """Project definitions plus workflow assets synchronized by devkit.

    A project definition shadows a synchronized one with the same id, so a
    repository can adapt a distributed workflow without editing managed files.
    """
    local, errors = load_all(definitions_dir)
    managed, managed_errors = _load_paths(p for p in managed_definition_paths(workspace_root) if p.is_file())
    local_ids = {d.id for d in local}
    docs = local + [d for d in managed if d.id not in local_ids]
    return docs, errors + managed_errors


def find(definitions_dir: Path, workflow_id: str, workspace_root: Path | None = None) -> WorkflowDocument:
    """The single definition whose id matches; zero or several matches are errors."""
    docs, errors = discover(workspace_root, definitions_dir) if workspace_root else load_all(definitions_dir)
    matches = [d for d in docs if d.id == workflow_id]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        hint = f" ({'; '.join(errors)})" if errors else ""
        where = definitions_dir.as_posix() + (" or the devkit installation receipt" if workspace_root else "")
        raise DefinitionError(f"no workflow with id {workflow_id!r} under {where}{hint}")
    paths = ", ".join(d.path.as_posix() for d in matches if d.path)
    raise DefinitionError(f"workflow id {workflow_id!r} is defined more than once: {paths}")


def resolve(definitions_dir: Path, ref: str, workspace_root: Path | None = None) -> WorkflowDocument:
    """``ref`` is a workflow id, or a path to a definition file."""
    candidate = Path(ref)
    if candidate.suffix == ".md" and candidate.is_file():
        return load(candidate)
    return find(definitions_dir, ref, workspace_root)
