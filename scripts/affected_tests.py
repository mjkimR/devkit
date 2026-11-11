"""Select and run the workspace tests the changes since a base ref can affect.

The changed paths since the merge base (committed, staged, unstaged and untracked) map to test paths: shared
foundations to the full suite, data files to the tests that read them (a fixed table plus the root-anchored
literal path reads of the test tree), a source area to the test groups that depend on it or on an area importing
it. Local development and integration use this selection; nightly and release full CI cover dependencies static
imports cannot show. Shared foundations still select the full suite.
"""

from __future__ import annotations

import ast
import fnmatch
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

# The handbook script tests also read release.sh; their literal read of .devkit/config.toml selects them for it.
HANDBOOK_TESTS = "tools/devkit-dev/tests/integration/test_handbook_script.py"
VERSION_TESTS = f"{DEVKIT}/tests/integration/package/test_version_script.py"
# Reads every document ID of docs/ and specs/: a new document can collide with an ID shipped bundle text cites.
CITATION_TESTS = "tools/devkit-dev/tests/integration/test_bundle_citations.py"
# Repository files that tests read directly, which imports do not show: prefix -> test paths. Literal path reads in
# the test tree add their readers on top (Workspace.readers); these rows cover readers that scan cannot see.
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
        # The scratch-cleanup guidance test reads the delivery roles capability by path.
        "docs/capabilities/delivery/",
        ("packages/devkit-spec/tests/integration/bundles/spec/test_scratch_cleanup_guidance.py",),
    ),
    (
        "docs/",
        (
            f"{DEVKIT}/tests/integration/package/test_documented_codes.py",
            "packages/devkit-docs/tests/integration/package/test_documented_codes.py",
            "packages/devkit-spec/tests/integration/package/test_documented_codes.py",
            "packages/devkit-adaptive/tests/integration/package/test_documented_codes.py",
            f"{DEVKIT}/tests/integration/features/rules/test_docs.py",
            f"{DEVKIT}/tests/integration/features/workflow/test_library.py",
            CITATION_TESTS,
        ),
    ),
    ("specs/", (CITATION_TESTS,)),
    (
        "docs/usecases/",
        ("packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py",),
    ),
    ("examples/", ("packages/devkit-starter/tests", f"{DEVKIT}/tests/integration/features/workflow/test_library.py")),
    ("models/", (f"{DIST}/tests/unit/features/search", f"{DIST}/tests/integration/features/search")),
    ("scripts/module.sh", (f"{DEVKIT}/tests/integration/package/test_module_script.py",)),
    ("scripts/_lib.sh", (f"{DEVKIT}/tests/integration/package/test_module_script.py",)),
    # test_version_script runs release.sh and `just release-build` by subprocess, which no literal read shows.
    ("justfile", (f"{DEVKIT}/tests/integration/package/test_module_script.py", VERSION_TESTS)),
    ("scripts/check_test_environment.py", (f"{DEVKIT}/tests/integration/package/test_test_environment.py",)),
    ("scripts/fetch_model.py", (f"{DIST}/tests/integration/features/search/test_packaging.py",)),
    ("scripts/affected_tests.py", (f"{DEVKIT}/tests/e2e/package/test_affected_tests.py",)),
    ("scripts/handbook.py", (HANDBOOK_TESTS,)),
    ("scripts/release.sh", (HANDBOOK_TESTS, VERSION_TESTS)),
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
# Tests that scan the sources of every package (the [FIX] literal contract), run for any package or tool source
# change.
ALL_SOURCES_TESTS = (f"{DEVKIT}/tests/integration/package/test_agent_output_contract.py",)

# The devkit-viewer frontend: a change there names the frontend checks (Node and npm), as the CI viewer job runs them,
# rebuilding the committed page last; it selects only the pytest tests that read it by a literal path.
FRONTEND_PREFIXES = ("packages/devkit-viewer/frontend/", "scripts/viewer.sh")
FRONTEND_CHECK = (
    "just viewer install && just viewer lint && just viewer check && just viewer test && just viewer pack"
    " && just viewer build"
)

