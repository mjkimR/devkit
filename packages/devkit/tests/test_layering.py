"""The module layering of the devkit-agt wheel, checked statically over every import statement and entry point.

Lower layers never import higher ones, so a module can be understood, tested and eventually split out without the
modules above it. Each area may use the devkit-dist areas its row allows (devkit-dist itself never references this
wheel: ``packages/devkit-dist/tests/test_layering.py``). Test files under ``src`` (each rule's ``tests/`` folder) are
not production modules and are not scanned. Besides import statements, a string literal naming a devkit module in
``importlib.import_module``, ``importlib.util.find_spec`` or ``importlib.resources.files`` counts as an import, and so
does an entry point of ``pyproject.toml``: the area that loads its group, in either wheel, imports its target.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest
from devkit.cli import HARNESS_COMMANDS
from distsupport.layering import group_loaders, referenced_areas
from testsupport.layering import ALLOWED, DATA_AREAS, DIST_ALLOWED, PYPROJECT, SRC, dist_src


def _modules(area: str) -> list[Path]:
    """The production modules of an area: every ``.py`` file except those under a ``tests`` directory."""
    return [path for path in sorted((SRC / area).rglob("*.py")) if "tests" not in path.relative_to(SRC).parts]


def _package(path: Path) -> str:
    return ".".join(("devkit", *path.relative_to(SRC).parent.parts))


def test_every_area_is_declared() -> None:
    areas = {p.name for p in SRC.iterdir() if p.is_dir() and (p / "__init__.py").is_file()}
    assert areas == set(ALLOWED)
    # devkit-dist ships the top-level modules; no file of this wheel sits directly under devkit/.
    assert [p.name for p in SRC.iterdir() if p.is_file()] == []


@pytest.mark.parametrize("area", sorted(ALLOWED))
def test_area_imports_only_lower_layers(area: str) -> None:
    violations = [
        f"{path.relative_to(SRC)}:{line} imports devkit.{target}"
        for path in _modules(area)
        for target, line in sorted(referenced_areas(path.read_text("utf-8"), _package(path), area))
        if target not in ALLOWED[area]
    ]
    assert violations == []


def test_test_folders_are_not_scanned() -> None:
    scanned = {path.relative_to(SRC).as_posix() for path in _modules("rules")}
    assert "rules/rules/markdown_link/rule.py" in scanned
    assert not any("/tests/" in name for name in scanned)


# Entry points whose target the loading area may not import, each a known runtime coupling (group, entry name).
ENTRY_POINT_EXCEPTIONS: dict[tuple[str, str], str] = {
    ("devkit.host.services", "integration"): "integration",
    # Dependency inversion: gate registers its hook installation as a post-sync extension; distribution calls it
    # through ``devkit_core.core.extensions`` without importing gate code.
    ("devkit.post_sync", "gate-hooks"): "gate",
    # Dependency inversion: workflow registers the envelope hold check as a finish guard; worktree loads it through
    # its entry point (failing closed) without importing workflow code.
    ("devkit.finish_guard", "workflow-envelopes"): "workflow",
    # Dependency inversion: worktree registers its stale activity branch report as a hygiene extension; rules calls
    # it through ``devkit_core.core.extensions`` without importing worktree code.
    ("devkit.hygiene", "worktree-stale"): "worktree",
    # Dependency inversion: the engines register the commented templates of their reserved configuration tables;
    # distribution renders them without importing engine code.
    ("devkit.config_tables", "workflow"): "workflow",
    ("devkit.config_tables", "worktree"): "worktree",
}


def _entry_points() -> list[tuple[str, str, str]]:
    """``(group, name, target module)`` of every devkit-agt entry point in ``pyproject.toml``."""
    data = tomllib.loads(PYPROJECT.read_text("utf-8"))["project"]
    assert "scripts" not in data  # devkit-dist owns the devkit console script
    return [
        (group, name, value.split(":", 1)[0].strip())
        for group, entries in sorted(data.get("entry-points", {}).items())
        for name, value in sorted(entries.items())
    ]


def test_entry_point_groups_have_a_loading_area() -> None:
    groups = group_loaders(dist_src(), SRC, PYPROJECT.parents[1] / "devkit-mcp/src")
    assert {group for group, _, _ in _entry_points()} <= groups.keys()
    assert groups["devkit.bundles"] == "distribution" and groups["devkit.commands"] == "cli"
    assert groups["devkit.config_tables"] == "distribution"


def test_entry_points_load_only_lower_layers() -> None:
    groups = group_loaders(dist_src(), SRC, PYPROJECT.parents[1] / "devkit-mcp/src")
    allowed = {**DIST_ALLOWED, **ALLOWED, "devkit_mcp": {"core", "host", "advisory"}}
    violations = []
    for group, name, module in _entry_points():
        loader, parts = groups[group], module.split(".")
        if loader == "cli" or parts[0] != "devkit" or len(parts) < 2:
            continue
        target = parts[1]
        if target == loader or target in allowed[loader] or target in DATA_AREAS:
            continue
        if ENTRY_POINT_EXCEPTIONS.get((group, name)) != target:
            violations.append(f"{group}:{name} = {module}: {loader} loads devkit.{target}")
    assert violations == []


def test_entry_point_exceptions_are_current() -> None:
    declared = {(group, name): module.split(".")[1] for group, name, module in _entry_points()}
    assert {key: declared.get(key) for key in ENTRY_POINT_EXCEPTIONS} == ENTRY_POINT_EXCEPTIONS


def test_the_harness_names_of_devkit_dist_are_the_commands_devkit_agt_mounts() -> None:
    mounted = {name: module for group, name, module in _entry_points() if group == "devkit.commands"}
    assert set(HARNESS_COMMANDS) == set(mounted)
    assert all(module.split(".")[1] in ALLOWED for module in mounted.values())


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
