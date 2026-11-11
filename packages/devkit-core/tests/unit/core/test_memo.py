"""``devkit_core.core.memo.envelope_problem``: only the exact memo envelope is accepted."""

from __future__ import annotations

import pytest
from devkit_core.core.memo import EnvelopeProblem, envelope_problem

VALID = {"version": 1, "fingerprint": "fp", "entries": {}}


def test_the_exact_envelope_has_no_problem() -> None:
    assert envelope_problem(dict(VALID), 1, "fp") is None


@pytest.mark.parametrize(
    ("loaded", "problem"),
    [
        ([VALID], EnvelopeProblem.SHAPE),
        (None, EnvelopeProblem.SHAPE),
        ({"version": 1, "fingerprint": "fp"}, EnvelopeProblem.SHAPE),
        ({**VALID, "extra": 1}, EnvelopeProblem.SHAPE),
        ({**VALID, "version": True}, EnvelopeProblem.VERSION),
        ({**VALID, "version": 2}, EnvelopeProblem.VERSION),
        ({**VALID, "version": "1"}, EnvelopeProblem.VERSION),
        ({**VALID, "fingerprint": "other"}, EnvelopeProblem.FINGERPRINT),
        ({**VALID, "entries": []}, EnvelopeProblem.SHAPE),
        ({**VALID, "version": 2, "fingerprint": "other", "entries": []}, EnvelopeProblem.VERSION),
        ({**VALID, "fingerprint": "other", "entries": []}, EnvelopeProblem.FINGERPRINT),
    ],
)
def test_every_other_object_has_its_first_problem(loaded: object, problem: EnvelopeProblem) -> None:
    assert envelope_problem(loaded, 1, "fp") is problem


def test_problems_read_as_the_reason_text() -> None:
    assert [str(problem) for problem in EnvelopeProblem] == [
        "not the expected shape",
        "another version",
        "another fingerprint",
    ]
