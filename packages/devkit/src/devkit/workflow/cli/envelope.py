"""``envelope new`` and ``envelope check``."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from devkit.core.cli import FORMAT_OPTION, boundary, echo_json, exit_on_problems, is_json
from devkit.workflow.cli.app import ANCHOR, UNIT, WORKSPACE, cli, workspace
from devkit.workflow.errors import EnvelopeFlagError
from devkit.workflow.render import quote, render_hold
from devkit.workflow.unit.envelope import (
    compose_envelope,
    envelope_timestamp,
    load_envelopes,
    render_envelope,
    skeleton,
    write_envelope,
)


@cli.group(name="envelope")
def envelope_group() -> None:
    """Envelope files under <unit>/envelopes/."""


def _read_items_file(flag: str, path: str | None, what: str) -> str | None:
    if path is None:
        return None
    if path == "-":
        return sys.stdin.read()
    try:
        return Path(path).read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        raise EnvelopeFlagError(
            f"{flag}: {exc}",
            target_files=[path],
            fix=f"Pass a readable YAML list of {what}, or - for stdin",
        ) from exc


@envelope_group.command(name="new")
@WORKSPACE
@UNIT
@ANCHOR
@click.option("--kind", required=True, help="Envelope kind, e.g. review, reverify, final-report")
@click.option("--stage", default="", help="Stage the envelope belongs to")
@click.option("--status", default=None, help="completed (default when authoring) | needs_input | failed")
@click.option("--summary", default=None, help="1-3 line judgment")
@click.option("--assume", "assumptions", multiple=True, help="An assumption the judgment rests on (repeatable)")
@click.option("--unverified", "unverified", multiple=True, help="An area that was not verified (repeatable)")
@click.option("--check", "checks", multiple=True, help="Check result name=PASS|FAIL|SKIP[ detail] (repeatable)")
@click.option("--base", default="", help="diff_scope base revision")
@click.option("--head", default="", help="diff_scope head commit id (hexadecimal; required for revision-ancestor)")
@click.option("--findings-file", default=None, help="YAML list of findings to record (path, or - for stdin)")
@click.option("--from", "source", default=None, help="Carry findings forward: latest, or a review/reverify file")
@click.option(
    "--resolve", "resolve", multiple=True, help="Mark a carried finding resolved: its number, or all (repeatable)"
)
@click.option("--waive", "waive", multiple=True, help="Mark a carried finding waived: <number>=<reason> (repeatable)")
@click.option("--questions-file", default=None, help="worker: YAML list of questions (path, or - for stdin)")
@click.option("--answers-to", default="", help="answer: the worker-NN.yaml whose questions it answers")
@click.option("--answers-file", default=None, help="answer: YAML list of rewritten answers (path, or - for stdin)")
@click.option("--problem", default="", help="An execution problem: its cause (with --recovery; needs_input or failed)")
@click.option("--tried", "attempts", multiple=True, help="What was tried against the problem (repeatable)")
@click.option("--recovery", default="", help="The recommended recovery for the problem")
@click.option("--resolves", default="", help="resolution: the worker-NN.yaml whose problem it resolves")
@click.option("--effort", default="", help="activity_effort the run applied: low | medium | high")
@FORMAT_OPTION
@boundary
def envelope_new_cmd(
    workspace_root: str | None,
    unit: str,
    anchor: str | None,
    kind: str,
    stage: str,
    status: str | None,
    summary: str | None,
    assumptions: tuple[str, ...],
    unverified: tuple[str, ...],
    checks: tuple[str, ...],
    base: str,
    head: str,
    findings_file: str | None,
    source: str | None,
    resolve: tuple[str, ...],
    waive: tuple[str, ...],
    questions_file: str | None,
    answers_to: str,
    answers_file: str | None,
    problem: str,
    attempts: tuple[str, ...],
    recovery: str,
    resolves: str,
    effort: str,
    output_format: str,
) -> None:
    """Write the next <kind>-NN.yaml; existing files are never overwritten.

    With only --kind (and --stage) a needs_input skeleton is written for the
    author to fill in. Any other flag switches to authoring: the envelope is
    written complete, status defaults to completed, and reverify carries the
    findings of the round it closes with --from latest.

    The envelope records the workflow the unit is bound to and the segment
    (finished handoffs) it is in; checks count it only in that segment. The
    definition itself is not loaded (only read for its id when the default is
    a .md path), so a review can be recorded while it is invalid, or missing
    when it is named by id.
    created_at is stamped after the segment's latest return, so a return never
    voids an envelope written after it.

    worker, answer and resolution envelopes carry their own fields: a worker
    envelope (one per run) --questions-file for what it asks a person and
    --problem/--tried/--recovery for an execution problem; an answer
    --answers-to and --answers-file; a resolution --resolves. --effort goes
    on any kind. The written envelope satisfies the contract of its kind,
    and answers_to/resolves must name one of the unit's worker envelopes.
    """
    ws = workspace(workspace_root)
    scope = ws.unit_scope(unit, anchor=anchor)
    unit_dir, workflow, segment = scope.dir, scope.workflow, scope.binding.segment
    content = (findings_file, source, resolve, waive, questions_file, answers_to, answers_file, problem, attempts)
    authoring = any((status is not None, summary is not None, assumptions, unverified, checks, base, head)) or any(
        (*content, recovery, resolves, effort)
    )
    created = envelope_timestamp(unit_dir, workflow, scope.binding.segment_start)
    if authoring:
        if [findings_file, questions_file, answers_file].count("-") > 1:
            raise EnvelopeFlagError(
                "only one of --findings-file, --questions-file and --answers-file can read stdin",
                fix="Pass the others as files",
            )
        findings_yaml = _read_items_file("--findings-file", findings_file, "findings")
        questions_yaml = _read_items_file("--questions-file", questions_file, "questions")
        answers_yaml = _read_items_file("--answers-file", answers_file, "answers")
        loaded = load_envelopes(unit_dir)
        draft = compose_envelope(
            unit_dir=unit_dir,
            envelopes=loaded.scoped(workflow, segment),
            loaded=loaded,
            kind=kind,
            stage=stage,
            workflow=workflow,
            segment=segment,
            status=status,
            summary=summary or "",
            assumptions=assumptions,
            unverified=unverified,
            checks=checks,
            base=base,
            head=head,
            findings_yaml=findings_yaml,
            source=source,
            resolve=resolve,
            waive=waive,
            questions_yaml=questions_yaml,
            answers_to=answers_to,
            answers_yaml=answers_yaml,
            problem=problem,
            attempts=attempts,
            recovery=recovery,
            resolves=resolves,
            effort=effort,
        )
        body = render_envelope(draft, created)
        written_status, open_findings = draft.status, draft.open_findings()
    else:
        body = skeleton(kind, stage, created, workflow, segment)
        written_status, open_findings = "needs_input", 0
    path, seq = write_envelope(unit_dir, kind, body)
    rel = ws.rel(path)
    if is_json(output_format):
        echo_json({"file": rel, "kind": kind, "seq": seq, "status": written_status, "open_findings": open_findings})
        return
    click.echo(f"[ENVELOPE: {rel} kind={kind} seq={seq:02d} status={written_status} open_findings={open_findings}]")


@envelope_group.command(name="check")
@WORKSPACE
@UNIT
@FORMAT_OPTION
@boundary
def envelope_check_cmd(workspace_root: str | None, unit: str, output_format: str) -> None:
    """Report every envelope file of a unit and any contract violation (exit 1 when a file is malformed).

    Also reports what holds the unit's gates: unresolved problems ([BLOCKED]) and
    unanswered questions ([PENDING_QUESTION]); neither changes the exit code.
    """
    ws = workspace(workspace_root)
    unit_dir = ws.unit_path(unit)
    ws.present_anchors(unit_dir)
    envelopes = load_envelopes(unit_dir)
    loaded = envelopes.all()
    hold = envelopes.hold()
    errors = sorted(envelopes.errors, key=lambda e: e.file)
    unit_rel = ws.rel(unit_dir)
    for err in errors:
        err.target_files = (f"{unit_rel}/{err.file}",)
    if is_json(output_format):
        echo_json(
            {"envelopes": [e.to_dict() for e in loaded], **hold.to_dict(), "errors": [e.to_dict() for e in errors]}
        )
    else:
        for e in loaded:
            click.echo(
                f"[ENVELOPE: {e.file} kind={e.kind} seq={e.seq:02d} status={e.status} open_findings={e.open_findings()}"
                f"{' problem=yes' if e.problem else ''}]"
            )
        click.echo(render_hold(hold), nl=False)
        for err in errors:
            click.echo(f"[ENVELOPE_ERROR: {err.file} {quote(err.message)}]")
        if not errors:
            click.echo(f"[OK: {len(loaded)} envelopes]")
    exit_on_problems(errors)
