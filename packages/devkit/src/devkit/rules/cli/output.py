"""Text and JSON rendering for ``devkit rules`` commands."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import click

from devkit.advisory import AdvisoryError
from devkit.rules.engine.config import CONFIG_PATH, RulesConfig
from devkit.rules.engine.models import Phase, Rule, Severity, Violation
from devkit.rules.engine.phases import (
    PhaseEntry,
    declared_promotion,
    effective_phase,
    remaining_by_rule,
    transition_entries,
)
from devkit.rules.engine.policy import effective_severity
from devkit.rules.engine.settings import SettingsResolver
from devkit.rules.rules.base import guide_path

_COLORS = {Severity.ERROR: "red", Severity.WARNING: "yellow", Severity.INFO: "cyan"}


def echo_json(data: object) -> None:
    click.echo(json.dumps(data, indent=2))


def echo_problems(problems: Sequence[AdvisoryError]) -> None:
    """Each problem as an Agent Advisory Protocol block on stderr."""
    for problem in problems:
        click.echo(problem.render(), err=True)


def echo_warnings(problems: Sequence[AdvisoryError]) -> None:
    """Problems that do not fail the command, one ``Warning: (CODE) message`` line each on stderr."""
    for problem in problems:
        click.secho(f"Warning: ({problem.code}) {problem}", fg="yellow", err=True)


def guide_display(rule: Rule | None, workspace_root: Path) -> str | None:
    path = guide_path(rule) if rule is not None else None
    if path is None:
        return None
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return str(path)


def _transition_line(entry: PhaseEntry, remaining: dict[str, int]) -> str:
    """One status line per pending transition. Transitions only exist in hygiene runs:
    overrides move rules to ``hygiene`` and ``promote_to`` is only valid on hygiene rules."""
    if entry.overridden:
        line = (
            f"[PHASE_OVERRIDE: {entry.rule_id}={entry.effective_phase.value} "
            f"default={entry.default_phase.value} source={CONFIG_PATH}"
        )
    else:
        promote_to = entry.promote_to.value if entry.promote_to else "-"
        line = f"[PROMOTION: {entry.rule_id}={entry.effective_phase.value} promote_to={promote_to}"
    return f"{line} remaining={remaining.get(entry.rule_id, 0)}]"


def print_transitions(entries: Sequence[PhaseEntry], active: Phase, violations: Sequence[Violation]) -> None:
    pending = transition_entries(entries, active)
    if not pending:
        return
    remaining = remaining_by_rule(violations)
    for entry in pending:
        click.secho(_transition_line(entry, remaining), dim=True)
    if any(remaining.get(e.rule_id, 0) == 0 for e in pending):
        click.secho(
            "  remaining=0: drop the override in config, or switch the rule's declared phase to its promote_to.",
            dim=True,
        )
    click.echo()


def _counts(violations: Sequence[Violation]) -> Counter[str]:
    """Unfixed findings per severity value, plus ``fixed``."""
    counts: Counter[str] = Counter()
    for v in violations:
        counts["fixed" if v.fixed else v.severity.value] += 1
    return counts


def _describe_counts(counts: Counter[str], *, always: Sequence[Severity] = ()) -> list[str]:
    """``N error(s), M warning(s), K info(s), F fixed``; a zero count is shown only for ``always`` severities."""
    parts = [
        f"{counts[severity.value]} {severity.value}(s)"
        for severity in Severity
        if severity in always or counts[severity.value]
    ]
    if counts["fixed"]:
        parts.append(f"{counts['fixed']} fixed")
    return parts


def _print_rule_counts(violations: Sequence[Violation]) -> None:
    """One line per rule with its unresolved counts per severity and its fixed count (``--summary-only``)."""
    by_rule: dict[str, list[Violation]] = {}
    for v in violations:
        by_rule.setdefault(v.rule_id, []).append(v)
    for rule_id in sorted(by_rule):
        counts = _counts(by_rule[rule_id])
        worst = next((s for s in Severity if counts[s.value]), None)
        color = _COLORS[worst] if worst is not None else "green"
        parts = _describe_counts(counts, always=(Severity.ERROR, Severity.WARNING))
        click.secho(f"{rule_id}: {', '.join(parts)}", fg=color)


def print_violations(
    violations: Sequence[Violation],
    errors: Sequence[object],
    rules_by_id: dict[str, Rule],
    workspace_root: Path,
    *,
    summary_only: bool = False,
) -> None:
    """Findings (or per-rule counts) followed by one summary line; nothing passes while errors exist."""
    if not violations:
        if not errors:
            click.secho("✓ All governance checks passed cleanly.", fg="green", bold=True)
        return
    if summary_only:
        _print_rule_counts(violations)
    else:
        for v in violations:
            color = "green" if v.fixed else _COLORS[v.severity]
            status_tag = " [FIXED]" if v.fixed else (" [FIXABLE]" if v.fixable else "")
            click.secho(
                f"[{v.severity.value.upper()}] {v.rule_id} ({v.file}:{v.line}){status_tag}", fg=color, bold=True
            )
            click.echo(f"  Message: {v.message}")
            if v.remediation:
                click.secho(f"  Remediation: {v.remediation}", dim=True)
            guide = guide_display(rules_by_id.get(v.rule_id), workspace_root)
            if guide:
                click.secho(f"  Guide: {guide}", dim=True)
            click.echo()
    click.echo(f"Summary: {', '.join(_describe_counts(_counts(violations)))}")


def print_phase_plan(entries: Sequence[PhaseEntry]) -> None:
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


def explain_entry(
    rule: Rule, config: RulesConfig, resolver: SettingsResolver | None, workspace_root: Path
) -> dict[str, Any]:
    promote_to = declared_promotion(rule)
    return {
        "rule_id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "default_phase": rule.phase.value,
        "effective_phase": effective_phase(rule, config.phase_overrides).value,
        "default_severity": rule.severity.value,
        "effective_severity": effective_severity(rule, config.severity_overrides).value,
        "promote_to": promote_to.value if promote_to else None,
        "settings": resolver.to_dict() if resolver else None,
        "guide": guide_display(rule, workspace_root),
    }


def print_explain(rule: Rule, entry: dict[str, Any], resolver: SettingsResolver | None) -> None:
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
    guide = guide_path(rule)
    if guide is not None:
        click.echo(f"  Guide: {entry['guide']}")
        click.echo()
        click.echo(guide.read_text("utf-8").rstrip())
