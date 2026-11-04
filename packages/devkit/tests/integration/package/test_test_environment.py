"""The workspace test preflight distinguishes unavailable execution from passing tests."""

from __future__ import annotations

import errno
import runpy
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

SCRIPT = Path(__file__).resolve().parents[5] / "scripts/check_test_environment.py"


def test_permitted_environment_is_silent() -> None:
    command = runpy.run_path(str(SCRIPT))["main"]
    result = CliRunner().invoke(command, ["--", "just", "test", "all"])
    assert result.exit_code == 0, result.output
    assert result.stdout == result.stderr == ""


@pytest.mark.parametrize("blocked_at", ["create", "send"])
def test_blocked_environment_reports_exact_retry_without_running_it(monkeypatch, blocked_at: str) -> None:
    namespace = runpy.run_path(str(SCRIPT))
    sender, receiver = MagicMock(), MagicMock()
    pair = MagicMock(return_value=(sender, receiver))
    if blocked_at == "create":
        pair.side_effect = PermissionError(errno.EPERM, "Operation not permitted")
    else:
        sender.sendall.side_effect = PermissionError(errno.EPERM, "Operation not permitted")
    monkeypatch.setattr(namespace["socket"], "socketpair", pair)
    result = CliRunner().invoke(namespace["main"], ["--", "just", "test-cov", "all", "-k", "foo and bar", "-n0"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "ASYNC_WAKEUP_BLOCKED" in result.stderr
    assert "[ACTION]" in result.stderr
    assert "command=just test-cov all -k 'foo and bar' -n0" in result.stderr
    assert "Do not skip tests or report a pass" in result.stderr
    receiver.recv.assert_not_called()
    if blocked_at == "send":
        sender.__exit__.assert_called_once()
        receiver.__exit__.assert_called_once()


@pytest.mark.parametrize(
    ("paths", "required"),
    [
        ((), True),
        ((".",), True),
        (("packages/devkit-viewer/tests",), True),
        (("packages/devkit-viewer/tests/integration/features/browse/test_cli.py::test_serves_two_repos",), True),
        (("packages/devkit-viewer/tests/integration/features/browse/test_server.py",), True),
        ((str(SCRIPT.parents[1] / "packages/devkit-viewer/tests/integration"),), True),
        (("packages/devkit/tests",), False),
        (("packages/devkit-viewer/tests/unit",), False),
        (("packages/devkit-viewer/tests/integration/features/browse/test_worktree.py",), False),
    ],
)
def test_selected_paths_require_only_known_loopback_consumers(paths: tuple[str, ...], required: bool) -> None:
    namespace = runpy.run_path(str(SCRIPT))
    assert namespace["needs_loopback"](paths) is required


def test_unrelated_selection_does_not_create_tcp_socket(monkeypatch) -> None:
    namespace = runpy.run_path(str(SCRIPT))
    # Create real socketpair sockets first: socketpair itself constructs socket.socket instances.
    pair = namespace["socket"].socketpair()
    monkeypatch.setattr(namespace["socket"], "socketpair", lambda: pair)
    tcp = MagicMock(side_effect=AssertionError("unrelated tests must not need TCP bind"))
    monkeypatch.setattr(namespace["socket"], "socket", tcp)
    result = CliRunner().invoke(
        namespace["main"], ["--test-path", "packages/devkit/tests", "--", "just", "test", "devkit"]
    )
    assert result.exit_code == 0, result.output
    assert result.stdout == result.stderr == ""
    tcp.assert_not_called()


@pytest.mark.parametrize("blocked_at", ["create", "bind", "listen"])
def test_loopback_denial_reports_exact_retry_and_closes_socket(monkeypatch, blocked_at: str) -> None:
    namespace = runpy.run_path(str(SCRIPT))
    pair = namespace["socket"].socketpair()
    monkeypatch.setattr(namespace["socket"], "socketpair", lambda: pair)
    listener = MagicMock()
    listener.__enter__.return_value = listener
    tcp = MagicMock(return_value=listener)
    denied = PermissionError(errno.EPERM, "Operation not permitted")
    if blocked_at == "create":
        tcp.side_effect = denied
    else:
        getattr(listener, blocked_at).side_effect = denied
    monkeypatch.setattr(namespace["socket"], "socket", tcp)
    result = CliRunner().invoke(namespace["main"], ["--", "just", "test", "all", "-k", "foo and bar", "-n0"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "TEST_LOOPBACK_BLOCKED" in result.stderr
    assert "[ACTION]" in result.stderr
    assert "command=just test all -k 'foo and bar' -n0" in result.stderr
    assert "Do not skip tests or report a pass" in result.stderr
    if blocked_at != "create":
        listener.__exit__.assert_called_once()
    if blocked_at == "bind":
        listener.listen.assert_not_called()
