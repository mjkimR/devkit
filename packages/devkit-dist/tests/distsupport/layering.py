"""Static imports and resource references of the independent distribution package."""

from __future__ import annotations

import ast
import importlib.util
import re
import tomllib
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src/devkit_dist"
PYPROJECT = SRC.parents[1] / "pyproject.toml"

DECLARATION = next(
    entry
    for entry in tomllib.loads((Path(__file__).resolve().parents[4] / ".devkit/architecture.toml").read_text())[
        "packages"
    ]
    if entry["namespace"] == "devkit_dist"
)
FEATURES = set(DECLARATION["features"])
TOP_LEVEL = {"cli", "__main__", "__init__"}
# Behavioral lazy-loading expectations, not architectural import permissions.
LAZY_IMPORT_AREAS = {
    "base": {"advisory"},
    "adapters": {"base", "project", "advisory"},
    "project": {"base", "advisory"},
    "search": {"base", "advisory"},
    "host": {"base", "adapters", "project", "advisory"},
    "shared": {"base", "adapters", "project", "advisory"},
    "distribution": {"base", "adapters", "project", "search", "host", "advisory"},
    "bundles.advisory": set(),
    "bundles.git_commits": set(),
    "bundles.devkit": set(),
}
DATA_AREAS = {"bundles.advisory", "bundles.git_commits", "bundles.devkit"}
IMPORTING_CALLS = {"import_module", "find_spec", "files", "__import__"}
_MODULE_REFERENCE = re.compile(
    r"(?:devkit_dist|devkit_agt|devkit)\.[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?::[A-Za-z_][\w.]*)?"
)


def area_of(module: str) -> str | None:
    parts = module.split(".")
    if parts[0] == "devkit_agt":
        return None if len(parts) == 1 or (parts[1] == "bundles" or parts[1].endswith("_guide")) else "agt"
    if module == "devkit.advisory" or module.startswith("devkit.advisory."):
        return "advisory"
    if parts[0] != "devkit_dist" or len(parts) < 2:
        return None
    if parts[1] == "features":
        return parts[2] if len(parts) > 2 else None
    if parts[1] == "bundles" or parts[1].endswith("_guide"):
        return ".".join(parts[1:3]) if len(parts) > 2 else None
    return parts[1]


def modules(area: str) -> list[Path]:
    if area in TOP_LEVEL:
        return [SRC / f"{area}.py"]
    rel = (
        area.replace(".", "/")
        if area.startswith("bundles.")
        else f"features/{area}"
        if area in {"project", "distribution", "host", "shared", "search"}
        else area
    )
    return [p for p in sorted((SRC / rel).rglob("*.py")) if "tests" not in p.relative_to(SRC).parts]


def package(path: Path) -> str:
    return ".".join(("devkit_dist", *path.relative_to(SRC).parent.parts))


def is_bundle_content(path: Path) -> bool:
    return "bundle" in path.relative_to(SRC).parts


def references(source: str, package: str, *, strings: bool = False) -> set[tuple[str, int]]:
    found = set()
    for node in ast.walk(ast.parse(source)):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = (
                importlib.util.resolve_name("." * node.level + (node.module or ""), package)
                if node.level
                else node.module or ""
            )
            names = [base, *[base + "." + a.name for a in node.names]]
        elif isinstance(node, ast.Call):
            called = (
                node.func.attr
                if isinstance(node.func, ast.Attribute)
                else node.func.id
                if isinstance(node.func, ast.Name)
                else None
            )
            if (
                called in IMPORTING_CALLS
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                names = [node.args[0].value]
        elif (
            strings
            and isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and _MODULE_REFERENCE.fullmatch(node.value)
        ):
            names = [node.value.split(":", 1)[0]]
        found.update((name, getattr(node, "lineno", 0)) for name in names)
    return found


def referenced_areas(source: str, package: str, area: str, *, strings: bool = False) -> set[tuple[str, int]]:
    return {
        (target, line)
        for name, line in references(source, package, strings=strings)
        if (target := area_of(name)) and target != area
    }
