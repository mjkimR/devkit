"""The commented template in ``.devkit/config.toml``: what a project can set, each key at its default.

Three parts, all comments a developer uncomments in place. devkit's own top-level keys go right after the file's
last top-level key, grouped in ``TemplateSection`` values that ``installation.config`` defines (top-level keys must
precede the first table header). The tables of the reserved top-level names follow the project's tables, then the
``[tool.<name>]`` tables of the installed tools. Both are contributed by installed packages, so distribution holds no
defaults of an engine it does not ship: each callable registered under the ``devkit.config_tables`` entry-point
group, named after a reserved table (``workflow``, ``worktree``: devkit-agt), returns that table's subtables, and
each callable registered under ``devkit.config_template``, named ``<name>``, returns the tables of ``[tool.<name>]``,
both as ``devkit.core.TemplateTable`` values with paths below their own table. devkit renders them
(``devkit.core.config_template``), so a package never writes outside its own table. Extensions run in sorted
entry-point name order, are called with no argument, and render the same for every project.

Rendering only adds: a key whose name the file already mentions (set, or commented anywhere), or a table whose
header it mentions (commented or not) or defines, is left out, so no line is changed and an uncommented line stays
where the developer put it. An extension that fails to load, raises, returns anything but valid tables, or (for
``devkit.config_tables``) is not named after a reserved table is left out with a
``CONFIG_TEMPLATE_EXTENSION_FAILED`` warning.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import tomlkit
from tomlkit.container import Container
from tomlkit.items import AoT, Table

from devkit.advisory import AdvisoryError
from devkit.core.config_template import (
    TemplateKey,
    TemplateTable,
    check_tables,
    prose,
    render_key,
    render_table,
    table_name,
)
from devkit.distribution.errors import ConfigTemplateExtensionFailedNotice

GROUP = "devkit.config_template"
RESERVED_GROUP = "devkit.config_tables"
TOOL_NAME = re.compile(r"[a-z][a-z0-9_-]*\Z")
# A key that cannot appear in a project's file: set where devkit's keys go, then replaced by them.
_MARKER = "devkit-config-template-position"
_COMMENTED_KEY = re.compile(r"^[ \t]*#+[ \t]*([A-Za-z0-9_-]+)[ \t]*=", re.MULTILINE)
_HEADER = re.compile(r"^[ \t]*#*[ \t]*\[\[?([^\[\]\n]+)\]\]?", re.MULTILINE)


@dataclass(frozen=True)
class TemplateSection:
    """A titled group of devkit's top-level keys; ``help`` is prose under the title."""

    title: str
    keys: tuple[TemplateKey, ...]
    help: str = ""


@dataclass(frozen=True)
class ToolTemplate:
    """The tables an installed package registered for ``[tool.<name>]`` (``devkit.config_template``) or for the
    reserved table ``[<name>]`` (``devkit.config_tables``); ``package`` is its distribution, when known."""

    name: str
    tables: tuple[TemplateTable, ...]
    package: str | None = None


def set_entry(container: Container | Table, name: str, value: object) -> None:
    """Set ``name``; a new key goes right after the container's last key-value entry.

    tomlkit appends a new key after the comment lines that follow a table's last entry, where a commented table
    of the template would take the key as its own once uncommented. Without a key-value entry the new key goes
    first. An existing key is replaced in place; another kind of container (an inline table) appends.
    """
    inner = container.value if isinstance(container, Table) else container
    if name in container or not isinstance(inner, Container):
        container[name] = value
        return
    keys = [key for key, item in inner.body if key is not None and not isinstance(item, (Table, AoT))]
    if keys:
        inner._insert_after(keys[-1], name, value)  # tomlkit has no public positional insert
    elif inner.body:
        inner._insert_at(0, name, value)
    else:
        container[name] = value


def _failed(name: str, problem: str, *, group: str = GROUP) -> ConfigTemplateExtensionFailedNotice:
    table = f"[tool.{name}]" if group == GROUP else f"[{name}]"
    return ConfigTemplateExtensionFailedNotice(
        f"config template extension {name} failed: {problem}",
        what_to_report=f"The failure of the {group} entry point {name}; its {table} tables are left out",
    )


def _load_templates(
    group: str, check_name: Callable[[str], str | None]
) -> tuple[list[ToolTemplate], list[AdvisoryError]]:
    """The templates registered under ``group`` in entry-point name order, and a warning for each one that failed.

    ``check_name`` returns why an entry-point name is not accepted, or ``None``.
    """
    found: list[ToolTemplate] = []
    notices: list[AdvisoryError] = []
    for entry in sorted(metadata.entry_points(group=group), key=lambda item: (item.name, item.value)):
        problem = check_name(entry.name)
        if problem is not None:
            notices.append(_failed(entry.name, problem, group=group))
            continue
        try:
            tables = check_tables(entry.load()())
        except Exception as exc:
            notices.append(_failed(entry.name, str(exc) or type(exc).__name__, group=group))
            continue
        dist = getattr(entry, "dist", None)
        found.append(ToolTemplate(entry.name, tables, dist.name if dist is not None else None))
    return found, notices


