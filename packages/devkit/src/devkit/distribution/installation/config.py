"""Project configuration (``.devkit/config.toml``): bundle selection.

A bundle is deployed when ``[presets]`` names it. An installed bundle that
declares ``auto_select``, built in or from any other package, is also deployed
with its default preset unless ``[presets]`` names it, which selects other
presets, or sets it to ``false``, which opts the project out. Native
projections go to every supported agent unless ``agents`` narrows the list;
``agents = []`` turns projection off.

A selection command that creates the file writes the commented template with
it, and ``refresh_config_template`` adds what an existing file lacks
(``installation.config_template``): devkit's top-level keys in
``TEMPLATE_SECTIONS``, common tables in ``TEMPLATE_TABLES`` and the ``[tool.<name>]`` tables of installed tools,
each at its default.
"""

from __future__ import annotations

import math
import os
from contextlib import nullcontext
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.exceptions import TOMLKitError

from devkit.advisory import AdvisoryError
from devkit.core.config_template import TemplateKey, TemplateTable
from devkit.core.errors import ConfigError
from devkit.core.project import read_toml
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH, Receipt
from devkit.distribution.bundles.common import AGENT_NAMES, SLUG
from devkit.distribution.content import Content
from devkit.distribution.errors import SelectionError
from devkit.distribution.installation.config_template import (
    TOOL_NAME,
    TemplateSection,
    add_template,
    load_tool_templates,
    set_entry,
)
from devkit.distribution.installation.discovery import InstalledBundle, unusable_bundles
from devkit.distribution.installation.transaction import project_lock, replace_file
from devkit.search import SearchMode

SCHEMA = 1
# ``rules`` is owned by ``devkit.rules`` (phase overrides), ``workflow`` by
# ``devkit.workflow`` (layout, approvals), ``gates`` by ``devkit.gate`` (gate
# settings) and ``worktree`` by ``devkit.worktree``; all are only passed through here. ``[tool.<name>]`` tables belong
# to whichever tool ``<name>`` is and are passed through unread, like ``[tool.*]`` in
# ``pyproject.toml``; every other top-level key is rejected so typos are caught.
FIELDS = frozenset(
    {
        "schema",
        "agents",
        "presets",
        "playbooks",
        "rules",
        "workflow",
        "gates",
        "worktree",
        "guidance_block",
        "override_drift",
        "tool",
    }
)
OVERRIDE_DRIFT = ("warn", "block")

# ``devkit playbook search`` bounds: the ``[playbooks]`` table, the command's options and the library all check these.
PLAYBOOK_LIMIT_MIN, PLAYBOOK_LIMIT_MAX = 1, 20
PLAYBOOK_MAX_BYTES_MIN, PLAYBOOK_MAX_BYTES_MAX = 1024, 65536
DEFAULT_PLAYBOOK_LIMIT = 5
DEFAULT_PLAYBOOK_MIN_SCORE = 0.1
DEFAULT_PLAYBOOK_MAX_BYTES = 8192
DEFAULT_PLAYBOOK_MODE = SearchMode.AUTO
# Measured on English metadata: keeps most matches while dropping the long tail of weak cosine similarities.
DEFAULT_PLAYBOOK_MIN_SIMILARITY = 0.35
# A requested preset that stands for the bundle's ``default_preset`` (a bare ``bundle`` on the command line).
DEFAULT_PRESET = ""


def all_agents() -> list[str]:
    return sorted(AGENT_NAMES)


TEMPLATE_HEADER = (
    "devkit project configuration, tracked by Git. A commented key shows its default: uncomment it to change it."
    " Lines starting with ## stay comments; to use a commented table, uncomment its header and the keys you change."
    " `devkit config template` adds the keys and tables that newly installed tools accept; it never changes a line."
)
# devkit's top-level keys in the template, at the defaults ``read_config`` applies.
TEMPLATE_SECTIONS = (
    TemplateSection(
        "Managed scope: what devkit sync deploys, and for which agents.",
        (
            TemplateKey(
                "agents",
                all_agents(),
                "agents that skills and subagents are projected for; unset: every supported agent, also ones added"
                " later; []: none, the managed copies stay",
                kind="array of agent names",
            ),
            TemplateKey("guidance_block", True, "devkit sync manages the DEVKIT block of the root AGENTS.md"),
        ),
        '[presets] selects bundles: <bundle> = "<preset>", an array of presets, or "all"; `devkit add` and'
        " `devkit remove` edit it. A bundle that declares auto_select deploys its default preset without an entry;"
        " <bundle> = false opts it out. `devkit list` shows every installed bundle, its presets and its selection.",
    ),
    TemplateSection(
        "Update policy: how devkit sync takes upstream changes.",
        (
            TemplateKey(
                "override_drift",
                OVERRIDE_DRIFT[0],
                'upstream changed a file a project override replaces: "warn" reports it, "block" stops syncs until'
                " `devkit override accept`",
                kind=" or ".join(f'"{value}"' for value in OVERRIDE_DRIFT),
            ),
        ),
    ),
)

