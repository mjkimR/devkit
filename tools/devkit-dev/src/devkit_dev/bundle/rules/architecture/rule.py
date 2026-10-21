"""Static repository layout and import directions from one structure declaration."""

from __future__ import annotations

import ast
import importlib.util
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins.base import BaseRule

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
    tree: ast.Module
    is_package: bool

    @property
    def feature(self) -> str | None:
        return self.parts[1] if len(self.parts) > 1 and self.parts[0] == "features" else None

    @property
    def layer(self) -> str | None:
        if self.parts and self.parts[0] == "adapters":
            return "adapters"
        return self.parts[2] if len(self.parts) > 2 and self.feature else None


def _imports(module: Module) -> list[tuple[str, int]]:
    """Resolve relative imports, including from-import submodules, without importing code."""
    result: list[tuple[str, int]] = []
    package = module.name if module.is_package else module.name.rpartition(".")[0]
    dynamic_names = {"__import__"}
    for node in ast.walk(module.tree):
        if isinstance(node, ast.ImportFrom) and node.module == "importlib":
            dynamic_names.update(alias.asname or alias.name for alias in node.names if alias.name == "import_module")
    for node in ast.walk(module.tree):
        if isinstance(node, ast.Import):
            result.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            name = node.module or ""
            if node.level:
                try:
                    name = importlib.util.resolve_name("." * node.level + name, package)
                except ImportError:
                    result.append(("<invalid-relative-import>", node.lineno))
                    continue
            result.extend((name if alias.name == "*" else f"{name}.{alias.name}", node.lineno) for alias in node.names)
        elif isinstance(node, ast.Call):
            function = node.func
            dynamic = (isinstance(function, ast.Name) and function.id in dynamic_names) or (
                isinstance(function, ast.Attribute) and function.attr == "import_module"
            )
            if dynamic and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                name = node.args[0].value
                if name.startswith("."):
                    context = next((keyword.value for keyword in node.keywords if keyword.arg == "package"), None)
                    if context is None and len(node.args) > 1:
                        context = node.args[1]
                    if isinstance(context, ast.Constant) and isinstance(context.value, str):
                        try:
                            name = importlib.util.resolve_name(name, context.value)
                        except ImportError:
                            name = "<invalid-relative-import>"
                result.append((name, node.lineno))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and ":" in node.value:
            name = node.value.split(":", 1)[0]
            if all(part.isidentifier() for part in name.split(".")):
                result.append((name, node.lineno))
    return list(dict.fromkeys(result))


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


