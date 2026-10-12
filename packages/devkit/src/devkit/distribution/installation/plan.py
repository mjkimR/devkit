"""``devkit bundle plan``: what a local bundle source would deploy, computed by the same inventory as ``sync``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from devkit.core.receipt import AssetRecord
from devkit.distribution.bundles.common import ALL
from devkit.distribution.bundles.manifest import Bundle
from devkit.distribution.content import sha256
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.inventory import AGENTS, desired_inventory
from devkit.distribution.installation.results import asset_json


@dataclass(frozen=True)
class PlannedFile:
    destination: str
    sha256: str
    mode: int

    def to_dict(self) -> dict[str, Any]:
        return {"destination": self.destination, "sha256": self.sha256, "mode": self.mode}


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "version": self.version,
            "preset": self.preset,
            "agents": list(self.agents),
            "assets": [asset_json(asset) for asset in self.assets],
            "files": [item.to_dict() for item in self.files],
            "seeded": [item.to_dict() for item in self.seeded],
        }


def plan_bundle(bundle: Bundle, preset: str | None = None, agents: list[str] | None = None) -> BundlePlan:
    """Every destination ``bundle`` deploys with ``preset`` (default preset, else ``all``) for ``agents``.

    The plan ignores project state: no overrides, no existing files, no root
    ``AGENTS.md`` block. ``agents`` defaults to every supported agent.
    """
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
    )
