"""Static repository layout and import directions from one structure declaration."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, WorkspaceCache
from devkit_agt.features.rules.services.builtins.base import BaseRule
from devkit_dev.source_index import (
    CONFIG,
    bind,
    context_of,
    feature_of,
    iter_sources,
    layer_of,
    longest_module,
    resolve_forward,
    resolve_relative,
)

from .facts import ArchitectureFacts, Import, descriptor

FACTS = descriptor(__name__, __file__)

LAYERS = {"cli", "mcp", "http", "usecases", "services", "repositories", "models"}
CONTRACTS = {"models", "errors"}
ALLOWED = {
    "models": CONTRACTS,
    "errors": CONTRACTS,
    "repositories": CONTRACTS | {"repositories"},
    "services": CONTRACTS | {"repositories", "services"},
    "usecases": CONTRACTS | {"repositories", "services", "usecases"},
    "cli": CONTRACTS | {"usecases", "cli", "adapters"},
    "adapters": CONTRACTS | {"usecases", "adapters"},
    "mcp": CONTRACTS | {"usecases", "mcp", "adapters"},
    "http": CONTRACTS | {"usecases", "http", "adapters"},
}


@dataclass(frozen=True)
class Module:
    name: str
    path: str
    package: str
    parts: tuple[str, ...]
    facts: ArchitectureFacts
    is_package: bool

    @property
    def feature(self) -> str | None:
        return feature_of(self.parts)

    @property
    def layer(self) -> str | None:
        return layer_of(self.parts)

    @property
    def context(self) -> str:
        return context_of(self.name, self.is_package)


def _bindings(statements: tuple[Import, ...], context: str) -> dict[str, str]:
    return bind(
        (
            (None if node.kind == "import" else node.module or "", node.level, [(a.name, a.asname) for a in node.names])
            for node in statements
        ),
        context,
    )


def _imports(module: Module) -> list[tuple[str, int]]:
    """Resolve relative imports, including from-import submodules, without importing code."""
    result: list[tuple[str, int]] = []
    package = module.context
    bindings = _bindings(module.facts.imports, package)
    for head, attributes, line in module.facts.attributes:
        if head in bindings:
            result.append((".".join((bindings[head], *attributes)), line))
    for node in module.facts.scan:
        if isinstance(node, Import) and node.kind == "import":
            result.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, Import):
            name = node.module or ""
            if node.level:
                resolved = resolve_relative("." * node.level + name, package)
                if resolved is None:
                    result.append(("<invalid-relative-import>", node.lineno))
                    continue
                name = resolved
            result.extend((name if alias.name == "*" else f"{name}.{alias.name}", node.lineno) for alias in node.names)
        else:
            name = node.name
            if node.kind == "dynamic" and name.startswith(".") and node.context is not None:
                name = resolve_relative(name, node.context) or "<invalid-relative-import>"
            result.append((name, node.lineno))
    return list(dict.fromkeys(result))


def _dependency_cycles(graph: dict[str, set[str]]) -> list[tuple[str, ...]]:
    visited: set[str] = set()
    active: list[str] = []
    cycles: list[tuple[str, ...]] = []

    def visit(feature: str) -> None:
        if feature in active:
            cycles.append((*active[active.index(feature) :], feature))
            return
        if feature in visited:
            return
        active.append(feature)
        for dependency in sorted(graph[feature]):
            visit(dependency)
        active.pop()
        visited.add(feature)

    for feature in sorted(graph):
        visit(feature)
    return cycles


def _layout(parts: tuple[str, ...], package: dict[str, Any]) -> str | None:
    if not parts:
        return None
    top = parts[0]
    if top in package.get("data_roots", []):
        return None
    if package["kind"] in {"content", "advisory", "foundation"}:
        allowed = {"__init__", *package.get("root_modules", [])}
        if top not in allowed:
            return f"undeclared {package['kind']} root {top}"
        return None
    if top in {"base", "utils"}:
        return None
    if top in {"__init__", *package.get("root_modules", [])}:
        return None
    if top != "features":
        return f"module belongs in a declared feature/layer, not {top}"
    if len(parts) == 1 or parts[1] == "__init__":
        return None
    if parts[1] not in package.get("features", []):
        return f"undeclared feature {parts[1]}"
    if len(parts) > 2 and parts[2] not in {*LAYERS, "__init__", "errors", "bootstrap", "__main__"}:
        return f"undeclared feature layer {parts[2]}"
    return None


def inspect_architecture(root: Path, *, cache: WorkspaceCache | None = None) -> list[tuple[str, int, str]]:
    """Return all graph violations; never execute inspected modules.

    Sources are parsed through ``cache`` (a fresh ``WorkspaceCache(root)`` when omitted), so a rules run shares one
    parsed tree per file with its other Python-source rules.
    """
    cache = cache if cache is not None else WorkspaceCache(root)
    findings: list[tuple[str, int, str]] = []
    configuration = root / CONFIG
    if not configuration.is_file():
        return [(CONFIG, 1, "architecture declaration is missing")]
    try:
        config = tomllib.loads(configuration.read_text())
        packages = config["packages"]
        if config.get("schema") != 1 or not isinstance(packages, list):
            raise ValueError("schema must be 1 and packages must be an array")
        if len({p["namespace"] for p in packages}) != len(packages):
            raise ValueError("package namespaces must be unique")
        declarations = {p["namespace"]: p for p in packages}
        allowed_fields = {
            "namespace",
            "root",
            "kind",
            "features",
            "dependencies",
            "root_modules",
            "data_roots",
            "embedded_test_roots",
            "public_modules",
            "feature_dependencies",
        }
        if set(config) - {"schema", "packages", "import_exceptions", "usecase_exceptions"}:
            raise ValueError("unknown architecture declaration field")
        for package in packages:
            if not isinstance(package["namespace"], str) or not all(
                part.isidentifier() for part in package["namespace"].split(".")
            ):
                raise ValueError("namespace must be a dotted Python module name")
            if set(package) - allowed_fields:
                raise ValueError(f"unknown package field for {package['namespace']}")
            for field in allowed_fields - {"namespace", "root", "kind", "feature_dependencies"}:
                values = package.get(field, [])
                if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
                    raise ValueError(f"{field} must be an array of nonempty strings")
                if len(values) != len(set(values)):
                    raise ValueError(f"{field} contains duplicate values")
            source = Path(package["root"])
            if source.is_absolute() or ".." in source.parts or not (root / source).is_dir():
                raise ValueError(f"invalid/missing source root {source}")
            if package["kind"] not in {"features", "foundation", "advisory", "content"}:
                raise ValueError(f"unknown package kind {package['kind']}")
            if set(package.get("dependencies", [])) - declarations.keys():
                raise ValueError(f"unknown dependency for {package['namespace']}")
        feature_ids = {
            f"{package['namespace']}.features.{feature}"
            for package in packages
            for feature in package.get("features", [])
        }
        for package in packages:
            directions = package.get("feature_dependencies", {})
            if not isinstance(directions, dict) or set(directions) != set(package.get("features", [])):
                raise ValueError(f"feature_dependencies must declare every feature of {package['namespace']}")
            for feature, dependencies in directions.items():
                if not isinstance(dependencies, list) or any(not isinstance(value, str) for value in dependencies):
                    raise ValueError(f"feature_dependencies.{feature} must be an array of feature names")
                if len(dependencies) != len(set(dependencies)) or set(dependencies) - feature_ids:
                    raise ValueError(f"duplicate or unknown feature dependency for {package['namespace']}.{feature}")
                if f"{package['namespace']}.features.{feature}" in dependencies:
                    raise ValueError(f"feature cannot depend on itself: {feature}")
        exceptions = config.get("import_exceptions", [])
        for entry in exceptions:
            if not all(
                isinstance(entry.get(key), str) and entry[key].strip() for key in ("source", "target", "reason")
            ):
                raise ValueError("import exceptions require exact source, target and reason")
            if any("*" in entry[key] for key in ("source", "target")):
                raise ValueError("import exceptions cannot use wildcards")
    except (KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        return [(CONFIG, 1, f"invalid architecture declaration: {exc}")]

    declared_roots = [root / package["root"] for package in packages]
    for area in ("packages", "tools"):
        for source in (root / area).glob("*/src"):
            for path in source.rglob("*.py"):
                if "__pycache__" not in path.parts and not any(path.is_relative_to(owner) for owner in declared_roots):
                    findings.append((path.relative_to(root).as_posix(), 1, "source has no declared package owner"))

    for package in packages:
        source = root / package["root"]
        # Namespace packages can have multiple path components below src.
        owner = source
        while owner != root and owner.name != "src":
            owner = owner.parent
        package_root = owner.parent if owner.name == "src" else source.parent.parent
        tests = package_root / "tests"
        for path in sorted(tests.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            relative = path.relative_to(tests)
            if relative.parts[0] in {"unit", "integration", "e2e", "support"}:
                continue
            if len(relative.parts) == 1 and relative.name in {"conftest.py", "__init__.py"}:
                continue
            findings.append(
                (path.relative_to(root).as_posix(), 1, "tests belong under unit, integration, e2e or support")
            )
        if package["kind"] == "features":
            for manifest in sorted(source.rglob("bundle.toml")):
                relative = manifest.relative_to(source)
                if len(relative.parts) != 4 or relative.parts[0] != "bundles" or relative.parts[2] != "bundle":
                    findings.append(
                        (manifest.relative_to(root).as_posix(), 1, "executable bundle belongs at bundles/<name>/bundle")
                    )

    modules: dict[str, Module] = {}
    complete = True
    fact_paths: list[str] = []
    for source in iter_sources(root, packages):
        if source.status == "misplaced-test":
            findings.append((source.path, 1, "tests belong in package tests or a declared bundled rule"))
        if source.status != "module":
            continue
        issue = _layout(source.relative, declarations[source.namespace])
        if issue:
            findings.append((source.path, 1, issue))
        try:
            facts = cache.get_file_facts(source.file, FACTS)
            fact_paths.append(source.path)
        except (SyntaxError, ValueError) as exc:
            complete = False
            findings.append((source.path, getattr(exc, "lineno", 1) or 1, f"cannot parse source: {exc}"))
            continue
        modules[source.name] = Module(
            source.name, source.path, source.namespace, source.parts, facts, source.is_package
        )

    for package in packages:
        for public in package.get("public_modules", []):
            if public not in modules or not public.startswith(package["namespace"] + ".features."):
                findings.append((CONFIG, 1, f"public module is missing or outside its features: {public}"))

    # Validate declared package dependencies independently of which optional module is imported today.
    def visit(namespace: str, trail: tuple[str, ...]) -> None:
        if namespace in trail:
            findings.append((CONFIG, 1, f"package dependency cycle: {' -> '.join((*trail, namespace))}"))
            return
        for dependency in declarations[namespace].get("dependencies", []):
            visit(dependency, (*trail, namespace))

    for namespace in declarations:
        visit(namespace, ())
    declared_features = {
        f"{package['namespace']}.features.{feature}": set(dependencies)
        for package in packages
        for feature, dependencies in package.get("feature_dependencies", {}).items()
    }
    for cycle in _dependency_cycles(declared_features):
        findings.append((CONFIG, 1, f"declared feature dependency cycle: {' -> '.join(cycle)}"))
    # Entry-point groups keep their external names; their Python target modules must exist.
    for package in packages:
        manifest = (root / package["root"]).parent.parent / "pyproject.toml"
        if not manifest.is_file():
            continue
        try:
            project = tomllib.loads(manifest.read_text()).get("project", {})
            groups = project.get("entry-points", {})
            entries = [
                *project.get("scripts", {}).values(),
                *(value for group in groups.values() for value in group.values()),
            ]
            for entry in entries:
                if ":" not in entry:
                    continue  # Bundle resource packages can be content-only roots.
                target = entry.split(":", 1)[0]
                if target not in modules:
                    findings.append(
                        (manifest.relative_to(root).as_posix(), 1, f"entry-point module is missing: {target}")
                    )
        except (ValueError, TypeError) as exc:
            findings.append((manifest.relative_to(root).as_posix(), 1, f"invalid entry-point declaration: {exc}"))

    facades: dict[str, dict[str, str]] = {}

    def forwards(module: Module) -> dict[str, str]:
        """The names a module's top-level imports bind, so a facade cannot conceal an upward dependency."""
        if module.name not in facades:
            facades[module.name] = _bindings(module.facts.facade, module.context)
        return facades[module.name]

    feature_graph: dict[str, set[str]] = {feature: set() for feature in feature_ids}
    feature_edges: dict[tuple[str, str], tuple[str, int]] = {}
    used: set[tuple[str, str]] = set()
    permitted = {(entry["source"], entry["target"]) for entry in exceptions}
    namespaces = sorted(declarations, key=len, reverse=True)
    for module in modules.values():
        package = declarations[module.package]
        seen: set[tuple[int, str]] = set()
        for imported, line in _imports(module):
            target_namespace = next((ns for ns in namespaces if imported == ns or imported.startswith(ns + ".")), None)
            issue: str | None = None
            if imported == "<invalid-relative-import>":
                issue = "relative import escapes its package"
            elif imported == "devkit" or (
                imported.startswith("devkit.") and not imported.startswith("devkit.advisory")
            ):
                issue = f"legacy shared namespace import {imported}"
            elif (
                target_namespace
                and target_namespace != module.package
                and target_namespace not in package.get("dependencies", [])
            ):
                issue = f"undeclared package dependency {module.package} -> {target_namespace}"
            # Match the actual module, not an imported attribute added by from-import expansion.
            target = longest_module(imported, modules)
            if issue is None and target_namespace:
                destination = modules.get(
                    longest_module(resolve_forward(imported, modules, forwards, indexed_only=True), modules)
                )
                if destination:
                    if module.feature and destination.feature:
                        source_feature = f"{module.package}.features.{module.feature}"
                        target_feature = f"{destination.package}.features.{destination.feature}"
                        if source_feature != target_feature:
                            feature_graph[source_feature].add(target_feature)
                            feature_edges.setdefault((source_feature, target_feature), (module.path, line))
                            allowed = package["feature_dependencies"][module.feature]
                            if target_feature not in allowed:
                                message = f"undeclared feature dependency {source_feature} -> {target_feature}"
                                if (line, message) not in seen:
                                    findings.append((module.path, line, message))
                                    seen.add((line, message))
                    if (
                        module.parts
                        and module.parts[0] == "base"
                        and destination.parts
                        and destination.parts[0] in {"utils", "features", "core", "adapters"}
                    ):
                        issue = f"base depends on implementation {target}"
                    elif (
                        module.parts
                        and module.parts[0] == "utils"
                        and (destination.feature or destination.layer == "adapters")
                    ):
                        issue = f"utils depends on implementation {target}"
                    elif (
                        module.layer in ALLOWED and destination.layer and destination.layer not in ALLOWED[module.layer]
                    ):
                        issue = f"{module.layer} cannot import {destination.layer}: {target}"
                    elif (access := modules.get(target, destination)).feature and (
                        module.package != access.package or (module.feature and module.feature != access.feature)
                    ):
                        public = declarations[access.package].get("public_modules", [])
                        facade = f"{access.package}.features.{access.feature}"
                        if target != facade and target not in public:
                            issue = f"cross-feature import bypasses public API: {target}"
            if issue:
                key = (module.name, target if target in modules else imported)
                if key in permitted:
                    used.add(key)
                elif (line, issue) not in seen:
                    findings.append((module.path, line, issue))
                    seen.add((line, issue))
    # Check the actual feature graph even when an edge also violates its declaration.
    # A public facade and a layer exception must never conceal a feature cycle.
    for cycle in _dependency_cycles(feature_graph):
        path, line = feature_edges[(cycle[-2], cycle[-1])]
        findings.append((path, line, f"feature dependency cycle: {' -> '.join(cycle)}"))
    for source, target in sorted(permitted - used):
        findings.append((CONFIG, 1, f"unused import exception: {source} -> {target}"))
    if complete:
        cache.complete_file_facts(FACTS, fact_paths)
    return findings


class ArchitectureRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-architecture",
            name="architecture-check",
            description="Check repository package layout and import direction.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
            inputs=("**/*.py", "**/pyproject.toml", "**/bundle.toml", ".devkit/architecture.toml"),
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        return [
            Violation(
                rule_id=self.id,
                file=path,
                line=line,
                message=message,
                remediation="Follow project-structure and update the single architecture declaration.",
                severity=self.severity,
                phase=self.phase,
            )
            for path, line, message in inspect_architecture(ctx.workspace_root, cache=ctx.cache)
        ]