# Paths that select no test unless a test reads them by a literal path: agent projections, guides, the handbook
# snapshot, CI and smoke scripts.
UNTESTED_PREFIXES = (
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
# Markdown at the repository root or a package root (README, AGENTS), with the same literal-read exception.
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


@dataclass(frozen=True)
class Read:
    """A repository path a test-tree file reads: ``base`` and everything under it, or only what ``pattern`` matches."""

    base: str  # repository-relative, never the root itself
    pattern: str | None = None  # a literal glob pattern relative to base

    def matches(self, path: str) -> bool:
        if path == self.base:
            return self.pattern is None
        if not path.startswith(f"{self.base}/"):
            return False
        if self.pattern is None:
            return True
        # A new or deleted subdirectory changes the glob result too, so an ancestor below the base may match.
        parts, pattern = path[len(self.base) + 1 :].split("/"), self.pattern.split("/")
        return any(_glob_match(parts[:end], pattern) for end in range(1, len(parts) + 1))


def _glob_match(parts: list[str], pattern: list[str]) -> bool:
    """Segment-wise glob matching where ``**`` spans zero or more segments (``PurePath.match`` treats it as ``*``)."""
    if not pattern:
        return not parts
    head, rest = pattern[0], pattern[1:]
    if head == "**":
        return any(_glob_match(parts[start:], rest) for start in range(len(parts) + 1))
    return bool(parts) and fnmatch.fnmatchcase(parts[0], head) and _glob_match(parts[1:], rest)


_SCOPES = (
    ast.Module,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Lambda,
    ast.ClassDef,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)
_IDENTITY_STEPS = frozenset({"resolve", "absolute"})
_MAX_VALUES = 64  # expansion bound per expression: loop products beyond it read their base instead


_Function = ast.FunctionDef | ast.AsyncFunctionDef
_Item = ast.expr | tuple[ast.expr, ast.expr]  # an iterable's element; a pair for dict.items()


@dataclass(frozen=True)
class _Binding:
    value: ast.expr | None  # None: bound to something the scan does not evaluate
    loop: bool = False  # value is the iterable a loop variable ranges over
    position: tuple[int, ...] = ()  # the index path of the variable in a tuple loop target
    function: _Function | None = None  # a parameter: its values are the arguments of the file's calls
    parameter: str = ""


@dataclass(frozen=True)
class _PathValue:
    path: str  # absolute and normalized
    exact: bool  # False once a runtime segment joined: the value stands for its base directory


class _ReadScanner:
    """The root-anchored literal path reads of one test-tree file, evaluated statically from ``Path(__file__)``."""

    def __init__(self, root: Path, path: Path, tree: ast.Module) -> None:
        self.root, self.path, self.tree = str(root), str(path), tree
        self.parents: dict[ast.AST, ast.AST] = {}
        self.scope_of: dict[ast.AST, ast.AST] = {}
        self.outer: dict[ast.AST, ast.AST] = {}
        self.bindings: dict[ast.AST, dict[str, list[_Binding]]] = {}
        self._paths: dict[ast.AST, list[_PathValue] | None] = {}
        self._strings: dict[ast.AST, list[str] | None] = {}
        self._active: set[ast.AST] = set()
        self.calls: dict[str, list[ast.Call]] = {}
        self.loads: dict[str, int] = {}
        self._index(tree, tree)

    def _bind(self, scope: ast.AST, name: str, binding: _Binding) -> None:
        self.bindings.setdefault(scope, {}).setdefault(name, []).append(binding)

    def _bind_target(
        self,
        scope: ast.AST,
        target: ast.AST,
        value: ast.expr | None,
        *,
        loop: bool = False,
        position: tuple[int, ...] = (),
    ) -> None:
        if isinstance(target, ast.Name):
            self._bind(scope, target.id, _Binding(value, loop, position))
        elif loop and isinstance(target, (ast.Tuple, ast.List)):
            for index, element in enumerate(target.elts):
                self._bind_target(scope, element, value, loop=True, position=(*position, index))
        else:
            for node in ast.walk(target):
                if isinstance(node, ast.Name):
                    self._bind(scope, node.id, _Binding(None))

    def _index(self, node: ast.AST, scope: ast.AST) -> None:
        """Record parents, enclosing scopes, calls by name and every name binding, once per binding site."""
        inner = scope
        if isinstance(node, _SCOPES) and node is not scope:
            inner = node
            self.outer[node] = scope
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self._bind(scope, node.name, _Binding(None))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                function = None if isinstance(node, ast.Lambda) else node
                for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
                    self._bind(inner, arg.arg, _Binding(None, function=function, parameter=arg.arg))
                for arg in (node.args.vararg, node.args.kwarg):
                    if arg:
                        self._bind(inner, arg.arg, _Binding(None))
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                for generator in node.generators:
                    self._bind_target(inner, generator.target, generator.iter, loop=True)
        self.scope_of[node] = inner
        if isinstance(node, ast.Assign):
            for target in node.targets:
                self._bind_target(inner, target, node.value)
        elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)) and node.value is not None:
            self._bind_target(inner, node.target, node.value)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            self._bind_target(inner, node.target, node.iter, loop=True)
        elif isinstance(node, (ast.AugAssign, ast.Delete)):
            for target in node.targets if isinstance(node, ast.Delete) else [node.target]:
                self._bind_target(inner, target, None)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    self._bind_target(inner, item.optional_vars, None)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                self._bind(inner, (alias.asname or alias.name).split(".")[0], _Binding(None))
        elif isinstance(node, ast.ExceptHandler) and node.name:
            self._bind(inner, node.name, _Binding(None))
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for name in node.names:
                self._bind(inner, name, _Binding(None))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            self.loads[node.id] = self.loads.get(node.id, 0) + 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            self.calls.setdefault(node.func.id, []).append(node)
        for child in ast.iter_child_nodes(node):
            self.parents[child] = node
            self._index(child, inner)

    def _lookup(self, node: ast.Name) -> _Binding | None:
        scope: ast.AST | None = self.scope_of[node]
        first = True
        while scope is not None:
            if first or not isinstance(scope, ast.ClassDef):
                found = self.bindings.get(scope, {}).get(node.id)
                if found:
                    return found[0] if len(found) == 1 else None
            first = False
            scope = self.outer.get(scope)
        return None

    def _elements(self, binding: _Binding) -> list[ast.expr] | None:
        """The expressions a name can stand for: its value, each loop element, or each call's argument."""
        if binding.function is not None:
            return self._arguments(binding.function, binding.parameter)
        if binding.value is None:
            return None
        if not binding.loop:
            return [binding.value]
        items = self._iterable(binding.value)
        if items is None:
            return None
        elements: list[ast.expr] = []
        for item in items:
            for index in binding.position:
                if isinstance(item, tuple):
                    item = item[index]
                elif isinstance(item, (ast.Tuple, ast.List)) and index < len(item.elts):
                    item = item.elts[index]
                else:
                    return None
            if isinstance(item, tuple):
                return None
            elements.append(item)
        return elements

    def _dict(self, node: ast.expr) -> ast.Dict | None:
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            binding = self._lookup(node)
            node = binding.value if binding and not binding.loop and binding.value is not None else node
        if isinstance(node, ast.Dict) and all(key is not None for key in node.keys):
            return node
        return None

    def _iterable(self, node: ast.expr, depth: int = 0) -> list[_Item] | None:
        """The literal elements a loop ranges over: a literal sequence, a name bound to one, or a literal dict view."""
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return None if any(isinstance(e, ast.Starred) for e in node.elts) else list(node.elts)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and depth < 8:
            binding = self._lookup(node)
            if binding and not binding.loop and binding.function is None and binding.value is not None:
                return self._iterable(binding.value, depth + 1)
            return None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and not node.args:
            mapping = self._dict(node.func.value)
            if mapping is None:
                return None
            keys = [key for key in mapping.keys if key is not None]
            views: dict[str, list[_Item]] = {
                "keys": list(keys),
                "values": list(mapping.values),
                "items": list(zip(keys, mapping.values, strict=True)),
            }
            return views.get(node.func.attr)
        return None

    def _arguments(self, function: _Function, parameter: str) -> list[ast.expr] | None:
        """A parameter's arguments at every call of its function in this file, when every use is such a call."""
        calls = self.calls.get(function.name, [])
        scope = self.outer.get(function)
        if not calls or self.loads.get(function.name) != len(calls) or scope is None:
            return None
        if len(self.bindings.get(scope, {}).get(function.name, [])) != 1:
            return None
        positional = [arg.arg for arg in [*function.args.posonlyargs, *function.args.args]]
        defaults = dict(
            zip(positional[len(positional) - len(function.args.defaults) :], function.args.defaults, strict=True)
        )
        for arg, default in zip(function.args.kwonlyargs, function.args.kw_defaults, strict=True):
            if default is not None:
                defaults[arg.arg] = default
        arguments: list[ast.expr] = []
        for call in calls:
            if any(isinstance(arg, ast.Starred) for arg in call.args) or any(kw.arg is None for kw in call.keywords):
                return None
            keyword = next((kw.value for kw in call.keywords if kw.arg == parameter), None)
            if parameter in positional and positional.index(parameter) < len(call.args):
                arguments.append(call.args[positional.index(parameter)])
            elif keyword is not None:
                arguments.append(keyword)
            elif parameter in defaults:
                arguments.append(defaults[parameter])
            else:
                return None
        return arguments

    def strings(self, node: ast.AST) -> list[str] | None:
        """The literal string values an expression can take, or None."""
        if node in self._strings:
            return self._strings[node]
        if node in self._active:
            return None
        self._active.add(node)
        try:
            result = self._evaluate_strings(node)
        finally:
            self._active.discard(node)
        if result is not None and len(result) > _MAX_VALUES:
            result = None
        self._strings[node] = result
        return result

    def _evaluate_strings(self, node: ast.AST) -> list[str] | None:
        if isinstance(node, ast.Constant):
            return [node.value] if isinstance(node.value, str) else None
        if isinstance(node, ast.JoinedStr):
            values = [""]
            for part in node.values:
                if isinstance(part, ast.FormattedValue):
                    if part.format_spec is not None or part.conversion not in (-1, ord("s")):
                        return None
                    found = self.strings(part.value)
                else:
                    found = self.strings(part)
                if found is None:
                    return None
                values = [value + item for value in values for item in found]
            return values
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = self.strings(node.left), self.strings(node.right)
            return None if left is None or right is None else [a + b for a in left for b in right]
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            binding = self._lookup(node)
            elements = self._elements(binding) if binding else None
            if elements is None:
                return None
            values: list[str] = []
            for element in elements:
                found = self.strings(element)
                if found is None:
                    return None
                values.extend(found)
            return values
        if isinstance(node, ast.Subscript) and (mapping := self._dict(node.value)) is not None:
            keys = self.strings(node.slice)
            chosen = [
                value
                for key, value in zip(mapping.keys, mapping.values, strict=True)
                if keys is None or (isinstance(key, ast.Constant) and key.value in keys)
            ]
            values = []
            for value in chosen or mapping.values:
                found = self.strings(value)
                if found is None:
                    return None
                values.extend(found)
            return values
        if isinstance(node, ast.Call) and _is_path_constructor(node.func) and node.args and not node.keywords:
            parts = [self.strings(arg) for arg in node.args]
            if any(part is None for part in parts):
                return None
            values = [""]
            for part in parts:
                values = [os.path.join(value, item) if value else item for value in values for item in part or ()]
            return values
        return None

    def paths(self, node: ast.AST) -> list[_PathValue] | None:
        """The anchored path values an expression can take, or None when it is not anchored at ``__file__``."""
        if node in self._paths:
            return self._paths[node]
        if node in self._active:
            return None
        self._active.add(node)
        try:
            result = self._evaluate_paths(node)
        finally:
            self._active.discard(node)
        if result is not None and len(result) > _MAX_VALUES:
            result = sorted({_PathValue(value.path, False) for value in result}, key=lambda value: value.path)
            result = result if len(result) <= _MAX_VALUES else None
        self._paths[node] = result
        return result

    def _join(self, values: list[_PathValue], segments: list[ast.expr]) -> list[_PathValue]:
        for segment in segments:
            found = self.strings(segment)
            joined: list[_PathValue] = []
            for value in values:
                if not value.exact or found is None:
                    joined.append(_PathValue(value.path, False))
                else:
                    joined.extend(_PathValue(os.path.normpath(os.path.join(value.path, item)), True) for item in found)
            values = list(dict.fromkeys(joined))
        return values

    def _evaluate_paths(self, node: ast.AST) -> list[_PathValue] | None:
        if isinstance(node, ast.Call):
            func = node.func
            if _is_path_constructor(func) and node.args and not node.keywords:
                first = node.args[0]
                if isinstance(first, ast.Name) and first.id == "__file__":
                    base = [_PathValue(self.path, True)]
                else:
                    base = self.paths(first)
                return None if base is None else self._join(base, list(node.args[1:]))
            if isinstance(func, ast.Attribute) and not node.keywords:
                base = self.paths(func.value)
                if base is None:
                    return None
                if func.attr in _IDENTITY_STEPS and not node.args:
                    return base
                if func.attr == "joinpath":
                    return self._join(base, list(node.args))
            return None
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            base = self.paths(node.value)
            return None if base is None else [_PathValue(os.path.dirname(v.path), v.exact) for v in base]
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == "parents":
            index = node.slice
            if not (isinstance(index, ast.Constant) and type(index.value) is int and index.value >= 0):
                return None
            base = self.paths(node.value.value)
            if base is None:
                return None
            values = []
            for value in base:
                path = value.path
                for _ in range(index.value + 1):
                    path = os.path.dirname(path)
                values.append(_PathValue(path, value.exact))
            return values
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            base = self.paths(node.left)
            return None if base is None else self._join(base, [node.right])
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            binding = self._lookup(node)
            elements = self._elements(binding) if binding else None
            if elements is None:
                return None
            values = []
            for element in elements:
                found = self.paths(element)
                if found is None:
                    return None
                values.extend(found)
            return values
        return None

    def _extends(self, node: ast.AST) -> bool:
        """Whether the enclosing expression continues this anchored path, so it, not the node, is the read."""
        parent = self.parents.get(node)
        target: ast.AST | None = None
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div) and parent.left is node:
            target = parent
        elif isinstance(parent, ast.Attribute) and parent.value is node:
            grand = self.parents.get(parent)
            subscripted = parent.attr == "parents" and isinstance(grand, ast.Subscript) and grand.value is parent
            called = parent.attr in {*_IDENTITY_STEPS, "joinpath"} and isinstance(grand, ast.Call)
            if parent.attr == "parent":
                target = parent
            elif subscripted or (called and isinstance(grand, ast.Call) and grand.func is parent):
                target = grand
        elif isinstance(parent, ast.Call) and _is_path_constructor(parent.func) and parent.args[:1] == [node]:
            target = parent
        return target is not None and self.paths(target) is not None

    @cached_property
    def _used_values(self) -> set[ast.AST]:
        """Bound values some name use in the file resolves to; a binding without one is read where it is bound."""
        used: set[ast.AST] = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                binding = self._lookup(node)
                if binding is not None and binding.value is not None and not binding.loop:
                    used.add(binding.value)
        return used

    def reads(self) -> set[Read]:
        found: set[Read] = set()
        for node in ast.walk(self.tree):
            if not isinstance(node, (ast.Call, ast.Attribute, ast.Subscript, ast.BinOp, ast.Name)):
                continue
            if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
                continue
            values = self.paths(node)
            if not values or self._extends(node):
                continue
            parent = self.parents.get(node)
            targets = (
                parent.targets
                if isinstance(parent, ast.Assign)
                else [parent.target]
                if isinstance(parent, ast.AnnAssign)
                else []
            )
            if (
                targets
                and getattr(parent, "value", None) is node
                and all(isinstance(t, ast.Name) for t in targets)
                and node in self._used_values
            ):
                continue  # binding a base to a name is not a read; its resolvable uses are
            patterns: list[str] | None = None
            grand = self.parents.get(parent) if parent else None
            if (
                isinstance(parent, ast.Attribute)
                and parent.attr in {"glob", "rglob"}
                and isinstance(grand, ast.Call)
                and grand.func is parent
                and grand.args
            ):
                patterns = self.strings(grand.args[0])
                if patterns is not None and parent.attr == "rglob":
                    patterns = [f"**/{pattern}" for pattern in patterns]
            for value in values:
                relative = os.path.relpath(value.path, self.root)
                if relative in {".", ".."} or relative.startswith(f"..{os.sep}") or value.path == self.path:
                    continue
                relative = relative.replace(os.sep, "/")
                if value.exact and patterns:
                    found.update(Read(relative, pattern.strip("/")) for pattern in patterns if pattern.strip("/"))
                else:
                    found.add(Read(relative))
        return found


