"""Check explicit execution boundaries without importing product modules."""

from __future__ import annotations

import ast
import importlib.util
import tomllib
from dataclasses import dataclass
from pathlib import Path

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, WorkspaceCache
from devkit_agt.features.rules.services.builtins.base import BaseRule

BASE = "devkit_core.base.usecase.BaseUseCase"
TRANSPORTS = {"cli", "mcp", "adapters"}
Function = ast.FunctionDef | ast.AsyncFunctionDef


def _walk(tree: ast.AST):
    """Walk one execution scope, excluding nested declarations."""
    yield tree
    for child in ast.iter_child_nodes(tree):
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            yield from _walk(child)


@dataclass
class Module:
    name: str
    path: str
    layer: str | None
    tree: ast.Module
    package: bool
    bindings: dict[str, str]


@dataclass(frozen=True)
class Value:
    symbol: str
    instance: bool = False


def _attribute(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and (parent := _attribute(node.value)):
        return f"{parent}.{node.attr}"
    return None


def _imports(module: Module, tree: ast.AST, cache: WorkspaceCache | None = None) -> dict[str, str]:
    bindings: dict[str, str] = {}
    if cache is not None:
        nodes = cache.get_python_nodes(module.path, ast.Import, ast.ImportFrom)
    else:
        nodes = tuple(node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                bindings[alias.asname or alias.name.split(".")[0]] = (
                    alias.name if alias.asname else alias.name.split(".")[0]
                )
        elif isinstance(node, ast.ImportFrom):
            name = node.module or ""
            if node.level:
                context = module.name if module.package else module.name.rpartition(".")[0]
                try:
                    name = importlib.util.resolve_name("." * node.level + name, context)
                except ImportError:
                    continue
            for alias in node.names:
                bindings[alias.asname or alias.name] = f"{name}.{alias.name}"
    return bindings


class Index:
    def __init__(self, root: Path, config: dict, cache: WorkspaceCache) -> None:
        self.modules: dict[str, Module] = {}
        self.definitions: dict[str, ast.ClassDef | Function] = {}
        for package in config["packages"]:
            source = root / package["root"]
            for path in sorted(source.rglob("*.py")):
                relative = path.relative_to(source).with_suffix("").parts
                if relative[0] in package.get("data_roots", []) or "tests" in relative:
                    continue
                parts = relative[:-1] if relative[-1] == "__init__" else relative
                name = ".".join((package["namespace"], *parts))
                layer = parts[2] if len(parts) > 2 and parts[0] == "features" else None
                if parts and parts[0] == "adapters":
                    layer = "adapters"
                module = Module(
                    name,
                    path.relative_to(root).as_posix(),
                    layer,
                    cache.get_python_ast(path),
                    relative[-1] == "__init__",
                    {},
                )
                module.bindings = _imports(module, module.tree, cache)
                self.modules[name] = module
                for statement in module.tree.body:
                    if isinstance(statement, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        self.definitions[f"{name}.{statement.name}"] = statement
                        if isinstance(statement, ast.ClassDef):
                            for method in statement.body:
                                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                    self.definitions[f"{name}.{statement.name}.{method.name}"] = method
                # Explicit aliases in public facades are resolved as well as import re-exports.
                for statement in module.tree.body:
                    if isinstance(statement, ast.Assign) and (value := _attribute(statement.value)):
                        head, _, tail = value.partition(".")
                        target = module.bindings.get(head, f"{name}.{head}") + (f".{tail}" if tail else "")
                        for destination in statement.targets:
                            if isinstance(destination, ast.Name):
                                module.bindings[destination.id] = target

        # Resolve bound-method facade aliases only after every class is indexed.
        for module in self.modules.values():
            for statement in module.tree.body:
                if isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Attribute):
                    value = self.value(statement.value, module, {})
                    if value:
                        for destination in statement.targets:
                            if isinstance(destination, ast.Name):
                                module.bindings[destination.id] = value.symbol

    def resolve(self, symbol: str, trail: frozenset[str] = frozenset()) -> str:
        if symbol in self.definitions or symbol == BASE or symbol in trail:
            return symbol
        name = symbol
        while name not in self.modules and "." in name:
            name = name.rpartition(".")[0]
        if name in self.modules and name != symbol:
            attribute, _, rest = symbol[len(name) + 1 :].partition(".")
            forwarded = self.modules[name].bindings.get(attribute)
            if forwarded:
                return self.resolve(forwarded + (f".{rest}" if rest else ""), trail | {symbol})
        return symbol

    def owner(self, symbol: str) -> Module | None:
        while symbol not in self.modules and "." in symbol:
            symbol = symbol.rpartition(".")[0]
        return self.modules.get(symbol)

    def usecase(self, symbol: str, trail: frozenset[str] = frozenset()) -> bool:
        symbol = self.resolve(symbol)
        if symbol == BASE:
            return True
        definition = self.definitions.get(symbol)
        module = self.owner(symbol)
        if not isinstance(definition, ast.ClassDef) or not module or symbol in trail:
            return False
        for base in definition.bases:
            if isinstance(base, ast.Subscript):
                base = base.value
            name = _attribute(base)
            if name:
                head, _, rest = name.partition(".")
                target = module.bindings.get(head, f"{module.name}.{head}") + (f".{rest}" if rest else "")
                if self.usecase(target, trail | {symbol}):
                    return True
        return False

    def value(self, node: ast.AST, module: Module, bindings: dict[str, Value]) -> Value | None:
        if isinstance(node, ast.Await):
            return self.value(node.value, module, bindings)
        name = _attribute(node)
        if name:
            if name in bindings:
                return bindings[name]
            for prefix in sorted(bindings, key=len, reverse=True):
                if name.startswith(prefix + "."):
                    parent = bindings[prefix]
                    return Value(self.resolve(parent.symbol + name[len(prefix) :]), parent.instance)
            head, _, rest = name.partition(".")
            target = module.bindings.get(head, f"{module.name}.{head}")
            return Value(self.resolve(target + (f".{rest}" if rest else "")))
        if isinstance(node, ast.Attribute):
            receiver = self.value(node.value, module, bindings)
            if receiver:
                return Value(self.resolve(f"{receiver.symbol}.{node.attr}"), receiver.instance)
        if isinstance(node, ast.Call):
            target = self.value(node.func, module, bindings)
            if target and isinstance(self.definitions.get(target.symbol), ast.ClassDef):
                return Value(target.symbol, True)
        return None

    def assignments(self, tree: ast.AST, module: Module, bindings: dict[str, Value]) -> None:
        # A few passes cover aliases and retained `self.operation = Operation(...)`.
        for _ in range(3):
            for node in _walk(tree):
                if isinstance(node, ast.Assign):
                    value = self.value(node.value, module, bindings)
                    if value:
                        for target in node.targets:
                            if name := _attribute(target):
                                bindings[name] = value
                elif isinstance(node, ast.AnnAssign):
                    value = self.value(node.value, module, bindings) if node.value else None
                    value = value or self.annotation(node.annotation, module, bindings)
                    if value and (name := _attribute(node.target)):
                        bindings[name] = value

    def annotation(self, node: ast.AST, module: Module, bindings: dict[str, Value]) -> Value | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            try:
                node = ast.parse(node.value, mode="eval").body
            except SyntaxError:
                return None
        value = self.value(node, module, bindings)
        return (
            Value(value.symbol, True)
            if value and isinstance(self.definitions.get(value.symbol), ast.ClassDef)
            else None
        )


def inspect_usecases(
    root: Path, config_path: str = ".devkit/architecture.toml", *, cache: WorkspaceCache | None = None
) -> list[tuple[str, int, str]]:
    """Check known static execution edges; computed dispatch remains a review responsibility.

    Sources are parsed through ``cache`` (a fresh ``WorkspaceCache(root)`` when omitted), so a rules run shares one
    parsed tree per file with its other Python-source rules.
    """
    try:
        config = tomllib.loads((root / config_path).read_text())
        index = Index(root, config, cache if cache is not None else WorkspaceCache(root))
        exceptions = config.get("usecase_exceptions", [])
        for entry in exceptions:
            if set(entry) != {"source", "target", "reason"} or any(
                not isinstance(entry[key], str) or not entry[key].strip() or "*" in entry[key]
                for key in ("source", "target", "reason")
            ):
                raise ValueError("usecase exceptions require exact source, callable target and reason")
        permitted = {(entry["source"], entry["target"]) for entry in exceptions}
        if len(permitted) != len(exceptions):
            raise ValueError("duplicate usecase exception")
    except (OSError, KeyError, TypeError, ValueError, SyntaxError) as exc:
        return [(config_path, 1, f"cannot inspect usecase boundaries: {exc}")]
    findings: set[tuple[str, int, str]] = set()
    used: set[tuple[str, str]] = set()

    def report(module: Module, node: ast.AST, message: str, target: str | None = None) -> None:
        key = (module.name, target)
        if target and key in permitted:
            used.add((module.name, target))
        else:
            findings.add((module.path, getattr(node, "lineno", 1), message))

    for symbol, definition in index.definitions.items():
        if not isinstance(definition, ast.ClassDef) or not index.usecase(symbol) or symbol == BASE:
            continue
        module = index.owner(symbol)
        assert module is not None
        if module.layer != "usecases":
            report(module, definition, f"BaseUseCase implementation belongs in features/<feature>/usecases: {symbol}")
        execute = next(
            (
                node
                for node in definition.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "execute"
            ),
            None,
        )
        if execute is None:
            report(module, definition, f"usecase must declare execute: {symbol}")
        else:
            arguments = [*execute.args.posonlyargs, *execute.args.args, *execute.args.kwonlyargs]
            arguments += [arg for arg in (execute.args.vararg, execute.args.kwarg) if arg]
            if execute.returns is None or any(
                arg.annotation is None for arg in arguments if arg.arg not in {"self", "cls"}
            ):
                report(module, execute, f"usecase execute requires explicit input and result annotations: {symbol}")
        constructor = next(
            (node for node in definition.body if isinstance(node, ast.FunctionDef) and node.name == "__init__"), None
        )
        if constructor:
            bindings: dict[str, Value] = {}
            for node in ast.walk(constructor):
                if isinstance(node, ast.Call):
                    target = index.value(node.func, module, bindings)
                    name = _attribute(node.func) or ""
                    # Dependency construction is wiring; invoking an operation is not.
                    if name in {"super", "dict", "list", "set", "tuple"} or (
                        isinstance(node.func, ast.Attribute) and node.func.attr == "__init__"
                    ):
                        continue
                    known = index.definitions.get(target.symbol) if target else None
                    is_constructor = isinstance(known, ast.ClassDef) or (
                        target is not None
                        and known is None
                        and name.split(".")[0] in module.bindings
                        and index.owner(target.symbol) is None
                        and name.rsplit(".", 1)[-1][:1].isupper()
                    )
                    if not is_constructor:
                        report(
                            module,
                            node,
                            f"usecase constructor must only wire dependencies; move {name or 'call'} to execute",
                        )
    for module in index.modules.values():
        if module.layer not in TRANSPORTS:
            continue
        global_bindings: dict[str, Value] = {}
        index.assignments(module.tree, module, global_bindings)
        contexts: list[tuple[ast.AST, dict[str, Value]]] = [(module.tree, {})]
        for statement in module.tree.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                contexts.append((statement, {}))
            elif isinstance(statement, ast.ClassDef):
                retained: dict[str, Value] = {}
                constructor = next(
                    (
                        method
                        for method in statement.body
                        if isinstance(method, ast.FunctionDef) and method.name == "__init__"
                    ),
                    None,
                )
                if constructor:
                    for arg in [*constructor.args.posonlyargs, *constructor.args.args, *constructor.args.kwonlyargs]:
                        if arg.annotation and (value := index.annotation(arg.annotation, module, retained)):
                            retained[arg.arg] = value
                    index.assignments(constructor, module, retained)
                contexts.extend(
                    (method, retained)
                    for method in statement.body
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
        for function, retained in contexts:
            bindings = {**global_bindings, **retained}
            if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                bindings.update({name: Value(target) for name, target in _imports(module, function).items()})
                for arg in [*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs]:
                    if arg.annotation and (value := index.annotation(arg.annotation, module, bindings)):
                        bindings[arg.arg] = value
            index.assignments(function, module, bindings)

            def nested(tree: ast.AST):
                for child in ast.iter_child_nodes(tree):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                        yield child
                    elif not isinstance(child, ast.ClassDef):
                        yield from nested(child)

            contexts.extend((child, dict(bindings)) for child in nested(function))
            for node in _walk(function):
                if not isinstance(node, ast.Call):
                    continue
                for argument in [*node.args, *(keyword.value for keyword in node.keywords)]:
                    callback = index.value(argument, module, bindings)
                    if callback:
                        callback_owner = index.owner(callback.symbol)
                        if (
                            callback_owner
                            and callback_owner.layer in {"usecases", "services", "repositories"}
                            and isinstance(
                                index.definitions.get(callback.symbol), (ast.FunctionDef, ast.AsyncFunctionDef)
                            )
                            and not any(
                                _attribute(decorator) == "property"
                                for decorator in index.definitions[callback.symbol].decorator_list
                            )
                            and not (
                                callback.instance
                                and callback.symbol.endswith(".execute")
                                and index.usecase(callback.symbol.rpartition(".")[0])
                            )
                        ):
                            report(
                                module,
                                argument,
                                f"transport passes raw execution callback: {callback.symbol}",
                                callback.symbol,
                            )
                target = index.value(node.func, module, bindings)
                if not target:
                    continue
                owner = index.owner(target.symbol)
                if not owner or owner.layer not in {"usecases", "services", "repositories"}:
                    continue
                definition = index.definitions.get(target.symbol)
                if isinstance(definition, ast.ClassDef):
                    if (
                        owner.layer == "usecases"
                        and not index.usecase(target.symbol)
                        and any(
                            isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name == "execute"
                            for method in definition.body
                        )
                    ):
                        report(
                            module,
                            node,
                            f"transport constructs a usecase without BaseUseCase: {target.symbol}",
                            target.symbol,
                        )
                    continue
                if (
                    target.instance
                    and target.symbol.endswith(".execute")
                    and index.usecase(target.symbol.rpartition(".")[0])
                ):
                    continue
                # Attribute calls on retained instances resolve against their concrete class.
                if isinstance(node.func, ast.Attribute):
                    receiver = index.value(node.func.value, module, bindings)
                    if (
                        receiver
                        and receiver.instance
                        and (
                            index.usecase(receiver.symbol)
                            or isinstance(index.definitions.get(target.symbol), (ast.FunctionDef, ast.AsyncFunctionDef))
                        )
                    ):
                        if index.usecase(receiver.symbol) and node.func.attr == "execute":
                            continue
                        report(
                            module, node, f"transport must invoke BaseUseCase.execute: {target.symbol}", target.symbol
                        )
                        continue
                if isinstance(definition, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    report(
                        module,
                        node,
                        f"transport calls execution function instead of BaseUseCase.execute: {target.symbol}",
                        target.symbol,
                    )
    for source, target in sorted(permitted - used):
        findings.add((config_path, 1, f"unused usecase exception: {source} -> {target}"))
    return sorted(findings)


class UsecaseBoundariesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-usecase-boundaries",
            name="usecase-boundaries-check",
            description="Check typed BaseUseCase execution boundaries.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
            inputs=("**/*.py", ".devkit/architecture.toml"),
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        return [
            Violation(
                rule_id=self.id,
                file=path,
                line=line,
                message=message,
                remediation="Expose a typed BaseUseCase.execute boundary; retain helpers behind it.",
                severity=self.severity,
                phase=self.phase,
            )
            for path, line, message in inspect_usecases(ctx.workspace_root, cache=ctx.cache)
        ]
