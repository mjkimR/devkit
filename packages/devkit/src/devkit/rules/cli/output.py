"""Text and JSON rendering for ``devkit rules`` commands.

Text output is one ``[KIND: ...]`` sentinel line per fact, without colour:
``[VIOLATION: ...]`` per finding (``[RULE_COUNTS: ...]`` per rule with
``--summary-only``), then ``[SUMMARY: errors=N warnings=N infos=N fixed=N]``
and ``[OK: ...]`` when the run passes. Free text (messages, remediations,
descriptions) is written as a JSON string, so every fact stays on one line.
Warnings and notices are advisory blocks on stderr (``devkit.core.cli.echo_notices``).
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import click

from devkit.core.receipt import CONFIG_PATH
from devkit.rules.engine.config import RulesConfig
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

OK_TEXT = "no error-severity violation remains"
NOTHING_TO_CHECK = "no changed files in the snapshot; nothing to check"


def _quote(value: str) -> str:
    """``value`` as a one-line JSON string literal."""
    return json.dumps(value, ensure_ascii=False)


def _value(value: object) -> str:
    """A setting value as one-line JSON (``null`` for ``None``)."""
    return json.dumps(value, ensure_ascii=False)


def echo_ok(text: str = OK_TEXT) -> None:
    click.echo(f"[OK: {text}]")


def guide_display(rule: Rule | None, workspace_root: Path) -> str | None:
    return _display_path(guide_path(rule) if rule is not None else None, workspace_root)


def _display_path(path: Path | None, workspace_root: Path) -> str | None:
    """``path`` relative to the workspace when it lies inside it, else absolute."""
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
        click.echo(_transition_line(entry, remaining))


def _counts(violations: Sequence[Violation]) -> Counter[str]:
    """Unfixed findings per severity value, plus ``fixed``."""
    counts: Counter[str] = Counter()
    for v in violations:
        counts["fixed" if v.fixed else v.severity.value] += 1
    return counts


def _count_fields(counts: Counter[str]) -> str:
    """``errors=N warnings=N infos=N fixed=N``."""
    return " ".join([*(f"{s.value}s={counts[s.value]}" for s in Severity), f"fixed={counts['fixed']}"])


def _status(v: Violation) -> str:
    if v.fixed:
        return "fixed"
    return "fixable" if v.fixable else "open"


def _violation_line(v: Violation, guides: Mapping[str, Path], workspace_root: Path) -> str:
    line = (
        f"[VIOLATION: {v.rule_id} severity={v.severity.value} file={v.file} line={v.line} "
        f"status={_status(v)} message={_quote(v.message)}"
    )
    if v.remediation:
        line += f" remediation={_quote(v.remediation)}"
    guide = _display_path(guides.get(v.rule_id), workspace_root)
    if guide:
        line += f" guide={guide}"
    return line + "]"


def print_violations(
    violations: Sequence[Violation],
    errors: Sequence[object],
    guides: Mapping[str, Path],
    workspace_root: Path,
    *,
    summary_only: bool = False,
) -> None:
    """Findings (or per-rule counts) and one summary line; a run with problems and no findings prints nothing.

    ``guides`` maps rule IDs to guide documents (``ProjectRun.guides``).
    """
    if errors and not violations:
        return
    if summary_only:
        by_rule: dict[str, list[Violation]] = {}
        for v in violations:
            by_rule.setdefault(v.rule_id, []).append(v)
        for rule_id in sorted(by_rule):
            click.echo(f"[RULE_COUNTS: {rule_id} {_count_fields(_counts(by_rule[rule_id]))}]")
    else:
        for v in violations:
            click.echo(_violation_line(v, guides, workspace_root))
    click.echo(f"[SUMMARY: {_count_fields(_counts(violations))}]")


def print_phase_plan(entries: Sequence[PhaseEntry]) -> None:
    for e in entries:
        promote_to = e.promote_to.value if e.promote_to else "-"
        click.echo(
            f"[PHASE: {e.rule_id} default={e.default_phase.value} effective={e.effective_phase.value} "
            f"overridden={'yes' if e.overridden else 'no'} promote_to={promote_to}]"
        )


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
    """Sentinel lines describing the rule and its settings, then the guide document as written."""
    click.echo(
        f"[RULE: {rule.id} name={_quote(rule.name)} phase={entry['default_phase']} "
        f"effective_phase={entry['effective_phase']} severity={entry['default_severity']} "
        f"effective_severity={entry['effective_severity']} promote_to={entry['promote_to'] or '-'} "
        f"guide={entry['guide'] or '-'}]"
    )
    click.echo(f"[DESCRIPTION: {_quote(rule.description)}]")
    for item in entry.get("related", []):
        click.echo(f"[RELATED: {item['ref']} kind={item['kind'] or '-'} path={item['path'] or '-'}]")
    if resolver is None:
        click.echo("[SETTINGS: none]")
    else:
        for key, value in resolver.base.items():
            default = getattr(resolver.default, key)
            click.echo(f"[SETTING: {key}={_value(value)} default={_value(default)}]")
        for override in resolver.overrides:
            values = " ".join(f"{k}={_value(v)}" for k, v in override.values.items())
            click.echo(f"[SETTING_OVERRIDE: path={override.path} {values}]")
    guide = guide_path(rule)
    if guide is not None:
        click.echo()
        click.echo(guide.read_text("utf-8").rstrip())
