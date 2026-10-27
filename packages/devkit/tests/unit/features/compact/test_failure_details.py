"""``CommandRun.failure_details``: the advisory details of a failed run."""

from __future__ import annotations

from pathlib import Path

from devkit.advisory import Level
from devkit_agt.features.compact import FAILURE_TAIL_LINES, CommandRun, Failure, RelayedAdvisory, Scan


def _run() -> CommandRun:
    output = "\n".join(["1 failed", *(f"line {n}" for n in range(FAILURE_TAIL_LINES + 2)), ""])
    found = Scan(
        summaries=("1 failed",),
        failures=(Failure("t.py::test_x", "failed", "boom"),),
        advisories=(RelayedAdvisory(Level.ERROR, "[ERROR] X\n[FIX] y"), RelayedAdvisory(Level.WARNING, "[WARN] w")),
        output=output,
    )
    return CommandRun(("sh", "-c", "x"), 1, Path("/l.log"), 0.0, found)


def test_details_list_summaries_tail_and_errors() -> None:
    tail = [f"  | line {n}" for n in range(2, FAILURE_TAIL_LINES + 2)]
    assert _run().failure_details() == [
        "exit=1  log=/l.log",
        "  summary: 1 failed",
        *tail,
        "  > [ERROR] X",
        "  > [FIX] y",
    ]


def test_prefix_and_failed_tests_are_optional() -> None:
    details = _run().failure_details("command: x  ", failed_tests=True)
    assert details[:3] == ["command: x  exit=1  log=/l.log", "  summary: 1 failed", "  failed: t.py::test_x: boom"]
