"""Question, answer, worker and resolution envelopes, and the hold they put on gates and integration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml
from devkit.workflow.errors import AuthoringError
from devkit.workflow.integration import finish_guard
from devkit.workflow.unit.envelope import compose_envelope, load_envelopes
from testsupport.workflow import SIMPLE_UNIT, run_cli, write_config

GATED = """---
id: w
schema_version: 1
stages:
  - id: review
    exit: [anchor-exists]
  - id: accept
    human_gate: plan-accept
    exit: [anchor-exists]
---
"""

QUESTIONS = """\
- id: q1
  title: Storage format
  prompt: Which format should settings use?
  context: proposal.md section 3
  options:
    - { id: a, description: Keep TOML, recommended: true }
    - { id: b, description: Switch to JSON }
- id: q2
  title: Migration scope
  prompt: How far should the migration go?
"""


def _write(unit: Path, name: str, data: dict[str, object]) -> None:
    (unit / "envelopes").mkdir(parents=True, exist_ok=True)
    (unit / "envelopes" / name).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _question(**extra: object) -> dict[str, object]:
    return {
        "kind": "question",
        "status": "needs_input",
        "questions": [
            {"id": "q1", "title": "Format", "prompt": "Which?", "options": [{"id": "a"}, {"id": "b"}]},
            {"id": "q2", "title": "Scope", "prompt": "How far?"},
        ],
        **extra,
    }


def _problem(**extra: object) -> dict[str, object]:
    return {
        "kind": "worker",
        "status": "failed",
        "problem": {"cause": "tests cannot start", "attempts": ["reinstalled"], "recovery": "fix the fixture"},
        **extra,
    }


@pytest.fixture
def root(tmp_path: Path) -> Path:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "w.md").write_text(GATED)
    write_config(tmp_path, '[workflow]\ndefault = "w"\n')
    assert run_cli("new", "-w", str(tmp_path), "u").exit_code == 0
    return tmp_path


# -- the file contract ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "data", "reason"),
    [
        ("question-01.yaml", {"kind": "question", "status": "needs_input"}, "needs questions"),
        ("question-01.yaml", _question(status="completed"), "status needs_input"),
        (
            "question-01.yaml",
            {**_question(), "problem": {"cause": "x", "recovery": "y"}},
            "only a worker envelope carries a problem",
        ),
        (
            "question-01.yaml",
            {
                "kind": "question",
                "status": "needs_input",
                "questions": [{"id": "q1", "title": "x" * 41, "prompt": "p"}],
            },
            "at most 40",
        ),
        (
            "question-01.yaml",
            {
                "kind": "question",
                "status": "needs_input",
                "questions": [{"id": "q1", "title": "t", "prompt": "p", "allow_note": False}],
            },
            "must allow a note",
        ),
        (
            "question-01.yaml",
            {
                "kind": "question",
                "status": "needs_input",
                "questions": [
                    {
                        "id": "q1",
                        "title": "t",
                        "prompt": "p",
                        "options": [{"id": "a", "recommended": True}, {"id": "b", "recommended": True}],
                    }
                ],
            },
            "at most one option is recommended",
        ),
        ("review-01.yaml", {"kind": "review", "status": "completed", "questions": []}, None),
        (
            "review-01.yaml",
            {"kind": "review", "status": "completed", "questions": [{"id": "q", "title": "t", "prompt": "p"}]},
            "only a question envelope",
        ),
        ("answer-01.yaml", {"kind": "answer", "status": "completed", "answers": []}, "answers_to"),
        ("worker-01.yaml", {"kind": "worker", "status": "failed"}, "needs a problem"),
        ("review-01.yaml", _problem(kind="review"), "only a worker envelope carries a problem"),
        ("worker-01.yaml", _problem(status="completed"), "completed envelope reports no problem"),
        ("worker-01.yaml", _problem(problem={"cause": "x"}), "missing required key recovery"),
        ("worker-01.yaml", {"kind": "worker", "status": "completed", "activity_effort": "max"}, "activity_effort"),
        ("resolution-01.yaml", {"kind": "resolution", "status": "completed", "summary": "x"}, "resolves"),
        (
            "resolution-01.yaml",
            {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml"},
            "needs a summary",
        ),
    ],
)
def test_kind_fields_are_validated(tmp_path: Path, name: str, data: dict[str, object], reason: str | None) -> None:
    _write(tmp_path, name, data)
    envelopes = load_envelopes(tmp_path)
    if reason is None:
        assert envelopes.errors == []
        return
    assert [e.file for e in envelopes.errors] == [f"envelopes/{name}"]
    assert reason in envelopes.errors[0].message


def test_references_must_fit(tmp_path: Path) -> None:
    _write(tmp_path, "question-01.yaml", _question())
    _write(tmp_path, "worker-01.yaml", {"kind": "worker", "status": "completed"})
    answer = {"kind": "answer", "status": "completed", "answers_to": "question-01.yaml"}
    _write(tmp_path, "answer-01.yaml", {**answer, "answers": [{"question": "q9", "decision": "d"}]})
    _write(tmp_path, "answer-02.yaml", {**answer, "answers": [{"question": "q1", "choice": "z", "decision": "d"}]})
    _write(tmp_path, "answer-03.yaml", {**answer, "answers_to": "question-07.yaml", "answers": [{"question": "q1", "decision": "d"}]})  # fmt: skip
    _write(tmp_path, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "s"})  # fmt: skip
    envelopes = load_envelopes(tmp_path)
    reasons = {e.file: e.message for e in envelopes.errors}
    assert "not a question of question-01.yaml" in reasons["envelopes/answer-01.yaml"]
    assert "'z' is not an option" in reasons["envelopes/answer-02.yaml"]
    assert "no well-formed question envelope" in reasons["envelopes/answer-03.yaml"]
    assert "no well-formed envelope with a problem" in reasons["envelopes/resolution-01.yaml"]
    assert "answer" not in envelopes.by_kind and "resolution" not in envelopes.by_kind
    # Answers that answer nothing leave every question pending.
    assert [q.id for _, q in envelopes.hold().questions] == ["q1", "q2"]


def test_a_problem_holds_until_a_resolution_names_it(tmp_path: Path) -> None:
    _write(tmp_path, "worker-01.yaml", _problem())
    _write(tmp_path, "worker-02.yaml", {"kind": "worker", "status": "completed", "summary": "later run went fine"})
    hold = load_envelopes(tmp_path).hold()
    assert hold.blocked and [e.file for e in hold.problems] == ["envelopes/worker-01.yaml"]
    assert hold.reasons("unit/") == ["unit/envelopes/worker-01.yaml: unresolved problem: tests cannot start"]
    _write(tmp_path, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "fixed"})  # fmt: skip
    assert not load_envelopes(tmp_path).hold()


def test_waiting_for_answers_is_not_a_problem(tmp_path: Path) -> None:
    _write(tmp_path, "question-01.yaml", _question())
    _write(tmp_path, "worker-01.yaml", {"kind": "worker", "status": "needs_input", "summary": "asked"})
    hold = load_envelopes(tmp_path).hold()
    assert not hold.blocked and [q.id for _, q in hold.questions] == ["q1", "q2"]
    answer = {"kind": "answer", "status": "completed", "answers_to": "question-01.yaml"}
    _write(tmp_path, "answer-01.yaml", {**answer, "answers": [{"question": "q1", "choice": "a", "decision": "Keep TOML."}]})  # fmt: skip
    assert [q.id for _, q in load_envelopes(tmp_path).hold().questions] == ["q2"]
    # Answers may be spread over several envelopes; a note-only answer has no choice.
    _write(tmp_path, "answer-02.yaml", {**answer, "answers": [{"question": "q2", "choice": None, "decision": "Only keys."}]})  # fmt: skip
    assert not load_envelopes(tmp_path).hold()


# -- authoring ---------------------------------------------------------------------------------------------------------


def _new(root: Path, *args: str, stdin: str | None = None) -> dict[str, object]:
    from click.testing import CliRunner
    from devkit.workflow.cli import cli

    result = CliRunner().invoke(
        cli, ["envelope", "new", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json", *args], input=stdin
    )
    return json.loads(result.stdout) if result.exit_code == 0 else {"exit": result.exit_code, "err": result.stdout}


def test_authoring_question_answer_problem_and_resolution(root: Path) -> None:
    unit = root / SIMPLE_UNIT
    asked = _new(root, "--kind", "question", "--stage", "review", "--summary", "two questions", "--questions-file", "-", stdin=QUESTIONS)  # fmt: skip
    assert asked["status"] == "needs_input" and asked["file"] == f"{SIMPLE_UNIT}/envelopes/question-01.yaml"
    data = yaml.safe_load((unit / "envelopes/question-01.yaml").read_text())
    assert data["questions"][0]["options"][0] == {"id": "a", "description": "Keep TOML", "recommended": True}
    (root / "answers.yaml").write_text(
        "- { question: q1, choice: a, decision: Keep TOML and tidy key names., constraints: [warn one release] }\n"
        "- { question: q2, choice: null, decision: Migrate keys only. }\n"
    )
    answered = _new(root, "--kind", "answer", "--stage", "review", "--summary", "q1 and q2 decided", "--answers-to", "envelopes/question-01.yaml", "--answers-file", str(root / "answers.yaml"), "--effort", "low")  # fmt: skip
    assert answered["status"] == "completed"
    data = yaml.safe_load((unit / "envelopes/answer-01.yaml").read_text())
    assert data["answers_to"] == "question-01.yaml" and data["activity_effort"] == "low"
    assert data["answers"][0]["constraints"] == ["warn one release"]
    failed = _new(root, "--kind", "worker", "--stage", "review", "--summary", "stopped", "--problem", "fixture broken", "--tried", "rerun", "--recovery", "repair the fixture")  # fmt: skip
    assert failed["status"] == "failed"
    assert load_envelopes(unit).hold().blocked
    resolved = _new(root, "--kind", "resolution", "--summary", "fixture repaired; tests pass", "--resolves", "worker-01.yaml")  # fmt: skip
    assert resolved["status"] == "completed"
    assert not load_envelopes(unit).hold()


@pytest.mark.parametrize(
    ("args", "code"),
    [
        (("--kind", "question", "--summary", "x"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "review", "--summary", "x", "--questions-file", "-"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "worker", "--status", "failed", "--summary", "x"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "worker", "--summary", "x", "--recovery", "y"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "worker", "--summary", "x", "--effort", "max"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "resolution", "--summary", "x", "--resolves", "worker-04.yaml"), "ENVELOPE_REFERENCE_INVALID"),
    ],
)
def test_authoring_refuses_what_the_contract_refuses(root: Path, args: tuple[str, ...], code: str) -> None:
    unit = root / SIMPLE_UNIT
    loaded = load_envelopes(unit)
    kwargs: dict[str, object] = {}
    flags = list(args)
    pairs = dict(zip(flags[::2], flags[1::2], strict=True))
    kwargs["kind"] = pairs.pop("--kind")
    kwargs["summary"] = pairs.pop("--summary")
    mapping = {"--status": "status", "--recovery": "recovery", "--effort": "effort", "--resolves": "resolves"}
    for flag, value in pairs.items():
        if flag == "--questions-file":
            kwargs["questions_yaml"] = QUESTIONS
        else:
            kwargs[mapping[flag]] = value
    with pytest.raises(AuthoringError) as caught:
        compose_envelope(unit_dir=unit, envelopes=loaded, loaded=loaded, **kwargs)  # type: ignore[arg-type]
    assert caught.value.code == code


def test_malformed_items_are_refused(root: Path) -> None:
    out = _new(root, "--kind", "question", "--summary", "x", "--questions-file", "-", stdin="- { id: Q, title: t, prompt: p }\n")  # fmt: skip
    assert out["exit"] == 2 and "ENVELOPE_ITEMS_INVALID" in str(out["err"])
    _new(root, "--kind", "question", "--summary", "x", "--questions-file", "-", stdin=QUESTIONS)
    out = _new(root, "--kind", "answer", "--summary", "x", "--answers-to", "question-01.yaml", "--answers-file", "-", stdin="- { question: q1, choice: c, decision: d }\n")  # fmt: skip
    assert out["exit"] == 2 and "ENVELOPE_REFERENCE_INVALID" in str(out["err"])


# -- evaluation, requests and answers -----------------------------------------------------------------------------------


def _next(root: Path, *args: str) -> dict[str, object]:
    return json.loads(run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint", "--format", "json", *args).stdout)  # fmt: skip


def test_questions_are_choose_requests_answered_by_an_envelope(root: Path) -> None:
    _new(root, "--kind", "question", "--stage", "review", "--summary", "x", "--questions-file", "-", stdin=QUESTIONS)
    result = _next(root)
    requests = {r["id"]: r for r in result["requests"]}  # type: ignore[union-attr]
    q1 = requests["question:question-01.q1"]
    assert (q1["kind"], q1["answer"], q1["context"]) == ("choose", "envelope", "proposal.md section 3")
    assert q1["target"] == {"type": "question", "name": "question-01.yaml#q1", "stage": "review"}
    assert [o["id"] for o in q1["options"] if o["recommended"]] == ["a"]
    assert result["waiting"] == {"class": "human", "checks": ["question:question-01.q1", "question:question-01.q2"]}
    text = run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint").stdout
    assert '[PENDING_QUESTION: envelopes/question-01.yaml id=q1 title="Storage format"]' in text
    assert (
        '[REQUEST: id=question:question-01.q1 kind=choose title="Storage format" target=question:question-01.yaml#q1'
        " stage=review options=a,b recommended=a note=allowed answer=envelope]" in text
    )
    refused = run_cli("answer", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint", "--request", "question:question-01.q1", "--action", "accept", "--value", "a")  # fmt: skip
    assert refused.exit_code == 2 and "DECISION_INVALID" in refused.stderr and "--kind answer" in refused.stderr


@pytest.mark.parametrize("policy", ["ask", "auto"])
def test_a_hold_keeps_every_gate_from_passing(root: Path, policy: str) -> None:
    write_config(root, f'[workflow]\ndefault = "w"\n[workflow.approvals]\nplan-accept = "{policy}"\n')
    unit = root / SIMPLE_UNIT
    _write(unit, "worker-01.yaml", _problem(stage="review"))
    for given in ((), ("--given", "plan-accept")):
        result = _next(root, *given)
        assert result["stage"]["id"] == "accept"  # type: ignore[index]
        assert result["gate"]["satisfied"] is False and result["gate"]["held"] is True  # type: ignore[index]
        assert [u["name"] for u in result["unmet"]] == ["envelope-hold"]  # type: ignore[union-attr]
        assert "blocked by envelopes/worker-01.yaml" in result["unmet"][0]["detail"]  # type: ignore[index]
        assert result["requests"] == [] and result["blocked"] is True
        assert result["problems"][0]["recovery"] == "fix the fixture"  # type: ignore[index]
    text = run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint").stdout
    assert '[BLOCKED: envelopes/worker-01.yaml cause="tests cannot start" recovery="fix the fixture"]' in text
    assert "held=yes" in text
    _write(unit, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "fixed"})  # fmt: skip
    result = _next(root)
    if policy == "auto":
        assert result["complete"] is True
    else:
        assert [r["id"] for r in result["requests"]] == ["gate:plan-accept"]  # type: ignore[union-attr]


def test_envelope_check_reports_the_hold(root: Path) -> None:
    unit = root / SIMPLE_UNIT
    _write(unit, "worker-01.yaml", _problem())
    _write(unit, "question-01.yaml", _question())
    text = run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert text.exit_code == 0
    assert (
        "[ENVELOPE: envelopes/worker-01.yaml kind=worker seq=01 status=failed open_findings=0 problem=yes]"
        in text.stdout
    )
    assert "[BLOCKED: envelopes/worker-01.yaml" in text.stdout and "[PENDING_QUESTION: envelopes/question-01.yaml id=q2" in text.stdout  # fmt: skip
    data = json.loads(run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json").stdout)
    assert data["blocked"] is True and [q["id"] for q in data["pending_questions"]] == ["q1", "q2"]


# -- the integration guard ---------------------------------------------------------------------------------------------


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def test_finish_guard_reads_the_units_the_branch_changed_at_its_tip(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo / "docs/old", "worker-01.yaml", _problem())  # already on the base: not the branch's
    (repo / "README.md").write_text("x\n")
    base = _commit(repo, "base")
    _git(repo, "switch", "-q", "-c", "dev-x")
    unit = repo / "docs/specs/x"
    _write(unit, "worker-01.yaml", _problem())
    _write(unit, "question-01.yaml", _question())
    tip = _commit(repo, "work")
    assert finish_guard(repo, "dev-x", base, tip) == [
        "docs/specs/x/envelopes/worker-01.yaml: unresolved problem: tests cannot start",
        "docs/specs/x/envelopes/question-01.yaml: unanswered question q1: Format",
        "docs/specs/x/envelopes/question-01.yaml: unanswered question q2: Scope",
    ]
    # Uncommitted envelopes neither block nor clear: the guard reads the tip.
    _write(unit, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "fixed"})  # fmt: skip
    assert len(finish_guard(repo, "dev-x", base, tip)) == 3
    answer = {"kind": "answer", "status": "completed", "answers_to": "question-01.yaml"}
    _write(unit, "answer-01.yaml", {**answer, "answers": [{"question": "q1", "decision": "a"}, {"question": "q2", "decision": "b"}]})  # fmt: skip
    tip = _commit(repo, "resolve and answer")
    assert finish_guard(repo, "dev-x", base, tip) == []
    _git(repo, "rm", "-q", "-r", "docs/specs/x")
    assert finish_guard(repo, "dev-x", base, _commit(repo, "drop the unit")) == []


def test_finish_merge_refuses_a_held_branch_through_the_installed_guard(tmp_path: Path) -> None:
    from click.testing import CliRunner
    from devkit.cli import cli
    from devkit.worktree import locate, start

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "README.md").write_text("x\n")
    head = _commit(repo, "base")
    worktree = start(locate(repo.resolve()), "dev-x").path
    unit = worktree / "docs/specs/x"
    _write(unit, "worker-01.yaml", _problem())
    _commit(worktree, "work")
    finish = ["worktree", "finish", "dev-x", "--merge", "-w", str(repo)]
    refused = CliRunner().invoke(cli, finish)
    assert refused.exit_code == 2 and "(WORKTREE_BLOCKED)" in refused.stderr
    assert "docs/specs/x/envelopes/worker-01.yaml: unresolved problem: tests cannot start" in refused.stderr
    assert _git(repo, "rev-parse", "HEAD") == head
    _write(unit, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "fixed"})  # fmt: skip
    _commit(worktree, "resolve")
    assert CliRunner().invoke(cli, finish).exit_code == 0
    assert (repo / "docs/specs/x/envelopes/resolution-01.yaml").is_file()
