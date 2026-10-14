"""Helpers for the tests in a rule's folder: load the rule as devkit does, then evaluate it on files a test writes.

A rule is one directory, and its tests live beside the code in
``<rule folder>/tests/`` (never imported by devkit's loaders; run them with
``devkit rules test``). A distributed or custom rule is a plugin package, so
its tests load it the way devkit loads a deployed copy::

    from devkit.rules.testing import check, load_rule

    RULE = load_rule(__file__)  # the rule defined in the folder above tests/


    def test_reports_a_missing_heading(tmp_path):
        found = check(RULE, tmp_path, {"docs/a.md": "no heading\\n"})
        assert [(v.file, v.line) for v in found] == [("docs/a.md", 1)]


    def test_settings_apply_per_path(tmp_path):
        settings = {"max_bytes": 10, "overrides": [{"path": "big/**", "max_bytes": 100}]}
        assert check(RULE, tmp_path, {"big/a.md": "x" * 50}, settings=settings) == []

Built-in rules are importable modules; their tests construct them directly
(``MarkdownLinkRule()``) and use ``check`` the same way. ``check`` runs the
real engine (``evaluate_rules``): settings go through the same parser and
``SettingsResolver`` as ``[rules.settings.<id>]`` in ``.devkit/config.toml``,
the evaluator sets each finding's effective phase and severity, and
``fix=True`` applies the fix and rechecks.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from devkit.core.plugins import TESTS_DIRECTORY, PluginPackage, plugin_modules
from devkit.core.receipt import MANAGED_PATH, RECEIPT_PATH
from devkit.rules.engine.config import parse_rules_config
from devkit.rules.engine.discovery import resolve_managed_rules
from devkit.rules.engine.errors import RuleLoadError, RulesRunError
from devkit.rules.engine.evaluator import EvaluationResult, evaluate_rules
from devkit.rules.engine.models import Phase, Rule, RuleContext, Violation
from devkit.rules.engine.project import expand_targets
from devkit.rules.engine.registry import RuleRegistry
from devkit.rules.rules.base import managed_counterpart, override_counterpart
from devkit.rules.workspace.cache import WorkspaceCache

__all__ = ["check", "evaluate", "load_rule", "rule_directory", "write_files"]


def rule_directory(anchor: str | Path) -> Path:
    """The rule folder of ``anchor``: the parent of the nearest ``tests`` directory containing it, else ``anchor``.

    ``anchor`` is a test file (``__file__``) anywhere under ``<rule folder>/tests/``,
    or the rule folder itself.
    """
    path = Path(anchor).resolve()
    if path.is_file():
        path = path.parent
    for candidate in (path, *path.parents):
        if candidate.name == TESTS_DIRECTORY:
            return candidate.parent
    return path


def _workspace_of(managed: Path) -> Path | None:
    """The workspace root a path under ``.devkit/managed/`` belongs to, else ``None``."""
    marker = PurePosixPath(MANAGED_PATH).parts
    parts = managed.parts
    for index in range(len(parts) - len(marker) + 1):
        if parts[index : index + len(marker)] == marker:
            return Path(*parts[:index])
    return None


def _receipt_package(workspace: Path, managed: Path, folder: Path) -> PluginPackage:
    """The package devkit builds from the receipt for the deployed rule at ``managed``: only the files the
    receipt lists, each verified against its hash, an override's file replacing the managed one.

    Raises ``RuleLoadError`` as devkit would report the rule: a listed file that is missing or drifted, or a
    folder the receipt does not list as a rule asset.
    """
    found = resolve_managed_rules(workspace)
    target = managed.resolve()
    owners = [
        (directory, package)
        for package in found.packages
        if package.root is not None and target.is_relative_to(directory := package.root.resolve())
    ]
    if owners:
        return max(owners, key=lambda owner: len(owner[0].parts))[1]
    for error in found.errors:
        listed = [workspace / item for item in error.target_files]
        if error.target_files == (RECEIPT_PATH,) or any(
            (managed_counterpart(path) or path).resolve().is_relative_to(target) for path in listed
        ):
            raise RuleLoadError(str(error), target_files=list(error.target_files), actor=error.actor, fix=error.fix)
    raise RuleLoadError(
        f"{folder} is not a rule asset the installation receipt {workspace / RECEIPT_PATH} lists",
        target_files=[str(folder)],
        fix="Run `devkit sync`, or test the rule in its source folder",
    )


def _rule_package(folder: Path) -> PluginPackage:
    """The plugin package of a rule folder, with a project override applied as devkit applies it.

    A deployed rule is the managed copy (``.devkit/managed/<bundle>/...``) with
    each module file the project override (``.devkit/overrides/<bundle>/...``)
    holds replacing the managed one, so the tests of either copy test the rule
    devkit runs: a managed copy's tests, which an override without its own
    ``tests/`` keeps, run against the overridden modules. When the project has
    an installation receipt, the package is the one devkit builds from it: only
    the module files the receipt lists for the rule, verified against their
    hashes (``_receipt_package``); without one the two folders are merged
    file by file. Any other folder is loaded as it is. Raises ``ValueError``
    when one module has two files.
    """
    managed = managed_counterpart(folder)
    base = managed if managed is not None and managed.is_dir() else folder
    deployed = managed if managed is not None else base
    workspace = _workspace_of(deployed)
    if workspace is not None and (workspace / RECEIPT_PATH).exists():
        return _receipt_package(workspace, deployed, folder)
    override = override_counterpart(base)
    if override is None or not override.is_dir():
        return PluginPackage.from_directory(base)
    modules = {**PluginPackage.from_directory(base).modules, **PluginPackage.from_directory(override).modules}
    return PluginPackage(str(base.resolve()), folder, plugin_modules(modules.items()))


def load_rule(anchor: str | Path, rule_id: str | None = None) -> Rule:
    """Load the rule folder of ``anchor`` as a plugin package, as devkit loads a deployed rule, and return one rule.

    The folder of a deployed copy is loaded with the project override applied:
    the managed modules, each replaced by the override's file when it holds one,
    whichever of the two folders ``anchor`` is in. With an installation receipt
    only the files it lists for the rule are loaded, verified as ``devkit rules
    check`` verifies them, so the tests run what devkit runs. ``rule_id`` selects among the
    rules the package defines; without it the package must define exactly one.
    Raises ``RuleLoadError`` (``RULES_LOAD_FAILED``) when the folder does not
    exist, is a deployed copy the receipt does not list or lists with a missing
    or drifted file, fails to load, defines no rule, several without a ``rule_id``, or
    none with ``rule_id``.
    """
    folder = rule_directory(anchor)
    if not folder.is_dir():
        raise RuleLoadError(f"rule folder {folder} does not exist", target_files=[str(folder)], rule_id=rule_id)
    registry = RuleRegistry()
    try:
        package = _rule_package(folder)
    except ValueError as exc:
        raise RuleLoadError(f"cannot load rule folder {folder}: {exc}", target_files=[str(folder)]) from None
    rules = registry.discover_from_packages([package])
    if registry.errors:
        problem = registry.errors[0]
        raise RuleLoadError(str(problem), target_files=list(problem.target_files), rule_id=rule_id)
    ids = [rule.id for rule in rules]
    if rule_id is not None:
        for rule in rules:
            if rule.id == rule_id:
                return rule
        raise RuleLoadError(
            f"{folder} defines no rule {rule_id}; it defines: {', '.join(ids) or 'none'}",
            target_files=[str(folder)],
            rule_id=rule_id,
        )
    if len(rules) != 1:
        raise RuleLoadError(
            f"{folder} defines {len(rules)} rules ({', '.join(ids) or 'none'}); "
            "pass rule_id when it defines several, and define a BaseRule subclass in the folder",
            target_files=[str(folder)],
        )
    return rules[0]


def write_files(root: Path, files: Mapping[str, str | bytes]) -> None:
    """Write each workspace-relative ``/`` path of ``files`` under ``root`` (text as UTF-8), creating directories.

    Raises ``ValueError`` for an absolute path or one with a ``..`` segment.
    """
    for name, content in files.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ValueError(f"expected a workspace-relative path without '..': {name!r}")
        path = root.joinpath(*relative.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_bytes(content.encode("utf-8"))


def evaluate(
    rule: Rule,
    root: Path,
    files: Mapping[str, str | bytes] | None = None,
    *,
    targets: Sequence[str] = (),
    fix: bool = False,
    dry_run: bool = False,
    settings: Mapping[str, Any] | None = None,
    phase: Phase | str | None = None,
    exclude: Sequence[str] = (),
) -> EvaluationResult:
    """Write ``files`` under ``root``, evaluate ``rule`` alone and return the whole ``EvaluationResult``.

    ``targets`` are workspace-relative files or directories (directories
    expand as in ``devkit rules check``); none means the whole workspace.
    ``settings`` is the ``[rules.settings.<rule id>]`` table as values, with
    path overrides under ``"overrides"`` (``[{"path": "docs/**", "max_lines": 800}]``);
    an invalid shape raises ``RulesConfigError`` and values that do not
    type-check are returned in ``errors``, as in a project run. ``phase``
    defaults to the rule's declared phase. ``exclude`` is ``[rules] exclude``
    (workspace-relative ``**`` patterns no rule targets). Problems are returned, not raised:
    use ``check`` for the findings of a run that must succeed.
    """
    root.mkdir(parents=True, exist_ok=True)
    root = root.resolve()
    write_files(root, files or {})
    configured = {} if settings is None else {rule.id: dict(settings)}
    config = parse_rules_config({"rules": {"settings": configured}})
    cache = WorkspaceCache(root)
    changed = expand_targets(root, cache, targets) if targets else []
    if targets and not changed:
        return EvaluationResult()  # an empty selection checks nothing; RuleContext would read [] as every file
    ctx = RuleContext(
        workspace_root=root,
        changed_files=changed,
        phase=Phase(phase) if phase is not None else rule.phase,
        fix=fix,
        dry_run=dry_run,
        cache=cache,
        rule_settings=dict(config.settings),
        exclude=tuple(exclude),
    )
    return evaluate_rules(ctx, [rule])


def check(
    rule: Rule,
    root: Path,
    files: Mapping[str, str | bytes] | None = None,
    *,
    targets: Sequence[str] = (),
    fix: bool = False,
    dry_run: bool = False,
    settings: Mapping[str, Any] | None = None,
    phase: Phase | str | None = None,
    exclude: Sequence[str] = (),
) -> list[Violation]:
    """The violations ``evaluate`` returns; raises ``RulesRunError`` (``RULES_RUN_FAILED``) with the problems
    when the evaluation reports any (invalid settings, a rule that raised)."""
    result = evaluate(
        rule, root, files, targets=targets, fix=fix, dry_run=dry_run, settings=settings, phase=phase, exclude=exclude
    )
    if result.errors:
        raise RulesRunError(result.errors)
    return result.violations
