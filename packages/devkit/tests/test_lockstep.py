"""devkit-dist, devkit-agt and devkit-advisory are released in lockstep from one tag, at one version.

devkit-agt pins the exact devkit-dist and devkit-advisory versions and devkit-dist the exact devkit-advisory version,
so a consumer that installs them together resolves one ``devkit`` namespace of matching parts. ``devkit`` stays a
namespace package all three wheels share: none ships ``devkit/__init__.py``, and no installed path belongs to two of
them (``ADR-dist-module-split``).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[2]
WHEELS = {"devkit-dist": "devkit-dist", "devkit-agt": "devkit", "devkit-advisory": "devkit-advisory"}


def _project(directory: str) -> dict:
    return tomllib.loads((PACKAGES / directory / "pyproject.toml").read_text())["project"]


def _pins(project: dict, name: str) -> list[str]:
    return [dep.split(";")[0].split("#")[0].replace(" ", "") for dep in project["dependencies"] if dep.startswith(name)]


def test_the_three_wheels_share_one_version() -> None:
    versions = {name: _project(directory)["version"] for name, directory in WHEELS.items()}
    assert len(set(versions.values())) == 1, versions


def test_each_wheel_pins_the_exact_version_of_the_wheels_below_it() -> None:
    agt, dist = _project("devkit"), _project("devkit-dist")
    version = agt["version"]
    assert _pins(agt, "devkit-dist") == [f"devkit-dist=={version}"]
    assert _pins(agt, "devkit-advisory") == [f"devkit-advisory=={version}"]
    assert _pins(dist, "devkit-advisory") == [f"devkit-advisory=={version}"]
    assert _pins(dist, "devkit-agt") == []  # devkit-dist never depends on the harness


def test_devkit_agt_extras_pass_through_to_devkit_dist() -> None:
    agt, dist = _project("devkit"), _project("devkit-dist")
    assert agt["optional-dependencies"] == {"mcp": ["devkit-dist[mcp]"], "search": ["devkit-dist[search]"]}
    assert set(dist["optional-dependencies"]) == {"mcp", "search"}


def test_devkit_is_a_namespace_package_and_no_path_has_two_owners() -> None:
    trees = {name: PACKAGES / directory / "src/devkit" for name, directory in WHEELS.items()}
    shipped: dict[str, str] = {}
    for name, tree in trees.items():
        assert not (tree / "__init__.py").exists(), name
        for path in tree.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                rel = path.relative_to(tree).as_posix()
                assert rel not in shipped, f"{rel} is shipped by {shipped.get(rel)} and {name}"
                shipped[rel] = name
    assert shipped["advisory/py.typed"] == "devkit-advisory"
    assert shipped["cli.py"] == "devkit-dist" and shipped["__main__.py"] == "devkit-dist"
    assert "py.typed" not in shipped  # each area carries its own marker (PEP 561 for namespace packages)
