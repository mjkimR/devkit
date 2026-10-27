"""Distribution configuration CLI adapters."""

from __future__ import annotations

import click

from devkit_dist.adapters.cli import echo_json, echo_notices, exit_on_warnings, resolve_root
from devkit_dist.features.distribution.usecases.commands import (
    PreviewConfigTemplate,
    RefreshConfigTemplate,
    ShowConfiguration,
)

from .output import WORKSPACE, _json_command


@click.group()
def config() -> None:
    """Maintain the project configuration, .devkit/config.toml."""


@config.command(name="show")
@WORKSPACE
@click.option("--effective", is_flag=True, required=True, help="Show effective configuration and source paths.")
@_json_command
def config_show(workspace_root: str | None, effective: bool) -> None:
    """Inspect effective checkout preferences without changing configuration.

    An unsupported [presentation] language resolves to en and is a warning under notices.
    """
    report = ShowConfiguration().execute(resolve_root(workspace_root))
    echo_json(report.to_dict())
    echo_notices(report.notices)
    exit_on_warnings(report.notices)


@config.command(name="template")
@WORKSPACE
@click.option(
    "--print",
    "print_only",
    is_flag=True,
    help="Write nothing; add the whole file the template would produce to the output as text.",
)
@_json_command
def config_template(workspace_root: str | None, print_only: bool) -> None:
    """Add the commented template to .devkit/config.toml: every key it lacks, at its default.

    devkit's top-level keys go after the file's last top-level key, the [tool.<name>] tables of installed tools
    (the devkit.config_template entry points) at the end. Existing lines are never changed. Prints path, state
    (created, updated or unchanged) and added; a tool whose template fails is a warning under notices. With
    --print nothing is written and text holds the resulting file.
    """
    root = resolve_root(workspace_root)
    result = PreviewConfigTemplate().execute(root) if print_only else RefreshConfigTemplate().execute(root)
    echo_json(result.to_dict())
    echo_notices(result.notices)
    exit_on_warnings(result.notices)
