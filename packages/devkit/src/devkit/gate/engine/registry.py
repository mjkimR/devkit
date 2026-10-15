"""Gate registry: built-in gates plus gate packages deployed by ``devkit sync``.

Bundles ship gates as ``kind = "gate"`` assets, each a plugin package
directory. ``devkit sync`` copies the selected ones under
``.devkit/managed/<bundle>/`` (or uses the project override under
``.devkit/overrides/``) and records each file in the asset's ``paths`` in
``.devkit/installation.json``. The registry loads each asset as one package,
as ``devkit.rules`` loads ``kind = "rule"`` assets:

- the receipt is read with ``devkit.core.receipt`` (strict: a receipt that
  exists but is malformed, or lists an unsafe path, is an error);
- every listed module file is found and checked with
  ``devkit.core.verified_asset_packages``, as ``devkit.rules`` and
  ``devkit.workflow`` find rule and plugin check packages: a file that is
  missing, resolves outside the project, or differs from the SHA-256 the
  receipt records for it is reported as that ``AssetFileError``
  (``ASSET_FILE_INVALID``), never a silent skip, and its package is not loaded;
- packages are imported with ``devkit.core.plugins.load_subclasses``,
  atomically per package.

A gate package may import from any package installed in the same environment,
which is how a content wheel ships its gate logic as a library and its gate as
a thin package.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit.core import PluginPackage, ReceiptError, load_receipt, load_subclasses, verified_asset_packages
from devkit.gate.engine.base import BaseGate
from devkit.gate.engine.models import Gate, Stage
from devkit.gate.errors import GateDefinitionError, GateLoadError
from devkit.gate.gates import NonEmptyMessageGate, RulesCheckGate, VerifyCommandsGate

GATE_KIND = "gate"
BUILTIN = "builtin"
PLUGIN_NAMESPACE = "devkit_gate"


@dataclass(frozen=True)
class DeployedGates:
    """Gate packages to load, in receipt order, and the receipt entries that cannot be loaded."""

    packages: tuple[PluginPackage, ...] = ()
    errors: tuple[AdvisoryError, ...] = ()  # ``RECEIPT_INVALID`` or ``ASSET_FILE_INVALID``


def deployed_gate_packages(repo_root: Path) -> DeployedGates:
    """The plugin package of every ``kind = "gate"`` asset in the receipt, its files checked against their hashes.

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
    packages, errors = verified_asset_packages(repo_root, receipt, GATE_KIND)
    return DeployedGates(packages, errors)


def display_path(path: Path, root: Path | None) -> str:
    """``path`` relative to ``root`` (POSIX separators) when it lies inside it, else as it is."""
    return path.relative_to(root).as_posix() if root is not None and path.is_relative_to(root) else str(path)


def _validate(gate: BaseGate) -> None:
    name = type(gate).__name__
    if not isinstance(gate.id, str) or not gate.id:
        raise GateDefinitionError(f"{name}: id must be a nonempty string")
    if not isinstance(gate.stage, Stage):
        raise GateDefinitionError(f"{name}: stage must be a devkit.gate.Stage, not {gate.stage!r}")
    if not isinstance(gate.order, int) or isinstance(gate.order, bool):
        raise GateDefinitionError(f"{name}: order must be an int")


class GateRegistry:
    def __init__(self) -> None:
        self._gates: dict[str, Gate] = {}
        self.sources: dict[str, str] = {}
        self.errors: list[AdvisoryError] = []

    def register(self, gate: Gate, source: str = BUILTIN) -> None:
        if gate.id in self._gates:
            self.errors.append(
                GateLoadError(f"duplicate gate id {gate.id!r} from {source} (already from {self.sources[gate.id]})")
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

    def load_packages(self, packages: Iterable[PluginPackage], root: Path | None = None) -> list[Gate]:
        """Register every concrete ``BaseGate`` subclass defined in the given plugin packages.

        A package that fails to import, or any of whose gates fails to
        instantiate or validate, contributes no gate at all and is reported in
        ``errors`` as a ``GateLoadError`` (``GATE_LOAD_FAILED``) naming the
        package. A gate's source is the module file defining it.
        """
        load = load_subclasses(packages, BaseGate, namespace=PLUGIN_NAMESPACE, validate=_validate)
        for failure in load.errors:
            name = display_path(failure.path, root)
            self.errors.append(
                GateLoadError(f"failed to load gate package {name}: {failure.message}", target_files=[name])
            )
        loaded: list[Gate] = []
        for plugin in load.plugins:
            self.register(plugin.instance, display_path(plugin.path, root))
            loaded.append(plugin.instance)
        return loaded


def default_gate_registry() -> GateRegistry:
    """A registry holding the built-in gates."""
    registry = GateRegistry()
    registry.register(NonEmptyMessageGate())
    registry.register(RulesCheckGate())
    registry.register(VerifyCommandsGate())
    return registry


def project_registry(repo_root: Path) -> GateRegistry:
    """Built-in gates plus every gate the receipt records as deployed."""
    registry = default_gate_registry()
    deployed = deployed_gate_packages(repo_root)
    registry.errors.extend(deployed.errors)
    registry.load_packages(deployed.packages, repo_root)
    return registry
