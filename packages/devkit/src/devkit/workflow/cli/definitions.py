"""``checks`` and ``validate``."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from devkit.advisory import ExitCode
from devkit.workflow.checks import Registry
from devkit.workflow.cli.app import FORMAT, WORKSPACE, boundary, cli, echo_json, is_json, workspace
from devkit.workflow.definition import schema_hash
from devkit.workflow.render import quote


@cli.command(name="checks")
@WORKSPACE
@FORMAT
@boundary
def checks_cmd(workspace_root: str | None, output_format: str) -> None:
    """List registered check names, classes and parameters."""
    ws = workspace(workspace_root)
    entries = Registry.build(ws.config.anchor, (), ws.plugins()).entries()
    if is_json(output_format):
        echo_json([c.to_dict() for c in entries])
        return
    for c in entries:
        params = f"({' '.join(c.params)})" if c.params else ""
        alias = f" alias={c.alias}" if c.alias else ""
        click.echo(f"[CHECK: {c.name}{params} class={c.class_.value}{alias} description={quote(c.description)}]")


@cli.command(name="validate")
@WORKSPACE
@click.argument("paths", nargs=-1, type=click.Path(exists=True, dir_okay=True, file_okay=True))
@FORMAT
@boundary
def validate_cmd(workspace_root: str | None, paths: tuple[str, ...], output_format: str) -> None:
    """Validate workflow definitions (default: definitions_dir plus synchronized workflow assets)."""
    ws = workspace(workspace_root)
    report = ws.validate_definitions([Path(p).resolve() for p in paths])
    if is_json(output_format):
        echo_json(
            {
                "valid": report.ok,
                "roles_checked": report.roles_checked,
                "definitions": [r.to_dict(ws.root) for r in report.definitions],
                "errors": [e.to_dict() for e in report.load_errors],
                "shared": [p.to_dict() for p in report.shared],
            }
        )
    else:
        if not report.roles_checked:
            click.echo(f"[NOTE: role check skipped: no installation receipt and no {ws.config.roles_dir}]")
        for err in report.load_errors:
            click.secho(f"[INVALID: {err}]", fg="red")
        for r in report.definitions:
            where = ws.rel(r.doc.path) if r.doc.path else r.doc.id
            if r.ok:
                click.secho(f"[VALID: {where} id={r.doc.id} hash={schema_hash(r.doc)}]", fg="green")
                continue
            click.secho(f"[INVALID: {where} id={r.doc.id} problems={len(r.problems)}]", fg="red")
            for p in r.problems:
                click.echo(f"  - {p}")
        for problem in report.shared:
            click.secho(f"[INVALID: {problem}]", fg="red")
        if not report.definitions and report.ok:
            click.echo(f"[VALID: no definitions under {ws.config.definitions_dir}]")
    if not report.ok:
        sys.exit(int(ExitCode.FINDINGS))
