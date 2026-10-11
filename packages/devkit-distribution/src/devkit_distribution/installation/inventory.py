from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.manifest import source_files

from .discovery import InstalledBundle

AGENTS = {"codex": (".agents/skills", ".codex/agents"), "claude-code": (".claude/skills", ".claude/agents")}


@dataclass(frozen=True)
class Content:
    data: bytes
    mode: int


def desired_inventory(
    installed: list[InstalledBundle], presets: dict[str, str], agents: list[str]
) -> tuple[dict[str, Content], list[dict[str, object]], list[dict[str, str]]]:
    files: dict[str, Content] = {}
    assets: list[dict[str, object]] = []
    packages = []
    unknown = set(presets) - {item.bundle.name for item in installed}
    if unknown:
        raise BundleError(f"preset bundle is not installed: {sorted(unknown)}")
    if set(agents) - AGENTS.keys():
        raise BundleError("unsupported agent selection")

    def add(destination: str, path: Path) -> None:
        if destination in files:
            raise BundleError(f"destination collision: {destination}")
        files[destination] = Content(path.read_bytes(), 0o755 if path.stat().st_mode & 0o111 else 0o644)

    for item in installed:
        bundle = item.bundle
        packages.append(
            {
                "package": item.package,
                "package_version": item.package_version,
                "bundle": bundle.name,
                "bundle_version": bundle.version,
            }
        )
        preset = presets.get(bundle.name)
        if preset is not None and preset not in bundle.presets:
            raise BundleError(f"{bundle.name}: unknown preset {preset}")
        selected = set(bundle.presets[preset]) if preset else {asset.id for asset in bundle.assets}
        prefix = f".devkit/managed/{bundle.name}/"
        add(prefix + "bundle.toml", bundle.root / "bundle.toml")
        managed: set[str] = {prefix + "bundle.toml"}
        for asset in bundle.assets:
            if asset.id not in selected:
                continue
            paths: set[str] = set()
            for _, source in asset.sources:
                for path in source_files(bundle.root, source):
                    dest = prefix + path.relative_to(bundle.root).as_posix()
                    if dest not in managed:
                        add(dest, path)
                        managed.add(dest)
                    paths.add(dest)
            for agent in agents:
                if asset.kind not in {"skill", "subagent"}:
                    continue
                sources = dict(asset.sources)
                source = sources.get(agent, sources.get("common") if asset.kind == "skill" else None)
                if source is None:
                    raise BundleError(f"{bundle.name}/{asset.id}: missing native variant for {agent}")
                origin = bundle.root / source
                skill_dir, subagent_dir = AGENTS[agent]
                for path in source_files(bundle.root, source):
                    if asset.kind == "skill":
                        dest = f"{skill_dir}/{asset.id}/{path.relative_to(origin).as_posix()}"
                    else:
                        suffix = ".toml" if agent == "codex" else ".md"
                        if not origin.is_file() or origin.suffix != suffix:
                            raise BundleError(f"{asset.id}: {agent} subagent must be one {suffix} file")
                        dest = f"{subagent_dir}/{asset.id}{suffix}"
                    add(dest, path)
                    paths.add(dest)
            assets.append({"bundle": bundle.name, "id": asset.id, "kind": asset.kind, "paths": sorted(paths)})
    return files, assets, packages
