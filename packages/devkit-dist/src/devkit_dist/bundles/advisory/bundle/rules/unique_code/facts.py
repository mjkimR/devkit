"""Advisory-owned class declarations, string expressions and scoped candidate calls."""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from devkit_agt.features.rules import FileFactsSource, JsonValue, capture_facts_dependency


@dataclass(frozen=True, slots=True)
class Expression:
    kind: str
    name: str = ""
    parent: Expression | None = None


@dataclass(frozen=True, slots=True)
class Import:
    module: str | None
    level: int
    aliases: tuple[tuple[str, str | None], ...]


@dataclass(frozen=True, slots=True)
class Class:
    name: str
    bases: tuple[Expression, ...]
    codes: tuple[tuple[Expression, int], ...]


@dataclass(frozen=True, slots=True)
class Call:
    function: Expression
    code: Expression | None
    line: int
    scopes: tuple[tuple[Import, ...], ...]


@dataclass(frozen=True, slots=True)
class AdvisoryFacts:
    classes: tuple[Class, ...]
    constants: tuple[tuple[str, str], ...]
    imports: tuple[Import, ...]
    calls: tuple[Call, ...]


def expression(node: ast.AST) -> Expression:
    if isinstance(node, ast.Name):
        return Expression("name", node.id)
    if isinstance(node, ast.Attribute):
        return Expression("attribute", node.attr, expression(node.value))
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return Expression("string", node.value)
    return Expression("unknown")


def _import(node: ast.Import | ast.ImportFrom) -> Import:
    return Import(
        node.module or "" if isinstance(node, ast.ImportFrom) else None,
        node.level if isinstance(node, ast.ImportFrom) else 0,
        tuple((alias.name, alias.asname) for alias in node.names),
    )


def _top_level(body: list[ast.stmt]) -> Iterator[ast.stmt]:
    for node in body:
        yield node
        if isinstance(node, ast.If | ast.With):
            yield from _top_level(node.body)
            if isinstance(node, ast.If):
                yield from _top_level(node.orelse)
        elif isinstance(node, ast.Try):
            for block in (node.body, *(handler.body for handler in node.handlers), node.orelse, node.finalbody):
                yield from _top_level(block)


def _function_imports(tree: ast.AST) -> tuple[Import, ...]:
    found = []

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Import | ast.ImportFrom):
                found.append(_import(child))
            elif not isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Lambda):
                visit(child)

    visit(tree)
    return tuple(found)


def extract(source: FileFactsSource) -> AdvisoryFacts:
    tree = source.get_python_ast()
    classes = []
    constants = []
    imports = []
    for node in _top_level(tree.body):
        if isinstance(node, ast.ClassDef):
            codes = []
            for statement in node.body:
                targets = statement.targets if isinstance(statement, ast.Assign) else []
                if isinstance(statement, ast.AnnAssign) and statement.value is not None:
                    targets = [statement.target]
                value = statement.value if isinstance(statement, ast.Assign | ast.AnnAssign) else None
                if value is not None and any(isinstance(t, ast.Name) and t.id == "code" for t in targets):
                    codes.append((expression(value), statement.lineno))
            classes.append(Class(node.name, tuple(expression(base) for base in node.bases), tuple(codes)))
        elif isinstance(node, ast.Assign | ast.AnnAssign) and isinstance(node.value, ast.Constant):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and isinstance(node.value.value, str):
                    constants.append((target.id, node.value.value))
        elif isinstance(node, ast.Import | ast.ImportFrom):
            imports.append(_import(node))
    calls = []

    def visit(node: ast.AST, scopes: tuple[tuple[Import, ...], ...]) -> None:
        for child in ast.iter_child_nodes(node):
            inner = scopes
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                inner = (*scopes, _function_imports(child))
            elif isinstance(child, ast.Call):
                keyword = next((k for k in child.keywords if k.arg == "code"), None)
                # Calls without code= never produce declarations in the existing judgment.
                if keyword is not None:
                    calls.append(Call(expression(child.func), expression(keyword.value), child.lineno, scopes))
            visit(child, inner)

    visit(tree, ())
    return AdvisoryFacts(tuple(classes), tuple(constants), tuple(imports), tuple(calls))


