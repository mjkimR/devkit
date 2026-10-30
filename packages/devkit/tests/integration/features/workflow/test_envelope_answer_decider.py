"""An answer entry records its decider, and a reverify refuses closed findings (``SPEC-envelope-answer-decider``)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from devkit_agt.features.workflow.cli import cli
from devkit_agt.features.workflow.services.envelope import load_envelopes
from testsupport.workflow import SIMPLE_UNIT, run_cli, simple_workspace

WORKER = {
    "kind": "worker",
    "stage": "s",
    "status": "needs_input",
    "questions": [
        {"id": "q1", "title": "Format", "prompt": "Which?", "options": [{"id": "a"}, {"id": "b"}]},
        {"id": "q2", "title": "Order", "prompt": "What first?"},
    ],
}
THREE = [
    {"issue": "Boundary names no area", "evidence": "proposal.md:12"},
    {"issue": "Option B unexplored", "evidence": "proposal.md:40"},
    {"issue": "No rollback path", "evidence": "proposal.md:55"},
]


@pytest.fixture
def root(tmp_path: Path) -> Path:
    simple_workspace(tmp_path)
    assert run_cli("new", "-w", str(tmp_path), "u").exit_code == 0
    return tmp_path


def _dir(root: Path) -> Path:
    return root / SIMPLE_UNIT / "envelopes"


def _put(root: Path, name: str, data: dict[str, object]) -> None:
    _dir(root).mkdir(parents=True, exist_ok=True)
    (_dir(root) / name).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _read(root: Path, name: str) -> dict[str, object]:
    return yaml.safe_load((_dir(root) / name).read_text(encoding="utf-8"))


def _names(root: Path) -> list[str]:
    return sorted(p.name for p in _dir(root).iterdir()) if _dir(root).is_dir() else []


def _envelope(root: Path, kind: str, *args: str, stdin: str | None = None) -> Result:
    return CliRunner().invoke(cli, ["envelope", kind, "-w", str(root), "--unit", SIMPLE_UNIT, *args], input=stdin)


def _answer(root: Path, answers: str) -> Result:
    return _envelope(
        root, "answer", "--summary", "decided", "--answers-to", "worker-01.yaml", "--answers-file", "-", stdin=answers
    )


# -- the decider of an answer -------------------------------------------------------------------------------------------


# AC-01, AC-05
def test_an_answer_entry_records_its_decider(root: Path) -> None:
    _put(root, "worker-01.yaml", WORKER)
    answers = (
        "- { question: q1, choice: a, decision: Keep TOML., constraints: [Warn once], by: user }\n"
        "- { question: q2, choice: null, decision: Ship first., by: host }\n"
    )
    result = _answer(root, answers)
    assert result.exit_code == 0, result.output
    written = _read(root, "answer-01.yaml")["answers"]
    assert isinstance(written, list)
    assert [a["by"] for a in written] == ["user", "host"]
    assert list(written[0]) == ["question", "choice", "decision", "constraints", "by"]
    assert list(written[1]) == ["question", "choice", "decision", "by"]
    out = json.loads(
        run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json", "--details").stdout
    )
    entries = {e["file"]: e for e in out["envelopes"]}
    assert [a["by"] for a in entries["envelopes/answer-01.yaml"]["answers"]] == ["user", "host"]


# AC-02, AC-05
def test_an_answer_without_a_decider_stays_valid(root: Path) -> None:
    _put(root, "worker-01.yaml", WORKER)
    result = _answer(
        root,
        "- { question: q1, choice: a, decision: Keep TOML. }\n- { question: q2, choice: null, decision: x, by: policy }\n",
    )
    assert result.exit_code == 0, result.output
    written = _read(root, "answer-01.yaml")["answers"]
    assert isinstance(written, list)
    assert "by" not in written[0] and written[1]["by"] == "policy"
    _put(
        root,
        "answer-02.yaml",
        {
            "kind": "answer",
            "status": "completed",
            "answers_to": "worker-01.yaml",
            "answers": [{"question": "q1", "choice": "b", "decision": "Use YAML.", "by": None}],
        },
    )
    envelopes = load_envelopes(root / SIMPLE_UNIT)
    assert not envelopes.errors
    out = json.loads(
        run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json", "--details").stdout
    )
    entries = {e["file"]: e for e in out["envelopes"]}
    assert "by" not in entries["envelopes/answer-02.yaml"]["answers"][0]


# AC-03
@pytest.mark.parametrize("by", ["person", "''", "User"])
def test_an_unknown_decider_is_refused_before_writing(root: Path, by: str) -> None:
    _put(root, "worker-01.yaml", WORKER)
    result = _answer(root, f"- {{ question: q1, choice: a, decision: Keep TOML., by: {by} }}\n")
    assert result.exit_code == 2, result.output
    assert "ENVELOPE_ITEMS_INVALID" in result.stderr
    assert "[TARGET] --answers-file" in result.stderr
    assert "user, host, policy" in result.stderr
    assert _names(root) == ["worker-01.yaml"]


# AC-04
def test_a_loaded_answer_with_an_unknown_decider_is_malformed(root: Path) -> None:
    _put(root, "worker-01.yaml", WORKER)
    _put(
        root,
        "answer-01.yaml",
        {
            "kind": "answer",
            "status": "completed",
            "answers_to": "worker-01.yaml",
            "answers": [{"question": "q1", "choice": "a", "decision": "Keep TOML.", "by": "person"}],
        },
    )
    result = run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert result.exit_code == 1
    assert "ENVELOPE_INVALID" in result.stderr and "envelopes/answer-01.yaml" in result.stderr
    envelopes = load_envelopes(root / SIMPLE_UNIT)
    assert "q1" in [q.id for _, q in envelopes.hold().questions]


# -- a reverify refuses closed findings ---------------------------------------------------------------------------------


def _closed_round(root: Path) -> None:
    _put(root, "challenger-01.yaml", {"kind": "challenger", "stage": "s", "status": "completed", "findings": THREE})
    first = _envelope(
        root, "reverify", "--summary", "turn 1", "--from", "envelopes/challenger-01.yaml", "--resolve", "1",
        "--waive", "2=kept as designed",
    )  # fmt: skip
    assert first.exit_code == 0, first.output


# AC-06
def test_closing_an_already_closed_finding_is_refused(root: Path) -> None:
    _closed_round(root)
    before = _names(root)
    result = _envelope(
        root, "reverify", "--summary", "turn 2", "--from", "envelopes/challenger-01.yaml", "--resolve", "2",
        "--waive", "1=kept", "--resolve", "3",
    )  # fmt: skip
    assert result.exit_code == 2, result.output
    assert "ENVELOPE_FINDING_CLOSED" in result.stderr
    assert "[TARGET] --resolve 2, --waive 1" in result.stderr
    assert '1: resolved "Boundary names no area"' in result.stderr
    assert '2: waived "Option B unexplored"' in result.stderr
    assert '3: open "No rollback path"' in result.stderr
    assert _names(root) == before


@pytest.mark.parametrize("flags", [("--resolve", "2"), ("--waive", "1=again")])
def test_one_closed_number_is_enough_to_refuse(root: Path, flags: tuple[str, str]) -> None:
    _closed_round(root)
    before = _names(root)
    result = _envelope(root, "reverify", "--summary", "x", "--from", "envelopes/challenger-01.yaml", *flags)
    assert result.exit_code == 2 and "ENVELOPE_FINDING_CLOSED" in result.stderr, result.output
    assert _names(root) == before


def test_an_out_of_range_number_keeps_its_own_code(root: Path) -> None:
    _closed_round(root)
    result = _envelope(
        root, "reverify", "--summary", "x", "--from", "envelopes/challenger-01.yaml", "--resolve", "2", "--resolve", "4"
    )
    assert result.exit_code == 2
    assert "ENVELOPE_FLAG_INVALID" in result.stderr and "finding numbers are 1..3" in result.stderr


# AC-07
def test_open_findings_still_close(root: Path) -> None:
    _closed_round(root)
    result = _envelope(
        root, "reverify", "--summary", "turn 2", "--from", "envelopes/challenger-01.yaml", "--resolve", "3"
    )
    assert result.exit_code == 0, result.output
    assert "open_findings=0" in result.stdout
    findings = _read(root, "reverify-02.yaml")["findings"]
    assert isinstance(findings, list)
    assert [f["resolution"] for f in findings] == ["resolved", "waived", "resolved"]
    assert findings[1]["waiver"] == "kept as designed"
    again = _envelope(
        root, "reverify", "--summary", "turn 3", "--from", "envelopes/challenger-01.yaml", "--resolve", "all"
    )
    assert again.exit_code == 0, again.output
