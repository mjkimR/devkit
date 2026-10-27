"""MCP command result presentation."""

from __future__ import annotations

import sys
from collections.abc import Iterator, Sequence

import click
from devkit.advisory import AdvisoryError
from devkit_dist.adapters.cli import echo_json, echo_notices, exit_on_warnings, is_json, report_exit_code


def report(
    data: dict,
    output_format: str,
    notices: Sequence[AdvisoryError] = (),
    errors: Sequence[AdvisoryError] | None = None,
) -> None:
    """Print one result, then its notices; exit ``1`` when ``errors`` lists a problem or a warning fails ``--strict``.

    Only a status report passes ``errors``: its problems are listed under ``errors`` and set the exit code.
    """
    if is_json(output_format):
        document = {**data, "notices": [item.to_dict() for item in notices]}
        if errors is not None:
            document["errors"] = [item.to_dict() for item in errors]
        echo_json(document)
    else:
        for line in _lines(data):
            click.echo(line)
        echo_notices([*(errors or ()), *notices])
    if errors:
        sys.exit(report_exit_code(errors))
    exit_on_warnings(notices)


def _lines(data: dict) -> Iterator[str]:
    """One ``[MCP: ...]`` line, then one ``[MCP_HOST: ...]`` line per host the result names; ``--descriptor`` prints
    one ``[MCP_DESCRIPTOR: ...]`` line. Facts that are always ``unknown`` (connection, effective enablement, form,
    trust, permissions) appear only in JSON."""
    if "descriptor" in data:
        launch = data["descriptor"]
        if launch is None:
            yield "[OK: no launch descriptor: the read-only profile exposes no tools]"
        else:
            yield (
                f"[MCP_DESCRIPTOR: command={launch['command']} profile={launch['profile']}"
                f" executor={launch['executor']} workspace={launch['workspace']}]"
            )
        return
    project = data.get("project")
    if project is None:
        yield f"[MCP: action={data['action']}]"
        for host, state in sorted(data.get("registrations", {}).items()):
            yield f"[MCP_HOST: {host} state={state}]"
        return
    yield f"[MCP: action={data['action']} package={data['package']} runtime={data['runtime']}]"
    for host, state in sorted(project.items()):
        line = f"{host} state={state['state']}"
        line += f" desired={'yes' if data['desired'].get(host) else 'no'}"
        line += f" recorded={'yes' if host in data['recorded'] else 'no'}"
        if "collisions" in state:
            line += f" collisions={','.join(state['collisions']) or 'none'}"
        yield f"[MCP_HOST: {line}]"
