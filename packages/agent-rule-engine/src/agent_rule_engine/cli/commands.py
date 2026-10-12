from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from agent_rule_engine.engine.config import CONFIG_PATH, ConfigError, RulesConfig, load_rules_config
from agent_rule_engine.engine.evaluator import EvaluationResult, evaluate
from agent_rule_engine.engine.models import Phase, RuleContext, Violation
from agent_rule_engine.engine.phases import (
    PhaseEntry,
    remaining_by_rule,
    resolve_phases,
    transition_entries,
    validate_phase_overrides,
)
from agent_rule_engine.engine.registry import RuleRegistry, default_registry
from agent_rule_engine.workspace.cache import WorkspaceCache


def _load_config(root_path: Path) -> RulesConfig:
    try:
        return load_rules_config(root_path)
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


def _build_registry(rules_dir: str | None) -> tuple[RuleRegistry, Path | None]:
    registry = default_registry()
    rules_path = Path(rules_dir).resolve() if rules_dir else None
    if rules_path:
        registry.discover_from_dir(rules_path)
    return registry, rules_path


def _transition_line(entry: PhaseEntry, active: Phase, remaining: dict[str, int] | None) -> str:
    """One status line per pending transition, mirroring the phase plan in text output."""
    if entry.overridden:
        line = (
            f"[PHASE_OVERRIDE: {entry.rule_id}={entry.effective_phase.value} "
            f"default={entry.default_phase.value} source={CONFIG_PATH}"
        )
    else:
        line = f"[PROMOTION: {entry.rule_id}={entry.effective_phase.value} promote_to={entry.promote_to.value}"  # type: ignore[union-attr]
    if remaining is not None and active == Phase.HYGIENE:
        line += f" remaining={remaining.get(entry.rule_id, 0)}"
    return line + "]"


def _print_transitions(entries: list[PhaseEntry], active: Phase, violations: list[Violation]) -> None:
    pending = transition_entries(entries, active)
    if not pending:
        return
    remaining = remaining_by_rule(violations)
    for entry in pending:
        click.secho(_transition_line(entry, active, remaining), dim=True)
    if active == Phase.HYGIENE and any(remaining.get(e.rule_id, 0) == 0 for e in pending):
        click.secho(
            "  remaining=0: drop the override in config, or switch the rule's declared phase to its promote_to.",
            dim=True,
        )
    click.echo()


def _run_rules(
    workspace_root: str,
    phase: str,
    fix: bool,
    dry_run: bool,
    rules_dir: str | None,
    output_format: str,
    target_files: tuple[str, ...],
) -> None:
    root_path = Path(workspace_root).resolve()
    cache = WorkspaceCache(root_path)
    config = _load_config(root_path)
    registry, rules_path = _build_registry(rules_dir)

    try:
        ctx = RuleContext(
            workspace_root=root_path,
            changed_files=list(target_files),
            phase=Phase(phase.lower()),
            fix=fix,
            dry_run=dry_run,
            cache=cache,
            rules_dir=rules_path,
            phase_overrides=dict(config.phase_overrides),
        )
    except ValueError as exc:
        raise click.BadParameter(str(exc), param_hint="files") from exc

    rules = registry.get_all()
    result = EvaluationResult(errors=list(registry.errors)) if registry.errors else evaluate(ctx, rules)
    entries = resolve_phases(rules, ctx.phase_overrides) if not result.errors else []

    if output_format.lower() == "json":
        data = [v.to_dict() for v in result.violations]
        click.echo(json.dumps(data, indent=2))
    else:
        # Human-readable text format
        _print_transitions(entries, ctx.phase, result.violations)
        if not result.violations and not result.errors:
            click.secho("✓ All governance checks passed cleanly.", fg="green", bold=True)
        else:
            for v in result.violations:
                prefix = f"[{v.severity.value.upper()}]"
                color = "green" if v.fixed else ("red" if v.severity.value == "error" else "yellow")
                status_tag = " [FIXED]" if v.fixed else (" [FIXABLE]" if v.fixable else "")

                click.secho(f"{prefix} {v.rule_id} ({v.file}:{v.line}){status_tag}", fg=color, bold=True)
                click.echo(f"  Message: {v.message}")
                if v.remediation:
                    click.secho(f"  Remediation: {v.remediation}", dim=True)
                click.echo()

            unfixed_errors = sum(1 for v in result.violations if v.severity.value == "error" and not v.fixed)
            fixed_count = sum(1 for v in result.violations if v.fixed)
            warnings = sum(1 for v in result.violations if v.severity.value == "warning")

            summary_parts = []
            if fixed_count:
                summary_parts.append(f"{fixed_count} fixed")
            if unfixed_errors:
                summary_parts.append(f"{unfixed_errors} errors")
            if warnings:
                summary_parts.append(f"{warnings} warnings")

            click.echo(f"Summary: {', '.join(summary_parts)}")

    if result.errors:
        for err in result.errors:
            click.secho(f"Error: {err}", fg="red", err=True)

    if result.has_errors:
        sys.exit(1)


