"""MCP command result presentation."""

from __future__ import annotations

import click
from devkit_dist.adapters.cli import echo_json, echo_notices, is_json


def report(data: dict, output_format: str, notices=()) -> None:
    if is_json(output_format):
        echo_json({**data, "notices": [item.to_dict() for item in notices]})
    else:
        click.echo(f"[MCP: action={data['action']} connection=unknown form=unknown trust=unknown permissions=unknown]")
        echo_notices(notices)
