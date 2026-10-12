from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import click

from agent_rule_engine.engine.config import CONFIG_PATH, ConfigError, RulesConfig, load_rules_config
from agent_rule_engine.engine.discovery import resolve_managed_rules
from agent_rule_engine.engine.evaluator import (
    EvaluationResult,
    effective_severity,
    evaluate,
    validate_severity_overrides,
)
from agent_rule_engine.engine.models import Phase, Rule, RuleContext, Violation
from agent_rule_engine.engine.phases import (
    PhaseEntry,
    effective_phase,
    remaining_by_rule,
    resolve_phases,
    transition_entries,
    validate_phase_overrides,
)
from agent_rule_engine.engine.registry import RuleRegistry, default_registry
from agent_rule_engine.engine.settings import build_resolvers
from agent_rule_engine.rules.base import guide_path
from agent_rule_engine.workspace.cache import WorkspaceCache
from agent_rule_engine.workspace.snapshot import Snapshot, SnapshotError, git_snapshot, materialize


def _load_config(root_path: Path) -> RulesConfig:
    try:
        return load_rules_config(root_path)
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


def _build_registry(
    root_path: Path, rules_dir: str | None, source_root: Path | None = None
) -> tuple[RuleRegistry, Path | None]:
    """Built-in rules, then rule assets recorded by ``devkit sync``, then ``--rules-dir``.

    ``source_root`` is the working tree behind a Git snapshot: Git-ignored
    managed rule files are read from there when they match the receipt.
    """
    registry = default_registry()
    managed = resolve_managed_rules(root_path, source_root=source_root)
    registry.errors.extend(managed.errors)
    registry.discover_from_files(managed.paths)
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


def _guide_display(rule: Rule | None, workspace_root: Path) -> str | None:
    path = guide_path(rule) if rule is not None else None
    if path is None:
        return None
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return str(path)


def _print_violations(result: EvaluationResult, rules_by_id: dict[str, Rule], workspace_root: Path) -> None:
    if not result.violations and not result.errors:
        click.secho("✓ All governance checks passed cleanly.", fg="green", bold=True)
        return
    for v in result.violations:
        prefix = f"[{v.severity.value.upper()}]"
        color = "green" if v.fixed else ("red" if v.severity.value == "error" else "yellow")
        status_tag = " [FIXED]" if v.fixed else (" [FIXABLE]" if v.fixable else "")

        click.secho(f"{prefix} {v.rule_id} ({v.file}:{v.line}){status_tag}", fg=color, bold=True)
        click.echo(f"  Message: {v.message}")
        if v.remediation:
            click.secho(f"  Remediation: {v.remediation}", dim=True)
        guide = _guide_display(rules_by_id.get(v.rule_id), workspace_root)
        if guide:
            click.secho(f"  Guide: {guide}", dim=True)
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


def _run_rules(
    workspace_root: str,
    phase: str,
    fix: bool,
    dry_run: bool,
    rules_dir: str | None,
    output_format: str,
    target_files: tuple[str, ...],
    snapshot: Snapshot | None = None,
) -> None:
    root_path = Path(workspace_root).resolve()
    is_json = output_format.lower() == "json"
    if snapshot is not None and not is_json:
        click.secho(snapshot.describe(), dim=True)
        if not snapshot.changed:
            click.secho("✓ No changed files in the snapshot; nothing to check.", fg="green", bold=True)
            return
    if snapshot is not None and not snapshot.changed:
        click.echo("[]")
        return

    cache = WorkspaceCache(root_path)
    config = _load_config(root_path)
    registry, rules_path = _build_registry(
        root_path, rules_dir, source_root=snapshot.root if snapshot is not None else None
    )

    try:
        ctx = RuleContext(
            workspace_root=root_path,
            changed_files=list(snapshot.changed) if snapshot is not None else list(target_files),
            phase=Phase(phase.lower()),
            fix=fix,
            dry_run=dry_run,
            cache=cache,
            rules_dir=rules_path,
            phase_overrides=dict(config.phase_overrides),
            severity_overrides=dict(config.severity_overrides),
            rule_settings=dict(config.settings),
        )
    except ValueError as exc:
        raise click.BadParameter(str(exc), param_hint="files") from exc

    rules = registry.get_all()
    result = EvaluationResult(errors=list(registry.errors)) if registry.errors else evaluate(ctx, rules)
    entries = resolve_phases(rules, ctx.phase_overrides) if not result.errors else []

    if is_json:
        data = [v.to_dict() for v in result.violations]
        click.echo(json.dumps(data, indent=2))
    else:
        _print_transitions(entries, ctx.phase, result.violations)
        _print_violations(result, {r.id: r for r in rules}, root_path)

    if result.errors:
        for err in result.errors:
            click.secho(f"Error: {err}", fg="red", err=True)

    if result.has_errors:
        sys.exit(1)


