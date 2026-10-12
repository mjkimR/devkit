"""``envelope new`` and ``envelope check``."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from devkit.core.cli import FORMAT_OPTION, boundary, echo_json, exit_on_problems, is_json
from devkit.workflow.cli.app import UNIT, WORKSPACE, cli, workspace
from devkit.workflow.errors import EnvelopeFlagError
from devkit.workflow.render import quote
from devkit.workflow.unit.decisions import utc_timestamp
from devkit.workflow.unit.envelope import compose_envelope, load_envelopes, render_envelope, skeleton, write_envelope


@cli.group(name="envelope")
def envelope_group() -> None:
    """Envelope files under <unit>/envelopes/."""


def _read_findings_file(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        return Path(path).read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        raise EnvelopeFlagError(
            f"--findings-file: {exc}",
            target_files=[path],
            fix="Pass a readable YAML list of findings, or - for stdin",
        ) from exc


@envelope_group.command(name="new")
@WORKSPACE
@UNIT
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
@FORMAT_OPTION
@boundary
def envelope_new_cmd(
    workspace_root: str | None,
    unit: str,
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
    output_format: str,
) -> None:
    """Write the next <kind>-NN.yaml; existing files are never overwritten.

    With only --kind (and --stage) a needs_input skeleton is written for the
    author to fill in. Any other flag switches to authoring: the envelope is
    written complete, status defaults to completed, and reverify carries the
    findings of the round it closes with --from latest.
    """
    ws = workspace(workspace_root)
    unit_dir = ws.unit_path(unit)
    ws.locate_anchor(unit_dir)
    authoring = any((status is not None, summary is not None, assumptions, unverified, checks, base, head)) or any(
        (findings_file, source, resolve, waive)
    )
    created = utc_timestamp()
    if authoring:
        findings_yaml = _read_findings_file(findings_file) if findings_file is not None else None
        draft = compose_envelope(
            unit_dir=unit_dir,
            envelopes=load_envelopes(unit_dir),
            kind=kind,
            stage=stage,
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
        )
        body = render_envelope(draft, created)
        written_status, open_findings = draft.status, draft.open_findings()
    else:
        body = skeleton(kind, stage, created)
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
    """Report every envelope file of a unit and any contract violation (exit 1 when a file is malformed)."""
    ws = workspace(workspace_root)
    unit_dir = ws.unit_path(unit)
    ws.locate_anchor(unit_dir)
    envelopes = load_envelopes(unit_dir)
    loaded = envelopes.all()
    errors = sorted(envelopes.errors, key=lambda e: e.file)
    if is_json(output_format):
        echo_json({"envelopes": [e.to_dict() for e in loaded], "errors": [e.to_dict() for e in errors]})
    else:
        for e in loaded:
            click.echo(
                f"[ENVELOPE: {e.file} kind={e.kind} seq={e.seq:02d} status={e.status} open_findings={e.open_findings()}]"
            )
        for err in errors:
            click.echo(f"[ENVELOPE_ERROR: {err.file} {quote(err.message)}]")
        if not errors:
            click.echo(f"[OK: {len(loaded)} envelopes]")
    unit_rel = ws.rel(unit_dir)
    for err in errors:
        err.target_files = (f"{unit_rel}/{err.file}",)
    exit_on_problems(errors)
