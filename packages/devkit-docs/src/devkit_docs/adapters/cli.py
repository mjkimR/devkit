"""Sentinel output shared by the ``devkit docs`` commands, on devkit's one field renderer.

Values render with ``devkit_dist.adapters.cli.field_value`` (``ARCH-08-1-agent-output`` section 3).
"""

from __future__ import annotations

import shlex
from collections.abc import Sequence

import click
from devkit_dist.adapters.cli import field_value

from devkit_docs.base.errors import DEVKIT

COMMAND = f"{DEVKIT} docs"


def sentinel(name: str, positional: object, /, **fields: object) -> str:
    """``[KIND: <positional> key=value ...]``."""
    parts = [field_value(positional), *(f"{key}={field_value(item)}" for key, item in fields.items())]
    return f"[{name}: {' '.join(parts)}]"


def fields_line(name: str, /, **fields: object) -> str:
    """``[KIND: key=value ...]``, a sentinel without a positional value."""
    return f"[{name}: {' '.join(f'{key}={field_value(item)}' for key, item in fields.items())}]"


def echo_page(total: int, offset: int, limit: int, count: int, next_command: Sequence[str]) -> None:
    """``[PAGE: total= offset= limit= count= next=]`` and, when more items follow, ``[NEXT_CMD: ...]``.

    ``next_command`` is the command's own argument list without ``--offset``; ``limit`` ``0`` means no limit.
    """
    following = offset + count if limit and offset + count < total else None
    click.echo(fields_line("PAGE", total=total, offset=offset, limit=limit, count=count, next=following))
    if following is not None:
        args = [*next_command, "--offset", str(following)]
        click.echo(f"[NEXT_CMD: {COMMAND} {shlex.join(args)}]")
