"""Plugin checks: evaluators loaded from Python files a bundle or the project provides.

A plugin check is a ``BaseCheck`` subclass defined in a ``.py`` file that is
either recorded in the installation receipt under a ``kind = "workflow-check"``
asset (synchronized by ``devkit sync``) or placed under the project's
``[workflow] checks_dir``. Loaded checks join the registry with class
``plugin`` and are referenced from definitions like any primitive:
``name`` or ``name(arg ...)`` with the parameters the check declares.

Loading is atomic per file (``devkit.core.plugins.load_subclasses``): a file
that fails to import, declares an invalid check or redefines a name already
loaded contributes nothing. Plugin files are executable Python and must come
from a trusted source, exactly like custom rules of ``devkit.rules``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from devkit.core.plugins import iter_plugin_files, load_subclasses
from devkit.core.receipt import Receipt, load_receipt, verified_asset_files
from devkit.workflow.definition.checks import Check, CheckClass, CheckResult
from devkit.workflow.definition.ids import IDENT_HINT, is_ident
from devkit.workflow.errors import PluginError
from devkit.workflow.unit.envelope import Envelopes

PLUGIN_KIND = "workflow-check"
NAMESPACE = "devkit_workflow_check"


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


def _validate(plugin: BaseCheck) -> None:
    if not is_ident(plugin.name):
        raise PluginError(f"check name {plugin.name!r} must match {IDENT_HINT}")
    if not isinstance(plugin.description, str):
        raise PluginError(f"{plugin.name}: description must be a string")
    params = plugin.params
    if not isinstance(params, (tuple, list)) or not all(is_ident(p) for p in params):
        raise PluginError(f"{plugin.name}: params must be a tuple of names matching {IDENT_HINT}")


def load_check_files(files: Iterable[Path]) -> tuple[list[BaseCheck], list[PluginError]]:
    """Instantiate every ``BaseCheck`` subclass defined in each of the files, in order, whatever its name.

    A file that fails contributes nothing and is reported as a ``PluginError``
    (``WORKFLOW_CHECK_LOAD_FAILED``); so is a file that defines a check name an
    earlier file already defined.
    """
    load = load_subclasses(files, BaseCheck, namespace=NAMESPACE, validate=_validate)
    errors = [PluginError(str(failure), target_files=[failure.path.as_posix()]) for failure in load.errors]
    by_file: dict[Path, list[BaseCheck]] = {}
    for plugin in load.plugins:
        by_file.setdefault(plugin.path, []).append(plugin.instance)
    loaded: list[BaseCheck] = []
    seen: dict[str, Path] = {}
    for path, checks in by_file.items():
        names = [c.name for c in checks]
        clash = next((n for n in names if n in seen), None) or next(
            (n for i, n in enumerate(names) if n in names[:i]), None
        )
        if clash is not None:
            where = seen.get(clash, path)
            errors.append(
                PluginError(f"{path}: check {clash!r} is already defined in {where}", target_files=[path.as_posix()])
            )
            continue
        for check in checks:
            seen[check.name] = path
        loaded.extend(checks)
    return loaded, errors


def plugin_check_paths(
    workspace_root: Path, checks_dir: str, receipt: Receipt | None = None
) -> tuple[list[Path], list[PluginError]]:
    """Plugin files in load order: receipt ``workflow-check`` assets, then ``checks_dir``.

    Receipt files are found and checked with ``devkit.core.receipt.verified_asset_files``,
    as rules and gates are: a file that is missing, resolves outside the project
    or differs from the SHA-256 the receipt records is a ``WORKFLOW_CHECK_LOAD_FAILED``
    problem (``devkit sync`` restores it, ``devkit override create`` keeps an
    edit), never a silent skip; a file without a record (a project override) is
    loaded as it is, and no receipt file is skipped for its name. Files under
    ``checks_dir`` whose name starts with ``_`` or ``.`` are private helpers and
    are not loaded (``devkit.core.plugins.iter_plugin_files``).
    """
    paths: list[Path] = []
    errors: list[PluginError] = []
    if receipt is not None:
        verified, failures = verified_asset_files(workspace_root, receipt, PLUGIN_KIND)
        paths.extend(verified)
        errors.extend(
            PluginError(f"synchronized check {exc.message}", target_files=exc.target_files, fix=exc.fix)
            for exc in failures
        )
    directory = workspace_root / checks_dir
    for path in iter_plugin_files(directory):
        if path.parent == directory and path not in paths:
            paths.append(path)
    return paths, errors


def load_plugin_checks(
    workspace_root: Path, checks_dir: str, receipt: Receipt | None = None
) -> tuple[list[BaseCheck], list[PluginError]]:
    """Every plugin check the project has, plus the loading problems.

    ``receipt`` defaults to the workspace's installation receipt; a malformed
    receipt raises ``devkit.core.errors.ReceiptError``.
    """
    if receipt is None:
        receipt = load_receipt(workspace_root)
    paths, errors = plugin_check_paths(workspace_root, checks_dir, receipt)
    loaded, load_errors = load_check_files(paths)
    return loaded, errors + load_errors
