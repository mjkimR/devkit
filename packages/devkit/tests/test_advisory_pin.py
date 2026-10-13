"""devkit and devkit-advisory are released in lockstep from one tag.

devkit pins the exact devkit-advisory version, so a consumer that installs both (devkit for tooling, the library
at runtime) resolves one ``devkit.advisory``, and ``devkit`` stays a namespace package that both wheels share.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[2]


def _project(name: str) -> dict:
    return tomllib.loads((PACKAGES / name / "pyproject.toml").read_text())["project"]


def test_devkit_pins_its_own_version_of_devkit_advisory() -> None:
    devkit, advisory = _project("devkit"), _project("devkit-advisory")
    assert advisory["version"] == devkit["version"]
    pins = [dep.split(";")[0].replace(" ", "") for dep in devkit["dependencies"] if dep.startswith("devkit-advisory")]
    assert pins == [f"devkit-advisory=={devkit['version']}"]


def test_devkit_is_a_namespace_package() -> None:
    assert not (PACKAGES / "devkit/src/devkit/__init__.py").exists()
    assert not (PACKAGES / "devkit/src/devkit/advisory").exists()  # shipped only by devkit-advisory
