"""Check explicit execution boundaries without importing product modules."""

from __future__ import annotations

import importlib.util
import tomllib
from dataclasses import dataclass
from pathlib import Path

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, WorkspaceCache
from devkit_agt.features.rules.services.builtins.base import BaseRule

from .facts import Expression, Scope, descriptor

FACTS = descriptor(__name__, __file__)

BASE = "devkit_core.base.usecase.BaseUseCase"
TRANSPORTS = {"cli", "mcp", "http", "adapters"}


@dataclass
class Module:
    name: str
    path: str
    layer: str | None
    tree: Scope
    package: bool
    bindings: dict[str, str]


@dataclass(frozen=True)
class Value:
    symbol: str
    instance: bool = False


def _attribute(node: Expression) -> str | None:
    if node.kind == "name":
        return node.name
    if node.kind == "attribute" and node.value is not None and (parent := _attribute(node.value)):
        return f"{parent}.{node.name}"
    return None


def _imports(module: Module, tree: Scope) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for node in tree.imports:
        if node.module is None:
            for name, asname in node.names:
                bindings[asname or name.split(".")[0]] = name if asname else name.split(".")[0]
        else:
            name = node.module
            if node.level:
                context = module.name if module.package else module.name.rpartition(".")[0]
                try:
                    name = importlib.util.resolve_name("." * node.level + name, context)
                except ImportError:
                    continue
            for alias, asname in node.names:
                bindings[asname or alias] = f"{name}.{alias}"
    return bindings


