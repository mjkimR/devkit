"""``devkit rules`` commands: argument handling and exit codes; rendering lives in ``cli.output``.

``--format json`` prints one object: ``{"violations", "errors"}`` (``check``,
``fix``), ``{"rules", "errors"}`` (``phases``), ``{"rule", "warnings",
"errors"}`` (``explain``), or ``{"error"}`` when the command fails outright.
Text output is ``[KIND: ...]`` sentinel lines (``cli.output``).

Exit codes (``devkit.advisory.ExitCode``): ``0`` no error-severity violation
remains; ``1`` violations remain (``check``/``fix``); ``2`` the command could
not do its job: an invalid argument (``ARGUMENT_INVALID``, including an
unknown rule), an unreadable configuration or an invalid ``[rules]`` table, a
bad target or snapshot. Collected loading, policy and execution problems exit
with the highest ``exit_code`` among them (``2`` for each of them today).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import click
from click.core import ParameterSource

from devkit.advisory import AdvisoryError, ExitCode
from devkit.core.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    existing_directory,
    exit_on_problems,
    is_json,
    resolve_root,
    workspace_option,
)
from devkit.core.errors import ArgumentError
from devkit.rules.cli import output
from devkit.rules.engine.errors import RuleProblem
from devkit.rules.engine.models import Phase, Rule
from devkit.rules.engine.phases import resolve_phases
from devkit.rules.engine.project import load_project_rules, run_project_rules
from devkit.rules.workspace.snapshot import Snapshot, git_snapshot


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


def _rules_path(rules_dir: str | None) -> Path | None:
    return existing_directory(rules_dir, "--rules-dir") if rules_dir else None


def _execute(request: RunRequest) -> None:
    snapshot = request.snapshot
    if snapshot is not None:
        if not request.json:
            click.echo(snapshot.describe())
        if not snapshot.changed and not snapshot.deleted:
            if request.json:
                echo_json({"violations": [], "errors": []})
            else:
                output.echo_ok(output.NOTHING_TO_CHECK)
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
        echo_json({"violations": [v.to_dict() for v in violations], "errors": [e.to_dict() for e in errors]})
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
        if run.ok:
            output.echo_ok()

    exit_on_problems(errors)
    if run.blocking_violations:
        raise SystemExit(int(ExitCode.FINDINGS))


def _snapshot_request(
    root: Path, *, phase: str, targets: tuple[str, ...], staged: bool, ci: bool, base_given: bool, base: str
) -> Snapshot:
    if staged and ci:
        raise ArgumentError("--staged and --ci are mutually exclusive", target_files=["--staged", "--ci"])
    if staged and base_given:
        raise ArgumentError("--base applies to --ci only", target_files=["--base"])
    if targets or phase.lower() != Phase.LINTER.value:
        raise ArgumentError(
            "Git snapshot gates run the linter phase without file arguments", target_files=["--phase", "FILES"]
        )
    return git_snapshot(root, staged=staged, base=base)


@click.group(name="rules")
def cli() -> None:
    """Agent-managed rule engine for repository governance."""


_workspace_option = workspace_option()
_rules_dir_option = click.option(
    "--rules-dir",
    type=str,
    default=None,
    help="Custom rules directory, loaded after rules synchronized by devkit",
)
_format_option = FORMAT_OPTION
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
@boundary
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
    root = resolve_root(workspace_root)
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
            json=is_json(output_format),
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
@boundary
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
            root=resolve_root(workspace_root),
            phase=Phase(phase.lower()),
            fix=True,
            dry_run=dry_run,
            rules_dir=_rules_path(rules_dir),
            json=is_json(output_format),
            summary_only=summary_only,
            targets=files,
        )
    )


@cli.command(name="phases")
@_workspace_option
@_rules_dir_option
@_format_option
@boundary
def phases_cmd(workspace_root: str | None, rules_dir: str | None, output_format: str) -> None:
    """Show each rule's default and effective phase, project overrides, and pending promotions."""
    project = load_project_rules(resolve_root(workspace_root), _rules_path(rules_dir))
    errors = project.errors
    entries = sorted(resolve_phases(project.rules, project.config.phase_overrides), key=lambda e: e.rule_id)
    if is_json(output_format):
        echo_json({"rules": [e.to_dict() for e in entries], "errors": [e.to_dict() for e in errors]})
    else:
        output.print_phase_plan(entries)
    exit_on_problems(errors)


def _concerns(problem: RuleProblem, rule: Rule | None) -> bool:
    """Whether a loading or policy problem is about ``rule`` (unattributed problems concern every rule)."""
    return rule is None or problem.rule_id is None or problem.rule_id == rule.id


@cli.command(name="explain")
@_workspace_option
@_rules_dir_option
@_format_option
@click.argument("rule_id", type=str)
@boundary
def explain_cmd(workspace_root: str | None, rules_dir: str | None, output_format: str, rule_id: str) -> None:
    """Describe one rule: phase, severity, effective settings and its guide.

    Loading problems and policy problems of other rules are printed as
    warnings; policy problems of this rule exit with status 2, and an unknown
    rule ID is an argument error.
    """
    root = resolve_root(workspace_root)
    project = load_project_rules(root, _rules_path(rules_dir))
    rule = project.registry.get(rule_id)
    errors: list[AdvisoryError] = [p for p in project.policy_errors if _concerns(p, rule)]
    warnings = [p for p in project.errors if p not in errors]
    output.echo_warnings(warnings)
    if rule is None:
        available = ", ".join(sorted(r.id for r in project.rules))
        raise ArgumentError(
            f"unknown rule: {rule_id}; available: {available}",
            target_files=["RULE_ID"],
            fix="Pass a rule ID listed by `devkit rules phases`",
        )
    resolver = project.resolvers.get(rule.id)
    entry = output.explain_entry(rule, project.config, resolver, root)
    if is_json(output_format):
        echo_json(
            {
                "rule": entry,
                "warnings": [w.to_dict() for w in warnings],
                "errors": [e.to_dict() for e in errors],
            }
        )
    elif not errors:
        output.print_explain(rule, entry, resolver)
    exit_on_problems(errors)
