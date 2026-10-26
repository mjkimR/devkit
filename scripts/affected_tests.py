"""Select and run the workspace tests the changes since a base ref can affect.

The changed paths since the merge base (committed, staged, unstaged and untracked) map to test paths: shared
foundations to the full suite, data files to the tests that read them, a source area to the test groups that depend
on it or on an area importing it. Local development and integration use this selection; nightly and release full
CI cover dependencies static imports cannot show. Shared foundations still select the full suite.
"""

from __future__ import annotations

import ast
import logging
import os
import re
import subprocess
import sys
import tomllib
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Literal

import click
from devkit.advisory import Actor, AdvisoryError, Retry
from devkit_dist.adapters.cli import boundary

ROOT = Path(__file__).resolve().parents[1]
DEVKIT = "packages/devkit"
DIST = "packages/devkit-dist"
DIST_SRC = f"{DIST}/src/devkit_dist"
# Application features are separate dependency nodes; foundation changes still trigger the full suite.
HOMES = {DIST: "devkit_dist", DEVKIT: "devkit_agt"}
# Shared test helper packages: name -> directory.
HELPERS = {"distsupport": f"{DIST}/tests/support/distsupport", "testsupport": f"{DEVKIT}/tests/support/testsupport"}

logger = logging.getLogger(__name__)

# Changes every test can depend on: the lowest layers, the CLI assembly, packaging and shared test fixtures.
FULL_PREFIXES = (
    "packages/devkit-core/",
    "packages/devkit-cli/",
    f"{DIST_SRC}/base/",
    f"{DIST_SRC}/adapters/",
    f"{DIST_SRC}/features/project/",
    "packages/devkit-advisory/",
    *(f"{path}/" for path in HELPERS.values()),
)
FULL_FILES = frozenset({f"{DIST_SRC}/cli.py", f"{DIST_SRC}/__main__.py", f"{DIST_SRC}/__init__.py", "uv.lock"})
FULL_NAMES = frozenset({"pyproject.toml", "conftest.py"})

# The handbook script tests also read release.sh (and .devkit/config.toml, which selects no test: nightly CI covers it).
HANDBOOK_TESTS = "tools/devkit-dev/tests/integration/test_handbook_script.py"
# Repository files that tests read directly, which imports do not show: prefix -> test paths.
DATA: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        ".devkit/architecture.toml",
        (
            "tools/devkit-dev/tests",
            "tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/tests",
        ),
    ),
    (
        "packages/devkit-mcp/",
        (
            "packages/devkit-mcp/tests",
            f"{DEVKIT}/tests/integration/features/integration",
            "packages/devkit-spec/tests/e2e/features/delivery/test_integration.py",
        ),
    ),
    (
        "docs/",
        (
            f"{DEVKIT}/tests/integration/package/test_documented_codes.py",
            "packages/devkit-spec/tests/integration/package/test_documented_codes.py",
            f"{DEVKIT}/tests/integration/features/rules/test_docs.py",
            f"{DEVKIT}/tests/integration/features/workflow/test_library.py",
        ),
    ),
    ("examples/", ("packages/devkit-starter/tests", f"{DEVKIT}/tests/integration/features/workflow/test_library.py")),
    ("models/", (f"{DIST}/tests/unit/features/search", f"{DIST}/tests/integration/features/search")),
    ("scripts/module.sh", (f"{DEVKIT}/tests/integration/package/test_module_script.py",)),
    ("scripts/_lib.sh", (f"{DEVKIT}/tests/integration/package/test_module_script.py",)),
    ("justfile", (f"{DEVKIT}/tests/integration/package/test_module_script.py",)),
    ("scripts/check_test_environment.py", (f"{DEVKIT}/tests/integration/package/test_test_environment.py",)),
    ("scripts/fetch_model.py", (f"{DIST}/tests/integration/features/search/test_packaging.py",)),
    ("scripts/affected_tests.py", (f"{DEVKIT}/tests/e2e/package/test_affected_tests.py",)),
    ("scripts/handbook.py", (HANDBOOK_TESTS,)),
    ("scripts/release.sh", (HANDBOOK_TESTS,)),
)
# Tests over devkit's whole source tree (layering, documented codes, CLI wiring, stdout kinds), run for any source
# change in either devkit distribution.
SOURCE_TREE_TESTS = (
    f"{DIST}/tests/unit/architecture/test_layering.py",
    f"{DIST}/tests/integration/cli/test_cli_imports.py",
    f"{DIST}/tests/integration/cli/test_cli_plugins.py",
    f"{DIST}/tests/integration/adapters/test_cli.py",
    f"{DEVKIT}/tests/integration/package/test_layering.py",
    f"{DEVKIT}/tests/integration/package/test_documented_codes.py",
)

