"""Run a command in a test and read its output as the agent-first contract defines it.

``invoke`` runs a click command in-process with stdout and stderr kept apart and returns an ``Outcome``: the exit
code, both streams, ``json()`` for the one JSON object a ``--format json`` run prints, and ``codes()`` for the
advisory codes on stderr. Import it from tests only (``from devkit_cli.testing import invoke``); the package root
does not import it.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import click
from click.testing import CliRunner

_HEADLINE = re.compile(r"^\[(?:ERROR|WARN|NOTICE)\] +\(([A-Z0-9_]+)\)", re.MULTILINE)


@dataclass(frozen=True)
class Outcome:
    """What one command run produced."""

    exit_code: int
    stdout: str
    stderr: str
    exception: BaseException | None = None

    def json(self) -> dict[str, Any]:
        """The one JSON object on stdout; ``AssertionError`` when stdout is anything else."""
        try:
            document = json.loads(self.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"stdout is not one JSON object: {exc}\n{self.stdout}") from exc
        if not isinstance(document, dict):
            raise AssertionError(f"stdout is JSON but not an object: {self.stdout}")
        return document

    def codes(self) -> list[str]:
        """The code of every ``[ERROR]``, ``[WARN]`` and ``[NOTICE]`` block on stderr, in order."""
        return _HEADLINE.findall(self.stderr)


def invoke(command: click.Command, args: Sequence[str] = (), *, env: Mapping[str, str | None] | None = None) -> Outcome:
    """Run ``command`` with ``args`` (and ``env`` overriding the environment) and return its ``Outcome``.

    An exception the command let escape (one no boundary caught) is kept on ``Outcome.exception``.
    """
    result = CliRunner().invoke(command, list(args), env=dict(env) if env is not None else None)
    exception = result.exception if not isinstance(result.exception, SystemExit) else None
    return Outcome(exit_code=result.exit_code, stdout=result.stdout, stderr=result.stderr, exception=exception)
