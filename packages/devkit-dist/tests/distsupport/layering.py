"""The module layering of the devkit-dist wheel: its areas, the edges between them and the static scanner.

Shared by ``test_layering`` (the edges and the devkit-agt boundary) and ``test_cli_imports`` (what a command
loads at run time). The scanner reads every import statement, including imports inside functions, a string literal
naming a devkit module in an importing call (``importlib.import_module``, ``importlib.util.find_spec``,
``importlib.resources.files``) and, with ``strings``, every string constant that is a dotted module path or a
``module:attribute`` reference.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src/devkit"
PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"
# Calls whose first argument, a module name, is imported (``files`` imports the module it reads resources of).
IMPORTING_CALLS = {"import_module", "find_spec", "files", "__import__"}

# ``advisory`` is the separate devkit-advisory distribution, below every area. The ``*_guide`` areas
# (``DATA_AREAS``) hold built-in bundle content and import nothing; ``distribution.guide`` is the ``devkit`` bundle.
ALLOWED: dict[str, set[str]] = {
    "advisory_guide": set(),
    "commits_guide": set(),
    "core": {"advisory"},
    "search": {"core", "advisory"},
    "host": {"core", "advisory"},
    "shared": {"core", "advisory"},
    "distribution": {"core", "advisory", "search", "host"},
}
DATA_AREAS = {"advisory_guide", "commits_guide"}
# The top-level modules (``devkit/cli.py``, ``devkit/__main__.py``) assemble the command line from any area above.
TOP_LEVEL = {"cli", "__main__"}
# The areas of the devkit-agt wheel: devkit-dist never references one, in code, strings or entry points.
AGT_AREAS = {
    "rules",
    "workflow",
    "gate",
    "worktree",
    "generated",
    "integration",
    "compact",
    "authoring_guide",
    "harness_guide",
}
# Rule code a data area ships under ``bundle/rules/`` is bundle content, not a module of this wheel: ``bundle/`` is no
# package, and the rule engine (devkit-agt) loads it from the synchronized, receipt-verified copies, so it may use the
# public rule API like the rules of any other bundle.
BUNDLE_CONTENT_ALLOWED: dict[str, set[str]] = {"advisory_guide": {"rules"}}

_MODULE_REFERENCE = re.compile(r"devkit\.([A-Za-z_]\w*)(?:\.[A-Za-z_]\w*)*(?::[A-Za-z_][\w.]*)?")


def modules(area: str) -> list[Path]:
    """The production modules of an area (or a top-level module): every ``.py`` file outside a ``tests`` directory."""
    if area in TOP_LEVEL:
        return [SRC / f"{area}.py"]
    return [path for path in sorted((SRC / area).rglob("*.py")) if "tests" not in path.relative_to(SRC).parts]


def package(path: Path) -> str:
    return ".".join(("devkit", *path.relative_to(SRC).parent.parts))


def is_bundle_content(path: Path) -> bool:
    """Whether ``path`` lies in the ``bundle/`` tree of a data area (content, never imported through the package)."""
    parts = path.relative_to(SRC).parts
    return parts[0] in DATA_AREAS and "bundle" in parts[1:]


def referenced_areas(source: str, package: str, area: str, *, strings: bool = False) -> set[tuple[str, int]]:
    """``(area, line)`` for every other devkit area ``source`` references: imports (also inside functions), string
    literals passed to ``IMPORTING_CALLS`` and, with ``strings``, string constants that are a dotted module path or a
    ``module:attribute`` reference.

    ``package`` is the dotted package containing the module, for resolving relative imports.
    """
    tree = ast.parse(source)
    found: set[tuple[str, int]] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Call):
            func = node.func
            called = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else None
            first = node.args[0] if node.args else None
            if called in IMPORTING_CALLS and isinstance(first, ast.Constant) and isinstance(first.value, str):
                names = [first.value]
        elif strings and isinstance(node, ast.Constant) and isinstance(node.value, str):
            match = _MODULE_REFERENCE.fullmatch(node.value)
            if match:
                names = [node.value.split(":", 1)[0]]
        elif not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        elif isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        else:
            if node.level:
                base = package.split(".")
                base = base[: len(base) - (node.level - 1)]
                names = [".".join([*base, node.module] if node.module else base)]
            elif node.module:
                names = [node.module]
            if names == ["devkit"]:
                names = [f"devkit.{alias.name}" for alias in node.names]
        for name in names:
            parts = name.split(".")
            if parts[0] == "devkit" and len(parts) > 1 and parts[1] != area:
                found.add((parts[1], getattr(node, "lineno", 0)))
    return found


def group_loaders(*sources: Path) -> dict[str, str]:
    """Entry-point group -> the area whose code loads it, from every ``*GROUP = "devkit..."`` constant of ``sources``."""
    groups: dict[str, str] = {}
    for src in sources:
        for path in sorted(src.rglob("*.py")):
            rel = path.relative_to(src)
            if "tests" in rel.parts:
                continue
            area = rel.parts[0] if len(rel.parts) > 1 else rel.stem
            for node in ast.walk(ast.parse(path.read_text("utf-8"))):
                if (
                    isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id.endswith("GROUP") for target in node.targets)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                    and node.value.value.startswith("devkit.")
                ):
                    groups[node.value.value] = area
    return groups