# Common module settings live here so distribution does not import higher layers.
# Gate names and stage ids are workflow-defined; these are representative names,
# with the policies the workflow reader applies to every name by default.
TEMPLATE_TABLES = (
    TemplateTable(
        (
            TemplateKey(
                "intent", "ask", "confirm user requirements, scope and verification (G1)", kind='"ask" | "auto" | "off"'
            ),
            TemplateKey(
                "direction", "ask", "approve implementation direction and design (G2)", kind='"ask" | "auto" | "off"'
            ),
            TemplateKey(
                "integration", "ask", "approve integration and PR creation (G3)", kind='"ask" | "auto" | "off"'
            ),
        ),
        path=("workflow", "approvals"),
        help="Workflow approval gates: ask waits for approval, auto satisfies the gate, off skips its stage."
        " Names come from workflow definitions; the delivery gates below are examples. Unset gates use ask.",
    ),
    TemplateTable(
        (TemplateKey("collect-feedback", "on", "set off to skip feedback collection", kind='"on" | "off"'),),
        path=("workflow", "stages"),
        help="Workflow stages: policies apply by stage id across workflows. The id below is an example;"
        " unset stages use on. Stage off takes precedence over approval policy.",
    ),
    TemplateTable(
        (
            TemplateKey(
                "pull_request", False, "integrate through a pull request; true refuses worktree finish --merge"
            ),
            TemplateKey("delete_branch", True, "worktree finish deletes the merged branch with git branch -d"),
            TemplateKey(
                "setup",
                help="shell command run in a newly created worktree; unset: no setup command",
                example="uv sync",
            ),
        ),
        path=("worktree",),
        help="Git worktree behavior: integration policy, branch cleanup and setup for new worktrees.",
    ),
)


@dataclass(frozen=True)
class ProjectConfig:
    agents: list[str] = field(default_factory=all_agents)
    presets: dict[str, list[str]] = field(default_factory=dict)
    # Bundles set to ``false`` in ``[presets]``: never selected by default.
    opted_out: frozenset[str] = frozenset()
    # ``guidance_block = false`` stops ``devkit sync`` from managing the block in root AGENTS.md.
    guidance_block: bool = True
    # ``override_drift = "block"`` makes upstream drift behind an override abort the sync.
    override_drift: str = "warn"


def _config_path(root: Path) -> Path:
    """``root/.devkit/config.toml``; it is read and written in place, so it must be a regular file."""
    path = root / CONFIG_PATH
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ConfigError(f"config must be a regular file: {CONFIG_PATH}")
    return path


def _load(root: Path) -> dict[str, Any] | None:
    data = read_toml(_config_path(root), CONFIG_PATH)
    if data is None:
        return None
    if "schema" in data and (type(data["schema"]) is not int or data["schema"] != SCHEMA):
        raise ConfigError("unsupported config schema")
    unknown = set(data) - FIELDS
    if unknown:
        raise ConfigError(f"config: unknown fields: {sorted(unknown)}")
    validate_tool_tables(data.get("tool"))
    return data


def validate_tool_tables(tool: object) -> None:
    """``[tool.<name>]`` must be a table of tables; their contents are never inspected."""
    if tool is None:
        return
    if not isinstance(tool, dict):
        raise ConfigError("config tool: expected a table of [tool.<name>] tables")
    for name, value in tool.items():
        if not (isinstance(name, str) and TOOL_NAME.fullmatch(name)):
            raise ConfigError(f"config tool: invalid tool name: {name!r}")
        if not isinstance(value, dict):
            raise ConfigError(f"config tool.{name}: expected a table")


def _agents(value: object) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) and v in AGENT_NAMES for v in value):
        raise ConfigError("config: invalid agents")
    return sorted(set(value))