def _run_on_snapshot(
    workspace_root: str,
    phase: str,
    rules_dir: str | None,
    output_format: str,
    target_files: tuple[str, ...],
    staged: bool,
    ci: bool,
    base: str,
) -> None:
    if staged and ci:
        raise click.UsageError("--staged and --ci are mutually exclusive")
    if target_files or phase.lower() != Phase.LINTER.value:
        raise click.UsageError("Git snapshot gates run the linter phase without file arguments")
    try:
        snapshot = git_snapshot(Path(workspace_root), staged=staged, base=base)
    except SnapshotError as exc:
        raise click.ClickException(f"{exc}; verify the Git repository and the --base ref") from exc
    with tempfile.TemporaryDirectory(prefix="agent-rules-snapshot-") as directory:
        try:
            materialize(snapshot, Path(directory))
        except SnapshotError as exc:
            raise click.ClickException(str(exc)) from exc
        _run_rules(
            workspace_root=directory,
            phase=phase,
            fix=False,
            dry_run=False,
            rules_dir=rules_dir,
            output_format=output_format,
            target_files=(),
            snapshot=snapshot,
        )


@click.group(name="agent-rules")
@click.version_option(package_name="agent-rule-engine")
def cli() -> None:
    """Agent-managed rule engine for repository governance."""


_workspace_option = click.option(
    "--workspace-root",
    "-w",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Workspace root directory",
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


@cli.command(name="check")
@_workspace_option
@_phase_option
@_rules_dir_option
@_format_option
@click.option("--staged", is_flag=True, help="Evaluate the exact staged Git tree instead of the working directory")
@click.option("--ci", is_flag=True, help="Evaluate the HEAD tree against its merge base with --base")
@click.option("--base", default="origin/main", show_default=True, help="Comparison base ref for --ci")
@click.argument("files", nargs=-1, type=str)
def check_cmd(
    workspace_root: str,
    phase: str,
    rules_dir: str | None,
    output_format: str,
    staged: bool,
    ci: bool,
    base: str,
    files: tuple[str, ...],
) -> None:
    """Check repository files against rules without modifying files."""
    if staged or ci:
        _run_on_snapshot(workspace_root, phase, rules_dir, output_format, files, staged, ci, base)
        return
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
@_workspace_option
@_phase_option
@_rules_dir_option
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview fixes without modifying files on disk",
)
@_format_option
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


def _policy_errors(registry: RuleRegistry, config: RulesConfig) -> list[str]:
    rules = registry.get_all()
    _, settings_errors = build_resolvers(rules, config.settings)
    return [
        *registry.errors,
        *validate_phase_overrides(rules, config.phase_overrides),
        *validate_severity_overrides(rules, config.severity_overrides),
        *settings_errors,
    ]


@cli.command(name="phases")
@_workspace_option
@_rules_dir_option
@_format_option
def phases_cmd(workspace_root: str, rules_dir: str | None, output_format: str) -> None:
    """Show each rule's default and effective phase, project overrides, and pending promotions."""
    root_path = Path(workspace_root).resolve()
    config = _load_config(root_path)
    registry, _ = _build_registry(root_path, rules_dir)
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


@cli.command(name="explain")
@_workspace_option
@_rules_dir_option
@_format_option
@click.argument("rule_id", type=str)
def explain_cmd(workspace_root: str, rules_dir: str | None, output_format: str, rule_id: str) -> None:
    """Describe one rule: phase, severity, effective settings and its guide."""
    root_path = Path(workspace_root).resolve()
    config = _load_config(root_path)
    registry, _ = _build_registry(root_path, rules_dir)
    rule = registry.get(rule_id)
    errors = _policy_errors(registry, config)
    if rule is None:
        errors.append(f"unknown rule: {rule_id}; available: {', '.join(sorted(r.id for r in registry.get_all()))}")
    if errors:
        for err in errors:
            click.secho(f"Error: {err}", fg="red", err=True)
        sys.exit(1)
    assert rule is not None
    resolvers, _ = build_resolvers([rule], {k: v for k, v in config.settings.items() if k == rule.id})
    resolver = resolvers.get(rule.id)
    guide = guide_path(rule)
    promote_to: Phase | None = getattr(rule, "promote_to", None)
    entry = {
        "rule_id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "default_phase": rule.phase.value,
        "effective_phase": effective_phase(rule, config.phase_overrides).value,
        "default_severity": rule.severity.value,
        "effective_severity": effective_severity(rule, config.severity_overrides).value,
        "promote_to": promote_to.value if promote_to else None,
        "settings": resolver.to_dict() if resolver else None,
        "guide": _guide_display(rule, root_path),
    }
    if output_format.lower() == "json":
        click.echo(json.dumps(entry, indent=2))
        return
    click.secho(f"{rule.id}: {rule.name}", bold=True)
    click.echo(f"  {rule.description}")
    click.echo(f"  Phase: {entry['default_phase']} (effective {entry['effective_phase']})")
    click.echo(f"  Severity: {entry['default_severity']} (effective {entry['effective_severity']})")
    if entry["promote_to"]:
        click.echo(f"  Promote to: {entry['promote_to']}")
    if resolver is not None:
        click.echo("  Settings:")
        for key, value in resolver.base.items():
            default = getattr(resolver.default, key)
            marker = "" if value == default else f" (default {default!r})"
            click.echo(f"    {key} = {value!r}{marker}")
        for override in resolver.overrides:
            values = ", ".join(f"{k} = {v!r}" for k, v in override.values.items())
            click.echo(f"    [{override.path}] {values}")
    else:
        click.echo("  Settings: none")
    if guide is not None:
        click.echo(f"  Guide: {entry['guide']}")
        click.echo()
        click.echo(guide.read_text("utf-8").rstrip())


if __name__ == "__main__":
    cli()
