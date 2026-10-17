"""Check local socket wakeups before starting the workspace's async tests."""

from __future__ import annotations

import shlex
import socket

import click
from devkit.advisory import Actor, AdvisoryError, Retry
from devkit.core.cli import boundary


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1, required=True, type=click.UNPROCESSED)
@boundary
def main(command: tuple[str, ...]) -> None:
    """Require the socket writes used by asyncio's cross-thread wakeups."""
    try:
        sender, receiver = socket.socketpair()
        with sender, receiver:
            sender.settimeout(1)
            receiver.settimeout(1)
            sender.sendall(b"\0")
            if receiver.recv(1) != b"\0":
                raise OSError("local socket wakeup was not delivered")
    except OSError as exc:
        raise AdvisoryError(
            "local socket wakeups are unavailable; async tests cannot run reliably",
            f"operation=socketpair_send_receive errno={exc.errno}",
            f"command={shlex.join(command)}",
            code="ASYNC_WAKEUP_BLOCKED",
            actor=Actor.USER,
            retry=Retry.AFTER_FIX,
            fix=shlex.join(command),
            what_to_report=(
                "Use the execution tool's approval mechanism to run [FIX] in an environment that permits local "
                "socket writes, or run it in a permitted local/CI environment. Do not skip tests or report a pass."
            ),
        ) from exc


if __name__ == "__main__":
    main()
