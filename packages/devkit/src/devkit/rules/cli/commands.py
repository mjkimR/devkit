"""``devkit rules`` commands: argument handling and exit codes; rendering lives in ``cli.output``.

Exit codes (``devkit.advisory.ExitCode``): ``0`` no error-severity violation
remains; ``1`` violations remain (``check``/``fix``); ``2`` the command could
not do its job: usage errors, an invalid ``[rules]`` table, rule loading,
policy or execution problems, a bad target or snapshot, an unknown rule.
"""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

import click
from click.core import ParameterSource

from devkit.advisory import AdvisoryError, ExitCode, as_advisory_error
from devkit.core import find_project_root
from devkit.rules.cli import output
from devkit.rules.engine.config import RulesConfig, load_rules_config
from devkit.rules.engine.errors import RuleProblem, RulesError
from devkit.rules.engine.models import Phase, Rule
from devkit.rules.engine.phases import resolve_phases
from devkit.rules.engine.policy import validate_policy
from devkit.rules.engine.project import build_project_registry, run_project_rules
from devkit.rules.engine.registry import RuleRegistry
from devkit.rules.workspace.snapshot import Snapshot, git_snapshot


def _is_json(output_format: object) -> bool:
    return str(output_format or "text").lower() == "json"


def _boundary(fn: Callable[..., None]) -> Callable[..., None]:
    """Render any error as an advisory on stderr (and as ``{"error": ...}`` on stdout under ``--format json``)."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            fn(*args, **kwargs)
        except (click.exceptions.Exit, click.ClickException, SystemExit):
            raise
        except Exception as exc:
            error = as_advisory_error(exc)
            if _is_json(kwargs.get("output_format")):
                output.echo_json({"error": error.to_dict()})
            click.echo(error.render(), err=True)
            sys.exit(int(error.exit_code))

    return wrapper


def _fail(problems: Sequence[AdvisoryError], *, json_error: bool = False) -> NoReturn:
    """Report collected problems as advisories and exit ``ERROR``; ``json_error`` also puts the first on stdout."""
    if json_error:
        output.echo_json({"error": problems[0].to_dict()})
    output.echo_problems(problems)
    sys.exit(int(ExitCode.ERROR))


@dataclass(frozen=True)
class RunRequest:
    """One ``check``/``fix`` invocation, after option parsing."""

    root: Path
    phase: Phase = Phase.LINTER
    fix: bool = False
    dry_run: bool = False
    rules_dir: Path | None = None
    json: bool = False
    summary_only: bool = False
    targets: tuple[str, ...] = ()
    snapshot: Snapshot | None = None


def _root(workspace_root: str | None) -> Path:
    """``--workspace-root``, or the project root found from the current directory."""
    if workspace_root is not None:
        return Path(workspace_root).resolve()
    return find_project_root(Path.cwd())


def _rules_path(rules_dir: str | None) -> Path | None:
    return Path(rules_dir).resolve() if rules_dir else None


def _execute(request: RunRequest) -> None:
    snapshot = request.snapshot
    if snapshot is not None:
        if not request.json:
            click.secho(snapshot.describe(), dim=True)
        if not snapshot.changed and not snapshot.deleted:
            if request.json:
                output.echo_json([])
            else:
                click.secho("✓ No changed files in the snapshot; nothing to check.", fg="green", bold=True)
            return

    run = run_project_rules(
        request.root,
        targets=(request.targets or None) if snapshot is None else None,
        snapshot=snapshot,
        phase=request.phase,
        fix=request.fix,
        dry_run=request.dry_run,
        rules_dir=request.rules_dir,
    )

    violations = run.result.violations
    errors = run.errors
    if request.json:
        output.echo_json([v.to_dict() for v in violations])
    else:
        entries = resolve_phases(run.rules, run.config.phase_overrides) if not errors else []
        output.print_transitions(entries, run.phase, violations)
        output.print_violations(
            violations,
            errors,
            {r.id: r for r in run.rules},
            run.workspace_root,
            summary_only=request.summary_only,
        )

    if errors:
        _fail(errors)
    if run.result.has_errors:
        sys.exit(int(ExitCode.FINDINGS))


def _snapshot_request(
    root: Path, *, phase: str, targets: tuple[str, ...], staged: bool, ci: bool, base_given: bool, base: str
) -> Snapshot:
    if staged and ci:
        raise click.UsageError("--staged and --ci are mutually exclusive")
    if staged and base_given:
        raise click.UsageError("--base applies to --ci only")
    if targets or phase.lower() != Phase.LINTER.value:
        raise click.UsageError("Git snapshot gates run the linter phase without file arguments")
    return git_snapshot(root, staged=staged, base=base)


@click.group(name="rules")
@click.version_option(package_name="devkit")
def cli() -> None:
    """Agent-managed rule engine for repository governance."""


_workspace_option = click.option(
    "--workspace-root",
    "-w",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Workspace root directory [default: the project root containing the current directory]",
)
_rules_dir_option = click.option(
    "--rules-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
    help="Custom rules directory, loaded after rules synchronized by devkit",
)
_format_option = click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)
_phase_option = click.option(
    "--phase",
    "-p",
    type=click.Choice(["linter", "hygiene"], case_sensitive=False),
    default="linter",
    help="Rule phase to execute",
)
_summary_option = click.option(
    "--summary-only",
    is_flag=True,
    help="Text output: per-rule counts, status lines and the summary only, no individual findings",
)


@cli.command(name="check")
@_workspace_option
@_phase_option
@_rules_dir_option
@_format_option
@_summary_option
@click.option("--staged", is_flag=True, help="Evaluate the exact staged Git tree instead of the working directory")
@click.option("--ci", is_flag=True, help="Evaluate the HEAD tree against its merge base with --base")
@click.option("--base", default="origin/main", show_default=True, help="Comparison base ref for --ci")
@click.argument("files", nargs=-1, type=str)
@click.pass_context
@_boundary
def check_cmd(
    ctx: click.Context,
    workspace_root: str | None,
    phase: str,
    rules_dir: str | None,
    output_format: str,
    summary_only: bool,
    staged: bool,
    ci: bool,
    base: str,
    files: tuple[str, ...],
) -> None:
    """Check repository files or directories against rules without modifying files."""
    root = _root(workspace_root)
    snapshot = None
    if staged or ci:
        base_given = ctx.get_parameter_source("base") is not ParameterSource.DEFAULT
        snapshot = _snapshot_request(
            root, phase=phase, targets=files, staged=staged, ci=ci, base_given=base_given, base=base
        )
        root = snapshot.root
    _execute(
        RunRequest(
            root=root,
            phase=Phase(phase.lower()),
            rules_dir=_rules_path(rules_dir),
            json=output_format.lower() == "json",
            summary_only=summary_only,
            targets=files,
            snapshot=snapshot,
        )
    )


@cli.command(name="fix")
@_workspace_option
@_phase_option
@_rules_dir_option
@click.option(
    "--dry-run",
    is_flag=True,
    help="Report the initial findings, marking fixable ones, without running fixers or writing files",
)
@_format_option
@_summary_option
@click.argument("files", nargs=-1, type=str)
@_boundary
def fix_cmd(
    workspace_root: str | None,
    phase: str,
    rules_dir: str | None,
    dry_run: bool,
    output_format: str,
    summary_only: bool,
    files: tuple[str, ...],
) -> None:
    """Automatically apply safe deterministic repairs to files or directories."""
    _execute(
        RunRequest(
            root=_root(workspace_root),
            phase=Phase(phase.lower()),
            fix=True,
            dry_run=dry_run,
            rules_dir=_rules_path(rules_dir),
            json=output_format.lower() == "json",
            summary_only=summary_only,
            targets=files,
        )
    )


def _registry_and_policy(root: Path, rules_dir: str | None) -> tuple[RulesConfig, RuleRegistry, list[RuleProblem]]:
    """The project's config and registry, with every loading and policy problem."""
    config = load_rules_config(root)
    registry = build_project_registry(root, rules_dir=_rules_path(rules_dir))
    _, policy_errors = validate_policy(
        registry.get_all(),
        phase_overrides=config.phase_overrides,
        severity_overrides=config.severity_overrides,
        settings=config.settings,
    )
    return config, registry, [*registry.errors, *policy_errors]


