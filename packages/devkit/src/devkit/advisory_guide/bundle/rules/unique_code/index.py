"""A static index of a workspace's Python modules: classes, string constants and imports, resolved without importing.

Module names come from paths (below the last ``src`` segment, else from the workspace root; ``__init__.py`` names
its package). A reference that leaves the workspace stays a dotted name (``Target.external``), so a base imported
from an installed package can still be matched by name.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Target:
    """What a name resolves to: a workspace class, a module, a string constant, or a name outside the workspace."""

    kind: Literal["class", "module", "constant", "external"]
    name: str  # qualified class, module or external name; the value of a constant


@dataclass
class Module:
    name: str
    file: str
    package: str  # the package relative imports resolve against
    tree: ast.Module
    classes: dict[str, ast.ClassDef] = field(default_factory=dict)
    constants: dict[str, str] = field(default_factory=dict)
    imports: dict[str, tuple[str, str | None]] = field(default_factory=dict)  # local -> (module, attribute)


def module_name(rel: str) -> tuple[str, bool]:
    """The dotted module name of workspace-relative ``rel``, and whether it is a package's ``__init__.py``."""
    parts = rel.removesuffix(".py").split("/")
    if "src" in parts[:-1]:
        parts = parts[len(parts) - parts[::-1].index("src", 1) :]
    is_package = parts[-1] == "__init__"
    return ".".join(parts[:-1] if is_package else parts), is_package


def _top_level(body: list[ast.stmt]) -> Iterator[ast.stmt]:
    """Module statements, including those under a top-level ``if``, ``try`` or ``with``."""
    for node in body:
        yield node
        if isinstance(node, ast.If | ast.With):
            yield from _top_level(node.body)
            if isinstance(node, ast.If):
                yield from _top_level(node.orelse)
        elif isinstance(node, ast.Try):
            for block in (node.body, *(handler.body for handler in node.handlers), node.orelse, node.finalbody):
                yield from _top_level(block)


def _record_import(
    module: Module, node: ast.Import | ast.ImportFrom, imports: dict[str, tuple[str, str | None]]
) -> None:
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.asname:
                imports.setdefault(alias.asname, (alias.name, None))
            else:
                head = alias.name.split(".")[0]
                imports.setdefault(head, (head, None))
        return
    source = node.module or ""
    if node.level:
        base = module.package.split(".") if module.package else []
        base = base[: len(base) - (node.level - 1)] if node.level > 1 else base
        source = ".".join([*base, *([node.module] if node.module else [])])
    for alias in node.names:
        if alias.name != "*":
            imports.setdefault(alias.asname or alias.name, (source, alias.name))


def parse_module(rel: str, text: str) -> Module | None:
    """Index ``text`` as the module at ``rel``; ``None`` when it does not parse or names no module."""
    name, is_package = module_name(rel)
    if not name:
        return None
    try:
        tree = ast.parse(text, filename=rel)
    except (SyntaxError, ValueError):
        return None
    module = Module(name=name, file=rel, package=name if is_package else name.rpartition(".")[0], tree=tree)
    for node in _top_level(tree.body):
        if isinstance(node, ast.ClassDef):
            module.classes.setdefault(node.name, node)
        elif (
            isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    module.constants.setdefault(target.id, node.value.value)
        elif isinstance(node, ast.Import | ast.ImportFrom):
            _record_import(module, node, module.imports)
    # Imports inside functions (lazy imports) bind names too; a top-level binding of the same name wins.
    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom):
            _record_import(module, node, module.imports)
    return module


class Index:
    """Resolves names across the indexed modules."""

    def __init__(self, modules: list[Module]) -> None:
        self.modules: dict[str, Module] = {}
        for module in sorted(modules, key=lambda m: m.file):
            self.modules.setdefault(module.name, module)  # the first path in sorted order owns a duplicate name

    def resolve(self, module: str, name: str, _seen: frozenset[tuple[str, str]] = frozenset()) -> Target:
        """What ``name`` means in ``module``, following imports and re-exports."""
        here = self.modules.get(module)
        if here is None or (module, name) in _seen:
            if f"{module}.{name}" in self.modules:
                return Target("module", f"{module}.{name}")
            return Target("external", f"{module}.{name}")
        if name in here.classes:
            return Target("class", f"{module}.{name}")
        if name in here.constants:
            return Target("constant", here.constants[name])
        if name in here.imports:
            source, attribute = here.imports[name]
            if attribute is None:
                return Target("module", source)
            return self.resolve(source, attribute, _seen | {(module, name)})
        if f"{module}.{name}" in self.modules:
            return Target("module", f"{module}.{name}")
        return Target("external", f"{module}.{name}")

    def resolve_dotted(self, dotted: str) -> Target:
        """A configured ``package.module.Name``, resolved as ``from package.module import Name`` would be."""
        module, _, name = dotted.rpartition(".")
        return self.resolve(module, name)

    def resolve_expression(self, module: str, node: ast.expr) -> Target | None:
        """``Name`` and dotted ``Attribute`` expressions; an attribute of a class resolves to the class."""
        if isinstance(node, ast.Name):
            return self.resolve(module, node.id)
        if isinstance(node, ast.Attribute):
            owner = self.resolve_expression(module, node.value)
            if owner is None:
                return None
            if owner.kind == "module":
                return self.resolve(owner.name, node.attr)
            if owner.kind == "external":
                return Target("external", f"{owner.name}.{node.attr}")
            if owner.kind == "class":
                return owner
        return None

    def class_node(self, qualname: str) -> tuple[Module, ast.ClassDef]:
        module, _, name = qualname.rpartition(".")
        return self.modules[module], self.modules[module].classes[name]

    def bases(self, qualname: str) -> list[Target]:
        module, node = self.class_node(qualname)
        found = (self.resolve_expression(module.name, base) for base in node.bases)
        return [target for target in found if target is not None]

    def string_value(self, module: str, node: ast.expr) -> str | None:
        """A string literal, or a name bound to a module-level string literal."""
        if isinstance(node, ast.Constant):
            return node.value if isinstance(node.value, str) else None
        target = self.resolve_expression(module, node)
        return target.name if target is not None and target.kind == "constant" else None
