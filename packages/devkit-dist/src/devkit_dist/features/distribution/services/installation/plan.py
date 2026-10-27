"""``devkit bundle plan``: what a local bundle source would deploy, computed by the same inventory as ``sync``."""

from __future__ import annotations

import shlex
from dataclasses import asdict, dataclass
from typing import Any

from devkit_dist.features.distribution.models.content import sha256
from devkit_dist.features.distribution.models.results import asset_json
from devkit_dist.features.distribution.services.bundles.common import ALL
from devkit_dist.features.distribution.services.bundles.manifest import Bundle
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.inventory import AGENTS, desired_inventory
from devkit_dist.features.project.models.invocation import devkit_command
from devkit_dist.features.project.repositories.receipt import AssetRecord, HostHookRecord


@dataclass(frozen=True)
class PlannedFile:
    destination: str
    sha256: str
    mode: int

    def to_dict(self) -> dict[str, Any]:
        # The permission bits as ``ls`` and ``chmod`` write them (``"0644"``), not the decimal integer.
        return {"destination": self.destination, "sha256": self.sha256, "mode": f"{self.mode:04o}"}


@dataclass(frozen=True)
class PlannedSeed:
    destination: str
    asset: str
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {"destination": self.destination, "asset": self.asset, "sha256": self.sha256}


@dataclass(frozen=True)
class BundlePlan:
    """Every destination a bundle source deploys for one preset and a set of agents."""

    bundle: str
    version: str
    preset: str
    agents: list[str]
    assets: list[AssetRecord]
    files: list[PlannedFile]
    seeded: list[PlannedSeed]
    host_hooks: list[HostHookRecord]

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "version": self.version,
            "preset": self.preset,
            "agents": list(self.agents),
            "assets": [asset_json(asset) for asset in self.assets],
            "files": [item.to_dict() for item in self.files],
            "seeded": [item.to_dict() for item in self.seeded],
            "host_hooks": [asdict(item) for item in self.host_hooks],
        }


def plan_bundle(
    bundle: Bundle, preset: str | None = None, agents: list[str] | None = None, *, source: str | None = None
) -> BundlePlan:
    """Every destination ``bundle`` deploys with ``preset`` (default preset, else ``all``) for ``agents``.

    The plan ignores project state: no overrides, no existing files, no root
    ``AGENTS.md`` block. ``agents`` defaults to every supported agent. ``source`` is the source argument as the
    caller passed it (default: the bundle root), named in the commands an unknown ``preset`` suggests.
    """
    if preset is not None and bundle.unknown_presets([preset]):
        plan = devkit_command(f"bundle plan {shlex.quote(source if source is not None else str(bundle.root))}")
        raise bundle.preset_error(
            f"{bundle.name}: unknown preset {preset}; available: {', '.join(bundle.preset_names)}",
            command=lambda name: f"{plan} --preset {name}",
            fix=plan,
            target="--preset",
        )
    preset = preset or bundle.default_preset or ALL
    targets = sorted(set(agents)) if agents is not None else sorted(AGENTS)
    item = InstalledBundle("(local source)", bundle.version, bundle)
    inventory = desired_inventory([item], {bundle.name: [preset]}, targets)
    return BundlePlan(
        bundle=bundle.name,
        version=bundle.version,
        preset=preset,
        agents=targets,
        assets=list(inventory.assets),
        files=[
            PlannedFile(name, sha256(content.data), content.mode) for name, content in sorted(inventory.files.items())
        ],
        seeded=[
            PlannedSeed(dest, seed.asset, sha256(seed.content.data)) for dest, seed in sorted(inventory.seeds.items())
        ],
        host_hooks=inventory.host_hooks,
    )