@cli.command(name="phases")
@_workspace_option
@_rules_dir_option
@_format_option
@_boundary
def phases_cmd(workspace_root: str | None, rules_dir: str | None, output_format: str) -> None:
    """Show each rule's default and effective phase, project overrides, and pending promotions."""
    config, registry, errors = _registry_and_policy(_root(workspace_root), rules_dir)
    entries = sorted(resolve_phases(registry.get_all(), config.phase_overrides), key=lambda e: e.rule_id)
    if output_format.lower() == "json":
        output.echo_json([e.to_dict() for e in entries])
    else:
        output.print_phase_plan(entries)
    if errors:
        _fail(errors)


def _concerns(problem: RuleProblem, rule: Rule | None) -> bool:
    """Whether a loading or policy problem is about ``rule`` (unattributed problems concern every rule)."""
    return rule is None or problem.rule_id is None or problem.rule_id == rule.id


@cli.command(name="explain")
@_workspace_option
@_rules_dir_option
@_format_option
@click.argument("rule_id", type=str)
@_boundary
def explain_cmd(workspace_root: str | None, rules_dir: str | None, output_format: str, rule_id: str) -> None:
    """Describe one rule: phase, severity, effective settings and its guide.

    Loading problems and policy problems of other rules are printed as
    warnings; policy problems of this rule, and an unknown rule ID, exit with
    status 2.
    """
    root = _root(workspace_root)
    config, registry, problems = _registry_and_policy(root, rules_dir)
    rule = registry.get(rule_id)
    load_errors = [id(p) for p in registry.errors]
    errors: list[AdvisoryError] = [p for p in problems if id(p) not in load_errors and _concerns(p, rule)]
    warnings = [p for p in problems if p not in errors]
    if rule is None:
        available = ", ".join(sorted(r.id for r in registry.get_all()))
        errors.insert(
            0,
            RulesError.invalid_input(
                f"unknown rule: {rule_id}; available: {available}",
                code="RULES_UNKNOWN_RULE",
                target_files=["RULE_ID"],
                fix="Pass a rule ID listed by `devkit rules phases`",
            ),
        )
    output.echo_warnings(warnings)
    if errors or rule is None:
        _fail(errors, json_error=_is_json(output_format))
    resolvers, _ = validate_policy(
        [rule],
        phase_overrides={},
        severity_overrides={},
        settings={k: v for k, v in config.settings.items() if k == rule.id},
    )
    resolver = resolvers.get(rule.id)
    entry = output.explain_entry(rule, config, resolver, root)
    if output_format.lower() == "json":
        output.echo_json(entry)
        return
    output.print_explain(rule, entry, resolver)
