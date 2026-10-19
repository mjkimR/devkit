"""The module layering of the devkit-dist wheel, checked statically over every import statement and entry point.

Lower layers never import higher ones, so a module can be understood, tested and split without the modules above
it, and no module of this wheel references the devkit-agt wheel that depends on it (``ADR-dist-module-split``):
not by import, not by an importing call, not by a dotted module path or ``module:attribute`` string (the root
``COMMANDS`` map included), and not by an entry point. ``devkit.cli`` and ``devkit.__main__`` assemble the command
line from this wheel's areas; the harness command names they hold are names, not module references. Test files under
``src`` are not production modules and are not scanned.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest
from distsupport.layering import (
    AGT_AREAS,
    ALLOWED,
    BUNDLE_CONTENT_ALLOWED,
    DATA_AREAS,
    PYPROJECT,
    SRC,
    TOP_LEVEL,
    group_loaders,
    is_bundle_content,
    modules,
    package,
    referenced_areas,
)


def test_every_area_is_declared() -> None:
    areas = {p.name for p in SRC.iterdir() if p.is_dir() and (p / "__init__.py").is_file()}
    assert areas == set(ALLOWED)
    assert {p.stem for p in SRC.glob("*.py")} == TOP_LEVEL
    assert not (SRC / "__init__.py").exists()  # a namespace package shared with devkit-advisory and devkit-agt


@pytest.mark.parametrize("area", sorted(ALLOWED))
def test_area_imports_only_lower_layers(area: str) -> None:
    violations = []
    for path in modules(area):
        allowed = ALLOWED[area] | (BUNDLE_CONTENT_ALLOWED.get(area, set()) if is_bundle_content(path) else set())
        violations += [
            f"{path.relative_to(SRC)}:{line} imports devkit.{target}"
            for target, line in sorted(referenced_areas(path.read_text("utf-8"), package(path), area))
            if target not in allowed
        ]
    assert violations == []


@pytest.mark.parametrize("area", sorted([*ALLOWED, *TOP_LEVEL]))
def test_no_module_references_a_devkit_agt_area(area: str) -> None:
    violations = [
        f"{path.relative_to(SRC)}:{line} references devkit.{target}"
        for path in modules(area)
        if not is_bundle_content(path)
        for target, line in sorted(referenced_areas(path.read_text("utf-8"), package(path), area, strings=True))
        if target in AGT_AREAS
    ]
    assert violations == []


def test_the_command_line_imports_only_this_wheel() -> None:
    for top in sorted(TOP_LEVEL):
        found = {target for target, _ in referenced_areas((SRC / f"{top}.py").read_text("utf-8"), "devkit", top)}
        assert found <= {*ALLOWED, "advisory", *TOP_LEVEL}


def test_the_scanner_sees_absolute_relative_and_nested_imports() -> None:
    source = (
        "from devkit.rules import x\nimport devkit.gate.hooks.hooks\nfrom devkit import workflow\n"
        "from . import sibling\nfrom .other import z\n"
        "def f():\n    from ..distribution import y\n"
    )
    found = {target for target, _ in referenced_areas(source, "devkit.core", "core")}
    assert found == {"rules", "gate", "workflow", "distribution"}


def test_the_scanner_sees_module_names_passed_to_importing_calls() -> None:
    source = (
        "import importlib\nfrom importlib import resources\n"
        "importlib.import_module('devkit.gate.engine')\nresources.files('devkit.rules.rules')\n"
        "importlib.util.find_spec('devkit.workflow')\nprint('devkit.search')\n"
    )
    found = {target for target, _ in referenced_areas(source, "devkit.core", "core")}
    assert found == {"gate", "rules", "workflow"}


def test_the_scanner_sees_module_strings_but_not_prose_or_names() -> None:
    source = (
        'COMMANDS = {"run": "devkit.compact.cli:run_cmd", "rules": "devkit.rules.cli:cli"}\n'
        'TARGET = "devkit.worktree"\n'
        'HARNESS = ("rules", "run")\n'
        'PROSE = "devkit.rules is a module of devkit-agt"\n'
        'def f():\n    """See devkit.gate for the hooks."""\n'
    )
    found = {target for target, _ in referenced_areas(source, "devkit", "cli", strings=True)}
    assert found == {"compact", "rules", "worktree"}


def test_bundle_rule_content_is_the_only_exception() -> None:
    # The advisory bundle's rule is loaded by devkit rules from the synchronized copy; nothing else may use the engine.
    content = [path.relative_to(SRC).as_posix() for path in modules("advisory_guide") if is_bundle_content(path)]
    assert "advisory_guide/bundle/rules/unique_code/rule.py" in content
    assert set(BUNDLE_CONTENT_ALLOWED) <= DATA_AREAS


def _entry_points() -> list[tuple[str, str, str]]:
    """``(group, name, target module)`` of every devkit-dist entry point (the console script included)."""
    data = tomllib.loads(PYPROJECT.read_text("utf-8"))["project"]
    found = [
        (group, name, value.split(":", 1)[0].strip())
        for group, entries in sorted(data.get("entry-points", {}).items())
        for name, value in sorted(entries.items())
    ]
    found += [("console_scripts", name, value.split(":", 1)[0].strip()) for name, value in data["scripts"].items()]
    return found


def test_entry_point_groups_have_a_loading_area() -> None:
    groups = group_loaders(SRC)
    assert {group for group, _, _ in _entry_points() if group != "console_scripts"} <= groups.keys()
    assert groups["devkit.bundles"] == "distribution" and groups["devkit.commands"] == "cli"
    assert groups["devkit.config_tables"] == "distribution" and groups["devkit.config_template"] == "distribution"


def test_entry_points_target_only_this_wheel_and_lower_layers() -> None:
    groups = {**group_loaders(SRC), "console_scripts": "cli"}
    violations = []
    for group, name, module in _entry_points():
        loader, target = groups[group], module.split(".")[1]
        if target in AGT_AREAS:
            violations.append(f"{group}:{name} = {module}: devkit-dist references devkit-agt")
        elif loader != "cli" and not (target == loader or target in ALLOWED[loader] or target in DATA_AREAS):
            violations.append(f"{group}:{name} = {module}: {loader} loads devkit.{target}")
    assert violations == []
    assert ("console_scripts", "devkit", "devkit.cli") in _entry_points()


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
    # loading the area for its resources never runs bundle code such as the advisory bundle's rule.
    package_modules = [path for path in modules(area) if not is_bundle_content(path)]
    imports = [
        f"{path.relative_to(SRC)}:{node.lineno}"
        for path in package_modules
        for node in ast.walk(ast.parse(path.read_text("utf-8")))
        if isinstance(node, (ast.Import, ast.ImportFrom)) and getattr(node, "module", None) != "__future__"
    ]
    assert imports == []
    assert [path.relative_to(SRC) for path in package_modules] == [Path(area, "__init__.py")]
    assert not list((SRC / area / "bundle").rglob("__init__.py"))
