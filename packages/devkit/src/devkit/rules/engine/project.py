"""Run a project's rules the way every caller must: one assembly of config, registry and context.

``devkit rules check``/``fix``, the ``rules-staged`` commit gate and the
workflow engine's ``lint-clean`` check all evaluate a project through
``run_project_rules``, so project policy (``[rules]`` in ``.devkit/config.toml``,
including ``exclude``), the synchronized rules recorded in the receipt and the
Git snapshot handling cannot differ between them. Callers render the returned
``ProjectRun`` and choose their own exit semantics. ``load_project_rules`` is
the loading half on its own (policy, rules and policy validation, no
evaluation), used by ``devkit rules phases``/``explain``.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from devkit.advisory import AdvisoryError
from devkit.rules.engine.config import RulesConfig, load_rules_config
from devkit.rules.engine.discovery import resolve_managed_rules
from devkit.rules.engine.errors import PolicyError, RuleProblem, RulesDirError, RulesRunError, TargetError
from devkit.rules.engine.evaluator import EvaluationResult, evaluate_rules
from devkit.rules.engine.models import Phase, Rule, RuleContext, Violation
from devkit.rules.engine.phases import promotion_notices, resolve_phases
from devkit.rules.engine.policy import validate_policy
from devkit.rules.engine.registry import RuleRegistry, default_rule_registry
from devkit.rules.engine.settings import SettingsResolver
from devkit.rules.workspace.cache import WorkspaceCache
from devkit.rules.workspace.markdown import local_target
from devkit.rules.workspace.snapshot import Snapshot, materialize_snapshot

SNAPSHOT_PREFIX = "devkit-rules-snapshot-"


@dataclass(frozen=True)
class ProjectRules:
    """A project's ``[rules]`` policy and loaded rules, validated against each other.

    ``load_errors`` are rule loading failures (an invalid receipt, a missing or
    drifted synchronized rule, a rule file that fails to import);
    ``policy_errors`` are ``[rules]`` entries that cannot apply to the loaded
    rules. ``resolvers`` are the settings resolvers of the rules whose settings
    type-check.
    """

    config: RulesConfig
    registry: RuleRegistry
    rules_dir: Path | None
    load_errors: tuple[RuleProblem, ...]
    policy_errors: tuple[PolicyError, ...]
    resolvers: dict[str, SettingsResolver]

    @property
    def rules(self) -> list[Rule]:
        return self.registry.get_all()

    @property
    def errors(self) -> list[RuleProblem]:
        """Load errors followed by policy errors."""
        return [*self.load_errors, *self.policy_errors]


def load_project_rules(root: Path, rules_dir: Path | None = None, *, source_root: Path | None = None) -> ProjectRules:
    """Read the ``[rules]`` policy of ``root``, load its rules and validate the policy against them.

    The rules are those of ``build_project_registry``. Raises
    ``RulesConfigError`` (``RULES_CONFIG_INVALID``) for an invalid ``[rules]``
    table and the core ``ConfigError`` for an unreadable config file; loading
    and policy problems are collected, not raised.
    """
    config = load_rules_config(root)
    rules_path = rules_dir.resolve() if rules_dir is not None else None
    registry = build_project_registry(root, rules_dir=rules_path, source_root=source_root)
    resolvers, policy_errors = validate_policy(
        registry.get_all(),
        phase_overrides=config.phase_overrides,
        severity_overrides=config.severity_overrides,
        settings=config.settings,
    )
    return ProjectRules(
        config=config,
        registry=registry,
        rules_dir=rules_path,
        load_errors=tuple(registry.errors),
        policy_errors=tuple(policy_errors),
        resolvers=resolvers,
    )


@dataclass(frozen=True)
class ProjectRun:
    """Everything one evaluation produced.

    ``workspace_root`` is the resolved directory the rules ran in; for a Git
    snapshot that is the temporary directory the tree was materialized into,
    which no longer exists when the run is returned. ``load_errors`` are rule
    loading failures (an invalid receipt, a missing or drifted synchronized
    rule, a rule file that fails to import); when there are any, no rule is
    evaluated. ``result.errors`` are policy and rule execution errors.
    ``context`` is ``None`` when there was nothing to evaluate (empty targets).
    """

    workspace_root: Path
    phase: Phase
    config: RulesConfig
    registry: RuleRegistry
    rules_dir: Path | None
    context: RuleContext | None
    result: EvaluationResult
    load_errors: tuple[RuleProblem, ...] = ()

    @property
    def rules(self) -> list[Rule]:
        return self.registry.get_all()

    @property
    def errors(self) -> list[RuleProblem]:
        """Load errors followed by evaluation errors; any of them means the run could not complete."""
        return [*self.load_errors, *self.result.errors]

    @property
    def blocking_violations(self) -> list[Violation]:
        """Unfixed error-severity violations: the findings that fail the run."""
        return self.result.blocking_violations

    @property
    def notices(self) -> list[AdvisoryError]:
        """Notices of a completed run (``RULES_PROMOTION_READY``); none when the run could not complete."""
        if self.errors:
            return []
        entries = resolve_phases(self.rules, self.config.phase_overrides)
        return promotion_notices(entries, self.phase, self.result.violations)

    @property
    def ok(self) -> bool:
        """Whether the run completed without problems and no blocking violation remains."""
        return not self.load_errors and self.result.ok

    def raise_for_problems(self) -> None:
        """Raise ``RulesRunError`` (``RULES_RUN_FAILED``) carrying ``errors`` when the run could not complete."""
        if self.errors:
            raise RulesRunError(self.errors)


def build_project_registry(
    workspace_root: Path, *, rules_dir: Path | None = None, source_root: Path | None = None
) -> RuleRegistry:
    """Built-in rules, then rule assets recorded by ``devkit sync``, then ``rules_dir``.

    ``source_root`` is the working tree behind a Git snapshot: Git-ignored
    managed rule files are read from there when they match the receipt.
    Loading problems are collected in the registry's ``errors``.
    """
    registry = default_rule_registry()
    managed = resolve_managed_rules(workspace_root, source_root=source_root)
    registry.errors.extend(managed.errors)
    registry.discover_from_files(managed.paths)
    if rules_dir is not None:
        registry.discover_from_dir(rules_dir)
    return registry


def expand_targets(workspace_root: Path, cache: WorkspaceCache, targets: Sequence[str | Path]) -> list[str]:
    """Explicit targets as workspace-relative files; a directory expands to the files under it.

    Expansion lists what ``WorkspaceCache.find_files`` lists (regular files,
    skipping ignored directories). Relative targets are taken from
    ``workspace_root``. Anything that is not an existing file or directory
    inside the workspace raises ``TargetError``.
    """
    files: list[str] = []
    for target in targets:
        path = Path(target)
        absolute = Path(os.path.normpath(path if path.is_absolute() else workspace_root / path))
        if not absolute.is_relative_to(workspace_root):
            absolute = absolute.resolve()
        if not absolute.is_relative_to(workspace_root):
            raise TargetError(f"{target} is outside the workspace {workspace_root}", target_files=[str(target)])
        if absolute.is_dir():
            for found in cache.find_files(absolute, extensions=None):
                rel = found.relative_to(workspace_root).as_posix()
                if rel not in files:
                    files.append(rel)
        elif absolute.is_file():
            if not absolute.resolve().is_relative_to(workspace_root):
                raise TargetError(
                    f"{target} is a symlink that resolves outside the workspace {workspace_root}",
                    target_files=[str(target)],
                )
            relative = absolute.relative_to(workspace_root).as_posix()
            if relative not in files:
                files.append(relative)
        else:
            raise TargetError(
                f"{target} is not an existing file or directory inside the workspace", target_files=[str(target)]
            )
    return files


def _run(
    workspace_root: Path,
    *,
    targets: Sequence[str | Path] | None,
    expand: bool,
    phase: Phase,
    fix: bool,
    dry_run: bool,
    rules_dir: Path | None,
    source_root: Path | None,
) -> ProjectRun:
    cache = WorkspaceCache(workspace_root, git_filter=source_root is None)
    project = load_project_rules(workspace_root, rules_dir, source_root=source_root)
    config = project.config

    # ``RuleContext`` reads an empty ``changed_files`` as "every file", so an
    # explicit selection that names no file must skip evaluation instead.
    if targets is None:
        changed: list[str] = []
        has_work = True
    else:
        changed = expand_targets(workspace_root, cache, targets) if expand else [Path(t).as_posix() for t in targets]
        has_work = bool(changed)
    context: RuleContext | None = None
    if has_work:
        # Targets are already workspace-relative (``expand_targets`` or the snapshot's diff).
        context = RuleContext(
            workspace_root=workspace_root,
            changed_files=changed,
            phase=phase,
            fix=fix,
            dry_run=dry_run,
            cache=cache,
            rules_dir=project.rules_dir,
            phase_overrides=dict(config.phase_overrides),
            severity_overrides=dict(config.severity_overrides),
            rule_settings=dict(config.settings),
            exclude=config.exclude,
        )

    result = EvaluationResult()
    if context is not None and not project.load_errors:
        result = evaluate_rules(context, project.rules)
    return ProjectRun(
        workspace_root=workspace_root,
        phase=phase,
        config=config,
        registry=project.registry,
        rules_dir=project.rules_dir,
        context=context,
        result=result,
        load_errors=project.load_errors,
    )


def run_project_rules(
    root: Path,
    *,
    targets: Sequence[str | Path] | None = None,
    snapshot: Snapshot | None = None,
    phase: Phase = Phase.LINTER,
    fix: bool = False,
    dry_run: bool = False,
    rules_dir: Path | None = None,
) -> ProjectRun:
    """Load the project's rule policy and rules, then evaluate them.

    ``root`` is the project working tree. The ``[rules]`` policy comes from
    ``root/.devkit/config.toml`` and the rules are the built-ins, then the
    rule assets recorded in the installation receipt, then the Python files
    under ``rules_dir``.

    ``targets`` selects what is checked: ``None`` checks the whole workspace;
    otherwise each entry is a file or directory (relative to ``root`` or
    absolute inside it) and directories expand to the files under them. An
    empty selection checks nothing. ``[rules] exclude`` applies either way.

    With ``snapshot`` (from ``git_snapshot(root, ...)``) the snapshot's tree is
    materialized into a temporary directory that becomes the workspace: the
    policy, the receipt and tracked rules come from the snapshot, Git-ignored
    managed rule copies come from ``root`` when they match the receipt's hash,
    and the snapshot's changed files are the targets, together with the
    Markdown files whose links point at a path the snapshot deletes. ``rules_dir`` must lie
    inside the repository and is read from the snapshot (``RulesDirError``
    otherwise), so unstaged rule edits cannot change the result. A snapshot
    run cannot take ``targets`` or ``fix``, and ``snapshot`` must come from
    ``root``; violating that contract is a programming error (``ValueError``).

    Raises ``RulesConfigError`` (``RULES_CONFIG_INVALID``) for an invalid ``[rules]``
    table, ``TargetError`` (``RULES_TARGET_INVALID``) for an invalid explicit
    target, ``RulesDirError`` (``RULES_DIR_INVALID``) and ``SnapshotError``
    (``RULES_SNAPSHOT_FAILED``) when the snapshot cannot be materialized. Rule
    loading problems (``RuleLoadError``) are returned in ``load_errors``;
    policy problems (``PolicyError``, ``SettingsError``) and rule execution
    errors (``RuleExecutionError``) in ``result.errors``.
    """
    if snapshot is None:
        return _run(
            root.resolve(),
            targets=targets,
            expand=True,
            phase=phase,
            fix=fix,
            dry_run=dry_run,
            rules_dir=rules_dir,
            source_root=None,
        )
    if targets is not None:
        raise ValueError("a snapshot run checks the snapshot's changed files; do not pass targets")
    if fix:
        raise ValueError("a snapshot run cannot apply fixes")
    if snapshot.root != root.resolve():
        raise ValueError(f"snapshot was taken from {snapshot.root}, not {root.resolve()}")
    rules_rel = _snapshot_rules_dir(snapshot, rules_dir)
    with tempfile.TemporaryDirectory(prefix=SNAPSHOT_PREFIX) as directory:
        workspace = Path(directory).resolve()
        materialize_snapshot(snapshot, workspace)
        snapshot_rules = None
        if rules_rel is not None:
            snapshot_rules = workspace / rules_rel
            if not snapshot_rules.is_dir():
                raise RulesDirError(
                    f"rules directory {rules_rel.as_posix()} is not in the {snapshot.mode} snapshot; "
                    "commit or stage it (untracked and ignored files are not part of a snapshot)",
                    target_files=["--rules-dir"],
                    fix=f"git add {rules_rel.as_posix()}",
                )
        return _run(
            workspace,
            targets=snapshot_targets(snapshot, workspace),
            expand=False,
            phase=phase,
            fix=False,
            dry_run=False,
            rules_dir=snapshot_rules,
            source_root=snapshot.root,
        )


def snapshot_targets(snapshot: Snapshot, workspace: Path) -> list[str]:
    """The snapshot's changed files, then every Markdown file whose relative links point at a deleted path.

    ``workspace`` is the materialized snapshot. Deleting a document breaks the
    links to it in files the commit does not touch, so those files are checked
    too.
    """
    targets = list(snapshot.changed)
    if not snapshot.deleted:
        return targets
    deleted = set(snapshot.deleted)
    for name in snapshot.deleted:  # links to a directory that lost files
        deleted.update(parent.as_posix() for parent in PurePosixPath(name).parents if parent.as_posix() != ".")
    cache = WorkspaceCache(workspace, git_filter=False)
    for path in cache.find_files(workspace, extensions=(".md",)):
        rel = path.relative_to(workspace).as_posix()
        if rel in targets:
            continue
        for link in cache.get_links(path):
            target = local_target(link.target)
            if target is None:
                continue
            resolved = Path(os.path.normpath(path.parent / target.path))
            if resolved.is_relative_to(workspace) and resolved.relative_to(workspace).as_posix() in deleted:
                targets.append(rel)
                break
    return targets


def _snapshot_rules_dir(snapshot: Snapshot, rules_dir: Path | None) -> Path | None:
    """``rules_dir`` relative to the repository, so it is read from the snapshot, not the working tree."""
    if rules_dir is None:
        return None
    resolved = rules_dir.resolve()
    if not resolved.is_relative_to(snapshot.root):
        raise RulesDirError(
            f"rules directory {resolved} is outside the repository {snapshot.root}; a snapshot run reads rules "
            "from the snapshot only, so keep custom rules in the repository",
            target_files=["--rules-dir"],
            fix="Move the custom rules into the repository and pass that directory to --rules-dir",
        )
    return resolved.relative_to(snapshot.root)
