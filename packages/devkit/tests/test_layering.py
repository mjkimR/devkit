"""Check harness package ownership, entry points and import-free bundle resources.

The repository architecture rule owns the generic dependency graph.
"""

from __future__ import annotations

import ast
import importlib.util
import tomllib
from pathlib import Path

import pytest
from devkit_dist.cli import HARNESS_COMMANDS
from testsupport.layering import DATA_AREAS, FEATURES, PYPROJECT, SRC

LAYERS = {"cli", "mcp", "usecases", "services", "repositories", "models"}


def _modules(area: str) -> list[Path]:
    return [
        path for path in sorted((SRC / "features" / area).rglob("*.py")) if "tests" not in path.relative_to(SRC).parts
    ]


def test_namespace_and_feature_layout() -> None:
    assert (SRC / "__init__.py").is_file()
    assert (SRC / "py.typed").is_file()
    assert not (SRC / "core").exists()
    assert {p.name for p in (SRC / "features").iterdir() if p.is_dir() and p.name != "__pycache__"} == FEATURES
    for feature in FEATURES:
        root = SRC / "features" / feature
        assert (root / "__init__.py").is_file()
        areas = {p.stem if p.is_file() else p.name for p in root.iterdir()}
        assert areas - {"__init__", "__main__", "py", "__pycache__", "py.typed"} <= LAYERS
        assert (root / "usecases").is_dir()


def test_rule_tests_are_excluded_from_production_scan() -> None:
    scanned = {path.relative_to(SRC).as_posix() for path in _modules("rules")}
    assert "features/rules/services/builtins/markdown_link/rule.py" in scanned
    assert not any("/tests/" in name for name in scanned)


def _entry_points() -> list[tuple[str, str, str]]:
    project = tomllib.loads(PYPROJECT.read_text("utf-8"))["project"]
    assert "scripts" not in project
    return [
        (group, name, value.split(":", 1)[0])
        for group, entries in project.get("entry-points", {}).items()
        for name, value in entries.items()
    ]


def test_entry_points_resolve_in_the_owning_namespace() -> None:
    for group, _, module in _entry_points():
        assert module.startswith("devkit_agt.")
        assert importlib.util.find_spec(module) is not None
        if group == "devkit.commands":
            assert module.split(".")[2] in FEATURES
            assert module.split(".")[3] == "cli"


def test_the_distribution_harness_names_match_the_mounted_commands() -> None:
    mounted = {name for group, name, _ in _entry_points() if group == "devkit.commands"}
    assert set(HARNESS_COMMANDS) == mounted


@pytest.mark.parametrize("area", sorted(DATA_AREAS))
def test_data_packages_import_nothing(area: str) -> None:
    path = SRC / area / "__init__.py"
    imports = [
        node
        for node in ast.walk(ast.parse(path.read_text("utf-8")))
        if isinstance(node, (ast.Import, ast.ImportFrom)) and getattr(node, "module", None) != "__future__"
    ]
    assert imports == []
    assert not list((SRC / area / "bundle").rglob("__init__.py"))