def _is_path_constructor(func: ast.expr) -> bool:
    return (isinstance(func, ast.Name) and func.id == "Path") or (
        isinstance(func, ast.Attribute) and func.attr == "Path"
    )


class UnsafeGraph(Exception):
    """An inventory or parse failure makes partial selection unsafe."""


class Workspace:
    """Static source inventory and per-file test dependencies; never imports inspected code."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.packages = self._packages()
        self._trees: dict[Path, ast.Module] = {}
        self._sources: dict[Path, bytes] = {}
        self._direct_cache: dict[Path, tuple[frozenset[str], tuple[Path, ...]]] = {}
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

    def _source(self, path: Path) -> bytes:
        if path not in self._sources:
            self._sources[path] = path.read_bytes()
        return self._sources[path]

    def _tree(self, path: Path) -> ast.Module:
        if path not in self._trees:
            try:
                self._trees[path] = ast.parse(self._source(path))
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
            nodes, helpers = self._direct(path)
            found |= nodes
            pending.extend(helpers)
        return found

    def _direct(self, path: Path) -> tuple[frozenset[str], tuple[Path, ...]]:
        """One file's dependency nodes and the local helper files its imports execute; cached per file."""
        if path in self._direct_cache:
            return self._direct_cache[path]
        found: set[str] = set()
        pending: list[Path] = []
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
                        module = ".".join([*parents[: len(parents) - node.level + 1], *([module] if module else [])])
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
        result = (frozenset(found), tuple(pending))
        self._direct_cache[path] = result
        return result

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

    @cached_property
    def test_tree(self) -> list[Path]:
        """Every Python file under a ``tests`` directory: test modules, embedded rule tests, conftests and helpers."""
        files: list[Path] = []
        for home in ("packages", "tools"):
            for directory, names, filenames in os.walk(self.root / home):
                names[:] = sorted(
                    n for n in names if n not in {"__pycache__", "node_modules"} and not n.startswith(".")
                )
                base = Path(directory)
                if "tests" in base.relative_to(self.root).parts:
                    files.extend(base / name for name in sorted(filenames) if name.endswith(".py"))
        return files

    @cached_property
    def read_map(self) -> list[tuple[Read, frozenset[str]]]:
        """Each literal read of the test tree and the test modules it belongs to."""
        tests = [path for path in self.test_tree if path.name.startswith("test_")]
        owned: dict[Read, set[Path]] = {}
        for path in self.test_tree:
            if b"__file__" not in self._source(path):
                continue  # no anchor, so no read; skipping the parse keeps a document-only selection cheap
            reads = _ReadScanner(self.root, path, self._tree(path)).reads()
            if not reads:
                continue
            if path.name.startswith("test_"):
                modules = {path}
            elif path.name == "conftest.py":
                modules = {test for test in tests if path.parent in test.parents}
            else:
                modules = self._importers(path, tests)
            for read in reads:
                owned.setdefault(read, set()).update(modules)
        return [(read, frozenset(self._relative(modules))) for read, modules in owned.items() if modules]

    def _importers(self, helper: Path, tests: list[Path]) -> set[Path]:
        """Test modules whose import discovery reaches a helper, directly, through other helpers or a conftest."""
        found: set[Path] = set()
        reached, pending = {helper}, [helper]
        while pending:
            target = pending.pop()
            name = target.parent.name if target.name == "__init__.py" else target.stem
            word = re.compile(rb"\b" + re.escape(name.encode()) + rb"\b")
            # A relative package import (`from . import x`) runs the initializer without naming its package.
            package = target.parent if target.name == "__init__.py" else None
            for path in self.test_tree:
                if path in reached:
                    continue
                # Every other import form names the module, so the text check skips only files that cannot reach it.
                relative = package is not None and (path.parent == package or package in path.parents)
                if not (relative or word.search(self._source(path))) or target not in self._direct(path)[1]:
                    continue
                reached.add(path)
                if path.name.startswith("test_"):
                    found.add(path)
                elif path.name == "conftest.py":
                    found.update(test for test in tests if path.parent in test.parents)
                else:
                    pending.append(path)
        return found

    def readers(self, changed: Iterable[str]) -> dict[str, set[str]]:
        """Changed path -> the test modules that read it by a literal path."""
        found: dict[str, set[str]] = {}
        for path in changed:
            tests = {test for read, modules in self.read_map if read.matches(path) for test in modules}
            if tests:
                found[path] = tests
        return found

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


