"""The desired state of a workspace: every file, asset record and seed a selection deploys."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from devkit.core.receipt import MANAGED_PATH, AssetRecord, HostHookRecord, OverrideRecord, PackageRecord
from devkit.distribution.bundles.fragments import read_fragment, references, render_fragment
from devkit.distribution.bundles.guidance import prepend_context
from devkit.distribution.bundles.instructions import read_instruction_header
from devkit.distribution.bundles.invocation import user_only, user_only_extras
from devkit.distribution.bundles.manifest import Asset, Bundle, source_files
from devkit.distribution.bundles.playbooks import playbook_entry
from devkit.distribution.bundles.subagents import (
    HOST_FILES,
    SUBAGENT_DIRS,
    projection_path,
    read_contract,
    render_projection,
)
from devkit.distribution.bundles.templates import Scalar, output_path, render_template, resolve_variables
from devkit.distribution.bundles.workflows import workflow_entry
from devkit.distribution.content import Content, normal_mode
from devkit.distribution.errors import BundleConflictError, BundleError, SelectionError
from devkit.distribution.installation import playbook_skill, workflow_skill
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.overrides import Drift, consumer_path, resolve_source, track_override
from devkit.host import adapter_for, read_hook

# Shared entry skills generated when at least one asset of the kind is synchronized.
GENERATED_SKILLS = {"playbook": playbook_skill, "workflow": workflow_skill}

# Agent name -> (skill directory, subagent directory). Codex and Antigravity share the
# ``.agents/skills`` standard, so identical skill projections are written once.
AGENTS = {
    "codex": (".agents/skills", SUBAGENT_DIRS["codex"]),
    "claude-code": (".claude/skills", SUBAGENT_DIRS["claude-code"]),
    "antigravity": (".agents/skills", SUBAGENT_DIRS["antigravity"]),
}


@dataclass(frozen=True)
class Seed:
    """A file written once to a project-owned destination by a seeded ``document`` asset."""

    bundle: str
    asset: str
    content: Content


@dataclass(frozen=True)
class Unprojected:
    """A subagent with ``variants`` that has no file for a selected agent."""

    bundle: str
    asset: str
    agent: str

    def to_dict(self) -> dict[str, str]:
        return {"bundle": self.bundle, "asset": self.asset, "agent": self.agent}


@dataclass(frozen=True)
class Fragment:
    """A selected ``guidance`` asset, rendered for the root ``AGENTS.md`` block."""

    bundle: str
    asset: str
    text: str


@dataclass
class Inventory:
    # Workspace-relative destination -> content; what the receipt's ``files`` will own.
    files: dict[str, Content] = field(default_factory=dict)
    assets: list[AssetRecord] = field(default_factory=list)
    packages: list[PackageRecord] = field(default_factory=list)
    overrides: dict[str, dict[str, OverrideRecord]] = field(default_factory=dict)
    drift: list[Drift] = field(default_factory=list)
    unprojected: list[Unprojected] = field(default_factory=list)
    # Seeded destinations -> origin; never part of ``files``.
    seeds: dict[str, Seed] = field(default_factory=dict)
    guidance: list[Fragment] = field(default_factory=list)
    # Projected skill directory or subagent file -> its owner (``bundle:asset``, or a generated entry skill).
    projections: dict[str, str] = field(default_factory=dict)
    host_hooks: list[HostHookRecord] = field(default_factory=list)

    def fragments(self) -> list[str]:
        """Rendered guidance in the block's stable order: by bundle, then asset ID."""
        return [item.text for item in sorted(self.guidance, key=lambda item: (item.bundle, item.asset))]

    def claim(self, unit: str, owner: str) -> None:
        """Give a projected skill directory or subagent file to one owner.

        A second owner is a ``BUNDLE_CONFLICT`` even where the bytes agree, so
        two bundles never merge their files into one skill directory. The same
        owner may claim a unit again: Codex and Antigravity share ``.agents/skills``.
        """
        existing = self.projections.setdefault(unit, owner)
        if existing != owner:
            raise BundleConflictError(f"destination collision: {unit} ({existing} and {owner})", target_files=[unit])

    def put(self, destination: str, content: Content) -> None:
        # Agents sharing a directory (Codex and Antigravity) project the same bytes twice.
        existing = self.files.get(destination)
        if existing is not None and existing != content:
            raise BundleConflictError(
                f"destination collision: {destination}",
                target_files=[destination],
            )
        self.files[destination] = content

    def copy(
        self,
        destination: str,
        path: Path,
        context_bundle: str | None = None,
        render: Callable[[bytes], bytes] | None = None,
    ) -> None:
        data = path.read_bytes()
        if render is not None:
            data = render(data)
        if context_bundle is not None:
            data = prepend_context(data, context_bundle, destination)
        self.put(destination, Content(data, normal_mode(path.stat().st_mode)))


