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
``TEMPLATE_SECTIONS``, the tables installed engines register for the ``RESERVED_TABLES`` and the ``[tool.<name>]``
tables of installed tools, each at its default.
"""

from __future__ import annotations

import math
import os
import re
from contextlib import nullcontext
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import tomlkit
from devkit.advisory import AdvisoryError
from tomlkit.exceptions import TOMLKitError

from devkit_dist.base.errors import ConfigError
from devkit_dist.features.distribution.models.content import Content
from devkit_dist.features.distribution.models.errors import SelectionError
from devkit_dist.features.distribution.models.invocation import AGENT_INVOCATION
from devkit_dist.features.distribution.models.settings import DEFAULT_PLAYBOOK_LIMIT as DEFAULT_PLAYBOOK_LIMIT
from devkit_dist.features.distribution.models.settings import DEFAULT_PLAYBOOK_MAX_BYTES as DEFAULT_PLAYBOOK_MAX_BYTES
from devkit_dist.features.distribution.models.settings import DEFAULT_PLAYBOOK_MIN_SCORE as DEFAULT_PLAYBOOK_MIN_SCORE
from devkit_dist.features.distribution.models.settings import (
    DEFAULT_PLAYBOOK_MIN_SIMILARITY as DEFAULT_PLAYBOOK_MIN_SIMILARITY,
)
from devkit_dist.features.distribution.models.settings import DEFAULT_PLAYBOOK_MODE as DEFAULT_PLAYBOOK_MODE
from devkit_dist.features.distribution.models.settings import DEFAULT_PRESET as DEFAULT_PRESET
from devkit_dist.features.distribution.models.settings import PLAYBOOK_LIMIT_MAX as PLAYBOOK_LIMIT_MAX
from devkit_dist.features.distribution.models.settings import PLAYBOOK_LIMIT_MIN as PLAYBOOK_LIMIT_MIN
from devkit_dist.features.distribution.models.settings import PLAYBOOK_MAX_BYTES_MAX as PLAYBOOK_MAX_BYTES_MAX
from devkit_dist.features.distribution.models.settings import PLAYBOOK_MAX_BYTES_MIN as PLAYBOOK_MAX_BYTES_MIN
from devkit_dist.features.distribution.models.subagents import SubagentPolicy
from devkit_dist.features.distribution.services.bundles.common import AGENT_NAMES, SLUG
from devkit_dist.features.distribution.services.bundles.templates import NAME, Scalar
from devkit_dist.features.distribution.services.installation.config_template import (
    TOOL_NAME,
    TemplateSection,
    ToolTemplate,
    add_template,
    load_reserved_templates,
    load_tool_templates,
    set_entry,
)
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle, unusable_bundles
from devkit_dist.features.distribution.services.installation.transaction import project_lock, replace_file
from devkit_dist.features.distribution.services.subagents import parse_subagents
from devkit_dist.features.project.repositories.local_config import read_effective_config, validate_runtime_tables
from devkit_dist.features.project.repositories.project import read_toml
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, RECEIPT_PATH, Receipt
from devkit_dist.features.project.services.config_template import TemplateKey, TemplateTable
from devkit_dist.features.search import SearchMode

SCHEMA = 1
# A line ending an edit adds (the commented template, a selection entry): a LF that no CR precedes.
_BARE_LF = re.compile(r"(?<!\r)\n")
# Reserved for the engines of devkit-agt and passed through unread, so a configuration reads the same with or
# without them: ``rules`` (``devkit_agt.features.rules``: phase overrides), ``workflow`` (``devkit_agt.features.workflow``: layout, approvals),
# ``gates`` (``devkit_agt.features.gate``: gate settings), ``worktree`` (``devkit_agt.features.worktree``) and ``integration``
# (``devkit_agt.features.integration``). Their commented templates come from the ``devkit.config_tables`` entry points.
RESERVED_TABLES = ("rules", "workflow", "gates", "worktree", "integration")
# ``[tool.<name>]`` tables belong to whichever tool ``<name>`` is and are passed through unread, like ``[tool.*]`` in
# ``pyproject.toml``; every other top-level key is rejected so typos are caught.
FIELDS = frozenset(
    {
        "schema",
        "execution",
        "presentation",
        "mcp",
        "shared",
        "agents",
        "presets",
        "playbooks",
        *RESERVED_TABLES,
        "guidance_block",
        "override_drift",
        "tool",
        "bundles",
        "subagents",
    }
)
OVERRIDE_DRIFT = ("warn", "block")

# ``devkit playbook search`` bounds: the ``[playbooks]`` table, the command's options and the library all check these.
# Measured on English metadata: keeps most matches while dropping the long tail of weak cosine similarities.
# A requested preset that stands for the bundle's ``default_preset`` (a bare ``bundle`` on the command line).


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
    variables: dict[str, dict[str, Scalar]] = field(default_factory=dict)
    subagents: SubagentPolicy = field(default_factory=SubagentPolicy)


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
    validate_runtime_tables(data, root / CONFIG_PATH)
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
        fix=f"Install the package that ships it (`uv sync`), or deselect it with `{AGENT_INVOCATION} remove <bundle>`",
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
    _load(root)
    data = read_effective_config(root).values
    return validate_playbooks_config(data.get("playbooks"))


def bundle_variables(raw: object) -> dict[str, dict[str, Scalar]]:
    if not isinstance(raw, dict):
        raise ConfigError("config bundles: expected a table")
    result = {}
    for bundle, settings in raw.items():
        if not isinstance(bundle, str) or not SLUG.fullmatch(bundle):
            raise ConfigError("config bundles: invalid bundle name")
        if not isinstance(settings, dict) or set(settings) - {"variables"}:
            raise ConfigError(f"config bundles.{bundle}: expected variables table only")
        values = settings.get("variables", {})
        if not isinstance(values, dict):
            raise ConfigError(f"config bundles.{bundle}.variables: expected a table")
        if any(
            not isinstance(k, str) or not NAME.fullmatch(k) or type(v) not in (str, bool, int)
            for k, v in values.items()
        ):
            raise ConfigError(
                f"config bundles.{bundle}.variables: expected identifier keys and string/boolean/integer values"
            )
        result[bundle] = dict(values)
    return result


def read_config(root: Path, *, effective: bool = True) -> ProjectConfig:
    data = _load(root)
    overlay = read_effective_config(root)
    if effective:
        data = overlay.values
    return parse_config(data)


def parse_config(data: dict[str, Any] | None) -> ProjectConfig:
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
        variables=bundle_variables(data.get("bundles", {})),
        subagents=parse_subagents(data.get("subagents", {})),
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
                fix=f"Install the content package that ships it, or run `{AGENT_INVOCATION} list`",
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


def _read_untranslated(path: Path) -> str:
    """The file's text without newline translation, so an edit keeps every existing line ending."""
    return path.read_bytes().decode("utf-8")


