"""Check selected tests' local socket prerequisites before starting pytest."""

from __future__ import annotations

import shlex
import socket
from pathlib import Path

import click
from devkit.advisory import Actor, AdvisoryError, Retry
from devkit_dist.adapters.cli import boundary

ROOT = Path(__file__).resolve().parents[1]
LOOPBACK_TESTS = (
    "packages/devkit-viewer/tests/integration/features/browse/test_cli.py",
    "packages/devkit-viewer/tests/integration/features/browse/test_server.py",
)


def needs_loopback(paths: tuple[str, ...]) -> bool:
    """No paths means full-suite; a path covering a known HTTP test needs loopback.

    Pytest expressions and ignore options do not narrow this conservative check.
    """
    if not paths:
        return True
    for value in paths:
        path = Path(value.split("::", 1)[0])
        path = path if path.is_absolute() else ROOT / path
        for consumer in LOOPBACK_TESTS:
            if (ROOT / consumer).is_relative_to(path.resolve()):
                return True
    return False


def check_loopback(command: tuple[str, ...]) -> None:
    """Bind and listen on an ephemeral loopback port, without external traffic."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
    except OSError as exc:
        raise AdvisoryError(
            "local loopback servers are unavailable; selected HTTP tests cannot run",
            f"operation=loopback_bind_listen address=127.0.0.1 port=0 errno={exc.errno}",
            f"command={shlex.join(command)}",
            code="TEST_LOOPBACK_BLOCKED",
            actor=Actor.USER,
            retry=Retry.AFTER_FIX,
            fix=shlex.join(command),
            what_to_report=(
                "Use the execution tool's approval mechanism to run [FIX] in an environment that permits local "
                "TCP bind and listen, or run it in a permitted local/CI environment. Do not skip tests or report a pass."
            ),
        ) from exc


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("--test-path", "test_paths", multiple=True, help="Resolved pytest path; omitted means the full suite.")
@click.argument("command", nargs=-1, required=True, type=click.UNPROCESSED)
@boundary
def main(test_paths: tuple[str, ...], command: tuple[str, ...]) -> None:
    """Require async wakeups and, for selected server tests, local TCP bind/listen."""
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

    if needs_loopback(test_paths):
        check_loopback(command)


if __name__ == "__main__":
    main()