class _BundleInventory:
    """Adds one selected bundle to an ``Inventory``."""

    def __init__(
        self, inventory: Inventory, bundle: Bundle, agents: list[str], root: Path | None, variables: dict[str, Scalar]
    ) -> None:
        self.inventory = inventory
        self.bundle = bundle
        self.agents = agents
        self.root = root
        self.variables = resolve_variables(bundle.variables, variables, bundle.name)
        self.prefix = f"{MANAGED_PATH}/{bundle.name}/"
        self.context_files: set[Path] = set()
        self.selected: set[str] = set()

    def add(self, presets: list[str], previous: dict[str, OverrideRecord]) -> None:
        bundle = self.bundle
        selected = bundle.select(presets)
        self.inventory.copy(self.prefix + "bundle.toml", bundle.root / "bundle.toml")
        constitution = bundle.constitution
        if constitution is not None:
            self.inventory.copy(self.prefix + "AGENTS.md", constitution)
        self.selected = selected
        chosen = [asset for asset in bundle.assets if asset.id in selected]
        # A bundle with a context (constitution or instructions) prefixes its skills with the load prerequisite.
        if constitution is not None or any(asset.kind == "instruction" for asset in chosen):
            self.context_files = {
                bundle.root / source / "SKILL.md"
                for asset in chosen
                if asset.kind == "skill"
                for _, source in asset.sources
            }
        for asset in chosen:
            if asset.seeded:
                self._seed(asset)
                continue
            paths = self._managed(asset)
            if asset.kind == "guidance":
                self._fragment(asset)
            if asset.kind == "hook":
                self._hook(asset)
            for agent in self.agents:
                paths |= self._project(asset, agent)
            self.inventory.assets.append(
                AssetRecord(bundle.name, asset.id, asset.kind, tuple(sorted(paths)), self._entrypoints(asset))
            )
            record, drift = track_override(self.root, bundle, asset, previous.get(asset.id))
            if record is not None:
                self.inventory.overrides.setdefault(bundle.name, {})[asset.id] = record
            if drift is not None:
                self.inventory.drift.append(drift)

    def _context(self, path: Path) -> str | None:
        return self.bundle.name if path in self.context_files else None

    def _hook(self, asset: Asset) -> None:
        ((_, source),) = asset.sources
        read_from, cited = resolve_source(self.root, self.bundle, source)
        hook = read_hook(read_from.read_bytes(), cited)
        for agent in self.agents:
            if agent != hook.host:
                self.inventory.unprojected.append(Unprojected(self.bundle.name, asset.id, agent))
        if hook.host not in self.agents:
            return
        self.inventory.host_hooks.append(adapter_for(hook.host).record(f"{self.bundle.name}:{asset.id}", hook))

    def _seed(self, asset: Asset) -> None:
        assert asset.target is not None
        ((_, source),) = asset.sources
        origin = self.bundle.root / source
        seeds = self.inventory.seeds
        targets = []
        for path in source_files(self.bundle.root, source):
            dest = (
                asset.target
                if origin.is_file()
                else f"{asset.target}/{output_path(path.relative_to(origin).as_posix())}"
            )
            if dest in seeds:
                raise BundleConflictError(
                    f"seeded target collision: {dest} ({seeds[dest].bundle} and {self.bundle.name})",
                    target_files=[dest],
                )
            data = (
                render_template(path.read_bytes(), self.variables, source)
                if path.name.endswith(".md.jinja")
                else path.read_bytes()
            )
            seeds[dest] = Seed(self.bundle.name, asset.id, Content(data, normal_mode(path.stat().st_mode)))
            targets.append(dest)
        self.inventory.assets.append(
            AssetRecord(self.bundle.name, asset.id, asset.kind, (), seeded=tuple(sorted(targets)))
        )

    def _managed(self, asset: Asset) -> set[str]:
        """Copy the upstream files into the managed root; return the paths consumers read (overrides win)."""
        paths = set()
        for _, source in asset.sources:
            for path in source_files(self.bundle.root, source):
                rel = path.relative_to(self.bundle.root).as_posix()
                if rel.endswith(".md.jinja"):
                    read_from, cited = resolve_source(self.root, self.bundle, rel)
                    data = render_template(read_from.read_bytes(), self.variables, cited)
                    if asset.kind == "instruction":
                        read_instruction_header(data, cited)
                    elif asset.kind == "guidance":
                        read_fragment(data, cited)
                    self.inventory.put(self.prefix + output_path(rel), Content(data, normal_mode(path.stat().st_mode)))
                else:
                    self.inventory.copy(self.prefix + rel, path, self._context(path))
                paths.add(consumer_path(self.root, self.bundle, rel))
        return paths

    def _fragment(self, asset: Asset) -> None:
        """Render a guidance asset (the project override, if any) with its placeholders resolved."""
        ((_, source),) = asset.sources
        read_from, cited = resolve_source(self.root, self.bundle, source)
        data = (
            self.inventory.files[self.prefix + output_path(source)].data
            if source.endswith(".md.jinja")
            else read_from.read_bytes()
        )
        text = read_fragment(data, cited)
        paths = {}
        for ref in references(text):
            target = self.bundle.single_file_source(ref)
            if target is None or ref not in self.selected:
                raise BundleError(
                    f"{cited}: {{path:{ref}}} must name a selected single-file, non-guidance asset of {self.bundle.name}"
                )
            paths[ref] = consumer_path(self.root, self.bundle, target)
        self.inventory.guidance.append(Fragment(self.bundle.name, asset.id, render_fragment(text, paths)))

    def _project(self, asset: Asset, agent: str) -> set[str]:
        """Native projections of a skill or subagent for ``agent``."""
        if asset.kind not in {"skill", "subagent"}:
            return set()
        sources = dict(asset.sources)
        if asset.kind == "subagent" and "common" in sources:
            return self._contract(asset, agent, sources["common"])
        source = sources.get(agent, sources.get("common") if asset.kind == "skill" else None)
        if source is None:
            # Never converted from another host's file: the agent simply gets no projection.
            self.inventory.unprojected.append(Unprojected(self.bundle.name, asset.id, agent))
            return set()
        origin = self.bundle.root / source
        skill_dir, subagent_dir = AGENTS[agent]
        owner = f"{self.bundle.name}:{asset.id}"
        if asset.kind == "skill":
            self.inventory.claim(f"{skill_dir}/{asset.id}", owner)
        paths = set()
        relatives = set()
        for path in source_files(self.bundle.root, source):
            read_from, cited = resolve_source(self.root, self.bundle, path.relative_to(self.bundle.root).as_posix())
            render = None
            if asset.kind == "skill":
                relative = path.relative_to(origin).as_posix()
                relatives.add(relative)
                dest = f"{skill_dir}/{asset.id}/{relative}"
                if asset.invocation == "user":
                    render = partial(user_only, relative, agent=agent, context=cited)
            else:
                suffix = HOST_FILES[agent]
                if not origin.is_file() or origin.suffix != suffix:
                    raise BundleError(f"{asset.id}: {agent} subagent must be one {suffix} file")
                dest = f"{subagent_dir}/{asset.id}{suffix}"
                self.inventory.claim(dest, owner)
            self.inventory.copy(dest, read_from, self._context(path), render)
            paths.add(dest)
        if asset.kind == "skill" and asset.invocation == "user":
            for relative, data in user_only_extras(agent, relatives).items():
                dest = f"{skill_dir}/{asset.id}/{relative}"
                self.inventory.put(dest, Content(data, 0o644))
                paths.add(dest)
        return paths

    def _contract(self, asset: Asset, agent: str, rel: str) -> set[str]:
        """A role contract: render the host projection from its declared block, citing the file it read."""
        read_from, cited = resolve_source(self.root, self.bundle, rel)
        contract = read_contract(read_from.read_bytes(), f"{self.bundle.name}/{asset.id}", asset.id)
        rendered = render_projection(agent, contract, cited)
        if rendered is None:
            return set()
        dest = projection_path(agent, asset.id)
        self.inventory.claim(dest, f"{self.bundle.name}:{asset.id}")
        self.inventory.put(dest, Content(rendered, 0o644))
        return {dest}

    def _entrypoints(self, asset: Asset) -> tuple[str, ...]:
        if asset.kind not in {"playbook", "workflow"}:
            return ()
        entry_of = playbook_entry if asset.kind == "playbook" else workflow_entry
        return tuple(
            sorted(
                {
                    resolve_source(
                        self.root,
                        self.bundle,
                        entry_of(self.bundle.root, source).relative_to(self.bundle.root).as_posix(),
                    )[1]
                    for _, source in asset.sources
                }
            )
        )


