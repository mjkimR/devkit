"""Workspace release versions and independently owned wheel import paths stay consistent."""

from __future__ import annotations

import tomllib
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[4]
WHEELS = {
    "devkit-core": "devkit-core",
    "devkit-cli": "devkit-cli",
    "devkit-dist": "devkit-dist",
    "devkit-agt": "devkit",
    "devkit-advisory": "devkit-advisory",
    "devkit-mcp": "devkit-mcp",
}


def _project(directory: str) -> dict:
    return tomllib.loads((PACKAGES / directory / "pyproject.toml").read_text())["project"]


def _pins(project: dict, name: str) -> list[str]:
    return [dep.split(";")[0].split("#")[0].replace(" ", "") for dep in project["dependencies"] if dep.startswith(name)]


def test_each_wheel_pins_actual_dependency_versions() -> None:
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name

    root = PACKAGES.parent
    projects = [
        tomllib.loads(p.read_text())["project"]
        for directory in ("packages", "tools")
        for p in (root / directory).glob("*/pyproject.toml")
    ]
    versions = {canonicalize_name(p["name"]): p["version"] for p in projects}
    for project in projects:
        requirements = [
            *project.get("dependencies", []),
            *(r for rs in project.get("optional-dependencies", {}).values() for r in rs),
        ]
        for raw in requirements:
            requirement = Requirement(raw)
            name = canonicalize_name(requirement.name)
            if name in versions and requirement.specifier:
                assert str(requirement.specifier) == "==" + versions[name]
    assert _pins(_project("devkit-dist"), "devkit-agt") == []


def test_devkit_agt_extras_pass_through_to_devkit_dist() -> None:
    agt, dist = _project("devkit"), _project("devkit-dist")
    assert agt["optional-dependencies"] == {
        "mcp": [f"devkit-mcp=={_project('devkit-mcp')['version']}"],
        "search": ["devkit-dist[search]"],
    }
    assert set(dist["optional-dependencies"]) == {"search"}


def test_application_wheels_own_independent_packages_and_no_path_has_two_owners() -> None:
    roots = {
        "devkit-core": "devkit_core",
        "devkit-cli": "devkit_cli",
        "devkit-dist": "devkit_dist",
        "devkit-agt": "devkit_agt",
        "devkit-advisory": "devkit",
        "devkit-mcp": "devkit_mcp",
    }
    shipped: dict[str, str] = {}
    for name, directory in WHEELS.items():
        source = PACKAGES / directory / "src"
        tree = source / roots[name]
        assert tree.is_dir(), name
        if name == "devkit-advisory":
            assert not (tree / "__init__.py").exists()
        else:
            assert (tree / "__init__.py").is_file(), name
            assert (tree / "py.typed").is_file(), name
            assert not any(
                path.is_file() for path in (source / "devkit").rglob("*") if "__pycache__" not in path.parts
            ), name
        for path in tree.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                rel = path.relative_to(source).as_posix()
                assert rel not in shipped, f"{rel} is shipped by {shipped.get(rel)} and {name}"
                shipped[rel] = name
    assert shipped["devkit/advisory/py.typed"] == "devkit-advisory"
    assert shipped["devkit_dist/cli.py"] == "devkit-dist"
    assert shipped["devkit_dist/__main__.py"] == "devkit-dist"
    assert "devkit/py.typed" not in shipped