Tier = Literal["unit-integration", "e2e", "all"]


def _tier_paths(root: Path, paths: Iterable[str], tier: Tier) -> tuple[str, ...]:
    """Expand mixed-tier directories so neither explicit maps nor full fallback escape the tier."""

    def allowed(path: str) -> bool:
        e2e = "/tests/e2e/" in path or path.startswith("tests/e2e/")
        return tier == "all" or (e2e if tier == "e2e" else not e2e)

    kept: set[str] = set()
    for name in paths:
        target = root / name
        if target.is_file():
            if allowed(name):
                kept.add(name)
        elif target.is_dir():
            files = sorted(
                p.relative_to(root).as_posix() for p in target.rglob("test_*.py") if "__pycache__" not in p.parts
            )
            selected = [p for p in files if allowed(p)]
            if selected and len(selected) == len(files):
                kept.add(name)
            else:
                kept.update(selected)
    return tuple(sorted(p for p in kept if not any(p.startswith(f"{other}/") for other in kept)))


def select(root: Path, changed: Iterable[str], *, include_e2e: bool = False, tier: Tier | None = None) -> Selection:
    chosen: Tier = tier or ("all" if include_e2e else "unit-integration")
    changed = sorted(set(changed))
    try:
        selection = _select(root, changed)
    except UnsafeGraph as exc:
        selection = Selection("full", (), str(exc), any(path.startswith(FRONTEND_PREFIXES) for path in changed))
    paths = selection.paths
    if selection.mode == "full":
        paths = tuple(
            p.relative_to(root).as_posix()
            for home in ("packages", "tools")
            for p in (root / home).rglob("test_*.py")
            if "tests" in p.parts and "__pycache__" not in p.parts
        )
    kept = _tier_paths(root, paths, chosen)
    return Selection(selection.mode if kept else "none", kept, selection.reason, selection.frontend)


