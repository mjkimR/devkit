"""Distribution output CLI adapters."""

from __future__ import annotations

import functools
import json
from collections import Counter
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

import click
from devkit.advisory import AdvisoryError, ExitCode

from devkit_dist.adapters.cli import (
    boundary,
    echo_json,
    echo_notices,
    exit_on_problems,
    exit_on_warnings,
    is_json,
    workspace_option,
)
from devkit_dist.features.distribution.models.errors import NotSynchronizedError
from devkit_dist.features.distribution.models.results import OverrideChange, SyncResult

WORKSPACE = workspace_option()
SOURCE = click.argument("source", type=click.Path(path_type=Path))


class _Result(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


def _json_command(fn: Callable[..., Any]) -> Callable[..., None]:
    """Run ``fn`` through the JSON-only error boundary and print its result, when it returns one.

    A result is a mapping or an object with ``to_dict()``.
    """

    @boundary(json_only=True)
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        result: Mapping[str, object] | _Result | None = fn(*args, **kwargs)
        if result is not None:
            echo_json(result if isinstance(result, Mapping) else result.to_dict())

    return wrapper


def _text_value(value: str) -> str:
    """``value`` bare, or as a JSON string when it would not stay one token of a sentinel line."""
    return json.dumps(value, ensure_ascii=False) if not value or any(c in value for c in ' "[]\\\n') else value


def _echo_sync_text(result: SyncResult) -> None:
    """The text form of a synchronization: what it wrote (or would write), never the deployed state it kept.

    The state (selection, packages, assets) is the same on every run, so it is left to
    ``--format json`` and ``devkit list``; drift, stray files, unprojected subagents and
    unselected bundles reach the agent as the advisories ``echo_notices`` prints.
    """
    counts = Counter(item.action for item in result.actions)
    fields = " ".join(f"{name}={counts[name]}" for name in ("create", "update", "remove", "seed"))
    click.echo(f"[SYNC: {fields} dry_run={'yes' if result.dry_run else 'no'}]")
    for item in result.actions:
        click.echo(f"[CHANGE: {item.action} {_text_value(item.path)}]")
    if not result.actions:
        click.echo("[OK: the workspace matches the selection]")


def _report(result: SyncResult, output_format: str, *, check: bool = False) -> None:
    """Print the result, then its warnings and notices on stderr.

    ``check`` (``sync --check``) that finds a synchronization needed reports it as ``NOT_SYNCHRONIZED`` (exit
    ``1``): under ``errors`` in the JSON result, which ``--check`` always carries, or as the last stderr block in
    text. Otherwise exits 1 under ``--strict`` when there is a warning.
    """
    problems: list[AdvisoryError] = []
    if check and result.actions:
        problems.append(
            NotSynchronizedError(
                f"the workspace does not match the selection: {len(result.actions)} planned changes",
                exit_code=ExitCode.FINDINGS,
            )
        )
    if is_json(output_format):
        data = result.to_dict()
        echo_json({**data, "errors": [problem.to_dict() for problem in problems]} if check else data)
    else:
        _echo_sync_text(result)
    echo_notices(result.notices)
    exit_on_problems(problems)
    exit_on_warnings(result.notices)


def _report_change(change: OverrideChange) -> None:
    """Print an override change, then the warnings and notices of the synchronization it ran."""
    echo_json(change.to_dict())
    echo_notices(change.notices)
    exit_on_warnings(change.notices)