def load_tool_templates() -> tuple[list[ToolTemplate], list[AdvisoryError]]:
    """The ``[tool.<name>]`` templates of the installed tools, and a warning for each one that failed."""

    def check(name: str) -> str | None:
        return (
            None
            if TOOL_NAME.fullmatch(name)
            else f"the entry-point name is not a [tool.<name>] name: {TOOL_NAME.pattern}"
        )

    return _load_templates(GROUP, check)


def load_reserved_templates(reserved: Collection[str]) -> tuple[list[ToolTemplate], list[AdvisoryError]]:
    """The templates installed packages register for the ``reserved`` top-level tables, and a warning for each
    one that failed or is named after a table that is not reserved."""

    def check(name: str) -> str | None:
        return (
            None if name in reserved else f"the entry-point name is not a reserved table: {', '.join(sorted(reserved))}"
        )

    return _load_templates(RESERVED_GROUP, check)


def _defined(data: dict[str, Any], path: Sequence[str]) -> bool:
    value: object = data
    for part in path:
        if not isinstance(value, dict) or part not in value:
            return False
        value = value[part]
    return True


def _mentioned_tables(text: str) -> set[str]:
    """Dotted names of the table headers in ``text``, commented or not, quotes and spaces dropped."""
    return {re.sub(r"[\s\"']", "", match) for match in _HEADER.findall(text)}


def _devkit_block(text: str, data: dict[str, Any], header: str, sections: Sequence[TemplateSection]) -> list[str]:
    mentioned = set(data) | set(_COMMENTED_KEY.findall(text))
    lines: list[str] = []
    for section in sections:
        missing = [key for key in section.keys if key.name not in mentioned]
        if missing:
            lines += ["", *prose(section.title), *prose(section.help), *(render_key(key) for key in missing)]
    header_lines = prose(header)
    if lines and header_lines[0] not in text:
        lines = ["", *header_lines, *lines]
    return lines


def _insert_top_level(text: str, lines: list[str]) -> str:
    """``text`` with ``lines`` right after its last top-level key, where tomlkit puts a new top-level key."""
    doc = tomlkit.parse(text)
    set_entry(doc, _MARKER, 0)
    marked = tomlkit.dumps(doc)
    line = f"{_MARKER} = 0\n"
    position = marked.index(line)
    after = marked[position + len(line) :]
    block = "\n".join(lines[1:] if position == 0 else lines) + "\n"
    if after and not after.startswith("\n"):
        block += "\n"
    return marked[:position] + block + after


def add_template(
    text: str,
    header: str,
    sections: Sequence[TemplateSection],
    tools: Sequence[ToolTemplate],
    *,
    reserved: Sequence[ToolTemplate] = (),
) -> tuple[str, list[str]]:
    """``text`` (valid TOML) with the template parts it lacks, and the names of the keys and tables added.

    ``header`` is the prose that opens devkit's part, added with it when ``text`` does not contain it yet;
    ``reserved`` holds the templates of reserved top-level tables, rendered before the ``tools`` without an intro.
    """
    data = tomllib.loads(text)
    added: list[str] = []
    block = _devkit_block(text, data, header, sections)
    if block:
        added += [key.name for section in sections for key in section.keys if render_key(key) in block]
        text = _insert_top_level(text, block)
    mentioned = _mentioned_tables(text)
    chunks: list[str] = []
    for owner in reserved:
        for table in owner.tables:
            name = table_name((owner.name,), table)
            if name in mentioned or _defined(data, (owner.name, *table.path)):
                continue
            mentioned.add(name)
            added.append(name)
            chunks.append(render_table((owner.name,), table))
    for tool in tools:
        tables: list[str] = []
        for table in tool.tables:
            name = table_name(("tool", tool.name), table)
            if name in mentioned or _defined(data, ("tool", tool.name, *table.path)):
                continue
            mentioned.add(name)
            added.append(name)
            tables.append(render_table(("tool", tool.name), table))
        if tables:
            owner = f" of {tool.package}" if tool.package else ""
            intro = prose(f"[tool.{tool.name}]: the settings{owner}; devkit passes [tool.*] tables through unread.")
            lead = "" if intro[0] in text else "\n".join(intro) + "\n"
            chunks.append(lead + "\n".join(tables))
    if chunks:
        text = text.rstrip("\n") + "\n\n" + "\n".join(chunks)
    return text, added
