"""Execution-boundary syntax: expressions, binding operations, declarations and execution scopes."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any

from devkit_agt.features.rules import FileFactsDescriptor, FileFactsSource, JsonValue, capture_facts_dependency


@dataclass(frozen=True, slots=True)
class Expression:
    kind: str
    name: str = ""
    value: Expression | None = None
    args: tuple[Expression, ...] = ()
    keywords: tuple[Expression, ...] = ()
    lineno: int = 1


@dataclass(frozen=True, slots=True)
class Parameter:
    arg: str
    annotation: Expression | None


@dataclass(frozen=True, slots=True)
class Assignment:
    targets: tuple[Expression, ...]
    value: Expression | None
    annotation: Expression | None = None


@dataclass(frozen=True, slots=True)
class Import:
    module: str | None
    level: int
    names: tuple[tuple[str, str | None], ...]


@dataclass(frozen=True, slots=True)
class Scope:
    kind: str
    name: str
    lineno: int
    bases: tuple[Expression, ...]
    parameters: tuple[Parameter, ...]
    variadics: tuple[Parameter, ...]
    returns: bool
    decorators: tuple[Expression, ...]
    declarations: tuple[Scope, ...]
    aliases: tuple[Assignment, ...]
    assignments: tuple[Assignment, ...]
    calls: tuple[Expression, ...]
    all_calls: tuple[Expression, ...]
    imports: tuple[Import, ...]
    nested: tuple[Scope, ...]


def expression(node: ast.AST, expressions: dict[ast.AST, Expression]) -> Expression:
    if node not in expressions:
        expressions[node] = _expression(node, expressions)
    return expressions[node]


def _expression(node: ast.AST, expressions: dict[ast.AST, Expression]) -> Expression:
    line = getattr(node, "lineno", 1)
    if isinstance(node, ast.Name):
        return Expression("name", node.id, lineno=line)
    if isinstance(node, ast.Attribute):
        return Expression("attribute", node.attr, expression(node.value, expressions), lineno=line)
    if isinstance(node, ast.Call):
        return Expression(
            "call",
            value=expression(node.func, expressions),
            args=tuple(expression(a, expressions) for a in node.args),
            keywords=tuple(expression(k.value, expressions) for k in node.keywords),
            lineno=line,
        )
    if isinstance(node, ast.Await | ast.Subscript):
        return Expression(
            "await" if isinstance(node, ast.Await) else "subscript",
            value=expression(node.value, expressions),
            lineno=line,
        )
    return Expression("unknown", lineno=line)


def annotation(node: ast.AST | None, expressions: dict[ast.AST, Expression]) -> Expression | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            node = ast.parse(node.value, mode="eval").body
        except SyntaxError:
            return Expression("unknown")
    return expression(node, expressions)


def _walk(tree: ast.AST):
    yield tree
    for child in ast.iter_child_nodes(tree):
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            yield from _walk(child)


def _nested(tree: ast.AST):
    for child in ast.iter_child_nodes(tree):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            yield child
        elif not isinstance(child, ast.ClassDef):
            yield from _nested(child)


def _assignment(node: ast.Assign | ast.AnnAssign, expressions: dict[ast.AST, Expression]) -> Assignment:
    return Assignment(
        tuple(expression(t, expressions) for t in node.targets)
        if isinstance(node, ast.Assign)
        else (expression(node.target, expressions),),
        expression(node.value, expressions) if node.value is not None else None,
        annotation(node.annotation, expressions) if isinstance(node, ast.AnnAssign) else None,
    )


def _scope(tree: ast.AST, scopes: dict[ast.AST, Scope], expressions: dict[ast.AST, Expression]) -> Scope:
    if tree not in scopes:
        scopes[tree] = _extract_scope(tree, scopes, expressions)
    return scopes[tree]


def _extract_scope(tree: ast.AST, scopes: dict[ast.AST, Scope], expressions: dict[ast.AST, Expression]) -> Scope:
    body = tree.body if isinstance(tree, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) else []
    args = tree.args if isinstance(tree, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) else None
    nodes = tuple(_walk(tree))
    all_nodes = tuple(ast.walk(tree))
    imports = []
    for node in all_nodes:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(
                Import(
                    node.module or "" if isinstance(node, ast.ImportFrom) else None,
                    node.level if isinstance(node, ast.ImportFrom) else 0,
                    tuple((a.name, a.asname) for a in node.names),
                )
            )
    # Scope records contain execution summaries rather than a serializable Python tree.
    return Scope(
        "class"
        if isinstance(tree, ast.ClassDef)
        else "async"
        if isinstance(tree, ast.AsyncFunctionDef)
        else "function"
        if isinstance(tree, ast.FunctionDef)
        else "lambda"
        if isinstance(tree, ast.Lambda)
        else "module",
        getattr(tree, "name", ""),
        getattr(tree, "lineno", 1),
        tuple(expression(b, expressions) for b in tree.bases) if isinstance(tree, ast.ClassDef) else (),
        tuple(
            Parameter(a.arg, annotation(a.annotation, expressions))
            for a in [*args.posonlyargs, *args.args, *args.kwonlyargs]
        )
        if args
        else (),
        tuple(Parameter(a.arg, annotation(a.annotation, expressions)) for a in (args.vararg, args.kwarg) if a)
        if args
        else (),
        getattr(tree, "returns", None) is not None,
        tuple(expression(d, expressions) for d in getattr(tree, "decorator_list", [])),
        tuple(
            _scope(n, scopes, expressions)
            for n in body
            if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        ),
        tuple(_assignment(n, expressions) for n in body if isinstance(n, ast.Assign)),
        tuple(_assignment(n, expressions) for n in nodes if isinstance(n, (ast.Assign, ast.AnnAssign))),
        tuple(expression(n, expressions) for n in nodes if isinstance(n, ast.Call)),
        tuple(expression(n, expressions) for n in all_nodes if isinstance(n, ast.Call)),
        tuple(imports),
        tuple(_scope(n, scopes, expressions) for n in _nested(tree)),
    )


def extract(source: FileFactsSource) -> Scope:
    return _scope(source.get_python_ast(), {}, {})


def encode(scope: Scope) -> JsonValue:
    # Expressions are one flat post-order record stream, so references always point backward and decoding is a
    # single pass without per-record containers: kind, name, receiver, line, then a call's counted arguments.
    expressions: list[JsonValue] = []
    scopes: list[JsonValue] = []
    expr_ids: dict[int, int] = {}
    scope_ids: dict[int, int] = {}

    def expr(e: Expression | None) -> int | None:
        if e is None:
            return None
        if id(e) not in expr_ids:
            receiver = expr(e.value)
            args = [expr(a) for a in e.args]
            keywords = [expr(k) for k in e.keywords]
            expr_ids[id(e)] = len(expr_ids)
            expressions.extend((e.kind, e.name, receiver, e.lineno))
            if e.kind == "call":
                expressions.extend((len(args), *args, len(keywords), *keywords))
            elif args or keywords:
                raise ValueError("only calls carry arguments")
        return expr_ids[id(e)]

    def assignment(a: Assignment) -> JsonValue:
        return [[expr(t) for t in a.targets], expr(a.value), expr(a.annotation)]

    def visit(s: Scope) -> int:
        if id(s) not in scope_ids:
            index = len(scopes)
            scope_ids[id(s)] = index
            scopes.append(None)
            scopes[index] = [
                s.kind,
                s.name,
                s.lineno,
                [expr(b) for b in s.bases],
                [[a.arg, expr(a.annotation)] for a in s.parameters],
                [[a.arg, expr(a.annotation)] for a in s.variadics],
                s.returns,
                [expr(d) for d in s.decorators],
                [visit(d) for d in s.declarations],
                [assignment(a) for a in s.aliases],
                [assignment(a) for a in s.assignments],
                [expr(c) for c in s.calls],
                [expr(c) for c in s.all_calls],
                [[i.module, i.level, [[name, alias] for name, alias in i.names]] for i in s.imports],
                [visit(n) for n in s.nested],
            ]
        return scope_ids[id(s)]

    visit(scope)
    return [expressions, scopes]


def _seq(value: Any, size: int | None = None) -> list[Any]:
    if type(value) is not list or (size is not None and len(value) != size):
        raise ValueError("invalid execution facts sequence")
    return value


def _str(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("invalid execution facts string")
    return value


def _int(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("invalid execution facts number")
    return value


_EXPRESSION_KINDS = frozenset({"name", "attribute", "call", "await", "subscript", "unknown"})
_RECEIVER_KINDS = frozenset({"attribute", "call", "await", "subscript"})


def _expressions(records: list[Any]) -> list[Expression]:
    """Decode the flat stream in one pass; a record names only earlier records, so no cycle is encodable."""
    built: list[Expression] = []
    position, end = 0, len(records)

    def reference(value: Any) -> Expression:
        if type(value) is not int or not 0 <= value < len(built):
            raise ValueError("invalid expression reference")
        return built[value]

    def counted() -> tuple[Expression, ...]:
        nonlocal position
        if position >= end or position + 1 + _int(records[position]) > end:
            raise ValueError("truncated execution expression")
        start, position = position + 1, position + 1 + records[position]
        return tuple([reference(item) for item in records[start:position]])

    while position < end:
        if position + 4 > end:
            raise ValueError("truncated execution expression")
        kind, name, receiver, line = records[position : position + 4]
        position += 4
        if kind not in _EXPRESSION_KINDS or not isinstance(name, str):
            raise ValueError("invalid execution expression")
        if kind in {"name", "attribute"}:
            if not name.isidentifier():
                raise ValueError("invalid expression binding")
        elif name:
            raise ValueError("unexpected expression name")
        if type(line) is not int or line < 1:
            raise ValueError("invalid expression location")
        if receiver is None:
            if kind in _RECEIVER_KINDS:
                raise ValueError("missing expression receiver")
            value = None
        elif kind in {"name", "unknown"}:
            raise ValueError("unexpected expression receiver")
        else:
            value = reference(receiver)
        if kind == "call":
            args = counted()
            built.append(Expression(kind, name, value, args, counted(), line))
        else:
            built.append(Expression(kind, name, value, lineno=line))
    return built


def decode(value: JsonValue) -> Scope:
    expr_rows, scope_rows = _seq(value, 2)
    expressions = _expressions(_seq(expr_rows))
    scope_rows = _seq(scope_rows)
    scopes: dict[int, Scope] = {}
    active_scope: set[int] = set()

    def expr(index: Any) -> Expression:
        if type(index) is not int or not 0 <= index < len(expressions):
            raise ValueError("invalid expression reference")
        return expressions[index]

    def param(value: Any) -> Parameter:
        name, a = _seq(value, 2)
        return Parameter(_str(name), expr(a) if a is not None else None)

    def assign(value: Any) -> Assignment:
        targets, v, a = _seq(value, 3)
        result = Assignment(
            tuple(expr(t) for t in _seq(targets)),
            expr(v) if v is not None else None,
            expr(a) if a is not None else None,
        )
        if not result.targets or (result.value is None and result.annotation is None):
            raise ValueError("invalid assignment operation")
        if any(target.kind not in {"name", "attribute", "subscript", "unknown"} for target in result.targets):
            raise ValueError("invalid assignment destination")
        return result

    def visit(index: Any) -> Scope:
        index = _int(index)
        if index >= len(scope_rows) or index in active_scope:
            raise ValueError("invalid scope reference")
        if index not in scopes:
            active_scope.add(index)
            (
                kind,
                name,
                line,
                bases,
                parameters,
                variadics,
                returns,
                decorators,
                declarations,
                aliases,
                assignments,
                calls,
                all_calls,
                imports,
                nested,
            ) = _seq(scope_rows[index], 15)
            if kind not in {"module", "class", "function", "async", "lambda"} or type(returns) is not bool:
                raise ValueError("invalid execution scope")
            imps = []
            for value in _seq(imports):
                module, level, names = _seq(value, 3)
                imps.append(
                    Import(
                        _str(module) if module is not None else None,
                        _int(level),
                        tuple(
                            (_str(n), _str(a) if a is not None else None) for n, a in (_seq(p, 2) for p in _seq(names))
                        ),
                    )
                )
            scopes[index] = Scope(
                kind,
                _str(name),
                _int(line),
                tuple(expr(b) for b in _seq(bases)),
                tuple(param(a) for a in _seq(parameters)),
                tuple(param(a) for a in _seq(variadics)),
                returns,
                tuple(expr(d) for d in _seq(decorators)),
                tuple(visit(d) for d in _seq(declarations)),
                tuple(assign(a) for a in _seq(aliases)),
                tuple(assign(a) for a in _seq(assignments)),
                tuple(expr(c) for c in _seq(calls)),
                tuple(expr(c) for c in _seq(all_calls)),
                tuple(imps),
                tuple(visit(n) for n in _seq(nested)),
            )
            result = scopes[index]
            if result.lineno < 1:
                raise ValueError("invalid scope location")
            if kind in {"class", "function", "async"}:
                if not result.name.isidentifier():
                    raise ValueError("invalid declaration name")
            elif result.name:
                raise ValueError("unexpected scope name")
            if kind != "class" and result.bases:
                raise ValueError("unexpected class bases")
            if kind not in {"function", "async", "lambda"} and (result.parameters or result.variadics):
                raise ValueError("unexpected scope parameters")
            if kind not in {"function", "async"} and result.returns:
                raise ValueError("unexpected return annotation")
            if kind in {"module", "lambda"} and result.decorators:
                raise ValueError("unexpected scope decorators")
            if any(not p.arg.isidentifier() for p in (*result.parameters, *result.variadics)):
                raise ValueError("invalid parameter name")
            if any(d.kind not in {"class", "function", "async"} for d in result.declarations):
                raise ValueError("invalid declaration role")
            if any(n.kind not in {"function", "async", "lambda"} for n in result.nested):
                raise ValueError("invalid nested execution scope")
            if any(c.kind != "call" for c in (*result.calls, *result.all_calls)):
                raise ValueError("non-call in execution call collection")
            if any(a.annotation is not None or a.value is None for a in result.aliases):
                raise ValueError("invalid facade assignment")
            active_scope.remove(index)
        return scopes[index]

    result = visit(0)
    if result.kind != "module":
        raise ValueError("execution facts root must be a module")
    # Unreferenced rows must also obey the codec, even when judgment never visits them.
    for index in range(len(scope_rows)):
        visit(index)
    return result


SOURCE = capture_facts_dependency("RULE-usecase-boundaries.facts", __file__, module_name=__name__)


def descriptor(module_name: str, filename: str) -> FileFactsDescriptor[Scope]:
    return FileFactsDescriptor(
        "RULE-usecase-boundaries",
        2,
        (capture_facts_dependency("RULE-usecase-boundaries.rule", filename, module_name=module_name), SOURCE),
        extract,
        encode,
        decode,
    )
