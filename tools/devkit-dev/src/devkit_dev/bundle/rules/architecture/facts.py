"""Architecture-owned unresolved imports and references; no package policy is extracted."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import cast

from devkit_agt.features.rules import (
    FileFactsDescriptor,
    FileFactsSource,
    JsonValue,
    capture_facts_dependency,
)


@dataclass(frozen=True, slots=True)
class Alias:
    name: str
    asname: str | None


@dataclass(frozen=True, slots=True)
class Import:
    kind: str
    module: str | None
    level: int
    names: tuple[Alias, ...]
    lineno: int


@dataclass(frozen=True, slots=True)
class Reference:
    kind: str
    name: str
    context: str | None
    lineno: int


@dataclass(frozen=True, slots=True)
class ArchitectureFacts:
    imports: tuple[Import, ...]
    attributes: tuple[tuple[str, tuple[str, ...], int], ...]
    scan: tuple[Import | Reference, ...]
    facade: tuple[Import, ...]


def _import(node: ast.Import | ast.ImportFrom) -> Import:
    return Import(
        "from" if isinstance(node, ast.ImportFrom) else "import",
        node.module if isinstance(node, ast.ImportFrom) else None,
        node.level if isinstance(node, ast.ImportFrom) else 0,
        tuple(Alias(alias.name, alias.asname) for alias in node.names),
        node.lineno,
    )


def extract(source: FileFactsSource) -> ArchitectureFacts:
    imports = tuple(
        _import(node)
        for node in source.get_python_nodes(ast.Import, ast.ImportFrom)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    dynamic_names = {"__import__"}
    for node in imports:
        if node.kind == "from" and node.module == "importlib":
            dynamic_names.update(alias.asname or alias.name for alias in node.names if alias.name == "import_module")
    attributes = []
    for node in source.get_python_nodes(ast.Attribute):
        assert isinstance(node, ast.Attribute)
        parts = []
        value = node
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            attributes.append((value.id, tuple(reversed(parts)), node.lineno))
    scan: list[Import | Reference] = []
    for node in source.get_python_nodes(ast.Import, ast.ImportFrom, ast.Call, ast.Constant):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            scan.append(_import(node))
        elif isinstance(node, ast.Call):
            function = node.func
            dynamic = (isinstance(function, ast.Name) and function.id in dynamic_names) or (
                isinstance(function, ast.Attribute) and function.attr == "import_module"
            )
            if dynamic and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                context = next((keyword.value for keyword in node.keywords if keyword.arg == "package"), None)
                if context is None and len(node.args) > 1:
                    context = node.args[1]
                scan.append(
                    Reference(
                        "dynamic",
                        node.args[0].value,
                        context.value if isinstance(context, ast.Constant) and isinstance(context.value, str) else None,
                        node.lineno,
                    )
                )
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and ":" in node.value:
            name = node.value.split(":", 1)[0]
            if all(part.isidentifier() for part in name.split(".")):
                scan.append(Reference("entrypoint", name, None, node.lineno))
    facade = tuple(
        _import(node) for node in source.get_python_ast().body if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    return ArchitectureFacts(imports, tuple(attributes), tuple(scan), facade)


def _encode_import(node: Import) -> JsonValue:
    return [node.kind, node.module, node.level, [[a.name, a.asname] for a in node.names], node.lineno]


def encode(facts: ArchitectureFacts) -> JsonValue:
    return [
        [_encode_import(node) for node in facts.imports],
        [[head, list(parts), line] for head, parts, line in facts.attributes],
        [
            _encode_import(node) if isinstance(node, Import) else [node.kind, node.name, node.context, node.lineno]
            for node in facts.scan
        ],
        [_encode_import(node) for node in facts.facade],
    ]


def _list(value: JsonValue, length: int | None = None) -> list:
    if not isinstance(value, list) or (length is not None and len(value) != length):
        raise ValueError("invalid architecture facts sequence")
    return value


def _str(value: JsonValue, *, optional: bool = False) -> str | None:
    if (value is None and optional) or isinstance(value, str):
        return value
    raise ValueError("invalid architecture facts string")


def _int(value: JsonValue) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("invalid architecture facts number")
    return value


def _decode_import(value: JsonValue) -> Import:
    kind, module, level, aliases, line = _list(value, 5)
    if kind not in {"import", "from"}:
        raise ValueError("invalid import kind")
    names = []
    for alias in _list(aliases):
        name, asname = _list(alias, 2)
        names.append(Alias(cast(str, _str(name)), _str(asname, optional=True)))
    return Import(kind, _str(module, optional=True), _int(level), tuple(names), _int(line))


def decode(value: JsonValue) -> ArchitectureFacts:
    imports, attributes, scan, facade = _list(value, 4)
    attrs = []
    for value in _list(attributes):
        head, parts, line = _list(value, 3)
        attrs.append((cast(str, _str(head)), tuple(cast(str, _str(p)) for p in _list(parts)), _int(line)))
    refs = []
    for value in _list(scan):
        row = _list(value)
        if row and row[0] in {"import", "from"}:
            refs.append(_decode_import(row))
        else:
            kind, name, context, line = _list(row, 4)
            if kind not in {"dynamic", "entrypoint"}:
                raise ValueError("invalid reference kind")
            refs.append(Reference(kind, cast(str, _str(name)), _str(context, optional=True), _int(line)))
    return ArchitectureFacts(
        tuple(_decode_import(v) for v in _list(imports)),
        tuple(attrs),
        tuple(refs),
        tuple(_decode_import(v) for v in _list(facade)),
    )


_SOURCE = capture_facts_dependency("RULE-architecture.facts", __file__, module_name=__name__)


def descriptor(rule_name: str, rule_file: str) -> FileFactsDescriptor[ArchitectureFacts]:
    return FileFactsDescriptor(
        "RULE-architecture",
        1,
        (capture_facts_dependency("RULE-architecture.rule", rule_file, module_name=rule_name), _SOURCE),
        extract,
        encode,
        decode,
    )
