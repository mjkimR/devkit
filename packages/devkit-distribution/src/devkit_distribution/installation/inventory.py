from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.guidance import prepend_context
from devkit_distribution.bundles.manifest import source_files
from devkit_distribution.bundles.playbooks import playbook_entry
from devkit_distribution.bundles.subagents import projection_path, read_contract, render
from devkit_distribution.bundles.workflows import workflow_entry

from . import playbook_skill, workflow_skill
from .discovery import InstalledBundle

# Shared entry skills generated when at least one asset of the kind is synchronized.
GENERATED_SKILLS = {"playbook": playbook_skill, "workflow": workflow_skill}

OVERRIDES = ".devkit/overrides"
AGENTS = {"codex": (".agents/skills", ".codex/agents"), "claude-code": (".claude/skills", ".claude/agents")}


@dataclass(frozen=True)
class Content:
    data: bytes
    mode: int


def desired_inventory(
    installed: list[InstalledBundle],
    presets: dict[str, list[str]],
    agents: list[str],
    *,
    root: Path | None = None,
    previous_overrides: dict[str, dict[str, dict[str, str]]] | None = None,
) -> tuple[
    dict[str, Content],
    list[dict[str, object]],
    list[dict[str, str]],
    dict[str, dict[str, dict[str, str]]],
    list[dict[str, str]],
]:
    files: dict[str, Content] = {}
    assets: list[dict[str, object]] = []
    packages = []
    overrides_record: dict[str, dict[str, dict[str, str]]] = {}
    drift_list: list[dict[str, str]] = []
    # Every bundle passed in is deployed, so each needs an explicit preset selection.
    if set(presets) != {item.bundle.name for item in installed}:
        raise BundleError("inventory requires exactly one preset selection per bundle")
    if set(agents) - AGENTS.keys():
        raise BundleError("unsupported agent selection")

    def add(destination: str, path: Path, context_bundle: str | None = None) -> None:
        if destination in files:
            raise BundleError(f"destination collision: {destination}")
        data = path.read_bytes()
        if context_bundle is not None:
            data = prepend_context(data, context_bundle)
        files[destination] = Content(data, 0o755 if path.stat().st_mode & 0o111 else 0o644)

    def add_bytes(destination: str, data: bytes) -> None:
        if destination in files:
            raise BundleError(f"destination collision: {destination}")
        files[destination] = Content(data, 0o644)

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
        selected = bundle.select(presets[bundle.name])
        prefix = f".devkit/managed/{bundle.name}/"
        add(prefix + "bundle.toml", bundle.root / "bundle.toml")
        managed: set[str] = {prefix + "bundle.toml"}
        constitution = bundle.constitution
        if constitution is not None:
            add(prefix + "AGENTS.md", constitution)
            managed.add(prefix + "AGENTS.md")
        has_context = constitution is not None or any(
            asset.kind == "instruction" and asset.id in selected for asset in bundle.assets
        )
        skill_files = {
            bundle.root / source / "SKILL.md"
            for asset in bundle.assets
            if asset.kind == "skill" and asset.id in selected
            for _, source in asset.sources
        }
        for asset in bundle.assets:
            if asset.id not in selected:
                continue
            paths: set[str] = set()
            asset_overridden = False
            for _, source in asset.sources:
                for path in source_files(bundle.root, source):
                    dest = prefix + path.relative_to(bundle.root).as_posix()
                    if dest not in managed:
                        add(dest, path, bundle.name if has_context and path in skill_files else None)
                        managed.add(dest)
                    rel = path.relative_to(bundle.root).as_posix()
                    override_file = root / OVERRIDES / bundle.name / rel if root else None
                    if override_file is not None and override_file.is_file():
                        asset_overridden = True
                        paths.add(f"{OVERRIDES}/{bundle.name}/{rel}")
                    else:
                        paths.add(dest)
            for agent in agents:
                if asset.kind not in {"skill", "subagent"}:
                    continue
                sources = dict(asset.sources)
                if asset.kind == "subagent" and "common" in sources:
                    # A role contract: render the host projection from its declared block.
                    rel = sources["common"]
                    override_file = root / OVERRIDES / bundle.name / rel if root else None
                    if override_file is not None and override_file.is_file():
                        asset_overridden = True
                        contract_source, cited = override_file, f"{OVERRIDES}/{bundle.name}/{rel}"
                    else:
                        contract_source, cited = bundle.root / rel, prefix + rel
                    contract = read_contract(contract_source.read_bytes(), f"{bundle.name}/{asset.id}", asset.id)
                    rendered = render(agent, contract, cited)
                    if rendered is not None:
                        dest = projection_path(agent, asset.id)
                        add_bytes(dest, rendered)
                        paths.add(dest)
                    continue
                source = sources.get(agent, sources.get("common") if asset.kind == "skill" else None)
                if source is None:
                    raise BundleError(f"{bundle.name}/{asset.id}: missing native variant for {agent}")
                origin = bundle.root / source
                skill_dir, subagent_dir = AGENTS[agent]
                for path in source_files(bundle.root, source):
                    rel = path.relative_to(bundle.root).as_posix()
                    override_file = root / OVERRIDES / bundle.name / rel if root else None
                    if override_file is not None and override_file.is_file():
                        asset_overridden = True
                        source_to_use = override_file
                    else:
                        source_to_use = path
                    if asset.kind == "skill":
                        dest = f"{skill_dir}/{asset.id}/{path.relative_to(origin).as_posix()}"
                    else:
                        suffix = ".toml" if agent == "codex" else ".md"
                        if not origin.is_file() or origin.suffix != suffix:
                            raise BundleError(f"{asset.id}: {agent} subagent must be one {suffix} file")
                        dest = f"{subagent_dir}/{asset.id}{suffix}"
                    add(dest, source_to_use, bundle.name if has_context and path in skill_files else None)
                    paths.add(dest)
            record: dict[str, object] = {
                "bundle": bundle.name,
                "id": asset.id,
                "kind": asset.kind,
                "paths": sorted(paths),
            }
            if asset.kind in {"playbook", "workflow"}:
                entrypoints = set()
                for _, source in asset.sources:
                    entry = (
                        playbook_entry(bundle.root, source)
                        if asset.kind == "playbook"
                        else workflow_entry(bundle.root, source)
                    )
                    rel = entry.relative_to(bundle.root).as_posix()
                    override_entry = root / OVERRIDES / bundle.name / rel if root else None
                    if override_entry is not None and override_entry.is_file():
                        entrypoints.add(f"{OVERRIDES}/{bundle.name}/{rel}")
                    else:
                        entrypoints.add(prefix + rel)
                record["entrypoints"] = sorted(entrypoints)
            assets.append(record)

            if asset_overridden and root is not None:
                chosen_upstream = None
                chosen_override = None
                for _, src in asset.sources:
                    p = bundle.root / src
                    up_f = (p / "SKILL.md") if p.is_dir() and (p / "SKILL.md").is_file() else p
                    rel_p = up_f.relative_to(bundle.root).as_posix()
                    ov_f = root / OVERRIDES / bundle.name / rel_p
                    if ov_f.is_file():
                        chosen_upstream = up_f
                        chosen_override = ov_f
                        break
                if chosen_upstream is not None and chosen_override is not None:
                    rel_primary = chosen_upstream.relative_to(bundle.root).as_posix()
                    cur_upstream_sha = hashlib.sha256(chosen_upstream.read_bytes()).hexdigest()
                    cur_override_sha = hashlib.sha256(chosen_override.read_bytes()).hexdigest()
                    prev_meta = (previous_overrides or {}).get(bundle.name, {}).get(asset.id, {})
                    baseline_sha = prev_meta.get("baseline_upstream_sha256", cur_upstream_sha)
                    if cur_upstream_sha != baseline_sha:
                        drift_list.append(
                            {
                                "bundle": bundle.name,
                                "asset": asset.id,
                                "path": rel_primary,
                                "message": f"upstream drift detected for {bundle.name}:{asset.id}",
                            }
                        )
                    if bundle.name not in overrides_record:
                        overrides_record[bundle.name] = {}
                    overrides_record[bundle.name][asset.id] = {
                        "kind": asset.kind,
                        "relative_path": rel_primary,
                        "baseline_upstream_sha256": baseline_sha,
                        "override_sha256": cur_override_sha,
                    }

    for kind, module in GENERATED_SKILLS.items():
        if not any(asset["kind"] == kind for asset in assets):
            continue
        projections = [(module.MANAGED_ROOT, None), *((f"{AGENTS[agent][0]}/{module.NAME}", agent) for agent in agents)]
        for directory, agent in projections:
            for relative, data in module.skill_files(agent).items():
                destination = f"{directory}/{relative}"
                if destination in files:
                    raise BundleError(f"destination collision: {destination}")
                files[destination] = Content(data, 0o644)
    return files, assets, packages, overrides_record, drift_list
