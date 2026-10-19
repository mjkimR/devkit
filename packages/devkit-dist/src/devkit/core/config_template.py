"""Commented templates of ``.devkit/config.toml``: every key a project can set, at its default.

A tool built on devkit describes its ``[tool.<name>]`` tables as ``TemplateTable`` values and registers a
callable returning them under the ``devkit.config_template`` entry-point group, named ``<name>``. ``devkit config
template``, and the selection command that creates the file, render them below the project's tables; devkit
renders its own top-level keys with the same ``TemplateKey``.

Prose is commented twice (``##``), keys and table headers once (``#``), so uncommenting a whole table in an editor
(which removes one ``#`` per line) yields valid TOML with the prose still a comment. A key left commented keeps its
default. ``uncomment`` does what the editor does, so a tool's tests can check that its template reads back as its
defaults. Rendering never reads the project: a template only shows what an installed tool accepts.
"""

from __future__ import annotations

import re
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass

BARE_KEY = re.compile(r"[A-Za-z0-9_-]+\Z")
PROSE_WIDTH = 116


@dataclass(frozen=True)
class TemplateKey:
    """One key: ``default`` as the reader applies it, or ``None`` when it is unset by default.

    A key unset by default shows ``example``, which must then be given, marked as one; its ``help`` says what
    applies while it is unset (``"unset: ..."``). ``kind`` names the accepted values (for example ``"integer from 1
    to 300"``); empty, it is derived from the value shown. ``help`` says what the key does.
    """

    name: str
    default: object = None
    help: str = ""
    kind: str = ""
    example: object = None


@dataclass(frozen=True)
class TemplateTable:
    """One table: ``path`` holds its keys below ``[tool.<name>]`` (``("scope",)`` is ``[tool.<name>.scope]``).

    ``array`` renders an array of tables (``[[...]]``): there is none by default, so its values are examples.
    """

    keys: tuple[TemplateKey, ...]
    path: tuple[str, ...] = ()
    help: str = ""
    array: bool = False


def _toml(value: object) -> str:
    import tomlkit  # only commands that render a template pay for the import

    return tomlkit.item(value).as_string()


def _kind(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (list, tuple)):
        return "array"
    return "table"


def prose(text: str) -> list[str]:
    """``text`` as ``##`` comment lines of at most ``PROSE_WIDTH`` characters of text."""
    return [f"## {line}" for line in textwrap.wrap(" ".join(text.split()), PROSE_WIDTH)]


def render_key(key: TemplateKey, *, indent: str = "", example: bool = False) -> str:
    """The commented ``name = value  # kind; help`` line of ``key``; ``example`` marks a key of an array of tables.

    A key unset by default outside an array of tables shows its example as ``example; kind; help``.
    """
    unset = key.default is None
    shown = key.example if unset else key.default
    note = key.kind or _kind(shown)
    if unset and not example:
        note = f"example; {note}"
    if key.help.strip():
        note += f"; {' '.join(key.help.split())}"
    return f"# {indent}{key.name} = {_toml(shown)}  # {note}"


def table_name(prefix: Sequence[str], table: TemplateTable) -> str:
    """The dotted name of ``table`` below ``prefix`` (``tool.spec.scope``)."""
    return ".".join((*prefix, *table.path))


def render_table(prefix: Sequence[str], table: TemplateTable) -> str:
    """The commented ``table`` below ``prefix`` (``("tool", "spec")``): its prose, its header and its keys."""
    name = table_name(prefix, table)
    note = " None by default; the values below are examples." if table.array else ""
    lines = [
        *prose(table.help + note),
        f"# [[{name}]]" if table.array else f"# [{name}]",
        *(render_key(key, indent="  ", example=table.array) for key in table.keys),
    ]
    return "\n".join(lines) + "\n"


def render_tool_template(name: str, tables: Sequence[TemplateTable]) -> str:
    """Every table of the tool ``name`` (``[tool.<name>...]``), blank-line separated."""
    return "\n".join(render_table(("tool", name), table) for table in check_tables(tables))


def check_tables(value: object) -> tuple[TemplateTable, ...]:
    """``value`` as the tables of a template; ``ValueError`` naming the first problem when it is not one.

    Table paths and key names are bare TOML keys, unique where they meet; every key shows a TOML value (its
    default, or the example of a key unset by default).
    """
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, TemplateTable) for item in value):
        raise ValueError(f"returned {type(value).__name__}, expected a list of TemplateTable")
    seen: set[tuple[str, ...]] = set()
    for table in value:
        where = ".".join(table.path) or "the top table"
        if not all(isinstance(part, str) and BARE_KEY.match(part) for part in table.path):
            raise ValueError(f"table path {table.path!r} is not made of bare TOML keys")
        if table.path in seen:
            raise ValueError(f"table {where} is listed twice")
        seen.add(table.path)
        if not table.keys or not all(isinstance(key, TemplateKey) for key in table.keys):
            raise ValueError(f"table {where}: expected one TemplateKey or more")
        names = [key.name for key in table.keys]
        if len(set(names)) != len(names):
            raise ValueError(f"table {where}: a key is listed twice")
        for key in table.keys:
            if not isinstance(key.name, str) or not BARE_KEY.match(key.name):
                raise ValueError(f"table {where}: key name {key.name!r} is not a bare TOML key")
            if key.default is None and key.example is None:
                raise ValueError(f"table {where}: key {key.name} has neither a default nor an example")
            try:
                render_key(key)
            except Exception as exc:  # tomlkit refuses values TOML cannot hold
                raise ValueError(f"table {where}: key {key.name}: {exc}") from exc
    return tuple(value)


def uncomment(text: str) -> str:
    """``text`` with one leading ``#`` removed from every line that starts with one, as an editor uncomments."""
    return "".join(line[1:] if line.startswith("#") else line for line in text.splitlines(keepends=True))
