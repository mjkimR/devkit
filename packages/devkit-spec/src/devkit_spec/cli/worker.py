"""Informational worker inspection CLI."""

from __future__ import annotations

from pathlib import Path

import click
from devkit.core.cli import FORMAT_OPTION, boundary, echo_json, echo_notices, is_json
from devkit.core.errors import ArgumentError

from devkit_spec.cli.output import sentinel
from devkit_spec.worker import inspect
from devkit_spec.worker.inspect import CheckNotRun


@click.group(name="worker")
def worker_group() -> None:
    """Inspect committed worker results without changing workflow decisions."""


@worker_group.command(name="inspect")
@click.option("--unit", default=None, help="Committed unit directory; otherwise derive from the activity branch")
@click.option("--base", default=None, help="Last accepted commit; otherwise derive from committed worker records")
@click.option("--head", default=None, help="Returned commit; otherwise the latest worker envelope's adding commit")
@click.option("--scope", multiple=True, help="Complete literal path scope (repeat); replaces derived scope")
@click.option(
    "--scope-file", type=click.Path(path_type=Path), default=None, help="UTF-8 complete scope, one prefix per line"
)
@click.option("--base-checkout", default=None, help="Base checkout to observe; otherwise the registered base")
@FORMAT_OPTION
@boundary
def inspect_cmd(
    unit: str | None,
    base: str | None,
    head: str | None,
    scope: tuple[str, ...],
    scope_file: Path | None,
    base_checkout: str | None,
    output_format: str,
) -> None:
    """Collect range, scope, cleanliness, envelope, rules and workflow evidence. Never writes or repairs."""
    if scope and scope_file is not None:
        raise ArgumentError("--scope and --scope-file are mutually exclusive", fix="Pass one complete scope input")
    entries = list(scope) if scope else None
    if scope_file is not None:
        try:
            entries = [line.strip() for line in scope_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (OSError, UnicodeError) as exc:
            raise ArgumentError(
                f"Cannot read scope file: {exc}", fix="Pass --scope-file with a readable UTF-8 file"
            ) from exc
    result = inspect(Path.cwd(), unit=unit, base=base, head=head, scope=entries, base_checkout=base_checkout)
    if is_json(output_format):
        echo_json(result)
    else:
        click.echo(sentinel("WORKER_INSPECTION", result["exit_code"], base=result["base"], head=result["head"]))
        for name, entry in result["inputs"].items():
            click.echo(sentinel("INPUT", name, **entry))
        for entry in result["scope"]:
            click.echo(sentinel("SCOPE", entry["path"], **{k: v for k, v in entry.items() if k != "path"}))
        for path in result["changed_paths"]:
            click.echo(sentinel("CHANGED", path, outside=path in result.get("outside_scope", [])))
        for name, check in result["checks"].items():
            click.echo(sentinel("CHECK", name, **check))
        if "base_checkout" in result:
            click.echo(sentinel("BASE_CHECKOUT", result["inputs"]["base_checkout"]["value"], **result["base_checkout"]))
    # Existing advisories retain their codes and deterministic actions in captured stderr.
    for check in result["checks"].values():
        if check.get("stderr"):
            click.echo(check["stderr"], err=True, nl=False)
    echo_notices(CheckNotRun(notice["message"]) for notice in result["notices"])
    raise click.exceptions.Exit(result["exit_code"])
