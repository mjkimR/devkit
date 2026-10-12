"""The ``devkit workflow`` group, shared options and the error boundary."""

from __future__ import annotations

import functools
import json
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import click

from devkit.advisory import AdvisoryError, as_advisory_error
from devkit.workflow.errors import input_error
from devkit.workflow.workspace import Workspace

FORMAT = click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)
WORKSPACE = click.option(
    "--workspace-root",
    "-w",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Workspace root directory (default: the devkit project containing the current directory)",
)
UNIT = click.option(
    "--unit", "-u", required=True, type=str, help="Work unit directory (workspace-relative or absolute)"
)
NO_LINT = click.option("--no-lint", is_flag=True, help="Skip lint-class checks")


class Reported(Exception):
    """An error whose JSON result is already on stdout; only the advisory goes to stderr."""

    def __init__(self, error: AdvisoryError) -> None:
        super().__init__(str(error))
        self.error = error


def boundary(fn: Callable[..., None]) -> Callable[..., None]:
    """Render any error as an advisory on stderr (and as JSON on stdout under --format json).

    The exit code is the error's: ``ERROR`` (2) unless the error reports a
    negative result (``WORKFLOW_DRIFT``, ``ENVELOPE_INVALID``: ``FINDINGS``, 1).
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            fn(*args, **kwargs)
        except (click.exceptions.Exit, click.ClickException, SystemExit):
            raise
        except Reported as reported:
            click.echo(reported.error.render(), err=True)
            sys.exit(int(reported.error.exit_code))
        except Exception as exc:
            error = as_advisory_error(exc)
            if is_json(kwargs.get("output_format")):
                echo_json({"error": error.to_dict()})
            click.echo(error.render(), err=True)
            sys.exit(int(error.exit_code))

    return wrapper


def is_json(output_format: object) -> bool:
    return str(output_format or "text").lower() == "json"


def echo_json(data: object) -> None:
    click.echo(json.dumps(data, indent=2))


def workspace(root: str | None) -> Workspace:
    return Workspace(Path(root) if root is not None else None)


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise input_error(f"--date: {exc}", code="DATE_INVALID", fix="Pass --date YYYY-MM-DD") from exc


@click.group(name="workflow")
@click.version_option(package_name="devkit")
def cli() -> None:
    """Data-driven delivery workflow engine for coding agents."""