def _select(root: Path, changed: Iterable[str]) -> Selection:
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
    uncaused: set[str] = set()  # paths that select nothing through the checks below
    for path in changed:
        data = [(prefix, tests) for prefix, tests in DATA if path.startswith(prefix)]
        for prefix, tests in data:
            paths.update(tests)
            causes.add(prefix)
        if not data and not path.startswith(FRONTEND_PREFIXES):
            uncaused.add(path)
        if re.fullmatch(r"(?:packages|tools)/[^/]+/src/.+", path):
            uncaused.discard(path)
            if path.startswith((f"{DIST}/src/", f"{DEVKIT}/src/")):
                paths.update(SOURCE_TREE_TESTS)
            paths.update(ALL_SOURCES_TESTS)
            node = _source_node(workspace, path)
            if not node:
                return Selection("full", (), path, frontend)
            nodes.add(node)
            causes.add(node)
        elif re.fullmatch(r"(?:packages|tools)/[^/]+/tests/.+", path):
            uncaused.discard(path)
            name = path.rsplit("/", 1)[-1]
            paths.add(path if re.fullmatch(r"test_.+\.py", name) else path.rsplit("/", 1)[0])
            causes.add("tests")
        elif path.startswith(FRONTEND_PREFIXES):
            causes.add("frontend")
        elif not data and not (
            path in UNTESTED_FILES or path.startswith(UNTESTED_PREFIXES) or UNTESTED_MARKDOWN.fullmatch(path)
        ):
            return Selection("full", (), path, frontend)
    # Literal reads only add tests: full triggers and the unknown-path fallback above keep precedence.
    for path, readers in workspace.readers(changed).items():
        paths.update(readers)
        if path in uncaused:
            causes.add("reads")
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
@click.option("--e2e", "include_e2e", is_flag=True, help="Compatibility alias for --tier all.")
@click.option(
    "--tier",
    type=click.Choice(["unit-integration", "e2e", "all"]),
    default=None,
    help="Test tier; default unit-integration. Full fallback stays within this tier.",
)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@boundary
def main(base: str, list_only: bool, include_e2e: bool, tier: Tier | None, pytest_args: tuple[str, ...]) -> None:
    """Run the tests the changes since BASE can affect; arguments after `--` go to pytest."""
    changed = changed_paths(ROOT, base)
    selection = select(ROOT, changed, include_e2e=include_e2e, tier=tier)
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
