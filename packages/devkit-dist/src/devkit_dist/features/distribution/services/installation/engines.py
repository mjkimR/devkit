"""Deployed assets that need an engine distribution does not ship: rules, gates and workflows (``devkit-agt``).

``devkit-dist`` deploys every asset kind, but only ``devkit-agt`` runs rule, gate and workflow assets. An
installation in which no ``devkit.commands`` entry point is named after the engine of a deployed kind gets one
``HARNESS_ENGINE_MISSING`` warning from ``devkit sync`` and ``devkit status``. Engine presence is read from entry
point names only: nothing here loads, imports or locates an engine.
"""

from __future__ import annotations

from collections.abc import Iterable
from importlib import metadata

from devkit.advisory import AdvisoryError

from devkit_dist.features.distribution.models.errors import HarnessEngineMissingNotice
from devkit_dist.features.project.repositories.receipt import AssetRecord

# The entry-point group the root command line loads (``devkit_dist.cli``); only its names are read here.
COMMAND_ENTRY_POINTS = "devkit.commands"
# Asset kind -> the command that runs it, mounted by devkit-agt.
ENGINE_COMMANDS = {"rule": "rules", "gate": "gate", "workflow": "workflow"}


def installed_commands() -> frozenset[str]:
    """The names of the installed ``devkit.commands`` entry points."""
    return frozenset(entry.name for entry in metadata.entry_points(group=COMMAND_ENTRY_POINTS))


def engine_notices(assets: Iterable[AssetRecord]) -> list[AdvisoryError]:
    """``HARNESS_ENGINE_MISSING`` for the deployed ``assets`` whose kind no installed command runs, else nothing."""
    needed: dict[str, set[str]] = {}
    for asset in assets:
        if asset.kind in ENGINE_COMMANDS:
            needed.setdefault(asset.bundle, set()).add(asset.kind)
    if not needed:
        return []
    installed = installed_commands()
    missing = {
        bundle: sorted(kind for kind in kinds if ENGINE_COMMANDS[kind] not in installed)
        for bundle, kinds in sorted(needed.items())
    }
    missing = {bundle: kinds for bundle, kinds in missing.items() if kinds}
    if not missing:
        return []
    listed = [f"{bundle} ({', '.join(kinds)})" for bundle, kinds in missing.items()]
    return [
        HarnessEngineMissingNotice(
            f"deployed assets that no installed engine runs: {', '.join(listed)}",
            *(
                f"{bundle}: {', '.join(kinds)} assets need devkit {', '.join(ENGINE_COMMANDS[kind] for kind in kinds)}"
                for bundle, kinds in missing.items()
            ),
        )
    ]