def inspect_architecture(root: Path, config_path: str = ".devkit/architecture.toml") -> list[tuple[str, int, str]]:
    """Return all graph violations; never execute inspected modules."""
    findings: list[tuple[str, int, str]] = []
    configuration = root / config_path
    if not configuration.is_file():
        return [(config_path, 1, "architecture declaration is missing")]
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
        }
        if set(config) - {"schema", "packages", "import_exceptions"}:
            raise ValueError("unknown architecture declaration field")
        for package in packages:
            if not isinstance(package["namespace"], str) or not all(
                part.isidentifier() for part in package["namespace"].split(".")
            ):
                raise ValueError("namespace must be a dotted Python module name")
            if set(package) - allowed_fields:
                raise ValueError(f"unknown package field for {package['namespace']}")
            for field in allowed_fields - {"namespace", "root", "kind"}:
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
        exceptions = config.get("import_exceptions", [])
        for entry in exceptions:
            if not all(
                isinstance(entry.get(key), str) and entry[key].strip() for key in ("source", "target", "reason")
            ):
                raise ValueError("import exceptions require exact source, target and reason")
            if any("*" in entry[key] for key in ("source", "target")):
                raise ValueError("import exceptions cannot use wildcards")
    except (KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        return [(config_path, 1, f"invalid architecture declaration: {exc}")]

    declared_roots = [root / package["root"] for package in packages]
    for area in ("packages", "tools"):
        for source in (root / area).glob("*/src"):
            for path in source.rglob("*.py"):
                if "__pycache__" not in path.parts and not any(path.is_relative_to(owner) for owner in declared_roots):
                    findings.append((path.relative_to(root).as_posix(), 1, "source has no declared package owner"))

    modules: dict[str, Module] = {}
    for package in packages:
        source = root / package["root"]
        for path in sorted(source.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            relative_path = path.relative_to(source)
            if "tests" in relative_path.parts:
                if any(relative_path.is_relative_to(prefix) for prefix in package.get("embedded_test_roots", [])):
                    continue
                if relative_path.parts[0] not in package.get("data_roots", []):
                    findings.append(
                        (
                            path.relative_to(root).as_posix(),
                            1,
                            "tests belong in package tests or a declared bundled rule",
                        )
                    )
                    continue
            relative = relative_path.with_suffix("").parts
            rel = path.relative_to(root).as_posix()
            if relative[0] in package.get("data_roots", []):
                continue
            issue = _layout(relative, package)
            if issue:
                findings.append((rel, 1, issue))
            try:
                tree = ast.parse(path.read_text(), filename=rel)
            except (SyntaxError, UnicodeError) as exc:
                findings.append((rel, getattr(exc, "lineno", 1) or 1, f"cannot parse source: {exc}"))
                continue
            parts = relative[:-1] if relative[-1] == "__init__" else relative
            name = ".".join((package["namespace"], *parts))
            modules[name] = Module(name, rel, package["namespace"], parts, tree, relative[-1] == "__init__")

    for package in packages:
        for public in package.get("public_modules", []):
            if public not in modules or not public.startswith(package["namespace"] + ".features."):
                findings.append((config_path, 1, f"public module is missing or outside its features: {public}"))

    # Validate declared package dependencies independently of which optional module is imported today.
    def visit(namespace: str, trail: tuple[str, ...]) -> None:
        if namespace in trail:
            findings.append((config_path, 1, f"package dependency cycle: {' -> '.join((*trail, namespace))}"))
            return
        for dependency in declarations[namespace].get("dependencies", []):
            visit(dependency, (*trail, namespace))

    for namespace in declarations:
        visit(namespace, ())
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

    def resolve(imported: str, trail: frozenset[str] = frozenset()) -> Module | None:
        """Follow explicit facade re-exports so a facade cannot conceal an upward dependency."""
        if imported in trail:
            return None
        target = imported
        while target not in modules and "." in target:
            target = target.rpartition(".")[0]
        destination = modules.get(target)
        if destination and imported != target:
            attribute = imported[len(target) + 1 :].split(".")[0]
            for statement in destination.tree.body:
                if not isinstance(statement, ast.ImportFrom):
                    continue
                base = statement.module or ""
                if statement.level:
                    context = destination.name if destination.is_package else destination.name.rpartition(".")[0]
                    try:
                        base = importlib.util.resolve_name("." * statement.level + base, context)
                    except ImportError:
                        continue
                for alias in statement.names:
                    if (alias.asname or alias.name) == attribute:
                        resolved = resolve(f"{base}.{alias.name}", trail | {imported})
                        if resolved:
                            return resolved
        return destination

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
            if issue is None and target_namespace:
                target = imported
                while target not in modules and "." in target:
                    target = target.rpartition(".")[0]
                destination = resolve(imported)
                if destination:
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
                # Match the actual module, not an imported attribute added by from-import expansion.
                target = imported
                while target not in modules and "." in target:
                    target = target.rpartition(".")[0]
                key = (module.name, target if target in modules else imported)
                if key in permitted:
                    used.add(key)
                elif (line, issue) not in seen:
                    findings.append((module.path, line, issue))
                    seen.add((line, issue))
    for source, target in sorted(permitted - used):
        findings.append((config_path, 1, f"unused import exception: {source} -> {target}"))
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
            for path, line, message in inspect_architecture(ctx.workspace_root)
        ]
