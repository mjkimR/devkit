"""Text and JSON rendering for ``devkit rules`` commands.

Text output is one ``[KIND: ...]`` sentinel line per fact, without colour:
``[VIOLATION: ...]`` per finding (``[RULE_COUNTS: ...]`` per rule with
``--summary-only``), then ``[SUMMARY: errors=N warnings=N infos=N fixed=N rules=N]``
and ``[OK: ...]`` when the run passes; ``test`` prints ``[RULE_TEST: ...]`` per
rule (with the failure view of a failed run) and ``[SUMMARY: rules=N ...]``. Free text (messages, remediations,
descriptions) is written as a JSON string, so every fact stays on one line.
Warnings and notices are advisory blocks on stderr (``devkit_dist.adapters.cli.echo_notices``).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import click
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH

from devkit_agt.features.rules.models.contracts import Phase, Rule, Severity, Violation
from devkit_agt.features.rules.models.phases import (
    PhaseEntry,
    remaining_by_rule,
    transition_entries,
)
from devkit_agt.features.rules.models.settings import SettingsResolver
from devkit_agt.features.rules.usecases.explain import ReadRuleGuideUseCase
from devkit_agt.features.rules.usecases.rule_tests import RuleTestRun

OK_TEXT = "no error-severity violation remains"
NOTHING_TO_CHECK = "no changed files in the snapshot; nothing to check"


def _quote(value: str) -> str:
    """``value`` as a one-line JSON string literal."""
    return json.dumps(value, ensure_ascii=False)


def _value(value: object) -> str:
    """A setting value as one-line JSON (``null`` for ``None``)."""
    return json.dumps(value, ensure_ascii=False)


_BARE = re.compile(r'[^\s"\]]+')


def _bare(value: str | None) -> str:
    """``-`` for none, bare without spaces, quotes or brackets, else a JSON string."""
    if not value:
        return "-"
    return value if _BARE.fullmatch(value) else _quote(value)


def echo_ok(text: str = OK_TEXT) -> None:
    click.echo(f"[OK: {text}]")


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
        f"[VIOLATION: {v.rule_id} severity={v.severity.value} file={_bare(v.file)} line={v.line} "
        f"status={_status(v)} message={_quote(v.message)}"
    )
    if v.remediation:
        line += f" remediation={_quote(v.remediation)}"
    guide = _display_path(guides.get(v.rule_id), workspace_root)
    if guide:
        line += f" guide={_bare(guide)}"
    return line + "]"


def violation_json(v: Violation, guides: Mapping[str, Path], workspace_root: Path) -> dict[str, Any]:
    """A finding under ``--format json``: ``Violation.to_dict()`` plus ``guide`` when the rule has one, as the
    ``[VIOLATION: ...]`` line carries it."""
    data = v.to_dict()
    guide = _display_path(guides.get(v.rule_id), workspace_root)
    if guide:
        data["guide"] = guide
    return data


def print_violations(
    violations: Sequence[Violation],
    errors: Sequence[object],
    guides: Mapping[str, Path],
    workspace_root: Path,
    *,
    rules: int,
    summary_only: bool = False,
) -> None:
    """Findings (or per-rule counts) and one summary line; a run with problems and no findings prints nothing.

    ``guides`` maps rule IDs to guide documents (``ProjectRun.guides``); ``rules`` is the number of rules active in
    the run's phase (``ProjectRun.active_rules``), so a pass that checked nothing reads ``rules=0``.
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
    click.echo(f"[SUMMARY: {_count_fields(_counts(violations))} rules={rules}]")


def print_phase_plan(entries: Sequence[PhaseEntry]) -> None:
    for e in entries:
        promote_to = e.promote_to.value if e.promote_to else "-"
        click.echo(
            f"[PHASE: {e.rule_id} default={e.default_phase.value} effective={e.effective_phase.value} "
            f"overridden={'yes' if e.overridden else 'no'} promote_to={promote_to}]"
        )


