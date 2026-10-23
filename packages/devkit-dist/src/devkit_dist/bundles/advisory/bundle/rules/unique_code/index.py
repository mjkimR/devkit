"""A static index of a workspace's Python modules: classes, string constants and imports, resolved without importing.

Module names come from paths (below the last ``src`` segment, else from the workspace root; ``__init__.py`` names
its package). Imports inside a function bind names in that function only (``function_imports``). A reference that leaves the workspace stays a dotted name (``Target.external``), so a base imported
from an installed package can still be matched by name.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from devkit_agt.features.rules import capture_facts_dependency

from .facts import AdvisoryFacts, Class, Expression, Import

Imports = dict[str, tuple[str, str | None]]  # local name -> (module, attribute or None for a module import)


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
    facts: AdvisoryFacts
    classes: dict[str, Class] = field(default_factory=dict)
    constants: dict[str, str] = field(default_factory=dict)
    imports: Imports = field(default_factory=dict)  # top-level bindings only


def module_name(rel: str) -> tuple[str, bool]:
    """The dotted module name of workspace-relative ``rel``, and whether it is a package's ``__init__.py``."""
    parts = rel.removesuffix(".py").split("/")
    if "src" in parts[:-1]:
        parts = parts[len(parts) - parts[::-1].index("src", 1) :]
    is_package = parts[-1] == "__init__"
    return ".".join(parts[:-1] if is_package else parts), is_package


def _record_import(module: Module, node: Import, imports: Imports) -> None:
    if node.module is None:
        for name, asname in node.aliases:
            if asname:
                imports.setdefault(asname, (name, None))
            else:
                head = name.split(".")[0]
                imports.setdefault(head, (head, None))
        return
    source = node.module or ""
    if node.level:
        base = module.package.split(".") if module.package else []
        base = base[: len(base) - (node.level - 1)] if node.level > 1 else base
        source = ".".join([*base, *([node.module] if node.module else [])])
    for name, asname in node.aliases:
        if name != "*":
            imports.setdefault(asname or name, (source, name))


def parse_module(rel: str, facts: AdvisoryFacts) -> Module | None:
    """Build current module identity and bindings from rule-owned unresolved syntax."""
    name, is_package = module_name(rel)
    if not name:
        return None
    module = Module(name=name, file=rel, package=name if is_package else name.rpartition(".")[0], facts=facts)
    for declaration in facts.classes:
        module.classes.setdefault(declaration.name, declaration)
    for binding, value in facts.constants:
        module.constants.setdefault(binding, value)
    for node in facts.imports:
        _record_import(module, node, module.imports)
    return module


def function_imports(module: Module, scope: tuple[Import, ...]) -> Imports:
    imports: Imports = {}
    for node in scope:
        _record_import(module, node, imports)
    return imports


class Index:
    """Resolves names across the indexed modules."""

    def __init__(self, modules: list[Module]) -> None:
        self.modules: dict[str, Module] = {}
        for module in sorted(modules, key=lambda m: m.file):
            self.modules.setdefault(module.name, module)  # the first path in sorted order owns a duplicate name

    def resolve(
        self, module: str, name: str, local: Imports | None = None, _seen: frozenset[tuple[str, str]] = frozenset()
    ) -> Target:
        """What ``name`` means in ``module`` (``local``: the bindings of the enclosing functions, which come first)."""
        if local and name in local:
            source, attribute = local[name]
            return Target("module", source) if attribute is None else self.resolve(source, attribute)
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
            return self.resolve(source, attribute, _seen=_seen | {(module, name)})
        if f"{module}.{name}" in self.modules:
            return Target("module", f"{module}.{name}")
        return Target("external", f"{module}.{name}")

    def resolve_dotted(self, dotted: str) -> Target:
        """A configured ``package.module.Name``, resolved as ``from package.module import Name`` would be."""
        module, _, name = dotted.rpartition(".")
        return self.resolve(module, name)

    def resolve_expression(self, module: str, node: Expression, local: Imports | None = None) -> Target | None:
        """``Name`` and dotted ``Attribute`` expressions; an attribute of a class resolves to the class."""
        if node.kind == "name":
            return self.resolve(module, node.name, local)
        if node.kind == "attribute":
            owner = self.resolve_expression(module, node.parent, local) if node.parent is not None else None
            if owner is None:
                return None
            if owner.kind == "module":
                return self.resolve(owner.name, node.name)
            if owner.kind == "external":
                return Target("external", f"{owner.name}.{node.name}")
            if owner.kind == "class":
                return owner
        return None

    def class_node(self, qualname: str) -> tuple[Module, Class]:
        module, _, name = qualname.rpartition(".")
        return self.modules[module], self.modules[module].classes[name]

    def bases(self, qualname: str) -> list[Target]:
        module, node = self.class_node(qualname)
        found = (self.resolve_expression(module.name, base) for base in node.bases)
        return [target for target in found if target is not None]

    def string_value(self, module: str, node: Expression, local: Imports | None = None) -> str | None:
        """A string literal, or a name bound to a module-level string literal."""
        if node.kind == "string":
            return node.name
        target = self.resolve_expression(module, node, local)
        return target.name if target is not None and target.kind == "constant" else None


SOURCE = capture_facts_dependency("RULE-advisory-unique-code.index", __file__, module_name=__name__)