def _expr_wire(expr: Expression | None) -> JsonValue:
    return None if expr is None else [expr.kind, expr.name, _expr_wire(expr.parent)]


def _import_wire(value: Import) -> JsonValue:
    return [value.module, value.level, [[name, alias] for name, alias in value.aliases]]


def encode(facts: AdvisoryFacts) -> JsonValue:
    return [
        [
            [c.name, [_expr_wire(b) for b in c.bases], [[_expr_wire(e), line] for e, line in c.codes]]
            for c in facts.classes
        ],
        [[name, value] for name, value in facts.constants],
        [_import_wire(i) for i in facts.imports],
        [
            [_expr_wire(c.function), _expr_wire(c.code), c.line, [[_import_wire(i) for i in s] for s in c.scopes]]
            for c in facts.calls
        ],
    ]


def _sequence(value: Any, length: int | None = None) -> list[Any]:
    if type(value) is not list or (length is not None and len(value) != length):
        raise ValueError("invalid advisory facts sequence")
    return value


def _string(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("invalid advisory facts string")
    return value


def _number(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("invalid advisory facts number")
    return value


def _expr(value: Any) -> Expression:
    kind, name, parent = _sequence(value, 3)
    if kind not in {"name", "attribute", "string", "unknown"}:
        raise ValueError("invalid advisory expression")
    name = _string(name)
    if kind == "attribute" and parent is None:
        raise ValueError("missing advisory attribute parent")
    if kind != "attribute" and parent is not None:
        raise ValueError("unexpected advisory expression parent")
    if kind in {"name", "attribute"} and not name.isidentifier():
        raise ValueError("invalid advisory expression binding")
    if kind == "unknown" and name:
        raise ValueError("unexpected unknown advisory expression name")
    return Expression(kind, name, _expr(parent) if parent is not None else None)


def _imp(value: Any) -> Import:
    module, level, aliases = _sequence(value, 3)
    return Import(
        _string(module) if module is not None else None,
        _number(level),
        tuple(
            (_string(name), _string(alias) if alias is not None else None)
            for name, alias in (_sequence(a, 2) for a in _sequence(aliases))
        ),
    )


def decode(value: JsonValue) -> AdvisoryFacts:
    classes, constants, imports, calls = _sequence(value, 4)
    result = AdvisoryFacts(
        tuple(
            Class(
                _string(name),
                tuple(_expr(b) for b in _sequence(bases)),
                tuple((_expr(e), _number(line)) for e, line in (_sequence(c, 2) for c in _sequence(codes))),
            )
            for name, bases, codes in (_sequence(c, 3) for c in _sequence(classes))
        ),
        tuple((_string(n), _string(v)) for n, v in (_sequence(c, 2) for c in _sequence(constants))),
        tuple(_imp(i) for i in _sequence(imports)),
        tuple(
            Call(
                _expr(function),
                _expr(code) if code is not None else None,
                _number(line),
                tuple(tuple(_imp(i) for i in _sequence(s)) for s in _sequence(scopes)),
            )
            for function, code, line, scopes in (_sequence(c, 4) for c in _sequence(calls))
        ),
    )

    if any(not c.name.isidentifier() or any(line < 1 for _, line in c.codes) for c in result.classes):
        raise ValueError("invalid advisory class declaration")
    if any(not name.isidentifier() for name, _ in result.constants):
        raise ValueError("invalid advisory constant binding")
    if any(c.code is None or c.line < 1 for c in result.calls):
        raise ValueError("invalid advisory candidate call")
    return result


SOURCE = capture_facts_dependency("RULE-advisory-unique-code.facts", __file__, module_name=__name__)
