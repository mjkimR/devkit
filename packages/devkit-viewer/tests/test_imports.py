"""Viewer uses shared primitives, distribution project/CLI support and immutable shared reports.

It never imports devkit-spec, so it stays independent of SDD models.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

SRC = Path(__file__).parents[1] / "src/devkit_viewer"
ALLOWED = (
    "devkit_core.base",
    "devkit_core.core",
    "devkit_dist.adapters.cli",
    "devkit_dist.features.project.repositories",
    "devkit.advisory",
    "devkit_viewer",
    "click",
    "devkit_dist.features.shared.models.api",
    "devkit_dist.features.shared.models.errors",
    "devkit_dist.features.shared.repositories.local",
)


def _imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def test_imports_stay_on_the_shared_core() -> None:
    offending = {
        f"{path.relative_to(SRC)}: {name}"
        for path in SRC.rglob("*.py")
        for name in _imports(path)
        if name.split(".")[0] not in sys.stdlib_module_names
        and not any(name == allowed or name.startswith(f"{allowed}.") for allowed in ALLOWED)
    }
    assert not offending


def test_browse_layers_do_not_import_transport_or_application_layers() -> None:
    feature = "devkit_viewer.features.browse."
    prohibited = {
        "models": {"repositories", "services", "usecases", "cli", "http"},
        "repositories": {"services", "usecases", "cli", "http"},
        "services": {"usecases", "cli", "http"},
        "usecases": {"cli", "http"},
    }
    violations = {
        f"{path.relative_to(SRC)}: {name}"
        for layer, forbidden in prohibited.items()
        for path in (SRC / "features/browse" / layer).rglob("*.py")
        for name in _imports(path)
        if name.startswith(feature) and name.removeprefix(feature).split(".")[0] in forbidden
    }
    assert not violations