def parse_presets(value: object, context: str = "config") -> dict[str, list[str]]:
    if not isinstance(value, dict):
        raise ConfigError(f"{context}: invalid presets")
    result = {}
    for bundle, presets in value.items():
        if isinstance(presets, str):
            presets = [presets]
        if (
            not (isinstance(bundle, str) and SLUG.fullmatch(bundle))
            or not isinstance(presets, list)
            or not presets
            or not all(isinstance(v, str) and SLUG.fullmatch(v) for v in presets)
            or len(set(presets)) != len(presets)
        ):
            raise ConfigError(f"{context}: invalid presets")
        result[bundle] = list(presets)
    return result


def parse_selection(value: object) -> tuple[dict[str, list[str]], frozenset[str]]:
    """``[presets]`` of the config: preset selections and the bundles set to ``false``."""
    if not isinstance(value, dict):
        raise ConfigError("config: invalid presets")
    opted_out = frozenset(name for name, presets in value.items() if presets is False)
    for name in opted_out:
        if not (isinstance(name, str) and SLUG.fullmatch(name)):
            raise ConfigError("config: invalid presets")
    return parse_presets({k: v for k, v in value.items() if k not in opted_out}), opted_out


def default_selection(installed: list[InstalledBundle], config: ProjectConfig) -> dict[str, list[str]]:
    """Auto-selected bundles the configuration neither names nor opts out of, with their default preset."""
    return {
        item.bundle.name: [item.bundle.default_preset]
        for item in installed
        if item.auto_selected
        and item.bundle.default_preset is not None
        and item.bundle.name not in config.presets
        and item.bundle.name not in config.opted_out
    }


def retained_selection(
    installed: list[InstalledBundle], config: ProjectConfig, receipt: Receipt | None
) -> dict[str, list[str]]:
    """Deployed bundles without a usable package that the configuration neither names nor opts out of.

    A package that cannot be loaded, or is not installed, cannot be read for
    ``auto_select``, so the bundle the receipt records as deployed stays
    selected with its recorded presets: the load error, or the missing package,
    then stops the command instead of a broken upgrade or a partial environment
    removing the bundle's files. Only ``devkit remove`` deselects it.
    """
    if receipt is None:
        return {}
    usable = {item.bundle.name for item in installed}
    return {
        name: list(presets)
        for name, presets in receipt.selection.presets.items()
        if name not in usable and name not in config.presets and name not in config.opted_out
    }


def missing_selection_error(missing: list[str], deployed: list[str]) -> SelectionError:
    """``SELECTION_INVALID`` for selected bundles that no installed package provides.

    ``deployed`` names those selected only because the receipt records them deployed (no ``config.toml`` entry),
    for which a sync would otherwise delete committed files.
    """
    return SelectionError(
        f"selected bundle is not installed: {missing}"
        + (f" (deployed per {RECEIPT_PATH}: {deployed})" if deployed else ""),
        fix="Install the package that ships it (`uv sync`), or deselect it with `devkit remove <bundle>`",
    )


def effective_selection(
    installed: list[InstalledBundle], config: ProjectConfig, receipt: Receipt | None = None
) -> dict[str, list[str]]:
    """What ``devkit sync`` deploys without command-line selections: defaults, then ``[presets]``.

    With the ``receipt``, deployed bundles without a usable package are kept (``retained_selection``).
    """
    return {
        **default_selection(installed, config),
        **retained_selection(installed, config, receipt),
        **config.presets,
    }


def merge_selection(
    installed: list[InstalledBundle], config: ProjectConfig, requested: dict[str, list[str]]
) -> dict[str, list[str]]:
    """``requested`` joined with the presets each bundle already deploys, existing presets first."""
    current = effective_selection(installed, config)
    return {name: list(dict.fromkeys([*current.get(name, []), *presets])) for name, presets in requested.items()}


