"""``devkit rules`` commands: argument handling and exit codes; rendering lives in ``cli.output``.

``--format json`` prints one object: ``{"violations", "errors", "notices"}``
(``check``, ``fix``), ``{"rules", "errors"}`` (``phases``), ``{"rule",
"notices", "errors"}`` (``explain``), ``{"results", "summary", "notices"}``
(``test``), or ``{"error"}`` when the command fails outright. Text output is ``[KIND: ...]`` sentinel lines (``cli.output``);
warnings and notices follow the result on stderr as advisory blocks.

Exit codes (``devkit.advisory.ExitCode``): ``0`` no error-severity violation
remains (``test``: no rule's tests failed); ``1`` violations remain
(``check``/``fix``) or a rule's tests failed (``test``); ``2`` the command could
not do its job: an invalid argument (``ARGUMENT_INVALID``, including an
unknown rule), an unreadable configuration or an invalid ``[rules]`` table, a
bad target or snapshot, pytest not importable (``RULES_TEST_UNAVAILABLE``). Collected loading, policy and execution problems exit
with the highest ``exit_code`` among them (``2`` for each of them today).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import click
from click.core import ParameterSource

from devkit.advisory import AdvisoryError, ExitCode, Level
from devkit.core.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    existing_directory,
    exit_on_problems,
    exit_on_warnings,
    is_json,
    resolve_root,
    workspace_option,
)
from devkit.core.errors import ArgumentError
from devkit.rules.cli import output
from devkit.rules.engine.errors import RuleProblem
from devkit.rules.engine.models import Phase, Rule
from devkit.rules.engine.phases import resolve_phases
from devkit.rules.engine.project import ProjectRules, load_project_rules, run_project_rules
from devkit.rules.engine.related import resolve_related
from devkit.rules.engine.rule_tests import run_rule_tests, summary
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
                echo_json({"violations": [], "errors": [], "notices": []})
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
    notices = run.notices
    if request.json:
        echo_json(
            {
                "violations": [v.to_dict() for v in violations],
                "errors": [e.to_dict() for e in errors],
                "notices": [n.to_dict() for n in notices],
            }
        )
    else:
        output.print_transitions(run.transitions, run.phase, violations)
        output.print_violations(
            violations,
            errors,
            run.guides,
            run.workspace_root,
            summary_only=request.summary_only,
        )
        if run.ok:
            output.echo_ok()

    echo_notices(notices)
    exit_on_problems(errors)
    if run.blocking_violations:
        raise SystemExit(int(ExitCode.FINDINGS))
    exit_on_warnings(notices)


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
    help="Custom rules directory (one plugin package per subdirectory), loaded after rules synchronized by devkit",
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


def _unknown_rule(project: ProjectRules, rule_id: str) -> ArgumentError:
    available = ", ".join(sorted(r.id for r in project.rules))
    return ArgumentError(
        f"unknown rule: {rule_id}; available: {available}",
        target_files=["RULE_ID"],
        fix="Pass a rule ID listed by `devkit rules phases`",
    )


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
    """Describe one rule: phase, severity, effective settings, related instructions and playbooks, and its guide.

    Loading problems and policy problems of other rules are reported as
    warnings (with ``--strict``, exit status 1); policy problems of this rule
    exit with status 2, and an unknown rule ID is an argument error.
    """
    root = resolve_root(workspace_root)
    project = load_project_rules(root, _rules_path(rules_dir))
    rule = project.registry.get(rule_id)
    errors: list[AdvisoryError] = [p for p in project.policy_errors if _concerns(p, rule)]
    warnings = [p.with_level(Level.WARNING) for p in project.errors if p not in errors]
    if rule is None:
        echo_notices(warnings)
        raise _unknown_rule(project, rule_id)
    resolver = project.resolvers.get(rule.id)
    entry = output.explain_entry(rule, project.config, resolver, root)
    related, unresolved = resolve_related(root, rule)
    entry["related"] = [item.to_dict() for item in related]
    warnings = [*warnings, *unresolved]
    if is_json(output_format):
        echo_json(
            {
                "rule": entry,
                "notices": [w.to_dict() for w in warnings],
                "errors": [e.to_dict() for e in errors],
            }
        )
    elif not errors:
        output.print_explain(rule, entry, resolver)
    echo_notices(warnings)
    exit_on_problems(errors)
    exit_on_warnings(warnings)


PYTEST_ARGS = "devkit.rules.pytest_args"


class _PytestArgsCommand(click.Command):
    """Arguments after the first ``--`` are pytest's: kept in ``ctx.meta``, apart from the rule IDs."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        if "--" in args:
            index = args.index("--")
            ctx.meta[PYTEST_ARGS] = tuple(args[index + 1 :])
            args = args[:index]
        return super().parse_args(ctx, args)


@cli.command(name="test", cls=_PytestArgsCommand)
@_workspace_option
@_rules_dir_option
@_format_option
@click.argument("rule_ids", nargs=-1, type=str, metavar="[RULE-ID]... [-- PYTEST-ARGS...]")
@click.pass_context
@boundary
def test_cmd(
    ctx: click.Context, workspace_root: str | None, rules_dir: str | None, output_format: str, rule_ids: tuple[str, ...]
) -> None:
    """Run the tests in each rule's folder (<rule folder>/tests/) with pytest; all rules when no RULE-ID is given.

    Rules resolve as for `explain` (built-in, synchronized, --rules-dir). Each
    tests directory runs once in a pytest subprocess from the workspace root,
    with its full output in a log file. Arguments after `--` go to pytest.
    Loading and policy problems are reported as warnings.
    """
    root = resolve_root(workspace_root)
    project = load_project_rules(root, _rules_path(rules_dir))
    warnings: list[AdvisoryError] = [p.with_level(Level.WARNING) for p in project.errors]
    if rule_ids:
        selected: list[Rule] = []
        for rule_id in dict.fromkeys(rule_ids):
            rule = project.registry.get(rule_id)
            if rule is None:
                echo_notices(warnings)
                raise _unknown_rule(project, rule_id)
            selected.append(rule)
    else:
        selected = sorted(project.rules, key=lambda r: r.id)
    try:
        results = run_rule_tests(root, selected, ctx.meta.get(PYTEST_ARGS, ()))
    except AdvisoryError:
        echo_notices(warnings)
        raise
    counts = summary(results)
    if is_json(output_format):
        echo_json(
            {
                "results": [output.rule_test_entry(item, root) for item in results],
                "summary": counts,
                "notices": [w.to_dict() for w in warnings],
            }
        )
    else:
        output.print_rule_tests(results, root, counts)
    echo_notices(warnings)
    if counts["failed"]:
        raise SystemExit(int(ExitCode.FINDINGS))
    exit_on_warnings(warnings)
