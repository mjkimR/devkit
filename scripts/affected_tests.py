"""Select and run the workspace tests the changes since a base ref can affect.

The changed paths since the merge base (committed, staged, unstaged and untracked) map to test paths: shared
foundations to the full suite, data files to the tests that read them, a source area to the test groups that depend
on it or on an area importing it. The selection narrows a development run; the full suite on the reviewed head stays
the safety net for what static imports cannot show.
"""

from __future__ import annotations

import ast
import logging
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Literal

import click
from devkit.advisory import Actor, AdvisoryError, Retry
from devkit.core.cli import boundary

ROOT = Path(__file__).resolve().parents[1]
DEVKIT = "packages/devkit"
DEVKIT_SRC = f"{DEVKIT}/src/devkit"

logger = logging.getLogger(__name__)

# Changes every test can depend on: the lowest layers, the CLI assembly, packaging and shared test fixtures.
FULL_PREFIXES = (f"{DEVKIT_SRC}/core/", "packages/devkit-advisory/", f"{DEVKIT}/tests/testsupport/")
FULL_FILES = frozenset({f"{DEVKIT_SRC}/cli.py", f"{DEVKIT_SRC}/__main__.py", "uv.lock"})
FULL_NAMES = frozenset({"pyproject.toml", "conftest.py"})

# Repository files that tests read directly, which imports do not show: prefix -> test paths.
DATA: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "docs/",
        (
            f"{DEVKIT}/tests/test_documented_codes.py",
            "packages/devkit-spec/tests/test_documented_codes.py",
            f"{DEVKIT}/tests/rules/test_docs.py",
            f"{DEVKIT}/tests/workflow/test_library.py",
        ),
    ),
    ("examples/", ("packages/devkit-starter/tests", f"{DEVKIT}/tests/workflow/test_library.py")),
    ("models/", (f"{DEVKIT}/tests/search",)),
    ("scripts/module.sh", (f"{DEVKIT}/tests/test_module_script.py",)),
    ("scripts/_lib.sh", (f"{DEVKIT}/tests/test_module_script.py",)),
    ("justfile", (f"{DEVKIT}/tests/test_module_script.py",)),
    ("scripts/check_test_environment.py", (f"{DEVKIT}/tests/test_test_environment.py",)),
    ("scripts/fetch_model.py", (f"{DEVKIT}/tests/search/test_packaging.py",)),
    ("scripts/affected_tests.py", (f"{DEVKIT}/tests/test_affected_tests.py",)),
)
# Tests over devkit's whole source tree (layering, documented codes, CLI wiring, stdout kinds), run for any devkit
# source change.
SOURCE_TREE_TESTS = tuple(
    f"{DEVKIT}/tests/{name}"
    for name in (
        "test_layering.py",
        "test_documented_codes.py",
        "test_cli_imports.py",
        "test_cli_plugins.py",
        "core/test_cli.py",
    )
)

# The devkit-viewer frontend: pytest never exercises it, so a change there selects no tests and names the frontend
# checks (Node and npm) instead, rebuilding the committed page last.
FRONTEND_PREFIXES = ("packages/devkit-viewer/frontend/", "scripts/viewer.sh")
FRONTEND_CHECK = "just viewer install && just viewer lint && just viewer check && just viewer test && just viewer build"

# Paths no test reads: planning records, agent projections, guides, CI and release scripts.
UNTESTED_PREFIXES = (
    "specs/",
    "guides/",
    ".claude/",
    ".agents/",
    ".codex/",
    ".devkit/",
    ".github/",
    "scripts/smoke.sh",
    "scripts/smoke_integration.py",
    "scripts/release.sh",
)
UNTESTED_FILES = frozenset({".gitignore", ".python-version"})
# Markdown at the repository root or a package root (README, AGENTS).
UNTESTED_MARKDOWN = re.compile(r"(packages/[^/]+/)?[^/]+\.md")

# Calls whose first argument, a module name, is imported (as in the layering test).
_IMPORTING_CALLS = frozenset({"import_module", "find_spec", "files", "__import__"})


@dataclass(frozen=True)
class Selection:
    mode: Literal["full", "partial", "none"]
    paths: tuple[str, ...]  # repository-relative and sorted; empty unless partial
    reason: str  # full: the triggering path; partial: what changed; none: "frontend" or "untested"
    frontend: bool = False  # a frontend path changed: the frontend checks are due


@dataclass(frozen=True)
class Group:
    """Test paths selected together, and the nodes (devkit areas or workspace packages) they depend on."""

    paths: tuple[str, ...]
    depends: frozenset[str]


