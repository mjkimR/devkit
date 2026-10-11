from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from agent_rule_engine.cache import WorkspaceCache
from agent_rule_engine.evaluator import evaluate
from agent_rule_engine.models import Phase, RuleContext
from agent_rule_engine.registry import default_registry


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

    ctx = RuleContext(
        workspace_root=root_path,
        changed_files=list(target_files),
        phase=Phase(phase.lower()),
        fix=fix,
        dry_run=dry_run,
        cache=cache,
        rules_dir=Path(rules_dir).resolve() if rules_dir else None,
    )

    registry = default_registry()
    if ctx.rules_dir:
        registry.discover_from_dir(ctx.rules_dir)

    rules = registry.get_all()
    result = evaluate(ctx, rules)

    if output_format.lower() == "json":
        data = [v.to_dict() for v in result.violations]
        click.echo(json.dumps(data, indent=2))
    else:
        # Human-readable text format
        if not result.violations:
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


if __name__ == "__main__":
    cli()
