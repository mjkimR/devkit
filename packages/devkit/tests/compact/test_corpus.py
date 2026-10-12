"""``devkit run`` over real tool output: how large the view is, and that no failed test goes missing from it.

Each fixture in ``fixtures/`` is what a tool printed, captured to a file as ``devkit run`` captures it, with
the paths rewritten to ``/work/project``; ``retry-loop.txt`` is a synthetic wait for a service that never
comes up. ``max_view`` is the measured size of the view with a small margin: a change to the scan's
patterns or budgets that grows a view past it, drops a line the agent needs or loses a failed test fails
here. Raise a limit only for a measured reason, and add a fixture for each tool or output shape the scan
learns.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.cli import cli

FIXTURES = Path(__file__).parent / "fixtures"
_PRINT = "import sys; sys.stdout.write(open(sys.argv[1], encoding='utf-8').read()); sys.exit(int(sys.argv[2]))"
_FAILED_TEST = re.compile(r"^(?:FAILED|ERROR) (\S+\.py(?:::[^\s\[]+(?:\[.*?\])?)*)", re.MULTILINE)


@dataclass(frozen=True)
class Case:
    fixture: str
    exit_code: int
    summaries: tuple[str, ...]
    max_view: int  # characters on stdout after the [RUN] line, and on stderr
    keep: tuple[str, ...] = ()  # what the view must show


CASES = [
    Case(
        "pytest-long-traceback.txt",
        1,
        ("42 failed, 203 passed, 1 warning, 1 error in 0.09s",),
        8_700,
        (
            "RuntimeError: database is not reachable",
            "FAILED tests/test_mass.py::test_compares_payloads[39]",
            "FAILED tests/test_small.py::test_add_wrong - AssertionError: two plus two",
        ),
    ),
    Case(
        "pytest-short-traceback.txt",
        1,
        ("42 failed, 203 passed, 1 warning, 1 error in 0.08s",),
        8_700,
        ("RuntimeError: database is not reachable", "FAILED tests/test_small.py::test_add_wrong"),
    ),
    Case(
        "pytest-150-failures-tb-line.txt",
        1,
        ("150 failed in 0.06s",),
        11_800,
        ('[RUN_FAILURE: "tests/test_many.py::test_limits[0]"', "FAILED tests/test_many.py::test_limits[149]"),
    ),
    Case("pytest-verbose.txt", 1, ("1 failed, 2 passed in 0.01s",), 800, ("AssertionError: two plus two",)),
    Case("uv-run-pytest-quiet.txt", 1, ("1 failed, 2 passed in 0.01s",), 850, ("assert 4 == 5",)),
    Case("ruff-check-full.txt", 1, ("Found 4 errors.",), 1_200, ("F841",)),
    Case("ruff-check-concise.txt", 1, ("Found 4 errors.",), 500, ("src/app/__init__.py:7:5: F841",)),
    Case("mypy-errors.txt", 1, ("Found 2 errors in 1 file (checked 1 source file)",), 400, ("[return-value]",)),
    Case("mypy-success.txt", 0, ("Success: no issues found in 1 source file",), 100),
    Case(
        "retry-loop.txt",
        1,
        (),
        450,
        ("previous line repeated 239 more times", "Error: database did not become ready after 240 attempts"),
    ),
]


def _run(case: Case, *options: str) -> Result:
    path = FIXTURES / case.fixture
    return CliRunner().invoke(
        cli, ["run", *options, "--", sys.executable, "-c", _PRINT, str(path), str(case.exit_code)]
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.fixture)
def test_the_view_stays_small_and_keeps_what_the_agent_needs(case: Case) -> None:
    result = _run(case)
    assert result.exit_code == (0 if case.exit_code == 0 else 1), result.output
    view = result.stdout.split("\n", 1)[1] + result.stderr
    assert len(view) <= case.max_view, view
    for text in case.keep:
        assert text in view
    data = json.loads(_run(case, "--format", "json").stdout)
    assert tuple(data["summaries"]) == case.summaries


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.fixture)
def test_every_failed_test_is_named_or_counted(case: Case) -> None:
    tests = set(_FAILED_TEST.findall((FIXTURES / case.fixture).read_text(encoding="utf-8")))
    data = json.loads(_run(case, "--format", "json").stdout)
    listed = {failure["test"] for failure in data["failures"]}
    shown = {test for test in tests if re.search(re.escape(test) + r"(?![\w\[])", data["output"] or "")}
    assert listed <= tests and not listed & shown
    assert len(tests - listed - shown) == data["omitted"]["failures"]


def test_every_fixture_has_a_case() -> None:
    assert {case.fixture for case in CASES} == {path.name for path in FIXTURES.glob("*.txt")}
