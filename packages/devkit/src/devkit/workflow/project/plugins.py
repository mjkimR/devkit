"""Plugin checks: evaluators loaded from plugin packages a bundle or the project provides.

A plugin check is a ``BaseCheck`` subclass defined in a module of a plugin
package (``devkit.core.plugins``): a directory that is either recorded in the
installation receipt as a ``kind = "workflow-check"`` asset (synchronized by
``devkit sync``) or an immediate subdirectory of the project's ``[workflow]
checks_dir``. Loaded checks join the registry with class ``plugin`` and are
referenced from definitions like any primitive: ``name`` or ``name(arg ...)``
with the parameters the check declares.

Loading is atomic per package (``devkit.core.plugins.load_subclasses``): a
package that fails to import, declares an invalid check or redefines a name
already loaded contributes nothing. Plugin packages are executable Python and
must come from a trusted source, exactly like custom rules of ``devkit.rules``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from devkit.core.plugins import PluginFailure, PluginPackage, iter_plugin_packages, load_subclasses
from devkit.core.receipt import Receipt, load_receipt, verified_asset_packages
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


def _failure(failure: PluginFailure) -> PluginError:
    return PluginError(str(failure), target_files=[failure.path.as_posix()], fix=failure.fix)


def load_check_packages(packages: Iterable[PluginPackage]) -> tuple[list[BaseCheck], list[PluginError]]:
    """Instantiate every ``BaseCheck`` subclass defined in each plugin package, in order.

    A package that fails contributes nothing and is reported as a
    ``PluginError`` (``WORKFLOW_CHECK_LOAD_FAILED``) naming the package; so is
    a package that defines a check name an earlier package (or another of its
    own classes) already defined.
    """
    load = load_subclasses(packages, BaseCheck, namespace=NAMESPACE, validate=_validate)
    errors = [_failure(failure) for failure in load.errors]
    by_package: dict[str, tuple[PluginPackage, list[BaseCheck]]] = {}
    for plugin in load.plugins:
        by_package.setdefault(plugin.package.key, (plugin.package, []))[1].append(plugin.instance)
    loaded: list[BaseCheck] = []
    seen: dict[str, Path] = {}
    for package, checks in by_package.values():
        where_now = package.location
        names = [c.name for c in checks]
        clash = next((n for n in names if n in seen), None) or next(
            (n for i, n in enumerate(names) if n in names[:i]), None
        )
        if clash is not None:
            where = seen.get(clash, where_now)
            errors.append(
                PluginError(
                    f"{where_now}: check {clash!r} is already defined in {where}", target_files=[where_now.as_posix()]
                )
            )
            continue
        for check in checks:
            seen[check.name] = where_now
        loaded.extend(checks)
    return loaded, errors


def plugin_check_packages(
    workspace_root: Path, checks_dir: str, receipt: Receipt | None = None
) -> tuple[list[PluginPackage], list[PluginError]]:
    """Plugin packages in load order: receipt ``workflow-check`` assets, then the packages of ``checks_dir``.

    Receipt packages are found and their files checked with
    ``devkit.core.receipt.verified_asset_packages``, as rules and gates are: a
    file that is missing, resolves outside the project or differs from the
    SHA-256 the receipt records is a ``WORKFLOW_CHECK_LOAD_FAILED`` problem
    (``devkit sync`` restores it, ``devkit override create`` keeps an edit) and
    its package is not loaded, never a silent skip; a file without a record (a
    project override) is loaded as it is. Under ``checks_dir`` each immediate
    subdirectory not starting with ``_`` or ``.`` is one package; a ``.py``
    file directly in it is a problem telling to move it into a package
    directory (``devkit.core.plugins.iter_plugin_packages``).
    """
    packages: list[PluginPackage] = []
    errors: list[PluginError] = []
    if receipt is not None:
        verified, failures = verified_asset_packages(workspace_root, receipt, PLUGIN_KIND)
        packages.extend(verified)
        errors.extend(
            PluginError(f"synchronized check {exc.message}", target_files=exc.target_files, fix=exc.fix)
            for exc in failures
        )
    found, misplaced = iter_plugin_packages(workspace_root / checks_dir)
    packages.extend(found)
    errors.extend(_failure(failure) for failure in misplaced)
    return packages, errors


def load_plugin_checks(
    workspace_root: Path, checks_dir: str, receipt: Receipt | None = None
) -> tuple[list[BaseCheck], list[PluginError]]:
    """Every plugin check the project has, plus the loading problems.

    ``receipt`` defaults to the workspace's installation receipt; a malformed
    receipt raises ``devkit.core.errors.ReceiptError``.
    """
    if receipt is None:
        receipt = load_receipt(workspace_root)
    packages, errors = plugin_check_packages(workspace_root, checks_dir, receipt)
    loaded, load_errors = load_check_packages(packages)
    return loaded, errors + load_errors