def desired_inventory(
    installed: list[InstalledBundle],
    presets: dict[str, list[str]],
    agents: list[str],
    *,
    root: Path | None = None,
    previous_overrides: dict[str, dict[str, OverrideRecord]] | None = None,
    variables: dict[str, dict[str, Scalar]] | None = None,
) -> Inventory:
    """Everything ``installed`` deploys for ``presets`` and ``agents``.

    ``root`` enables project overrides (``None`` plans pristine upstream
    content); ``previous_overrides`` carries override baselines over from the
    last receipt.
    """
    # Every bundle passed in is deployed, so each needs an explicit preset selection.
    if set(presets) != {item.bundle.name for item in installed}:
        raise SelectionError("inventory requires exactly one preset selection per bundle")
    if set(agents) - AGENTS.keys():
        raise SelectionError(f"unsupported agent selection: {sorted(set(agents) - AGENTS.keys())}")
    inventory = Inventory()
    for item in installed:
        bundle = item.bundle
        inventory.packages.append(PackageRecord(item.package, item.package_version, bundle.name, bundle.version))
        _BundleInventory(inventory, bundle, agents, root, (variables or {}).get(bundle.name, {})).add(
            presets[bundle.name], dict((previous_overrides or {}).get(bundle.name, {}))
        )
    for kind, module in GENERATED_SKILLS.items():
        if not any(asset.kind == kind for asset in inventory.assets):
            continue
        projections = [(module.MANAGED_ROOT, None), *((f"{AGENTS[agent][0]}/{module.NAME}", agent) for agent in agents)]
        for directory, agent in projections:
            if agent is not None:
                inventory.claim(directory, f"generated skill {module.NAME}")
            for relative, data in module.skill_files(agent).items():
                inventory.put(f"{directory}/{relative}", Content(data, 0o644))
    for dest in inventory.seeds:
        if dest in inventory.files:
            raise BundleConflictError(
                f"seeded target collides with a managed destination: {dest}",
                target_files=[dest],
            )
    return inventory
