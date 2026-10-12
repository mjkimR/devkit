"""Plugin checks: evaluators loaded from Python files a bundle or the project provides.

A plugin check is a ``BaseCheck`` subclass defined in a ``.py`` file that is
either recorded in the installation receipt under a ``kind = "workflow-check"``
asset (synchronized by ``devkit sync``) or placed under the project's
``[workflow] checks_dir``. Loaded checks join the registry with class
``plugin`` and are referenced from definitions like any primitive:
``name`` or ``name(arg ...)`` with the parameters the check declares.

Plugin files are executable Python and must come from a trusted source, exactly
like custom rules of ``agent-rule-engine``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from agent_workflow_engine.checks import Check, CheckClass, CheckResult
from agent_workflow_engine.envelope import Envelopes
from agent_workflow_engine.receipt import asset_paths, receipt_assets

PLUGIN_KIND = "workflow-check"
CHECK_NAME = re.compile(r"^[a-z][a-z0-9-]*$")
PARAM_NAME = re.compile(r"^[a-z][a-z0-9-]*$")


class PluginError(ValueError):
    """A plugin file could not be loaded or declares an invalid check."""


@dataclass(frozen=True)
class CheckContext:
    """What a plugin check may inspect: the unit, its envelopes and the invocation."""

    workspace_root: Path
    unit_dir: Path
    anchor: str
    ref: str  # the reference text as written in the definition
    name: str
    args: tuple[str, ...]
    envelopes: Envelopes

    def read(self, name: str) -> str | None:
        """Text of a file in the unit directory, or ``None`` when missing or unreadable."""
        try:
            return (self.unit_dir / name).read_text("utf-8")
        except (OSError, UnicodeError):
            return None

    def passed(self, detail: str = "") -> CheckResult:
        return CheckResult(self.ref, CheckClass.PLUGIN, True, True, detail)

    def failed(self, detail: str = "") -> CheckResult:
        return CheckResult(self.ref, CheckClass.PLUGIN, False, True, detail)


class BaseCheck:
    """Subclass and set ``name``, ``description`` and optionally ``params``; implement ``evaluate``."""

    name: str = ""
    description: str = ""
    params: tuple[str, ...] = ()

    def evaluate(self, ctx: CheckContext) -> CheckResult:
        raise NotImplementedError

    def to_check(self) -> Check:
        return Check(self.name, CheckClass.PLUGIN, self.description, tuple(self.params))


def _validate(plugin: BaseCheck, where: Path) -> None:
    if not isinstance(plugin.name, str) or not CHECK_NAME.match(plugin.name):
        raise PluginError(f"{where}: check name {plugin.name!r} must match [a-z][a-z0-9-]*")
    if not isinstance(plugin.description, str):
        raise PluginError(f"{where}: {plugin.name}: description must be a string")
    params = plugin.params
    if not isinstance(params, (tuple, list)) or not all(isinstance(p, str) and PARAM_NAME.match(p) for p in params):
        raise PluginError(f"{where}: {plugin.name}: params must be a tuple of names matching [a-z][a-z0-9-]*")


def load_check_files(files: Iterable[Path]) -> tuple[list[BaseCheck], list[str]]:
    """Instantiate every ``BaseCheck`` subclass defined in the files, in order.

    A failure is recorded as an error string and does not stop the other files.
    A name defined twice is an error as well.
    """
    loaded: list[BaseCheck] = []
    errors: list[str] = []
    seen: dict[str, Path] = {}
    for py_file in files:
        if py_file.name.startswith(("_", ".")) or py_file.suffix != ".py":
            continue
        digest = hashlib.sha256(str(py_file.resolve()).encode()).hexdigest()[:16]
        module_name = f"workflow_check_{digest}"
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if spec is None or spec.loader is None:
            errors.append(f"{py_file}: cannot load as a Python module")
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ != module_name or not issubclass(obj, BaseCheck) or obj is BaseCheck:
                    continue
                if inspect.isabstract(obj):
                    continue
                plugin = obj()
                _validate(plugin, py_file)
                if plugin.name in seen:
                    raise PluginError(f"{py_file}: check {plugin.name!r} is already defined in {seen[plugin.name]}")
                seen[plugin.name] = py_file
                loaded.append(plugin)
        except Exception as exc:
            sys.modules.pop(module_name, None)
            errors.append(f"{py_file}: {exc}")
    return loaded, errors


def plugin_check_paths(workspace_root: Path, checks_dir: str) -> tuple[list[Path], list[str]]:
    """Plugin files in load order: receipt ``workflow-check`` assets, then ``checks_dir``.

    A receipt path that is not on disk is an error, not a silent skip: the
    managed copy must be restored with ``devkit sync``.
    """
    paths: list[Path] = []
    errors: list[str] = []
    for asset in receipt_assets(workspace_root, PLUGIN_KIND):
        for rel in asset_paths(asset, ".py"):
            path = workspace_root / rel
            if not path.is_file():
                errors.append(f"synchronized check {rel} is missing from the working tree (run devkit sync)")
                continue
            if path not in paths:
                paths.append(path)
    directory = workspace_root / checks_dir
    if directory.is_dir():
        for path in sorted(directory.glob("*.py")):
            if path.is_file() and path not in paths:
                paths.append(path)
    return paths, errors


def load_plugin_checks(workspace_root: Path, checks_dir: str) -> tuple[list[BaseCheck], list[str]]:
    """Every plugin check the project has, plus the loading errors."""
    paths, errors = plugin_check_paths(workspace_root, checks_dir)
    loaded, load_errors = load_check_files(paths)
    return loaded, errors + load_errors
