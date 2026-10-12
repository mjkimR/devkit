"""Gate registry: built-in gates plus gate files deployed by ``devkit sync``.

Bundles ship gates as ``kind = "gate"`` assets. ``devkit sync`` copies the
selected ones under ``.devkit/managed/<bundle>/`` (or uses the project override
under ``.devkit/overrides/``) and records each file in the asset's ``paths`` in
``.devkit/installation.json``. The registry loads every ``.py`` file listed
there, exactly as ``agent-rule-engine`` loads ``kind = "rule"`` assets. A gate
file may import from any package installed in the same environment, which is
how a content wheel ships its gate logic as a library and its gate as a thin file.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from agent_commit_gate.base import BaseGate
from agent_commit_gate.gates import NonEmptyMessageGate, StagedRulesGate
from agent_commit_gate.models import Gate, GateConfigError, Stage

RECEIPT_PATH = ".devkit/installation.json"
GATE_KIND = "gate"
BUILTIN = "builtin"


def deployed_gate_paths(repo_root: Path) -> tuple[list[Path], list[str]]:
    """Gate files recorded in the receipt: those present, and those the receipt lists but the disk lacks."""
    receipt = repo_root / RECEIPT_PATH
    if not receipt.is_file():
        return [], []
    try:
        data = json.loads(receipt.read_text("utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise GateConfigError(f"unreadable receipt {RECEIPT_PATH}: {exc}", fix="devkit sync") from exc
    assets = data.get("assets") if isinstance(data, dict) else None
    found: list[Path] = []
    missing: list[str] = []
    for asset in assets if isinstance(assets, list) else []:
        if not isinstance(asset, dict) or asset.get("kind") != GATE_KIND:
            continue
        paths = asset.get("paths")
        for item in paths if isinstance(paths, list) else []:
            if isinstance(item, str) and item.endswith(".py"):
                path = repo_root / item
                if path.is_file():
                    found.append(path)
                else:
                    missing.append(item)
    return found, missing


class GateRegistry:
    def __init__(self) -> None:
        self._gates: dict[str, Gate] = {}
        self.sources: dict[str, str] = {}
        self.errors: list[GateConfigError] = []

    def register(self, gate: Gate, source: str = BUILTIN) -> None:
        if gate.id in self._gates:
            self.errors.append(
                GateConfigError(f"duplicate gate id {gate.id!r} from {source} (already from {self.sources[gate.id]})")
            )
            return
        self._gates[gate.id] = gate
        self.sources[gate.id] = source

    def get(self, gate_id: str) -> Gate | None:
        return self._gates.get(gate_id)

    def get_all(self) -> list[Gate]:
        stages = list(Stage)
        return sorted(self._gates.values(), key=lambda g: (stages.index(g.stage), g.order, g.id))

    def for_stage(self, stage: Stage) -> list[Gate]:
        return [gate for gate in self.get_all() if gate.stage is stage]

    def load_files(self, files: Iterable[Path], root: Path | None = None) -> list[Gate]:
        """Register every concrete ``BaseGate`` subclass defined in the given files."""
        loaded: list[Gate] = []
        for path in files:
            if path.name.startswith(("_", ".")) or path.suffix != ".py":
                continue
            source = path.relative_to(root).as_posix() if root and path.is_relative_to(root) else str(path)
            module_name = f"devkit_gate_{hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            try:
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_name and issubclass(obj, BaseGate) and not inspect.isabstract(obj):
                        gate_cls: type[Any] = obj
                        gate = gate_cls()
                        self.register(gate, source)
                        loaded.append(gate)
            except Exception as exc:
                sys.modules.pop(module_name, None)
                self.errors.append(GateConfigError(f"failed to load gate file {source}: {exc}", target_files=[source]))
        return loaded


def default_registry() -> GateRegistry:
    registry = GateRegistry()
    registry.register(StagedRulesGate())
    registry.register(NonEmptyMessageGate())
    return registry


def project_registry(repo_root: Path) -> GateRegistry:
    """Built-in gates plus every gate the receipt records as deployed."""
    registry = default_registry()
    try:
        found, missing = deployed_gate_paths(repo_root)
    except GateConfigError as exc:
        registry.errors.append(exc)
        return registry
    for item in missing:
        registry.errors.append(
            GateConfigError(f"deployed gate file is missing: {item}", fix="devkit sync", target_files=[item])
        )
    registry.load_files(found, repo_root)
    return registry
