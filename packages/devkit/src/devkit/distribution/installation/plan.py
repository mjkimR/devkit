"""``devkit bundle plan``: what a local bundle source would deploy, computed by the same inventory as ``sync``."""

from __future__ import annotations

from typing import TypedDict

from ..bundles.common import ALL
from ..bundles.manifest import Bundle
from .discovery import InstalledBundle
from .inventory import AGENTS, desired_inventory
from .results import AssetJSON, asset_json
from .workspace import sha256


class PlannedFile(TypedDict):
    destination: str
    sha256: str
    mode: int


class PlannedSeed(TypedDict):
    destination: str
    asset: str
    sha256: str


class BundlePlan(TypedDict):
    bundle: str
    version: str
    preset: str
    agents: list[str]
    assets: list[AssetJSON]
    files: list[PlannedFile]
    seeded: list[PlannedSeed]


def plan_bundle(bundle: Bundle, preset: str | None = None, agents: list[str] | None = None) -> BundlePlan:
    """Every destination ``bundle`` deploys with ``preset`` (default preset, else ``all``) for ``agents``.

    The plan ignores project state: no overrides, no existing files, no root
    ``AGENTS.md`` block. ``agents`` defaults to every supported agent.
    """
    preset = preset or bundle.default_preset or ALL
    targets = sorted(set(agents)) if agents is not None else sorted(AGENTS)
    item = InstalledBundle("(local source)", bundle.version, bundle)
    inventory = desired_inventory([item], {bundle.name: [preset]}, targets)
    return {
        "bundle": bundle.name,
        "version": bundle.version,
        "preset": preset,
        "agents": targets,
        "assets": [asset_json(asset) for asset in inventory.assets],
        "files": [
            {"destination": name, "sha256": sha256(content.data), "mode": content.mode}
            for name, content in sorted(inventory.files.items())
        ],
        "seeded": [
            {"destination": dest, "asset": seed.asset, "sha256": sha256(seed.content.data)}
            for dest, seed in sorted(inventory.seeds.items())
        ],
    }