class Workspace:
    """The nodes, their static import graph and the test groups of one workspace checkout."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.packages = self._packages()
        self._helpers: dict[Path, set[str]] = {}
        directories = [*(root / DEVKIT_SRC).iterdir(), *(root / DEVKIT / "tests").iterdir()]
        self.areas = sorted({p.name for p in directories if p.is_dir()} - {"__pycache__", "testsupport"})

    def _packages(self) -> dict[str, str]:
        """Package directory -> its import package, for every workspace package except devkit and devkit-advisory."""
        found: dict[str, str] = {}
        for src in sorted((self.root / "packages").glob("*/src")):
            directory = src.parent.name
            if directory in ("devkit", "devkit-advisory"):
                continue
            names = [p.name for p in src.iterdir() if p.is_dir() and p.name.isidentifier()]
            if len(names) == 1:
                found[directory] = names[0]
        return found

    def node_of(self, module: str) -> str | None:
        """The node a dotted module name belongs to."""
        parts = module.split(".")
        if parts[0] == "devkit" and len(parts) > 1:
            if parts[1] in ("cli", "__main__"):
                return "devkit.core"
            return f"devkit.{parts[1]}" if parts[1] in self.areas or parts[1] == "advisory" else None
        return parts[0] if parts[0] in self.packages.values() else None

    def imports(self, files: Iterable[Path]) -> set[str]:
        """The nodes the given Python files import, by statement or by an importing call on a literal name."""
        found: set[str] = set()
        for path in files:
            try:
                tree = ast.parse(path.read_bytes())
            except (OSError, SyntaxError, ValueError) as exc:
                logger.info("skipped %s: %s", path, exc)
                continue
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                    names = [node.module, *(f"{node.module}.{alias.name}" for alias in node.names)]
                elif isinstance(node, ast.Call) and node.args:
                    func = node.func
                    called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
                    first = node.args[0]
                    if called in _IMPORTING_CALLS and isinstance(first, ast.Constant) and isinstance(first.value, str):
                        names = [first.value]
                found.update(n for n in map(self.node_of, names) if n)
            found |= self._helper_imports(tree)
        return found

    def _helper_imports(self, tree: ast.Module) -> set[str]:
        """The nodes of the shared ``testsupport`` helpers a file imports at module level.

        A helper imported inside a function counts for that test only, so it is left out like any data dependency.
        """
        found: set[str] = set()
        for node in tree.body:
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                modules = [node.module, *(f"{node.module}.{alias.name}" for alias in node.names)]
            for module in modules:
                parts = module.split(".")
                if parts[0] != "testsupport" or len(parts) < 2:
                    continue
                helper = self.root / DEVKIT / "tests/testsupport" / f"{parts[1]}.py"
                if helper not in self._helpers:
                    self._helpers[helper] = set()  # a cycle between helpers ends here
                    self._helpers[helper] = self.imports([helper]) if helper.is_file() else set()
                found |= self._helpers[helper]
        return found

    def _python(self, directory: Path, *, tests: bool) -> Iterator[Path]:
        """The Python files under a directory: only those in a ``tests`` directory, or only those outside one."""
        if not directory.is_dir():
            return
        for path in sorted(directory.rglob("*.py")):
            in_tests = "tests" in path.relative_to(directory).parts[:-1]
            if in_tests == tests and "__pycache__" not in path.parts:
                yield path

    def sources(self) -> dict[str, Path]:
        """Node -> its production source directory."""
        nodes = {f"devkit.{area}": self.root / DEVKIT_SRC / area for area in self.areas}
        for directory, package in self.packages.items():
            nodes[package] = self.root / "packages" / directory / "src" / package
        return nodes

    def dependents(self, changed: set[str]) -> set[str]:
        """The changed nodes and every node that imports one of them, transitively."""
        imported_by: dict[str, set[str]] = {}
        for node, directory in self.sources().items():
            for imported in self.imports(self._python(directory, tests=False)):
                if imported != node:
                    imported_by.setdefault(imported, set()).add(node)
        affected, pending = set(changed), list(changed)
        while pending:
            for node in imported_by.get(pending.pop(), ()):
                if node not in affected:
                    affected.add(node)
                    pending.append(node)
        return affected

    def _has_tests(self, directory: Path) -> bool:
        return directory.is_dir() and any(p.name.startswith("test_") for p in directory.rglob("*.py"))

    @cached_property
    def groups(self) -> list[Group]:
        groups: list[Group] = []
        for area in self.areas:
            tests, src = self.root / DEVKIT / "tests" / area, self.root / DEVKIT_SRC / area
            paths = [p for p in (tests, src) if self._has_tests(p)]
            if paths:
                files = [*self._python(tests, tests=False), *self._python(src, tests=True)]
                groups.append(Group(self._relative(paths), frozenset({f"devkit.{area}", *self.imports(files)})))
        for path in sorted((self.root / DEVKIT / "tests").glob("test_*.py")):
            groups.append(Group(self._relative([path]), frozenset(self.imports([path]))))
        for directory, package in self.packages.items():
            base = self.root / "packages" / directory
            paths = [p for p in (base / "tests", base / "src") if self._has_tests(p)]
            files = [*self._python(base / "tests", tests=False), *self._python(base / "src", tests=True)]
            groups.append(Group(self._relative(paths), frozenset({package, *self.imports(files)})))
        return groups

    def _relative(self, paths: Iterable[Path]) -> tuple[str, ...]:
        return tuple(p.relative_to(self.root).as_posix() for p in paths)


def _full_trigger(path: str) -> bool:
    return path in FULL_FILES or path.rsplit("/", 1)[-1] in FULL_NAMES or path.startswith(FULL_PREFIXES)


def _source_node(workspace: Workspace, path: str) -> str | None:
    """The node a changed source file belongs to, if it is a package source file."""
    if path.startswith(f"{DEVKIT_SRC}/"):
        area = path[len(DEVKIT_SRC) + 1 :].split("/")
        return f"devkit.{area[0]}" if len(area) > 1 else None
    match = re.fullmatch(r"packages/([^/]+)/src/.+", path)
    return workspace.packages.get(match.group(1)) if match else None


def select(root: Path, changed: Iterable[str]) -> Selection:
    """The test paths a set of changed repository-relative paths can affect."""
    changed = sorted(set(changed))
    frontend = any(path.startswith(FRONTEND_PREFIXES) for path in changed)
    for path in changed:
        if _full_trigger(path):
            return Selection("full", (), path, frontend)
    workspace = Workspace(root)
    paths: set[str] = set()
    causes: set[str] = set()
    nodes: set[str] = set()
    for path in changed:
        data = [(prefix, tests) for prefix, tests in DATA if path.startswith(prefix)]
        for prefix, tests in data:
            paths.update(tests)
            causes.add(prefix)
        if re.fullmatch(r"packages/[^/]+/src/.+", path):
            if path.startswith(f"{DEVKIT}/src/"):
                paths.update(SOURCE_TREE_TESTS)
            node = _source_node(workspace, path)
            if node:
                nodes.add(node)
            causes.add(node or path)
        elif re.fullmatch(r"packages/[^/]+/tests/.+", path):
            name = path.rsplit("/", 1)[-1]
            paths.add(path if re.fullmatch(r"test_.+\.py", name) else path.rsplit("/", 1)[0])
            causes.add("tests")
        elif path.startswith(FRONTEND_PREFIXES):
            causes.add("frontend")
        elif not data and not (
            path in UNTESTED_FILES or path.startswith(UNTESTED_PREFIXES) or UNTESTED_MARKDOWN.fullmatch(path)
        ):
            return Selection("full", (), path, frontend)
    if nodes:
        affected = workspace.dependents(nodes)
        for group in workspace.groups:
            if group.depends & affected:
                paths.update(group.paths)
    kept = sorted(p for p in paths if (root / p).exists())
    kept = [p for p in kept if not any(p.startswith(f"{other}/") for other in kept)]
    if not kept:
        return Selection("none", (), "frontend" if frontend else "untested", frontend)
    return Selection("partial", tuple(kept), ",".join(sorted(causes)), frontend)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, env=env, check=False)


def changed_paths(root: Path, base: str) -> list[str]:
    """Paths changed since the merge base of HEAD and ``base``: committed, staged, unstaged, deleted, both sides of a
    rename, and untracked files that are not ignored."""
    resolved = _git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    merge_base = _git(root, "merge-base", "HEAD", base) if resolved.returncode == 0 else resolved
    if merge_base.returncode != 0:
        raise AdvisoryError.invalid_input(
            f"base ref {base!r} does not resolve to a commit with a merge base; rerun with --base set to an "
            "existing branch",
            f"base={base}",
            code="TEST_BASE_UNKNOWN",
            fix="git branch --all --list",
        )
    found: set[str] = set()
    for args in (
        ("diff", "--name-only", "--no-renames", "-z", merge_base.stdout.decode().strip()),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        result = _git(root, *args)
        if result.returncode != 0:
            raise AdvisoryError(
                f"git {args[0]} failed",
                result.stderr.decode(errors="replace").strip(),
                code="TEST_CHANGES_UNREADABLE",
                actor=Actor.USER,
                retry=Retry.AFTER_FIX,
            )
        found.update(p for p in os.fsdecode(result.stdout).split("\0") if p)
    return sorted(found)


def _replace_process(argv: list[str]) -> None:
    """Hand the run over to the module script, which owns the preflight, xdist options and exit code."""
    sys.stdout.flush()
    os.execvp(argv[0], argv)


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("--base", default="main", show_default=True, help="Ref whose merge base with HEAD starts the changes.")
@click.option("--list", "list_only", is_flag=True, help="Print the selection and its paths without running pytest.")
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@boundary
def main(base: str, list_only: bool, pytest_args: tuple[str, ...]) -> None:
    """Run the tests the changes since BASE can affect; arguments after `--` go to pytest."""
    changed = changed_paths(ROOT, base)
    selection = select(ROOT, changed)
    click.echo(
        f"[TEST_SELECTION: mode={selection.mode} base={base} changed={len(changed)} "
        f"paths={len(selection.paths)} reason={selection.reason}]"
    )
    if selection.frontend:
        click.echo(f"[FRONTEND_CHECK: {FRONTEND_CHECK}]")
    if list_only:
        for path in selection.paths:
            click.echo(f"[TEST_PATH: {path}]")
        return
    if selection.mode == "none":
        return
    _replace_process(["bash", str(ROOT / "scripts/module.sh"), "test", "all", *selection.paths, *pytest_args])


if __name__ == "__main__":
    main()
