"""Distribution ownership, feature boundaries and dependency direction."""

from __future__ import annotations

import ast
import tomllib

import pytest
from distsupport.layering import (
    DATA_AREAS,
    FEATURES,
    LAZY_IMPORT_AREAS,
    PYPROJECT,
    SRC,
    TOP_LEVEL,
    is_bundle_content,
    modules,
    package,
    references,
)


def test_package_structure() -> None:
    assert (SRC / "__init__.py").is_file()
    assert not (SRC / "core").exists()
    assert {p.name for p in (SRC / "features").iterdir() if p.is_dir() and p.name != "__pycache__"} == FEATURES


@pytest.mark.parametrize("area", sorted([*LAZY_IMPORT_AREAS, *TOP_LEVEL]))
def test_distribution_never_imports_the_harness(area: str) -> None:
    assert not [
        (str(p), line)
        for p in modules(area)
        if not is_bundle_content(p)
        for name, line in references(p.read_text(), package(p), strings=True)
        if name == "devkit_agt" or name.startswith("devkit_agt.")
    ]


@pytest.mark.parametrize("area", sorted(DATA_AREAS))
def test_bundle_packages_only_contain_data(area: str) -> None:
    paths = [p for p in modules(area) if not is_bundle_content(p)]
    assert len(paths) == 1 and paths[0].name == "__init__.py"
    assert not [
        n for p in paths for n in ast.walk(ast.parse(p.read_text())) if isinstance(n, (ast.Import, ast.ImportFrom))
    ]


def test_entrypoints_resolve_only_to_owned_modules() -> None:
    project = tomllib.loads(PYPROJECT.read_text())["project"]
    entries = [*project["scripts"].values(), *[v for group in project["entry-points"].values() for v in group.values()]]
    assert entries and all(v.startswith("devkit_dist.") for v in entries)
    for value in entries:
        path = SRC.joinpath(*value.split(":", 1)[0].split(".")[1:])
        assert path.with_suffix(".py").is_file() or (path / "__init__.py").is_file()


def test_reference_scanner_sees_relative_imports_and_dynamic_paths() -> None:
    source = "from ..usecases.sync import run\nfrom devkit_agt.features.rules import rule\nimportlib.import_module('devkit_dist.features.host.cli')\n"
    found = references(source, "devkit_dist.features.distribution.services")
    assert {name for name, _ in found} >= {
        "devkit_dist.features.distribution.usecases.sync",
        "devkit_agt.features.rules",
        "devkit_dist.features.host.cli",
    }
