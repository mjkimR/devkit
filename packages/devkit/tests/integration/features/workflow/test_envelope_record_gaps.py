"""A reverify closes a challenger round, and an answer settles worker assumptions (``SPEC-envelope-record-gaps``)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import Result
from devkit_agt.features.workflow.services.envelope import load_envelopes
from testsupport.workflow import SIMPLE_UNIT, run_cli, simple_workspace

FINDINGS = [
    {"issue": "Boundary names no area", "evidence": "proposal.md:12", "severity": "P2"},
    {"issue": "Option B unexplored", "evidence": "proposal.md:40", "severity": "P3"},
]
WORKER = {
    "kind": "worker",
    "stage": "s",
    "status": "needs_input",
    "assumptions": ["Settings stay in TOML", "Keys keep their names", "No migration tool"],
    "questions": [{"id": "q1", "title": "Format", "prompt": "Which?", "options": [{"id": "a"}, {"id": "b"}]}],
}


@pytest.fixture
def root(tmp_path: Path) -> Path:
    simple_workspace(tmp_path)
    assert run_cli("new", "-w", str(tmp_path), "u").exit_code == 0
    return tmp_path


def _unit(root: Path) -> Path:
    return root / SIMPLE_UNIT


def _put(root: Path, name: str, data: dict[str, object]) -> None:
    directory = _unit(root) / "envelopes"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _envelope(root: Path, kind: str, *args: str, stdin: str | None = None) -> Result:
    from click.testing import CliRunner
    from devkit_agt.features.workflow.cli import cli

    return CliRunner().invoke(cli, ["envelope", kind, "-w", str(root), "--unit", SIMPLE_UNIT, *args], input=stdin)


def _read(root: Path, name: str) -> dict[str, object]:
    return yaml.safe_load((_unit(root) / "envelopes" / name).read_text(encoding="utf-8"))


def _names(root: Path) -> list[str]:
    directory = _unit(root) / "envelopes"
    return sorted(p.name for p in directory.iterdir()) if directory.is_dir() else []


def _challenger(root: Path) -> None:
    _put(root, "challenger-01.yaml", {"kind": "challenger", "stage": "s", "status": "completed", "findings": FINDINGS})


# -- a reverify closes a challenger round -------------------------------------------------------------------------------


# AC-01
def test_reverify_closes_a_challenger_round(root: Path) -> None:
    _challenger(root)
    result = _envelope(
        root, "reverify", "--summary", "folded", "--from", "envelopes/challenger-01.yaml", "--resolve", "1",
        "--waive", "2=kept as designed",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    assert "open_findings=0" in result.stdout
    data = _read(root, "reverify-01.yaml")
    assert data["review"] == "challenger-01.yaml"
    findings = data["findings"]
    assert isinstance(findings, list)
    assert [f["resolution"] for f in findings] == ["resolved", "waived"]
    assert findings[1]["waiver"] == "kept as designed" and findings[1]["severity"] == "P3"
    text = run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT).stdout
    assert (
        "[ENVELOPE: envelopes/reverify-01.yaml kind=reverify seq=01 status=completed open_findings=0"
        " review=challenger-01.yaml]" in text
    )
    assert "[ENVELOPE: envelopes/challenger-01.yaml kind=challenger seq=01 status=completed open_findings=2]" in text
    out = json.loads(run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json").stdout)
    entries = {e["file"]: e for e in out["envelopes"]}
    assert entries["envelopes/reverify-01.yaml"]["review"] == "challenger-01.yaml"
    # A reverify of the reverify keeps naming the challenger round.
    again = _envelope(root, "reverify", "--summary", "x", "--from", "envelopes/reverify-01.yaml")
    assert again.exit_code == 0, again.output
    assert _read(root, "reverify-02.yaml")["review"] == "challenger-01.yaml"
    assert load_envelopes(_unit(root)).deciding("challenger").name == "reverify-02.yaml"  # type: ignore[union-attr]


# AC-03
@pytest.mark.parametrize("source", ["latest", "envelopes/scout-01.yaml"])
def test_from_refusals_name_the_challenger_form(root: Path, source: str) -> None:
    _challenger(root)
    _put(root, "scout-01.yaml", {"kind": "scout", "stage": "s", "status": "completed", "findings": FINDINGS})
    before = _names(root)
    result = _envelope(root, "reverify", "--summary", "x", "--from", source, "--resolve", "all")
    assert result.exit_code == 2
    assert "ENVELOPE_FROM_INVALID" in result.stderr
    assert "--from envelopes/challenger-NN.yaml" in result.stderr
    assert _names(root) == before


# AC-04
@pytest.mark.parametrize("kind", ["challenger", "review"])
def test_a_round_records_findings_as_found(root: Path, kind: str) -> None:
    findings = "- { issue: x, evidence: y, severity: P2, resolution: resolved }\n"
    args = ("new", "--kind", kind) if kind == "challenger" else (kind,)
    result = _envelope(root, *args, "--stage", "s", "--summary", "x", "--findings-file", "-", stdin=findings)
    assert result.exit_code == 2 and "ENVELOPE_FLAG_INVALID" in result.stderr
    assert f"a {kind} records findings as found" in result.stderr
    assert _names(root) == []


# AC-05
def test_a_reverify_names_a_review_or_challenger_round(root: Path) -> None:
    _challenger(root)
    _put(root, "reverify-01.yaml", {"kind": "reverify", "status": "completed", "review": "scout-01.yaml"})
    _put(root, "reverify-02.yaml", {"kind": "reverify", "status": "completed", "review": "challenger-01.yaml"})
    result = run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert result.exit_code == 1
    assert (
        '[ENVELOPE_ERROR: envelopes/reverify-01.yaml "reverify needs `review: review-NN.yaml` or'
        ' `review: challenger-NN.yaml` naming the round it closes"]' in result.stdout
    )
    assert "[ENVELOPE: envelopes/reverify-02.yaml kind=reverify" in result.stdout


# -- an answer settles worker assumptions -------------------------------------------------------------------------------


# AC-06
def test_an_answer_settles_assumptions_by_position(root: Path) -> None:
    _put(root, "worker-01.yaml", WORKER)
    answer = "- { question: q1, choice: a, decision: Keep TOML. }\n"
    first = _envelope(
        root, "answer", "--summary", "q1 decided", "--answers-to", "worker-01.yaml", "--answers-file", "-",
        "--settle", "2=Keep the TOML layout", stdin=answer,
    )  # fmt: skip
    assert first.exit_code == 0, first.output
    data = _read(root, "answer-01.yaml")
    assert data["settles"] == [{"assumption": 2, "decision": "Keep the TOML layout"}]
    assert list(data).index("settles") == list(data).index("answers") + 1
    only = _envelope(root, "answer", "--summary", "settled", "--answers-to", "worker-01.yaml", "--settle", "3=No tool")
    assert only.exit_code == 0, only.output
    data = _read(root, "answer-02.yaml")
    assert "answers" not in data and data["settles"] == [{"assumption": 3, "decision": "No tool"}]
    out = json.loads(
        run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json", "--details").stdout
    )
    entries = {e["file"]: e for e in out["envelopes"]}
    assert entries["envelopes/answer-02.yaml"]["settles"] == [{"assumption": 3, "decision": "No tool"}]
    assert entries["envelopes/worker-01.yaml"]["settles"] == []


def test_a_settles_only_answer_answers_no_question(root: Path) -> None:
    _put(root, "worker-01.yaml", WORKER)
    result = _envelope(root, "answer", "--summary", "settled", "--answers-to", "worker-01.yaml", "--settle", "1=TOML")
    assert result.exit_code == 0, result.output
    text = run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT).stdout
    assert "[PENDING_QUESTION: envelopes/worker-01.yaml id=q1" in text


# AC-07
@pytest.mark.parametrize(
    ("settles", "code"),
    [
        (("--settle", "4=x"), "ENVELOPE_REFERENCE_INVALID"),
        (("--settle", "1=a", "--settle", "1=b"), "ENVELOPE_FLAG_INVALID"),
        (("--settle", "x"), "ENVELOPE_FLAG_INVALID"),
        (("--settle", "0=x"), "ENVELOPE_FLAG_INVALID"),
    ],
)
def test_settles_that_do_not_fit_are_refused(root: Path, settles: tuple[str, ...], code: str) -> None:
    _put(root, "worker-01.yaml", WORKER)
    result = _envelope(root, "answer", "--summary", "x", "--answers-to", "worker-01.yaml", *settles)
    assert result.exit_code == 2 and code in result.stderr, result.output
    assert _names(root) == ["worker-01.yaml"]


@pytest.mark.parametrize(
    ("settles", "reason"),
    [
        ([{"assumption": 5, "decision": "x"}], "settles: assumption 5 is not an assumption of worker-01.yaml"),
        ([{"assumption": 1, "decision": "x"}, {"assumption": 1, "decision": "y"}], "each assumption at most once"),
        ([{"assumption": "1", "decision": "x"}], "expected a 1-based assumption number"),
        ([{"assumption": 1}], "missing required key decision"),
        ([{"assumption": 1, "decision": "x", "why": "y"}], "unknown keys"),
    ],
)
def test_a_loaded_answer_whose_settles_do_not_fit_is_malformed(
    root: Path, settles: list[dict[str, object]], reason: str
) -> None:
    _put(root, "worker-01.yaml", WORKER)
    answer = {
        "kind": "answer",
        "status": "completed",
        "answers_to": "worker-01.yaml",
        "answers": [{"question": "q1", "choice": "a", "decision": "Keep TOML."}],
        "settles": settles,
    }
    _put(root, "answer-01.yaml", answer)
    envelopes = load_envelopes(_unit(root))
    assert [e.file for e in envelopes.errors] == ["envelopes/answer-01.yaml"]
    assert reason in envelopes.errors[0].message
    assert [q.id for _, q in envelopes.hold().questions] == ["q1"]


def test_only_an_answer_carries_settles(root: Path) -> None:
    _put(root, "review-01.yaml", {"kind": "review", "status": "completed", "settles": [{"assumption": 1, "decision": "x"}]})  # fmt: skip
    _put(root, "answer-01.yaml", {"kind": "answer", "status": "completed", "answers_to": "worker-01.yaml"})
    errors = {e.file: e.message for e in load_envelopes(_unit(root)).errors}
    assert "only an answer envelope carries them" in errors["envelopes/review-01.yaml"]
    assert "an answer envelope needs answers or settles" in errors["envelopes/answer-01.yaml"]
