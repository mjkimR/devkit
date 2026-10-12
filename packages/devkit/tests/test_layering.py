"""The module layering of ``devkit``, checked statically over every import statement.

Lower layers never import higher ones, so a module can be understood, tested
and eventually split out without the modules above it. ``devkit.cli`` and
``devkit.__main__`` assemble the command line and may import anything.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).parents[1] / "src/devkit"

ALLOWED: dict[str, set[str]] = {
    "advisory": set(),
    "core": {"advisory"},
    "rules": {"core", "advisory"},
    "workflow": {"core", "advisory", "rules"},
    "gate": {"core", "advisory", "rules"},
    "distribution": {"core", "advisory"},
}


def _package(path: Path) -> str:
    return ".".join(("devkit", *path.relative_to(SRC).parent.parts))


def _imported_areas(source: str, package: str, area: str) -> set[tuple[str, int]]:
    """``(area, line)`` for every other devkit area ``source`` imports, including imports inside functions.

    ``package`` is the dotted package containing the module, for resolving relative imports.
    """
    tree = ast.parse(source)
    found: set[tuple[str, int]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        else:
            if node.level:
                base = package.split(".")
                base = base[: len(base) - (node.level - 1)]
                names = [".".join([*base, node.module] if node.module else base)]
            elif node.module:
                names = [node.module]
            if names == ["devkit"]:
                names = [f"devkit.{alias.name}" for alias in node.names]
        for name in names:
            parts = name.split(".")
            if parts[0] == "devkit" and len(parts) > 1 and parts[1] != area:
                found.add((parts[1], node.lineno))
    return found


def test_every_area_is_declared() -> None:
    areas = {p.name for p in SRC.iterdir() if p.is_dir() and (p / "__init__.py").is_file()}
    assert areas == set(ALLOWED)


@pytest.mark.parametrize("area", sorted(ALLOWED))
def test_area_imports_only_lower_layers(area: str) -> None:
    violations = [
        f"{path.relative_to(SRC)}:{line} imports devkit.{target}"
        for path in sorted((SRC / area).rglob("*.py"))
        for target, line in sorted(_imported_areas(path.read_text("utf-8"), _package(path), area))
        if target not in ALLOWED[area]
    ]
    assert violations == []


def test_the_scanner_sees_absolute_relative_and_nested_imports() -> None:
    source = (
        "from devkit.rules import x\nimport devkit.gate.hooks.hooks\nfrom devkit import workflow\n"
        "from . import sibling\nfrom .other import z\n"
        "def f():\n    from ..distribution import y\n"
    )
    found = {target for target, _ in _imported_areas(source, "devkit.core", "core")}
    assert found == {"rules", "gate", "workflow", "distribution"}


def test_distribution_bundles_have_no_workspace_knowledge() -> None:
    # Bundle authoring shares only the neutral ``devkit.distribution.content`` helpers with installation.
    violations = [
        f"{path.relative_to(SRC)}:{node.lineno}"
        for path in sorted((SRC / "distribution/bundles").rglob("*.py"))
        for node in ast.walk(ast.parse(path.read_text("utf-8")))
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("devkit.distribution.installation")
    ]
    assert violations == []