# The devkit-viewer frontend: pytest never exercises it, so a change there selects no tests and names the frontend
# checks (Node and npm) instead, as the CI viewer job runs them, rebuilding the committed page last.
FRONTEND_PREFIXES = ("packages/devkit-viewer/frontend/", "scripts/viewer.sh")
FRONTEND_CHECK = (
    "just viewer install && just viewer lint && just viewer check && just viewer test && just viewer pack"
    " && just viewer build"
)

# Paths no test reads: planning records, agent projections, guides, the handbook snapshot, CI and smoke scripts.
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
    "handbook/",
)
UNTESTED_FILES = frozenset({".gitignore", ".python-version"})
# Markdown at the repository root or a package root (README, AGENTS).
UNTESTED_MARKDOWN = re.compile(r"((packages|tools)/[^/]+/)?[^/]+\.md")

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


class UnsafeGraph(Exception):
    """An inventory or parse failure makes partial selection unsafe."""


class Workspace:
    """Static source inventory and per-file test dependencies; never imports inspected code."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.packages = self._packages()
        self._trees: dict[Path, ast.Module] = {}
        self._helper_paths: dict[tuple[Path, str], set[Path]] = {}
        self.homes: dict[str, str] = {}
        for home, namespace in HOMES.items():
            source = root / home / "src" / namespace
            if source.is_dir():
                for directory in sorted(source.iterdir()):
                    if not directory.is_dir() or directory.name == "__pycache__":
                        continue
                    if directory.name == "features":
                        for feature in sorted(directory.iterdir()):
                            if feature.is_dir() and feature.name != "__pycache__":
                                self.homes[f"{namespace}.features.{feature.name}"] = home
                    else:
                        self.homes[f"{namespace}.{directory.name}"] = home
        self.areas = sorted(self.homes)
        self.fine: dict[str, Path] = {}
        for directory, package in self.packages.items():
            if package != "devkit_spec":
                continue
            base = root / directory / "src"
            for path in self._python(base / package, tests=False):
                parts = path.relative_to(base).with_suffix("").parts
                module = ".".join(parts[:-1] if parts[-1] == "__init__" else parts)
                if module in self.fine:
                    raise UnsafeGraph(f"ambiguous:{module}")
                self.fine[module] = path
        self.modules = {path: module for module, path in self.fine.items()}
        self.test_roots = sorted(root.glob("packages/*/tests")) + sorted(root.glob("tools/*/tests"))
        config = root / "pyproject.toml"
        if config.exists():
            try:
                options = tomllib.loads(config.read_text()).get("tool", {}).get("pytest", {}).get("ini_options", {})
                self.test_roots += [root / path for path in options.get("pythonpath", [])]
            except (OSError, ValueError) as exc:
                raise UnsafeGraph("pyproject.toml") from exc
        self.test_roots = sorted(set(self.test_roots))

    def _packages(self) -> dict[str, str]:
        found: dict[str, str] = {}
        for src in sorted([*self.root.glob("packages/*/src"), *self.root.glob("tools/*/src")]):
            directory = src.parent.relative_to(self.root).as_posix()
            if directory in HOMES or directory == "packages/devkit-advisory":
                continue
            names = [p.name for p in src.iterdir() if p.is_dir() and p.name.isidentifier() and p.name != "__pycache__"]
            if len(names) != 1:
                raise UnsafeGraph(f"inventory:{directory}")
            found[directory] = names[0]
        return found

    def node_of(self, module: str) -> str | None:
        parts = module.split(".")
        if module == "devkit.advisory" or module.startswith("devkit.advisory."):
            return "devkit.advisory"
        if parts[0] in HOMES.values():
            return next((area for area in self.areas if module == area or module.startswith(f"{area}.")), None)
        if parts[0] == "devkit_spec":
            return module if module in self.fine and len(parts) > 1 else "@devkit_spec"
        return parts[0] if parts[0] in self.packages.values() else None

    def _tree(self, path: Path) -> ast.Module:
        if path not in self._trees:
            try:
                self._trees[path] = ast.parse(path.read_bytes())
            except (OSError, SyntaxError, ValueError) as exc:
                raise UnsafeGraph(path.relative_to(self.root).as_posix()) from exc
        return self._trees[path]

    def _owner(self, path: Path) -> str | None:
        relative = path.relative_to(self.root).as_posix()
        for home, namespace in HOMES.items():
            if relative.startswith(f"{home}/src/{namespace}/"):
                module = relative[len(f"{home}/src/") :].replace("/", ".").removesuffix(".py")
                return self.node_of(module)
            if relative.startswith(f"{home}/tests/"):
                parts = relative[len(f"{home}/tests/") :].split("/")
                if parts[0] in {"unit", "integration", "e2e"}:
                    parts = parts[1:]
                area = parts[1] if parts[0] == "features" and len(parts) > 1 else parts[0]
                feature = f"{namespace}.features.{area}"
                return feature if feature in self.homes else self.node_of(f"{namespace}.{area}")
        for directory, package in self.packages.items():
            if relative.startswith(f"{directory}/"):
                return "@devkit_spec" if package == "devkit_spec" else package
        return None

    def _module_dependencies(self, module: str, *, exact_root: bool = False) -> set[str]:
        node = "devkit_spec" if exact_root and module == "devkit_spec" else self.node_of(module)
        found = {node} if node else set()
        if module in self.fine:
            parts = module.split(".")
            for end in range(1, len(parts)):
                parent = ".".join(parts[:end])
                if parent in self.fine and self.fine[parent].name == "__init__.py":
                    found.add(parent)
        return found

    def _helpers_for(self, path: Path, module: str) -> set[Path]:
        """Union all plausible test-root/local resolutions; never guess a same-named helper."""
        key = (path.parent, module)
        if key in self._helper_paths:
            return self._helper_paths[key]
        found: set[Path] = set()
        for base in {*self.test_roots, path.parent}:
            target = base.joinpath(*module.split("."))
            for candidate in (target.with_suffix(".py"), target / "__init__.py"):
                if candidate.is_file():
                    found.add(candidate)
            # Importing a nested helper executes its package initializers as well.
            for parent in target.parents:
                if parent == base or base not in parent.parents:
                    break
                if (parent / "__init__.py").is_file():
                    found.add(parent / "__init__.py")
        self._helper_paths[key] = found
        return found

    def imports(self, files: Iterable[Path]) -> set[str]:
        found: set[str] = set()
        pending, seen = list(files), set()
        while pending:
            path = pending.pop()
            if path in seen:
                continue
            seen.add(path)
            for node in ast.walk(self._tree(path)):
                names: list[tuple[str, bool]] = []
                if isinstance(node, ast.Import):
                    names = [(alias.name, False) for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if node.level:
                        current = self.modules.get(path)
                        if current:
                            package = current if path.name == "__init__.py" else current.rpartition(".")[0]
                            parents = package.split(".")
                            module = ".".join(
                                [*parents[: len(parents) - node.level + 1], *([module] if module else [])]
                            )
                        else:
                            base = path.parent
                            for _ in range(node.level - 1):
                                base = base.parent
                            target = base.joinpath(*module.split(".")) if module else base
                            helpers = [target.with_suffix(".py"), target / "__init__.py"]
                            helpers += [
                                candidate
                                for alias in node.names
                                for candidate in (target / f"{alias.name}.py", target / alias.name / "__init__.py")
                            ]
                            resolved = [helper for helper in helpers if helper.is_file()]
                            pending.extend(resolved)
                            if not resolved and (owner := self._owner(path)):
                                found.add(owner)
                            continue
                    names = [(module, True)] if module else []
                    for alias in node.names:
                        candidate = f"{module}.{alias.name}"
                        if alias.name == "*" and module.startswith("devkit_spec"):
                            found.add("@devkit_spec")
                        elif candidate in self.fine:
                            names.append((candidate, True))
                        elif not module.startswith("devkit_spec"):
                            names.append((candidate, False))
                elif isinstance(node, ast.Call) and node.args:
                    func = node.func
                    called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
                    if called in _IMPORTING_CALLS:
                        first = node.args[0]
                        if (
                            isinstance(first, ast.Constant)
                            and isinstance(first.value, str)
                            and not first.value.startswith(".")
                        ):
                            names = [(first.value, False)]
                        else:
                            # A runtime name cannot establish any narrower dependency.
                            if owner := self._owner(path):
                                found.add(owner)
                for name, exact_root in names:
                    found |= self._module_dependencies(name, exact_root=exact_root)
                    if name in {"devkit_dist.cli", "devkit_dist.__main__"}:
                        found.add("@root_cli")
                    if not self.node_of(name):
                        helpers = self._helpers_for(path, name)
                        pending.extend(helpers)
                        if len(helpers) > 1 and (owner := self._owner(path)):
                            found.add(owner)
        return found

    def _python(self, directory: Path, *, tests: bool) -> Iterator[Path]:
        if not directory.is_dir():
            return
        for path in sorted(directory.rglob("*.py")):
            in_tests = "tests" in path.relative_to(directory).parts[:-1]
            if in_tests == tests and "__pycache__" not in path.parts:
                yield path

    def sources(self) -> dict[str, Path]:
        nodes = {area: self.root / home / "src" / Path(*area.split(".")) for area, home in self.homes.items()}
        for directory, package in self.packages.items():
            if package != "devkit_spec":
                nodes[package] = self.root / directory / "src" / package
        return {**nodes, **self.fine}

    def dependents(self, changed: set[str]) -> set[str]:
        imported_by: dict[str, set[str]] = {}
        for node, source in self.sources().items():
            files = [source] if source.is_file() else self._python(source, tests=False)
            for imported in self.imports(files):
                if imported != node:
                    imported_by.setdefault(imported, set()).add(node)
        imported_by.setdefault("devkit_mcp", set()).update({"devkit_agt.features.integration", "@devkit_spec"})
        changed = changed | (set(self.fine) if "@devkit_spec" in changed else set())
        affected, pending = set(changed), list(changed)
        while pending:
            node = pending.pop()
            followers = set(imported_by.get(node, ()))
            if node.startswith("devkit_spec"):
                followers.add("@devkit_spec")
            for follower in followers - affected:
                affected.add(follower)
                pending.append(follower)
        return affected

    @cached_property
    def groups(self) -> list[Group]:
        groups: list[Group] = []
        for path in sorted([*self.root.glob("packages/**/test_*.py"), *self.root.glob("tools/**/test_*.py")]):
            if "tests" not in path.relative_to(self.root).parts or "__pycache__" in path.parts:
                continue
            files = [path]
            for parent in path.parents:
                if parent == self.root.parent:
                    break
                conftest = parent / "conftest.py"
                if conftest.is_file():
                    files.append(conftest)
            depends = self.imports(files)
            owner = self._owner(path)
            if "@root_cli" in depends and (
                owner == "@devkit_spec" or any(node.startswith("devkit_spec") for node in depends)
            ):
                # Root CLI loading of the spec entry point is independent of any direct fine imports.
                depends.add("@devkit_spec")
            depends.discard("@root_cli")
            if owner and (owner != "@devkit_spec" or not any(n.startswith("devkit_spec") for n in depends)):
                depends.add(owner)
            # These consumers scan sources or load the command/bundle through runtime entry points.
            if (owner == "@devkit_spec" and "/src/" in path.relative_to(self.root).as_posix()) or path.relative_to(
                self.root
            ).as_posix() in {
                "packages/devkit-spec/tests/integration/package/test_documented_codes.py",
                "packages/devkit-spec/tests/e2e/package/test_package.py",
                "packages/devkit-spec/tests/integration/bundles/spec/test_workflows.py",
                "packages/devkit-spec/tests/e2e/features/delivery/test_integration.py",
            }:
                depends.add("@devkit_spec")
            groups.append(Group(self._relative([path]), frozenset(depends)))
        return groups

    def _relative(self, paths: Iterable[Path]) -> tuple[str, ...]:
        return tuple(p.relative_to(self.root).as_posix() for p in paths)


def _full_trigger(path: str) -> bool:
    if path in UNTESTED_FILES or path.startswith(UNTESTED_PREFIXES) or bool(UNTESTED_MARKDOWN.fullmatch(path)):
        return False
    return (
        path in FULL_FILES
        or path.rsplit("/", 1)[-1] in FULL_NAMES
        or path.startswith(FULL_PREFIXES)
        or bool(re.fullmatch(r"(?:packages|tools)/[^/]+/tests/support(?:/.*)?", path))
    )


def _source_node(workspace: Workspace, path: str) -> str | None:
    """The node a changed source file belongs to, if it is a package source file."""
    if path.endswith(".py") and not (workspace.root / path).is_file():
        raise UnsafeGraph(path)
    for home in HOMES:
        prefix = f"{home}/src/"
        if path.startswith(prefix):
            return workspace.node_of(path[len(prefix) :].replace("/", ".").removesuffix(".py"))
    match = re.fullmatch(r"((?:packages|tools)/[^/]+)/src/.+", path)
    package = workspace.packages.get(match.group(1)) if match else None
    if package == "devkit_spec":
        if path.endswith(".py"):
            module = workspace.modules.get(workspace.root / path)
            if module is None:
                raise UnsafeGraph(path)
            return module
        return "@devkit_spec"
    return package


def select(root: Path, changed: Iterable[str], *, include_e2e: bool = False) -> Selection:
    changed = sorted(set(changed))
    try:
        return _select(root, changed, include_e2e=include_e2e)
    except UnsafeGraph as exc:
        return Selection("full", (), str(exc), any(path.startswith(FRONTEND_PREFIXES) for path in changed))


def _select(root: Path, changed: Iterable[str], *, include_e2e: bool = False) -> Selection:
    """The test paths a set of changed repository-relative paths can affect."""
    changed = sorted(set(changed))
    frontend = any(path.startswith(FRONTEND_PREFIXES) for path in changed)
    for path in changed:
        if _full_trigger(path):
            return Selection("full", (), path, frontend)
    workspace = Workspace(root)
    paths: set[str] = set()
    data_targets: set[str] = set()
    causes: set[str] = set()
    nodes: set[str] = set()
    has_e2e_change = any("/tests/e2e/" in path or path.startswith("tests/e2e/") for path in changed)
    allow_e2e = include_e2e or has_e2e_change
    for path in changed:
        data = [(prefix, tests) for prefix, tests in DATA if path.startswith(prefix)]
        for prefix, tests in data:
            paths.update(tests)
            data_targets.update(tests)
            causes.add(prefix)
        if re.fullmatch(r"(?:packages|tools)/[^/]+/src/.+", path):
            if path.startswith((f"{DIST}/src/", f"{DEVKIT}/src/")):
                paths.update(SOURCE_TREE_TESTS)
            node = _source_node(workspace, path)
            if not node:
                return Selection("full", (), path, frontend)
            nodes.add(node)
            causes.add(node)
        elif re.fullmatch(r"(?:packages|tools)/[^/]+/tests/.+", path):
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
    if not allow_e2e:
        kept = [p for p in kept if "/tests/e2e/" not in p or p in data_targets]
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
@click.option("--e2e", "include_e2e", is_flag=True, help="Include slow end-to-end tests.")
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@boundary
def main(base: str, list_only: bool, include_e2e: bool, pytest_args: tuple[str, ...]) -> None:
    """Run the tests the changes since BASE can affect; arguments after `--` go to pytest."""
    changed = changed_paths(ROOT, base)
    selection = select(ROOT, changed, include_e2e=include_e2e)
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
