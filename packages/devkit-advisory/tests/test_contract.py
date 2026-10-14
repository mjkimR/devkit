"""The runtime contract of devkit-advisory: standard library only, nothing registered, nothing else of devkit.

Other repositories install this distribution in their production environments, so anything it imports or
registers reaches them: a third-party dependency, an import of another devkit module (which this wheel does not
ship) or an entry point that makes devkit discover content there.
"""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "src/devkit/advisory"


def _imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text("utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            names.add(node.module)
    return names


def test_advisory_is_standard_library_only() -> None:
    foreign = {
        f"{path.name}: {name}"
        for path in sorted(SOURCE.glob("*.py"))
        for name in _imports(path)
        if not name.startswith("devkit.advisory") and name.split(".")[0] not in sys.stdlib_module_names
    }
    assert foreign == set()


def test_the_distribution_registers_and_requires_nothing() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project["dependencies"] == []
    assert "entry-points" not in project and "scripts" not in project
    # `devkit` stays a namespace package: an __init__.py here would shadow the devkit distribution's modules.
    assert not (ROOT / "src/devkit/__init__.py").exists()


def test_the_public_names_are_pinned() -> None:
    # The semver surface: removing or renaming a name here is breaking (a minor bump within 0.x); adding one is not.
    import devkit.advisory as advisory
    from devkit.advisory import CONTINUATION, FIELDS, HEADLINE, Level

    assert set(advisory.__all__) == {
        "ACTION_TEXT",
        "CONTINUATION",
        "FIELDS",
        "HEADLINE",
        "UNEXPECTED_CODE",
        "ActionMode",
        "Actor",
        "Advisory",
        "AdvisoryError",
        "AdvisoryFields",
        "ExitCode",
        "Level",
        "Retry",
        "as_advisory_error",
        "render_error",
    }
    assert all(hasattr(advisory, name) for name in advisory.__all__)
    # The block grammar parsers such as devkit.compact recognize: protocol, section 3.
    assert HEADLINE == {Level.ERROR: "[ERROR]  ", Level.WARNING: "[WARN]   ", Level.NOTICE: "[NOTICE] "}
    assert FIELDS == ("[ACTION] ", "[WHEN]   ", "[TARGET] ", "[FIX]    ", "[REPORT] ", "[DETAIL] ")
    assert CONTINUATION == " " * 9