def _match_line_endings(before: str | None, text: str) -> str:
    """``text`` with its bare-LF line endings turned into CRLF when every line ending of ``before`` is CRLF.

    Lines an edit adds end in a bare LF; an LF, mixed, single-line or missing file keeps them so.
    """
    if before is not None and "\n" in before and before.count("\r\n") == before.count("\n"):
        return _BARE_LF.sub("\r\n", text)
    return text


def _document(root: Path) -> tomlkit.TOMLDocument:
    path = _config_path(root)
    if not path.exists():
        doc = tomlkit.document()
        doc["schema"] = SCHEMA
        return doc
    try:
        return tomlkit.parse(_read_untranslated(path))
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
    Unrelated tables, comments, formatting and line endings are preserved; a new
    key goes after the last entry of its table, never below a commented template
    table, and its line ends in CRLF only when every line ending of the file is
    CRLF (``_match_line_endings``, the rule of ``config template``). A file
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
        return ConfigUpdate(root, _match_line_endings(before.data.decode("utf-8"), text), before)
    tools, reserved, notices = _templates()
    text, _ = add_template(text, TEMPLATE_HEADER, TEMPLATE_SECTIONS, tools, reserved=reserved)
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
    """What ``refresh_config_template`` did, or what ``preview_config_template`` would do.

    ``added`` names the keys and tables written, in file order; ``text`` is the whole file a preview would write
    (``None`` for a write).
    """

    state: TemplateState
    added: list[str] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)
    text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"path": CONFIG_PATH, "state": self.state.value, "added": list(self.added)}
        if self.text is not None:
            result["text"] = self.text
        result["notices"] = [notice.to_dict() for notice in self.notices]
        return result


