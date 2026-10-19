"""``devkit_viewer`` builds on devkit's shared core only: ``devkit.core``, ``devkit.advisory``, ``click`` and the
standard library. It never imports devkit-spec or another devkit area, so it stays independent of SDD models."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

SRC = Path(__file__).parents[1] / "src/devkit_viewer"
ALLOWED = ("devkit.core", "devkit.advisory", "devkit_viewer", "click")


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