def print_explain(rule: Rule, entry: dict[str, Any], resolver: SettingsResolver | None) -> None:
    """Sentinel lines describing the rule and its settings, then the guide document as written."""
    click.echo(
        f"[RULE: {rule.id} name={_quote(rule.name)} phase={entry['default_phase']} "
        f"effective_phase={entry['effective_phase']} severity={entry['default_severity']} "
        f"effective_severity={entry['effective_severity']} promote_to={entry['promote_to'] or '-'} "
        f"guide={_bare(entry['guide'])} inputs={_bare(','.join(entry['inputs'] or []))}]"
    )
    click.echo(f"[DESCRIPTION: {_quote(rule.description)}]")
    for item in entry.get("related", []):
        click.echo(f"[RELATED: {item['ref']} kind={item['kind'] or '-'} path={_bare(item['path'])}]")
    if resolver is None:
        click.echo("[SETTINGS: none]")
    else:
        for key, value in resolver.base.items():
            default = getattr(resolver.default, key)
            click.echo(f"[SETTING: {key}={_value(value)} default={_value(default)}]")
        for override in resolver.overrides:
            values = " ".join(f"{k}={_value(v)}" for k, v in override.values.items())
            click.echo(f"[SETTING_OVERRIDE: path={_bare(override.path)} {values}]")
    guide = ReadRuleGuideUseCase().execute(rule)
    if guide is not None:
        click.echo()
        click.echo(guide.rstrip())


def _shows_failure(item: RuleTestRun) -> bool:
    """Whether a run's failure view belongs to this result: a failed run that ran to the end."""
    return item.failed and item.run is not None and not item.run.interrupted


def rule_test_entry(item: RuleTestRun, workspace_root: Path, *, details: bool = True) -> dict[str, Any]:
    """One rule's result as JSON; ``details`` adds the failure view (summaries, failed tests, excerpt)."""
    run = item.run
    entry: dict[str, Any] = {
        "rule_id": item.rule_id,
        "tests": _display_path(item.tests, workspace_root),
        "result": item.result.value,
        "exit_code": item.exit_code,
        "log": str(run.log) if run is not None else None,
        "summaries": [],
        "failures": [],
        "output": None,
        "omitted": None,
    }
    if details and run is not None and _shows_failure(item):
        found = run.scan
        entry["summaries"] = list(found.summaries)
        entry["failures"] = [{"test": f.test, "kind": f.kind, "message": f.message} for f in found.failures]
        entry["output"] = found.output
        entry["omitted"] = {"failures": found.omitted.failures, "output": found.omitted.output}
    return entry


def print_rule_tests(results: Sequence[RuleTestRun], workspace_root: Path, summary: Mapping[str, int]) -> None:
    """One ``[RULE_TEST: ...]`` line per rule, the failure view after a failed run, then ``[SUMMARY: ...]``.

    The failure view is compact's (``devkit run``): the run's summary lines, the
    failed tests the excerpt cuts out, then the excerpt. Rules sharing a run
    show it once.
    """
    shown: set[Path] = set()
    for item in results:
        run = item.run
        exit_code = "-" if item.exit_code is None else str(item.exit_code)
        tests = _display_path(item.tests, workspace_root)
        click.echo(
            f"[RULE_TEST: {item.rule_id} tests={_bare(tests)} result={item.result.value} exit={exit_code} "
            f"log={_bare(str(run.log) if run is not None else None)}]"
        )
        if run is None or not _shows_failure(item) or run.log in shown:
            continue
        shown.add(run.log)
        found = run.scan
        for line in found.summaries:
            click.echo(f"[RULE_TEST_SUMMARY: {item.rule_id} {_quote(line)}]")
        for failure in found.failures:
            click.echo(
                f"[RULE_TEST_FAILURE: {item.rule_id} {_quote(failure.test)} kind={failure.kind} "
                f"message={_bare(failure.message)}]"
            )
        omitted = found.omitted
        click.echo(
            f"[RULE_TEST_OUTPUT: {item.rule_id} shown={len(found.output)} omitted={omitted.output} "
            f"filtered={found.filtered}]"
        )
        if found.output:
            click.echo(found.output, nl=not found.output.endswith("\n"))
    click.echo(
        f"[SUMMARY: rules={summary['rules']} passed={summary['passed']} failed={summary['failed']} "
        f"no_tests={summary['no_tests']} interrupted={summary['interrupted']}]"
    )