def _template(root: Path) -> tuple[str | None, str, list[str], list[AdvisoryError]]:
    """The file before (``None`` when missing), the file with the template added, the added parts and notices.

    The file is read without newline translation, so the rendered text keeps every existing byte; the added lines
    follow ``_match_line_endings``.
    """
    read_config(root)
    path = _config_path(root)
    before = _read_untranslated(path) if path.exists() else None
    tools, reserved, notices = _templates()
    text, added = add_template(
        before if before is not None else f"schema = {SCHEMA}\n",
        TEMPLATE_HEADER,
        TEMPLATE_SECTIONS,
        tools,
        reserved=reserved,
    )
    return before, _match_line_endings(before, text), added, notices


def _templates() -> tuple[list[ToolTemplate], list[ToolTemplate], list[AdvisoryError]]:
    """The installed ``[tool.<name>]`` templates, the reserved tables' templates and the warnings of both loads."""
    reserved, reserved_notices = load_reserved_templates(RESERVED_TABLES)
    reserved.insert(
        0,
        ToolTemplate(
            "shared",
            (
                TemplateTable(
                    (
                        TemplateKey(
                            "adapter",
                            "local",
                            "Installed immutable artifact adapter; DEVKIT_SHARED_ADAPTER overrides this key",
                        ),
                    )
                ),
            ),
            "devkit-dist",
        ),
    )
    reserved.insert(
        1,
        ToolTemplate(
            "subagents",
            (
                TemplateTable(
                    (
                        TemplateKey(
                            "default_level",
                            None,
                            "Unset: source level, then inheritance; explicit inherit resets common contracts; native variants stay verbatim",
                            example="inherit",
                        ),
                        TemplateKey(
                            "levels",
                            tomlkit.inline_table(),
                            "Partial level/host mappings; omitted fields retain built-ins, inherit clears a field",
                        ),
                        TemplateKey(
                            "roles",
                            tomlkit.inline_table(),
                            'Bundle-qualified role overrides: {"spec:scout" = {level = "compact"}}; common contracts only',
                        ),
                    ),
                    help="Shared-only subagent model policy; levels: inherit, minimal, compact, standard, deep, maximal. Antigravity supports model tiers but no effort.",
                ),
            ),
            "devkit-dist",
        ),
    )
    tools, tool_notices = load_tool_templates()
    return tools, reserved, [*reserved_notices, *tool_notices]


def _template_state(before: str | None, text: str) -> TemplateState:
    if text == before:
        return TemplateState.UNCHANGED
    return TemplateState.CREATED if before is None else TemplateState.UPDATED


def refresh_config_template(root: Path) -> ConfigTemplateResult:
    """Create ``.devkit/config.toml`` with the commented template, or add the parts of it the file lacks.

    The file is validated first (``read_config``); an invalid one is a ``ConfigError`` and is left alone. Lines
    already in the file are never changed (``installation.config_template``). Under the project lock when
    ``.devkit/`` exists; a project without it gets the directory and the file, and no lock file.
    """
    exists = (root / CONFIG_PATH).parent.is_dir()
    with project_lock(root) if exists else nullcontext():
        before, text, added, notices = _template(root)
        state = _template_state(before, text)
        if state is TemplateState.UNCHANGED:
            return ConfigTemplateResult(state, notices=notices)
        _check_writable(root)
        _write(root, text)
    return ConfigTemplateResult(state, added, notices)


def preview_config_template(root: Path) -> ConfigTemplateResult:
    """What ``refresh_config_template`` would write, without writing: ``text`` is the whole resulting file.

    The file is validated the same way (an invalid one is a ``ConfigError``). Nothing is created, not even
    ``.devkit/`` or a lock file; ``state`` and ``added`` are those the write would report.
    """
    before, text, added, notices = _template(root)
    state = _template_state(before, text)
    return ConfigTemplateResult(state, added if state is not TemplateState.UNCHANGED else [], notices, text)