@click.group(name="agent-rules")
@click.version_option(package_name="agent-rule-engine")
def cli() -> None:
    """Agent-managed rule engine for specifications and governance."""


@cli.command(name="check")
@click.option(
    "--workspace-root",
    "-w",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Workspace root directory",
)
@click.option(
    "--phase",
    "-p",
    type=click.Choice(["linter", "hygiene"], case_sensitive=False),
    default="linter",
    help="Rule phase to execute",
)
@click.option(
    "--rules-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
    help="Custom rules directory",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)
@click.argument("files", nargs=-1, type=str)
def check_cmd(
    workspace_root: str,
    phase: str,
    rules_dir: str | None,
    output_format: str,
    files: tuple[str, ...],
) -> None:
    """Check repository files against rules without modifying files."""
    _run_rules(
        workspace_root=workspace_root,
        phase=phase,
        fix=False,
        dry_run=False,
        rules_dir=rules_dir,
        output_format=output_format,
        target_files=files,
    )


@cli.command(name="fix")
@click.option(
    "--workspace-root",
    "-w",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Workspace root directory",
)
@click.option(
    "--phase",
    "-p",
    type=click.Choice(["linter", "hygiene"], case_sensitive=False),
    default="linter",
    help="Rule phase to execute",
)
@click.option(
    "--rules-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
    help="Custom rules directory",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview fixes without modifying files on disk",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)
@click.argument("files", nargs=-1, type=str)
def fix_cmd(
    workspace_root: str,
    phase: str,
    rules_dir: str | None,
    dry_run: bool,
    output_format: str,
    files: tuple[str, ...],
) -> None:
    """Automatically apply safe deterministic repairs to files."""
    _run_rules(
        workspace_root=workspace_root,
        phase=phase,
        fix=True,
        dry_run=dry_run,
        rules_dir=rules_dir,
        output_format=output_format,
        target_files=files,
    )


@cli.command(name="phases")
@click.option(
    "--workspace-root",
    "-w",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Workspace root directory",
)
@click.option(
    "--rules-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
    help="Custom rules directory",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)
def phases_cmd(workspace_root: str, rules_dir: str | None, output_format: str) -> None:
    """Show each rule's default and effective phase, project overrides, and pending promotions."""
    root_path = Path(workspace_root).resolve()
    config = _load_config(root_path)
    registry, _ = _build_registry(rules_dir)
    rules = registry.get_all()
    errors = list(registry.errors) + validate_phase_overrides(rules, config.phase_overrides)
    entries = sorted(resolve_phases(rules, config.phase_overrides), key=lambda e: e.rule_id)

    if output_format.lower() == "json":
        click.echo(json.dumps([e.to_dict() for e in entries], indent=2))
    else:
        width = max((len(e.rule_id) for e in entries), default=len("RULE"))
        click.echo(f"{'RULE'.ljust(width)}  DEFAULT  EFFECTIVE  TRANSITION")
        for e in entries:
            if e.overridden:
                note = f"override -> {e.default_phase.value} (remove from {CONFIG_PATH} when clean)"
            elif e.promote_to:
                note = f"promote_to -> {e.promote_to.value} (flip declared phase when clean)"
            else:
                note = "-"
            click.echo(f"{e.rule_id.ljust(width)}  {e.default_phase.value:<7}  {e.effective_phase.value:<9}  {note}")

    for err in errors:
        click.secho(f"Error: {err}", fg="red", err=True)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    cli()
