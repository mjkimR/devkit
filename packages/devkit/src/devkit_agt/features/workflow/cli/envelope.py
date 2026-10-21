"""``envelope new``, its kind commands (``worker``, ``answer``, ``resolution``, ``review``, ``reverify``) and
``envelope check``."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import click
from devkit_dist.adapters.cli import FORMAT_OPTION, boundary, echo_json, exit_on_problems, is_json

from devkit_agt.features.workflow.cli.app import ANCHOR, UNIT, WORKSPACE, cli, workspace
from devkit_agt.features.workflow.cli.render import quote, render_hold
from devkit_agt.features.workflow.models.errors import EnvelopeFlagError
from devkit_agt.features.workflow.usecases.envelopes import CheckEnvelopesUseCase, WriteEnvelopeUseCase

# Kinds whose fields need options of their own; ``envelope new`` refuses them.
KIND_COMMANDS = ("worker", "answer", "resolution", "review", "reverify")


@cli.group(name="envelope")
def envelope_group() -> None:
    """Envelope files under <unit>/envelopes/."""


def _common(stage_required: bool = False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """The options every authoring command takes; ``--stage`` is required where the contract needs it."""
    options = (
        WORKSPACE,
        UNIT,
        ANCHOR,
        # click counts any default, None included, as a value and then never asks for a required option.
        click.option("--stage", required=True, help="Stage the envelope belongs to")
        if stage_required
        else click.option("--stage", default="", help="Stage the envelope belongs to"),
        click.option("--status", default=None, help="completed (default when authoring) | needs_input | failed"),
        click.option("--summary", default=None, help="1-3 line judgment"),
        click.option("--assume", "assumptions", multiple=True, help="An assumption the judgment rests on (repeatable)"),
        click.option("--unverified", "unverified", multiple=True, help="An area that was not verified (repeatable)"),
        click.option("--check", "checks", multiple=True, help="Check result name=PASS|FAIL|SKIP[ detail] (repeatable)"),
        click.option(
            "--base", default="", help="diff_scope base revision (resolved to a full commit id in Git workspaces)"
        ),
        click.option(
            "--head",
            default="",
            help="diff_scope head commit id (hexadecimal; resolved and verified in Git workspaces)",
        ),
        click.option("--effort", default="", help="activity_effort the run applied: low | medium | high"),
    )

    def apply(fn: Callable[..., Any]) -> Callable[..., Any]:
        for option in reversed(options):
            fn = option(fn)
        return fn

    return apply


FINDINGS_FILE = click.option(
    "--findings-file", default=None, help="YAML list of findings to record (path, or - for stdin)"
)


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


def _write(
    kind: str,
    *,
    workspace_root: str | None,
    unit: str,
    anchor: str | None,
    stage: str,
    status: str | None,
    summary: str | None,
    assumptions: tuple[str, ...],
    unverified: tuple[str, ...],
    checks: tuple[str, ...],
    base: str,
    head: str,
    effort: str,
    output_format: str,
    findings_file: str | None = None,
    source: str | None = None,
    resolve: tuple[str, ...] = (),
    waive: tuple[str, ...] = (),
    questions_file: str | None = None,
    answers_to: str = "",
    answers_file: str | None = None,
    settle: tuple[str, ...] = (),
    problem: str = "",
    attempts: tuple[str, ...] = (),
    recovery: str = "",
    resolves: str = "",
) -> None:
    """Translate CLI file/stdin options and render the envelope operation result."""
    content = (
        findings_file,
        source,
        resolve,
        waive,
        questions_file,
        answers_to,
        answers_file,
        settle,
        problem,
        attempts,
    )
    authoring = any((status is not None, summary is not None, assumptions, unverified, checks, base, head)) or any(
        (*content, recovery, resolves, effort)
    )
    if [findings_file, questions_file, answers_file].count("-") > 1:
        raise EnvelopeFlagError(
            "only one of --findings-file, --questions-file and --answers-file can read stdin",
            fix="Pass the others as files",
        )
    result = WriteEnvelopeUseCase().execute(
        kind,
        workspace=workspace(workspace_root),
        authoring=authoring,
        unit=unit,
        anchor=anchor,
        stage=stage,
        status=status,
        summary=summary,
        assumptions=assumptions,
        unverified=unverified,
        checks=checks,
        base=base,
        head=head,
        effort=effort,
        findings_yaml=_read_items_file("--findings-file", findings_file, "findings"),
        source=source,
        resolve=resolve,
        waive=waive,
        questions_yaml=_read_items_file("--questions-file", questions_file, "questions"),
        answers_to=answers_to,
        answers_yaml=_read_items_file("--answers-file", answers_file, "answers"),
        settle=settle,
        problem=problem,
        attempts=attempts,
        recovery=recovery,
        resolves=resolves,
    )
    if is_json(output_format):
        echo_json(result)
        return
    click.echo(
        f"[ENVELOPE: {result['file']} kind={kind} seq={result['seq']:02d} status={result['status']} open_findings={result['open_findings']}]"
    )


@envelope_group.command(name="new", hidden=True)
@click.option("--kind", required=True, help="Envelope kind, e.g. scout, red, final-report")
@_common()
@FINDINGS_FILE
@FORMAT_OPTION
@boundary
def envelope_new_cmd(kind: str, **options: Any) -> None:
    """Write the next <kind>-NN.yaml of a kind without fields of its own; existing files are never overwritten.

    worker, answer, resolution, review and reverify envelopes are written by
    their own commands (`envelope <kind>`), which take the options of their
    fields; this command refuses them.

    With only --kind (and --stage) a needs_input skeleton is written for the
    author to fill in. Any other flag switches to authoring: the envelope is
    written complete and status defaults to completed. The same holds for
    every kind command.

    The envelope records the workflow the unit is bound to and the segment
    (finished handoffs) it is in; checks count it only in that segment. The
    definition itself is not loaded (only read for its id when the default is
    a .md path), so a review can be recorded while it is invalid, or missing
    when it is named by id.
    created_at is stamped after the segment's latest return, so a return never
    voids an envelope written after it.
    """
    if kind in KIND_COMMANDS:
        raise EnvelopeFlagError(
            f"kind {kind} has its own command",
            fix=f"Use `devkit workflow envelope {kind}` with the same options",
        )
    _write(kind, **options)


@envelope_group.command(name="worker")
@_common(stage_required=True)
@click.option(
    "--questions-file",
    default=None,
    help=(
        "YAML list of questions for a person, each {id, title, prompt, context?, options?: [{id, description,"
        " recommended?}], allow_note?} (path, or - for stdin)"
    ),
)
@click.option("--problem", default="", help="An execution problem: its cause (with --recovery; needs_input or failed)")
@click.option("--tried", "attempts", multiple=True, help="What was tried against the problem (repeatable)")
@click.option("--recovery", default="", help="The recommended recovery for the problem")
@FINDINGS_FILE
@FORMAT_OPTION
@boundary
def envelope_worker_cmd(**options: Any) -> None:
    """Write the next worker-NN.yaml, the record of one run (one per run).

    --questions-file holds what it asks a person (status needs_input);
    --problem/--tried/--recovery an execution problem (status failed, or
    needs_input when only a person can decide); --findings-file what the
    problem consists of, one finding each.
    """
    _write("worker", **options)


@envelope_group.command(name="answer")
@_common()
@click.option("--answers-to", default="", help="The worker-NN.yaml whose questions it answers")
@click.option(
    "--answers-file",
    default=None,
    help="YAML list of rewritten answers, each {question, choice, decision, constraints?} (path, or - for stdin)",
)
@click.option(
    "--settle",
    "settle",
    multiple=True,
    help="A worker assumption the user settled: <assumption-number>=<decision> (1-based; repeatable)",
)
@FORMAT_OPTION
@boundary
def envelope_answer_cmd(**options: Any) -> None:
    """Write the next answer-NN.yaml: the decisions on a worker envelope's questions and assumptions.

    --answers-to must name one of the unit's worker envelopes with those
    questions and options; --settle positions must be among its assumptions.
    With --settle the answers file may be omitted.
    """
    _write("answer", **options)


@envelope_group.command(name="resolution")
@_common()
@click.option("--resolves", default="", help="The worker-NN.yaml whose problem it resolves")
@FORMAT_OPTION
@boundary
def envelope_resolution_cmd(**options: Any) -> None:
    """Write the next resolution-NN.yaml: the fix of a worker envelope's problem.

    --resolves must name one of the unit's worker envelopes with a problem.
    """
    _write("resolution", **options)


@envelope_group.command(name="review")
@_common()
@FINDINGS_FILE
@FORMAT_OPTION
@boundary
def envelope_review_cmd(**options: Any) -> None:
    """Write the next review-NN.yaml: findings as found (all open); envelope reverify closes the round."""
    _write("review", **options)


@envelope_group.command(name="reverify")
@_common()
@click.option(
    "--from",
    "source",
    default=None,
    help="The round it closes: latest (the review round), or a review, challenger or reverify file",
)
@click.option(
    "--resolve", "resolve", multiple=True, help="Mark a carried finding resolved: its number, or all (repeatable)"
)
@click.option("--waive", "waive", multiple=True, help="Mark a carried finding waived: <number>=<reason> (repeatable)")
@FINDINGS_FILE
@FORMAT_OPTION
@boundary
def envelope_reverify_cmd(**options: Any) -> None:
    """Write the next reverify-NN.yaml: carry the findings of the round it closes (--from latest, or a
    challenger-NN.yaml of Planning) and close them.

    --findings-file adds findings found while reverifying.
    """
    _write("reverify", **options)


@envelope_group.command(name="check")
@WORKSPACE
@UNIT
@click.option("--details", is_flag=True, help="Include complete envelope bodies in JSON output")
@FORMAT_OPTION
@boundary
def envelope_check_cmd(workspace_root: str | None, unit: str, details: bool, output_format: str) -> None:
    """Report every envelope file of a unit and any contract violation (exit 1 when a file is malformed).

    Also reports what holds the unit's gates: unresolved problems ([BLOCKED]) and
    unanswered questions ([PENDING_QUESTION]); neither changes the exit code.
    """
    ws = workspace(workspace_root)
    envelopes = CheckEnvelopesUseCase().execute(ws, unit)
    loaded = envelopes.all()
    hold = envelopes.hold()
    errors = sorted(envelopes.errors, key=lambda e: e.file)
    if is_json(output_format):
        echo_json(envelopes.inspection_dict(details=details))
    else:
        for e in loaded:
            click.echo(
                f"[ENVELOPE: {e.file} kind={e.kind} seq={e.seq:02d} status={e.status} open_findings={e.open_findings()}"
                f"{' problem=yes' if e.problem else ''}{f' review={e.review}' if e.review else ''}]"
            )
        click.echo(render_hold(hold), nl=False)
        for err in errors:
            click.echo(f"[ENVELOPE_ERROR: {err.file} {quote(err.message)}]")
        if not errors:
            click.echo(f"[OK: {len(loaded)} envelopes]")
    exit_on_problems(errors)
