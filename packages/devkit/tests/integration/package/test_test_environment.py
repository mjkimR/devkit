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
