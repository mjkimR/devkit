"""``checks`` and ``validate``."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from devkit.core.cli import FORMAT_OPTION, boundary, echo_json, echo_notices, highest_exit_code, is_json
from devkit.core.errors import ArgumentError
from devkit.workflow.cli.app import WORKSPACE, cli, workspace
from devkit.workflow.definition.checks import Registry
from devkit.workflow.definition.definition import schema_hash
from devkit.workflow.render import quote


@cli.command(name="checks")
@WORKSPACE
@FORMAT_OPTION
@boundary
def checks_cmd(workspace_root: str | None, output_format: str) -> None:
    """List registered check names, classes and parameters."""
    ws = workspace(workspace_root)
    entries = Registry.build(ws.config.anchor, (), ws.plugins()).entries()
    if is_json(output_format):
        echo_json({"checks": [c.to_dict() for c in entries]})
        return
    for c in entries:
        params = f"({' '.join(c.params)})" if c.params else ""
        alias = f" alias={c.alias}" if c.alias else ""
        click.echo(f"[CHECK: {c.name}{params} class={c.class_.value}{alias} description={quote(c.description)}]")


@cli.command(name="validate")
@WORKSPACE
@click.argument("paths", nargs=-1, type=str)
@FORMAT_OPTION
@boundary
def validate_cmd(workspace_root: str | None, paths: tuple[str, ...], output_format: str) -> None:
    """Validate workflow definitions (default: definitions_dir plus synchronized workflow assets).

    Exits with the highest exit code among the problems: 1 when a definition
    is invalid or definitions disagree on a shared stage, 2 when a definition
    or plugin check file cannot be loaded.
    """
    ws = workspace(workspace_root)
    missing = [p for p in paths if not Path(p).exists()]
    if missing:
        raise ArgumentError(
            f"PATHS: no such file or directory: {', '.join(missing)}",
            target_files=missing,
            fix="Pass existing definition files or directories",
        )
    report = ws.validate_definitions([Path(p).resolve() for p in paths])
    if is_json(output_format):
        echo_json(report.to_dict(ws.root))
    else:
        for err in report.load_errors:
            click.echo(f"[INVALID: {err}]")
        for r in report.definitions:
            where = ws.rel(r.doc.path) if r.doc.path else r.doc.id
            if r.ok:
                click.echo(f"[VALID: {where} id={r.doc.id} hash={schema_hash(r.doc)}]")
                continue
            click.echo(f"[INVALID: {where} id={r.doc.id} problems={len(r.problems)}]")
            for problem in r.problems:
                click.echo(f"[PROBLEM: {problem}]")
        for problem in report.shared:
            click.echo(f"[INVALID: {problem}]")
        if not report.definitions and report.ok:
            click.echo(f"[VALID: no definitions under {ws.config.definitions_dir}]")
    echo_notices(report.notices)
    if not report.ok:
        sys.exit(highest_exit_code(report.errors))
