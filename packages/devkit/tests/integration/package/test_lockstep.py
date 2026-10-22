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


def test_release_wheels_share_one_version() -> None:
    versions = {name: _project(directory)["version"] for name, directory in WHEELS.items()}
    assert len(set(versions.values())) == 1, versions


def test_each_wheel_pins_the_exact_version_of_the_wheels_below_it() -> None:
    agt, dist = _project("devkit"), _project("devkit-dist")
    version = agt["version"]
    assert _pins(agt, "devkit-dist") == [f"devkit-dist=={version}"]
    assert _pins(agt, "devkit-advisory") == [f"devkit-advisory=={version}"]
    assert _pins(dist, "devkit-advisory") == [f"devkit-advisory=={version}"]
    assert _pins(dist, "devkit-cli") == [f"devkit-cli=={version}"]
    assert _pins(_project("devkit-cli"), "devkit-advisory") == [f"devkit-advisory=={version}"]
    assert _pins(dist, "devkit-agt") == []  # devkit-dist never depends on the harness


def test_every_release_install_command_with_devkit_dist_names_its_companion_wheels() -> None:
    # SPEC-cli-toolkit AC-11: no index serves the wheels devkit-dist pins, so each command must name them.
    release = (PACKAGES.parent / "scripts/release.sh").read_text()
    commands = [line for line in release.splitlines() if line.startswith("uv ") and "$dist_wheel" in line]
    assert commands
    assert [line for line in commands if not all(f"${w}_wheel" in line for w in ("core", "cli", "advisory"))] == []


def test_devkit_agt_extras_pass_through_to_devkit_dist() -> None:
    agt, dist = _project("devkit"), _project("devkit-dist")
    assert agt["optional-dependencies"] == {"mcp": ["devkit-mcp==0.1.1"], "search": ["devkit-dist[search]"]}
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
