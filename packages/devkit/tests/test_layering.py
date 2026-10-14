"""The module layering of ``devkit``, checked statically over every import statement and entry point.

Lower layers never import higher ones, so a module can be understood, tested
and eventually split out without the modules above it. ``devkit.cli`` and
``devkit.__main__`` assemble the command line and may import anything. Test
files under ``src`` (each rule's ``tests/`` folder) are not production modules
and are not scanned. Besides import statements, a string literal naming a
devkit module in ``importlib.import_module``, ``importlib.util.find_spec`` or
``importlib.resources.files`` counts as an import, and so does an entry point
of ``pyproject.toml``: the area that loads its group imports its target.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest

SRC = Path(__file__).parents[1] / "src/devkit"
PYPROJECT = Path(__file__).parents[1] / "pyproject.toml"
# Calls whose first argument, a module name, is imported (``files`` imports the module it reads resources of).
_IMPORTING_CALLS = {"import_module", "find_spec", "files", "__import__"}

# ``advisory`` is the separate devkit-advisory distribution (``test_advisory_is_standard_library_only`` there),
# below every area. The ``*_guide`` areas (``DATA_AREAS``) hold built-in bundle content: ``authoring_guide`` ships
# rule code under ``bundle/rules/``, built on the public rule API and loaded by ``devkit rules`` from the synchronized
# copies, never imported through the package.
ALLOWED: dict[str, set[str]] = {
    "advisory_guide": set(),
    "authoring_guide": {"core", "advisory", "rules"},
    "commits_guide": set(),
    "core": {"advisory"},
    "rules": {"core", "advisory", "compact"},
    "workflow": {"core", "advisory", "rules"},
    "gate": {"core", "advisory", "rules", "compact"},
    "search": {"core", "advisory"},
    "distribution": {"core", "advisory", "search"},
    "compact": {"core", "advisory"},
    "worktree": {"core", "advisory"},
    "generated": {"core", "advisory", "compact"},
}


def _modules(area: str) -> list[Path]:
    """The production modules of an area: every ``.py`` file except those under a ``tests`` directory."""
    return [path for path in sorted((SRC / area).rglob("*.py")) if "tests" not in path.relative_to(SRC).parts]


def _package(path: Path) -> str:
    return ".".join(("devkit", *path.relative_to(SRC).parent.parts))


def _imported_areas(source: str, package: str, area: str) -> set[tuple[str, int]]:
    """``(area, line)`` for every other devkit area ``source`` imports, including imports inside functions and
    string literals passed to ``_IMPORTING_CALLS``.

    ``package`` is the dotted package containing the module, for resolving relative imports.
    """
    tree = ast.parse(source)
    found: set[tuple[str, int]] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Call):
            func = node.func
            called = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else None
            first = node.args[0] if node.args else None
            if called in _IMPORTING_CALLS and isinstance(first, ast.Constant) and isinstance(first.value, str):
                names = [first.value]
        elif not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        elif isinstance(node, ast.Import):
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
        for path in _modules(area)
        for target, line in sorted(_imported_areas(path.read_text("utf-8"), _package(path), area))
        if target not in ALLOWED[area]
    ]
    assert violations == []


def test_test_folders_are_not_scanned() -> None:
    scanned = {path.relative_to(SRC).as_posix() for path in _modules("rules")}
    assert "rules/rules/markdown_link/rule.py" in scanned
    assert not any("/tests/" in name for name in scanned)


def test_the_scanner_sees_absolute_relative_and_nested_imports() -> None:
    source = (
        "from devkit.rules import x\nimport devkit.gate.hooks.hooks\nfrom devkit import workflow\n"
        "from . import sibling\nfrom .other import z\n"
        "def f():\n    from ..distribution import y\n"
    )
    found = {target for target, _ in _imported_areas(source, "devkit.core", "core")}
    assert found == {"rules", "gate", "workflow", "distribution"}


def test_the_scanner_sees_module_names_passed_to_importing_calls() -> None:
    source = (
        "import importlib\nfrom importlib import resources\n"
        "importlib.import_module('devkit.gate.engine')\nresources.files('devkit.rules.rules')\n"
        "importlib.util.find_spec('devkit.workflow')\nprint('devkit.search')\n"
    )
    found = {target for target, _ in _imported_areas(source, "devkit.core", "core")}
    assert found == {"gate", "rules", "workflow"}


def _entry_point_groups() -> dict[str, str]:
    """Entry-point group -> the area whose code loads it, from every ``*GROUP = "devkit..."`` constant."""
    groups: dict[str, str] = {}
    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(SRC)
        if "tests" in rel.parts:
            continue
        area = rel.parts[0] if len(rel.parts) > 1 else rel.stem
        for node in ast.walk(ast.parse(path.read_text("utf-8"))):
            if (
                isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id.endswith("GROUP") for target in node.targets)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
                and node.value.value.startswith("devkit.")
            ):
                groups[node.value.value] = area
    return groups


# Areas that hold bundle content and import no code: any area may load them. Locating a bundle's resources imports
# its module, so bundle discovery runs only these empty packages, never an engine (``test_data_areas_import_nothing``).
DATA_AREAS = {"advisory_guide", "authoring_guide", "commits_guide"}

# Entry points whose target the loading area may not import, each a known runtime coupling (group, entry name).
ENTRY_POINT_EXCEPTIONS: dict[tuple[str, str], str] = {
    # Dependency inversion: gate registers its hook installation as a post-sync extension; distribution calls it
    # through ``devkit.core.extensions`` without importing gate code.
    ("devkit.post_sync", "gate-hooks"): "gate",
}


def _entry_points() -> list[tuple[str, str, str]]:
    """``(group, name, target module)`` of every devkit entry point in ``pyproject.toml``."""
    data = tomllib.loads(PYPROJECT.read_text("utf-8"))
    return [
        (group, name, value.split(":", 1)[0].strip())
        for group, entries in sorted(data["project"].get("entry-points", {}).items())
        for name, value in sorted(entries.items())
    ]


def test_entry_point_groups_have_a_loading_area() -> None:
    groups = _entry_point_groups()
    assert {group for group, _, _ in _entry_points()} <= groups.keys()
    assert groups["devkit.bundles"] == "distribution" and groups["devkit.commands"] == "cli"


def test_entry_points_load_only_lower_layers() -> None:
    groups = _entry_point_groups()
    violations = []
    for group, name, module in _entry_points():
        loader, parts = groups[group], module.split(".")
        if loader == "cli" or parts[0] != "devkit" or len(parts) < 2:
            continue
        target = parts[1]
        if target == loader or target in ALLOWED[loader] or target in DATA_AREAS:
            continue
        if ENTRY_POINT_EXCEPTIONS.get((group, name)) != target:
            violations.append(f"{group}:{name} = {module}: {loader} loads devkit.{target}")
    assert violations == []


def test_entry_point_exceptions_are_current() -> None:
    declared = {(group, name): module.split(".")[1] for group, name, module in _entry_points()}
    assert {key: declared.get(key) for key in ENTRY_POINT_EXCEPTIONS} == ENTRY_POINT_EXCEPTIONS


def test_distribution_bundles_have_no_workspace_knowledge() -> None:
    # Bundle authoring shares only the neutral ``devkit.distribution.content`` helpers with installation.
    violations = [
        f"{path.relative_to(SRC)}:{node.lineno}"
        for path in sorted((SRC / "distribution/bundles").rglob("*.py"))
        for node in ast.walk(ast.parse(path.read_text("utf-8")))
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("devkit.distribution.installation")
    ]
    assert violations == []


@pytest.mark.parametrize("area", sorted(DATA_AREAS))
def test_data_areas_import_nothing(area: str) -> None:
    # The package modules of a data area import nothing, and ``bundle/`` is no subpackage (no ``__init__.py``):
    # loading the area for its resources never runs bundle code such as ``authoring_guide``'s rules.
    package_modules = [path for path in _modules(area) if "bundle" not in path.relative_to(SRC / area).parts]
    imports = [
        f"{path.relative_to(SRC)}:{node.lineno}"
        for path in package_modules
        for node in ast.walk(ast.parse(path.read_text("utf-8")))
        if isinstance(node, (ast.Import, ast.ImportFrom)) and getattr(node, "module", None) != "__future__"
    ]
    assert imports == []
    assert [path.relative_to(SRC) for path in package_modules] == [Path(area, "__init__.py")]
    assert not list((SRC / area / "bundle").rglob("__init__.py"))