class Index:
    def __init__(self, root: Path, config: dict, cache: WorkspaceCache) -> None:
        self.modules: dict[str, Module] = {}
        self.definitions: dict[str, Scope] = {}
        fact_paths: list[str] = []
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
                    cache.get_file_facts(path, FACTS),
                    relative[-1] == "__init__",
                    {},
                )
                module.bindings = _imports(module, module.tree)
                fact_paths.append(module.path)
                self.modules[name] = module
                for statement in module.tree.declarations:
                    if statement.kind in {"class", "function", "async"}:
                        self.definitions[f"{name}.{statement.name}"] = statement
                        if statement.kind == "class":
                            for method in statement.declarations:
                                if method.kind in {"function", "async"}:
                                    self.definitions[f"{name}.{statement.name}.{method.name}"] = method
                # Explicit aliases in public facades are resolved as well as import re-exports.
                for statement in module.tree.aliases:
                    if statement.value is not None and (value := _attribute(statement.value)):
                        head, _, tail = value.partition(".")
                        target = module.bindings.get(head, f"{name}.{head}") + (f".{tail}" if tail else "")
                        for destination in statement.targets:
                            if destination.kind == "name":
                                module.bindings[destination.name] = target

        # Resolve bound-method facade aliases only after every class is indexed.
        for module in self.modules.values():
            for statement in module.tree.aliases:
                if statement.value is not None and statement.value.kind == "attribute":
                    value = self.value(statement.value, module, {})
                    if value:
                        for destination in statement.targets:
                            if destination.kind == "name":
                                module.bindings[destination.name] = value.symbol

        cache.complete_file_facts(FACTS, fact_paths)

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
        if (definition is None or definition.kind != "class") or not module or symbol in trail:
            return False
        for base in definition.bases:
            if base.kind == "subscript" and base.value is not None:
                base = base.value
            name = _attribute(base)
            if name:
                head, _, rest = name.partition(".")
                target = module.bindings.get(head, f"{module.name}.{head}") + (f".{rest}" if rest else "")
                if self.usecase(target, trail | {symbol}):
                    return True
        return False

    def value(self, node: Expression | None, module: Module, bindings: dict[str, Value]) -> Value | None:
        if node is None:
            return None
        if node.kind == "await" and node.value is not None:
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
        if node.kind == "attribute" and node.value is not None:
            receiver = self.value(node.value, module, bindings)
            if receiver:
                return Value(self.resolve(f"{receiver.symbol}.{node.name}"), receiver.instance)
        if node.kind == "call" and node.value is not None:
            target = self.value(node.value, module, bindings)
            if target and (
                self.definitions.get(target.symbol) is not None and self.definitions[target.symbol].kind == "class"
            ):
                return Value(target.symbol, True)
        return None

    def assignments(self, tree: Scope, module: Module, bindings: dict[str, Value]) -> None:
        for _ in range(3):
            for node in tree.assignments:
                value = self.value(node.value, module, bindings) if node.value is not None else None
                if value is None and node.annotation is not None:
                    value = self.annotation(node.annotation, module, bindings)
                if value:
                    for target in node.targets:
                        if name := _attribute(target):
                            bindings[name] = value

    def annotation(self, node: Expression, module: Module, bindings: dict[str, Value]) -> Value | None:
        value = self.value(node, module, bindings)
        definition = self.definitions.get(value.symbol) if value else None
        return Value(value.symbol, True) if value and definition and definition.kind == "class" else None


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

    def report(module: Module, node: Expression | Scope, message: str, target: str | None = None) -> None:
        key = (module.name, target)
        if target and key in permitted:
            used.add((module.name, target))
        else:
            findings.add((module.path, getattr(node, "lineno", 1), message))

    for symbol, definition in index.definitions.items():
        if (definition is None or definition.kind != "class") or not index.usecase(symbol) or symbol == BASE:
            continue
        module = index.owner(symbol)
        assert module is not None
        if module.layer != "usecases":
            report(module, definition, f"BaseUseCase implementation belongs in features/<feature>/usecases: {symbol}")
        execute = next(
            (node for node in definition.declarations if node.kind in {"function", "async"} and node.name == "execute"),
            None,
        )
        if execute is None:
            report(module, definition, f"usecase must declare execute: {symbol}")
        else:
            arguments = [*execute.parameters, *execute.variadics]
            if not execute.returns or any(
                arg.annotation is None for arg in arguments if arg.arg not in {"self", "cls"}
            ):
                report(module, execute, f"usecase execute requires explicit input and result annotations: {symbol}")
        constructor = next(
            (node for node in definition.declarations if node.kind == "function" and node.name == "__init__"), None
        )
        if constructor:
            bindings: dict[str, Value] = {}
            for node in constructor.all_calls:
                if node.value is not None:
                    target = index.value(node.value, module, bindings)
                    name = _attribute(node.value) or ""
                    # Dependency construction is wiring; invoking an operation is not.
                    if name in {"super", "dict", "list", "set", "tuple"} or (
                        node.value.kind == "attribute" and node.value.name == "__init__"
                    ):
                        continue
                    known = index.definitions.get(target.symbol) if target else None
                    is_constructor = (known is not None and known.kind == "class") or (
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
        contexts: list[tuple[Scope, dict[str, Value]]] = [(module.tree, {})]
        for statement in module.tree.declarations:
            if statement.kind in {"function", "async"}:
                contexts.append((statement, {}))
            elif statement.kind == "class":
                retained: dict[str, Value] = {}
                constructor = next(
                    (
                        method
                        for method in statement.declarations
                        if method.kind == "function" and method.name == "__init__"
                    ),
                    None,
                )
                if constructor:
                    for arg in constructor.parameters:
                        if arg.annotation and (value := index.annotation(arg.annotation, module, retained)):
                            retained[arg.arg] = value
                    index.assignments(constructor, module, retained)
                contexts.extend(
                    (method, retained) for method in statement.declarations if method.kind in {"function", "async"}
                )
        for function, retained in contexts:
            bindings = {**global_bindings, **retained}
            if function.kind in {"function", "async"}:
                bindings.update({name: Value(target) for name, target in _imports(module, function).items()})
                for arg in function.parameters:
                    if arg.annotation and (value := index.annotation(arg.annotation, module, bindings)):
                        bindings[arg.arg] = value
            index.assignments(function, module, bindings)

            contexts.extend((child, dict(bindings)) for child in function.nested)
            for node in function.calls:
                for argument in [*node.args, *node.keywords]:
                    callback = index.value(argument, module, bindings)
                    if callback:
                        callback_owner = index.owner(callback.symbol)
                        if (
                            callback_owner
                            and callback_owner.layer in {"usecases", "services", "repositories"}
                            and index.definitions.get(callback.symbol) is not None
                            and index.definitions[callback.symbol].kind in {"function", "async"}
                            and not any(
                                _attribute(decorator) == "property"
                                for decorator in index.definitions[callback.symbol].decorators
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
                target = index.value(node.value, module, bindings)
                if not target:
                    continue
                owner = index.owner(target.symbol)
                if not owner or owner.layer not in {"usecases", "services", "repositories"}:
                    continue
                definition = index.definitions.get(target.symbol)
                if definition is not None and definition.kind == "class":
                    if (
                        owner.layer == "usecases"
                        and not index.usecase(target.symbol)
                        and any(
                            method.kind in {"function", "async"} and method.name == "execute"
                            for method in definition.declarations
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
                if node.value is not None and node.value.kind == "attribute":
                    receiver = index.value(node.value.value, module, bindings)
                    if (
                        receiver
                        and receiver.instance
                        and (
                            index.usecase(receiver.symbol)
                            or (
                                index.definitions.get(target.symbol) is not None
                                and index.definitions[target.symbol].kind in {"function", "async"}
                            )
                        )
                    ):
                        if index.usecase(receiver.symbol) and node.value.name == "execute":
                            continue
                        report(
                            module, node, f"transport must invoke BaseUseCase.execute: {target.symbol}", target.symbol
                        )
                        continue
                if definition is not None and definition.kind in {"function", "async"}:
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
