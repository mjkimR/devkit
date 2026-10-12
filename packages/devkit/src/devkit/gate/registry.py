"""Gate registry: built-in gates plus gate files deployed by ``devkit sync``.

Bundles ship gates as ``kind = "gate"`` assets. ``devkit sync`` copies the
selected ones under ``.devkit/managed/<bundle>/`` (or uses the project override
under ``.devkit/overrides/``) and records each file in the asset's ``paths`` in
``.devkit/installation.json``. The registry loads every ``.py`` file listed
there, as ``devkit.rules`` loads ``kind = "rule"`` assets:

- the receipt is read with ``devkit.core.receipt`` (strict: a receipt that
  exists but is malformed, or lists an unsafe path, is an error);
- every listed file is checked with ``devkit.core.verified_asset_file``, the
  check ``devkit.rules`` and ``devkit.workflow`` apply to rule and plugin check files too: a file that is missing,
  resolves outside the project, or differs from the SHA-256 the receipt
  records for it is an error, never a silent skip;
- files are imported with ``devkit.core.plugins.load_subclasses``, atomically
  per file.

A gate file may import from any package installed in the same environment,
which is how a content wheel ships its gate logic as a library and its gate as
a thin file.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit.core import AssetFileError, ReceiptError, load_receipt, load_subclasses, verified_asset_file
from devkit.gate.base import BaseGate
from devkit.gate.gates import NonEmptyMessageGate, StagedRulesGate
from devkit.gate.models import Gate, GateConfigError, Stage

GATE_KIND = "gate"
BUILTIN = "builtin"
PLUGIN_NAMESPACE = "devkit_gate"
GATE_INVALID = "GATE_INVALID"  # a gate class declares an unusable id, stage or order


@dataclass(frozen=True)
class DeployedGates:
    """Gate files to load, in receipt order, and the receipt entries that cannot be loaded."""

    paths: tuple[Path, ...] = ()
    errors: tuple[AdvisoryError, ...] = ()  # ``RECEIPT_INVALID`` or ``GATE_CONFIG_INVALID``


def deployed_gate_paths(repo_root: Path) -> DeployedGates:
    """Every ``.py`` file of every ``kind = "gate"`` asset in the receipt, checked against its recorded hash.

    A file without a ``files`` entry in the receipt (a project override) is
    loaded as it is; a file with one must match it. A malformed receipt is
    reported as the ``ReceiptError`` itself (``RECEIPT_INVALID``).
    """
    try:
        receipt = load_receipt(repo_root)
    except ReceiptError as exc:
        return DeployedGates(errors=(exc,))
    if receipt is None:
        return DeployedGates()
    paths: list[Path] = []
    errors: list[GateConfigError] = []
    for asset in receipt.assets(kind=GATE_KIND):
        for item in asset.paths:
            if not item.endswith(".py"):
                continue
            try:
                paths.append(verified_asset_file(repo_root, item, receipt, asset))
            except AssetFileError as exc:
                errors.append(
                    GateConfigError(f"deployed gate file {exc.message}", fix=exc.fix, target_files=exc.target_files)
                )
    return DeployedGates(tuple(paths), tuple(errors))


def _validate(gate: BaseGate) -> None:
    name = type(gate).__name__
    if not isinstance(gate.id, str) or not gate.id:
        raise GateConfigError(f"{name}: id must be a nonempty string", code=GATE_INVALID, input_error=False)
    if not isinstance(gate.stage, Stage):
        raise GateConfigError(
            f"{name}: stage must be a devkit.gate.Stage, not {gate.stage!r}", code=GATE_INVALID, input_error=False
        )
    if not isinstance(gate.order, int) or isinstance(gate.order, bool):
        raise GateConfigError(f"{name}: order must be an int", code=GATE_INVALID, input_error=False)


class GateRegistry:
    def __init__(self) -> None:
        self._gates: dict[str, Gate] = {}
        self.sources: dict[str, str] = {}
        self.errors: list[AdvisoryError] = []

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
        """Register every concrete ``BaseGate`` subclass defined in the given files.

        A file that fails to import, or any of whose gates fails to instantiate
        or validate, contributes no gate at all and is reported in ``errors``.
        """

        def source(path: Path) -> str:
            return path.relative_to(root).as_posix() if root and path.is_relative_to(root) else str(path)

        load = load_subclasses(files, BaseGate, namespace=PLUGIN_NAMESPACE, validate=_validate)
        for failure in load.errors:
            name = source(failure.path)
            self.errors.append(
                GateConfigError(f"failed to load gate file {name}: {failure.message}", target_files=[name])
            )
        loaded: list[Gate] = []
        for plugin in load.plugins:
            self.register(plugin.instance, source(plugin.path))
            loaded.append(plugin.instance)
        return loaded


def default_registry() -> GateRegistry:
    registry = GateRegistry()
    registry.register(StagedRulesGate())
    registry.register(NonEmptyMessageGate())
    return registry


def project_registry(repo_root: Path) -> GateRegistry:
    """Built-in gates plus every gate the receipt records as deployed."""
    registry = default_registry()
    deployed = deployed_gate_paths(repo_root)
    registry.errors.extend(deployed.errors)
    registry.load_files(deployed.paths, repo_root)
    return registry