def validate_playbooks_config(playbooks: object) -> dict[str, int | float | str]:
    if playbooks is None:
        return {}
    if not isinstance(playbooks, dict):
        raise ConfigError("config playbooks: expected a table")
    unknown = set(playbooks) - {"min_score", "limit", "max_bytes", "mode", "min_similarity"}
    if unknown:
        raise ConfigError(f"config playbooks: unknown fields: {sorted(unknown)}")
    result: dict[str, int | float | str] = {}
    if "limit" in playbooks:
        val = playbooks["limit"]
        if type(val) is not int or not PLAYBOOK_LIMIT_MIN <= val <= PLAYBOOK_LIMIT_MAX:
            raise ConfigError(
                f"config playbooks: limit must be an integer between {PLAYBOOK_LIMIT_MIN} and {PLAYBOOK_LIMIT_MAX}"
            )
        result["limit"] = val
    if "min_score" in playbooks:
        val = playbooks["min_score"]
        if not isinstance(val, (int, float)) or not math.isfinite(val) or val < 0:
            raise ConfigError("config playbooks: min_score must be a finite nonnegative number")
        result["min_score"] = float(val)
    if "max_bytes" in playbooks:
        val = playbooks["max_bytes"]
        if type(val) is not int or not PLAYBOOK_MAX_BYTES_MIN <= val <= PLAYBOOK_MAX_BYTES_MAX:
            raise ConfigError(
                "config playbooks: max_bytes must be an integer between"
                f" {PLAYBOOK_MAX_BYTES_MIN} and {PLAYBOOK_MAX_BYTES_MAX}"
            )
        result["max_bytes"] = val
    if "mode" in playbooks:
        val = playbooks["mode"]
        modes = [mode.value for mode in SearchMode]
        if not isinstance(val, str) or val.lower() not in modes:
            raise ConfigError(f"config playbooks: mode must be one of {', '.join(modes)}")
        result["mode"] = val.lower()
    if "min_similarity" in playbooks:
        val = playbooks["min_similarity"]
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not 0 <= val <= 1:
            raise ConfigError("config playbooks: min_similarity must be a number between 0 and 1")
        result["min_similarity"] = float(val)
    return result


def read_playbook_config(root: Path) -> dict[str, int | float | str]:
    data = _load(root)
    return validate_playbooks_config(data.get("playbooks")) if data else {}


def read_config(root: Path) -> ProjectConfig:
    data = _load(root)
    if data is None:
        return ProjectConfig()
    validate_playbooks_config(data.get("playbooks"))
    guidance_block = data.get("guidance_block", True)
    if type(guidance_block) is not bool:
        raise ConfigError("config: guidance_block must be a boolean")
    override_drift = data.get("override_drift", "warn")
    if override_drift not in OVERRIDE_DRIFT:
        raise ConfigError(f"config: override_drift must be one of {list(OVERRIDE_DRIFT)}")
    presets, opted_out = parse_selection(data.get("presets", {}))
    return ProjectConfig(
        agents=_agents(data["agents"]) if "agents" in data else all_agents(),
        presets=presets,
        opted_out=opted_out,
        guidance_block=guidance_block,
        override_drift=override_drift,
    )


def resolve_selection(installed: list[InstalledBundle], requested: dict[str, list[str]]) -> dict[str, list[str]]:
    """Resolve CLI selections; ``DEFAULT_PRESET``, or an empty preset list, means the bundle's ``default_preset``."""
    bundles = {item.bundle.name: item.bundle for item in installed}
    result = {}
    for name, presets in requested.items():
        bundle = bundles.get(name)
        if bundle is None:
            unusable = unusable_bundles(installed)
            if name in unusable:
                raise unusable[name]
            raise SelectionError(
                f"bundle is not installed: {name}",
                fix="Install the content package that ships it, or run `devkit list`",
            )
        if not presets or DEFAULT_PRESET in presets:
            default = bundle.default_preset
            if default is None:
                raise SelectionError(
                    f"{name}: the bundle declares no default preset",
                    fix=f"Select one of: {', '.join(f'{name}:{p}' for p in bundle.preset_names)}",
                )
            presets = [default if preset == DEFAULT_PRESET else preset for preset in presets] or [default]
        bundle.select(presets)
        result[name] = list(dict.fromkeys(presets))
    return result


def _document(root: Path) -> tomlkit.TOMLDocument:
    path = _config_path(root)
    if not path.exists():
        doc = tomlkit.document()
        doc["schema"] = SCHEMA
        return doc
    try:
        return tomlkit.parse(path.read_text("utf-8"))
    except (OSError, UnicodeError, TOMLKitError) as exc:
        raise ConfigError(f"invalid config: {exc}") from exc


def _check_writable(root: Path) -> None:
    """Fail before anything is synchronized when the configuration could not be saved afterwards."""
    path = _config_path(root)
    directory = next((parent for parent in (path.parent, root) if parent.exists()), root)
    if path.exists() and not os.access(path, os.R_OK):
        raise ConfigError(f"config is not readable: {CONFIG_PATH}")
    if not os.access(directory, os.W_OK | os.X_OK):
        raise ConfigError(f"cannot write {CONFIG_PATH}: {directory} is not writable")


def _write(root: Path, text: str) -> None:
    """Replace the configuration atomically, keeping its permission bits."""
    path = _config_path(root)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    replace_file(path, Content(text.encode("utf-8"), mode))


def _preset_value(presets: list[str]) -> str | list[str]:
    return presets[0] if len(presets) == 1 else presets


@dataclass(frozen=True)
class ConfigUpdate:
    """A rendered and checked selection edit: ``apply`` saves it, ``revert`` puts the file back as it was."""

    root: Path
    text: str | None
    # The file before the edit; ``None`` when it did not exist.
    before: Content | None = None
    # What rendering the edit reports although it succeeded (a config template extension that failed).
    notices: tuple[AdvisoryError, ...] = ()

    def apply(self) -> None:
        if self.text is not None:
            _write(self.root, self.text)

    def revert(self) -> None:
        if self.text is not None:
            replace_file(_config_path(self.root), self.before)


def prepare_config_update(
    root: Path,
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    opt_out: list[str] | tuple[str, ...] = (),
) -> ConfigUpdate:
    """Render a selection edit and check that it can be saved, without writing.

    ``deselect`` deletes a bundle's entry; ``opt_out`` records ``<bundle> = false``
    so a built-in bundle stays unselected. Selecting a bundle replaces either.
    Unrelated tables, comments and formatting are preserved; a new key goes after
    the last entry of its table, never below a commented template table. A file
    the edit creates gets the commented template too, and the update carries the
    warnings of the template extensions that failed. Nothing to change yields an
    update whose ``apply`` does nothing.
    """
    read_config(root)
    if agents is None and not (presets or deselect or opt_out):
        return ConfigUpdate(root, None)
    doc = _document(root)
    if agents is not None:
        set_entry(doc, "agents", sorted(set(agents)))
    if presets or deselect or opt_out:
        table = doc.get("presets")
        if table is None:
            table = tomlkit.table()
            doc["presets"] = table
        for name, values in (presets or {}).items():
            set_entry(table, name, _preset_value(values))
        for name in deselect:
            if name in table:
                del table[name]
        for name in opt_out:
            set_entry(table, name, False)
    _check_writable(root)
    path = _config_path(root)
    before = Content(path.read_bytes(), path.stat().st_mode & 0o777) if path.exists() else None
    text = tomlkit.dumps(doc)
    if before is not None:
        return ConfigUpdate(root, text, before)
    tools, notices = load_tool_templates()
    text, _ = add_template(text, TEMPLATE_HEADER, TEMPLATE_SECTIONS, tools, devkit_tables=TEMPLATE_TABLES)
    return ConfigUpdate(root, text, None, tuple(notices))


def update_config(
    root: Path,
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    opt_out: list[str] | tuple[str, ...] = (),
) -> list[AdvisoryError]:
    """Edit selection entries in place (``prepare_config_update`` then ``apply``); return the update's notices.

    The notices are the warnings of the config template extensions that failed when the edit created the file.
    Under the project lock when ``.devkit/`` exists, as ``refresh_config_template``.
    """
    exists = (root / CONFIG_PATH).parent.is_dir()
    with project_lock(root) if exists else nullcontext():
        update = prepare_config_update(root, agents=agents, presets=presets, deselect=deselect, opt_out=opt_out)
        update.apply()
    return list(update.notices)


class TemplateState(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class ConfigTemplateResult:
    """What ``refresh_config_template`` did: ``added`` names the keys and tables it wrote, in file order."""

    state: TemplateState
    added: list[str] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": CONFIG_PATH,
            "state": self.state.value,
            "added": list(self.added),
            "notices": [notice.to_dict() for notice in self.notices],
        }


def refresh_config_template(root: Path) -> ConfigTemplateResult:
    """Create ``.devkit/config.toml`` with the commented template, or add the parts of it the file lacks.

    The file is validated first (``read_config``); an invalid one is a ``ConfigError`` and is left alone. Lines
    already in the file are never changed (``installation.config_template``). Under the project lock when
    ``.devkit/`` exists; a project without it gets the directory and the file, and no lock file.
    """
    exists = (root / CONFIG_PATH).parent.is_dir()
    with project_lock(root) if exists else nullcontext():
        read_config(root)
        path = _config_path(root)
        before = path.read_text("utf-8") if path.exists() else None
        tools, notices = load_tool_templates()
        text, added = add_template(
            before if before is not None else f"schema = {SCHEMA}\n",
            TEMPLATE_HEADER,
            TEMPLATE_SECTIONS,
            tools,
            devkit_tables=TEMPLATE_TABLES,
        )
        if text == before:
            return ConfigTemplateResult(TemplateState.UNCHANGED, notices=notices)
        _check_writable(root)
        _write(root, text)
    return ConfigTemplateResult(TemplateState.CREATED if before is None else TemplateState.UPDATED, added, notices)
