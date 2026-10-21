"""Worker (questions, problem), answer and resolution envelopes, and the hold they put on gates and integration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml
from devkit.workflow.errors import AuthoringError
from devkit.workflow.integration import finish_guard
from devkit.workflow.unit.envelope import compose_envelope, load_envelopes
from devkit_core.base.errors import GitError
from testsupport.workflow import SIMPLE_UNIT, run_cli, write_config

GATED = """---
id: w
schema_version: 1
stages:
  - id: review
    exit: [anchor-exists]
  - id: accept
    human_gate: accept
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
        "kind": "worker",
        "stage": "build",
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
        "stage": "build",
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
        ("worker-02.yaml", _question(status="completed"), "status needs_input"),
        ("worker-02.yaml", _question(status="failed", problem={"cause": "x", "recovery": "y"}), "status needs_input"),
        ("question-01.yaml", _question(kind="question"), "only a worker envelope carries questions"),
        (
            "worker-02.yaml",
            {**_question(), "problem": {"cause": "x", "recovery": "y"}},
            None,
        ),
        (
            "worker-02.yaml",
            {
                "kind": "worker",
                "status": "needs_input",
                "questions": [{"id": "q1", "title": "x" * 41, "prompt": "p"}],
            },
            "at most 40",
        ),
        (
            "worker-02.yaml",
            {
                "kind": "worker",
                "status": "needs_input",
                "questions": [{"id": "q1", "title": "t", "prompt": "p", "allow_note": False}],
            },
            "must allow a note",
        ),
        (
            "worker-02.yaml",
            {
                "kind": "worker",
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
            "only a worker envelope carries questions",
        ),
        ("answer-01.yaml", {"kind": "answer", "status": "completed", "answers": []}, "answers_to"),
        ("worker-01.yaml", {"kind": "worker", "stage": "build", "status": "failed"}, "needs a problem"),
        (
            "worker-01.yaml",
            {"kind": "worker", "stage": "build", "status": "needs_input"},
            "asks questions or reports a problem",
        ),
        ("review-01.yaml", _problem(kind="review"), "only a worker envelope carries a problem"),
        ("worker-01.yaml", _problem(status="completed"), "completed envelope reports no problem"),
        ("worker-01.yaml", _problem(problem={"cause": "x"}), "missing required key recovery"),
        (
            "worker-01.yaml",
            {"kind": "worker", "stage": "build", "status": "completed", "activity_effort": "max"},
            "activity_effort",
        ),
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
    _write(tmp_path, "worker-02.yaml", _question())
    _write(tmp_path, "worker-01.yaml", {"kind": "worker", "stage": "build", "status": "completed"})
    answer = {"kind": "answer", "status": "completed", "answers_to": "worker-02.yaml"}
    _write(tmp_path, "answer-01.yaml", {**answer, "answers": [{"question": "q9", "decision": "d"}]})
    _write(tmp_path, "answer-02.yaml", {**answer, "answers": [{"question": "q1", "choice": "z", "decision": "d"}]})
    _write(tmp_path, "answer-03.yaml", {**answer, "answers_to": "worker-07.yaml", "answers": [{"question": "q1", "decision": "d"}]})  # fmt: skip
    _write(tmp_path, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "s"})  # fmt: skip
    _write(tmp_path, "answer-04.yaml", {**answer, "answers_to": "worker-01.yaml", "answers": [{"question": "q1", "decision": "d"}]})  # fmt: skip
    envelopes = load_envelopes(tmp_path)
    reasons = {e.file: e.message for e in envelopes.errors}
    assert "not a question of worker-02.yaml" in reasons["envelopes/answer-01.yaml"]
    assert "'z' is not an option" in reasons["envelopes/answer-02.yaml"]
    assert "no well-formed worker envelope with questions" in reasons["envelopes/answer-03.yaml"]
    assert "no well-formed worker envelope with questions" in reasons["envelopes/answer-04.yaml"]
    assert "no well-formed worker envelope with a problem" in reasons["envelopes/resolution-01.yaml"]
    assert "answer" not in envelopes.by_kind and "resolution" not in envelopes.by_kind
    # Answers that answer nothing leave every question pending.
    assert [q.id for _, q in envelopes.hold().questions] == ["q1", "q2"]


def test_a_problem_holds_until_a_resolution_names_it(tmp_path: Path) -> None:
    _write(tmp_path, "worker-01.yaml", _problem())
    _write(
        tmp_path,
        "worker-02.yaml",
        {"kind": "worker", "stage": "build", "status": "completed", "summary": "later run went fine"},
    )
    hold = load_envelopes(tmp_path).hold()
    assert hold.blocked and [e.file for e in hold.problems] == ["envelopes/worker-01.yaml"]
    assert hold.reasons("unit/") == ["unit/envelopes/worker-01.yaml: unresolved problem: tests cannot start"]
    _write(tmp_path, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "fixed"})  # fmt: skip
    assert not load_envelopes(tmp_path).hold()


def test_waiting_for_answers_is_not_a_problem(tmp_path: Path) -> None:
    _write(tmp_path, "worker-02.yaml", _question())
    hold = load_envelopes(tmp_path).hold()
    assert not hold.blocked and [q.id for _, q in hold.questions] == ["q1", "q2"]
    answer = {"kind": "answer", "status": "completed", "answers_to": "worker-02.yaml"}
    _write(tmp_path, "answer-01.yaml", {**answer, "answers": [{"question": "q1", "choice": "a", "decision": "Keep TOML."}]})  # fmt: skip
    assert [q.id for _, q in load_envelopes(tmp_path).hold().questions] == ["q2"]
    # Answers may be spread over several envelopes; a note-only answer has no choice.
    _write(tmp_path, "answer-02.yaml", {**answer, "answers": [{"question": "q2", "choice": None, "decision": "Only keys."}]})  # fmt: skip
    assert not load_envelopes(tmp_path).hold()


# -- authoring ---------------------------------------------------------------------------------------------------------


def _new(root: Path, kind: str, *args: str, stdin: str | None = None) -> dict[str, object]:
    from click.testing import CliRunner
    from devkit.workflow.cli import cli

    result = CliRunner().invoke(
        cli, ["envelope", kind, "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json", *args], input=stdin
    )
    return json.loads(result.stdout) if result.exit_code == 0 else {"exit": result.exit_code, "err": result.stdout}


def test_authoring_question_answer_problem_and_resolution(root: Path) -> None:
    unit = root / SIMPLE_UNIT
    asked = _new(root, "worker", "--stage", "review", "--summary", "two questions", "--questions-file", "-", stdin=QUESTIONS)  # fmt: skip
    assert asked["status"] == "needs_input" and asked["file"] == f"{SIMPLE_UNIT}/envelopes/worker-01.yaml"
    data = yaml.safe_load((unit / "envelopes/worker-01.yaml").read_text())
    assert data["questions"][0]["options"][0] == {"id": "a", "description": "Keep TOML", "recommended": True}
    (root / "answers.yaml").write_text(
        "- { question: q1, choice: a, decision: Keep TOML and tidy key names., constraints: [warn one release] }\n"
        "- { question: q2, choice: null, decision: Migrate keys only. }\n"
    )
    answered = _new(root, "answer", "--stage", "review", "--summary", "q1 and q2 decided", "--answers-to", "envelopes/worker-01.yaml", "--answers-file", str(root / "answers.yaml"), "--effort", "low")  # fmt: skip
    assert answered["status"] == "completed"
    data = yaml.safe_load((unit / "envelopes/answer-01.yaml").read_text())
    assert data["answers_to"] == "worker-01.yaml" and data["activity_effort"] == "low"
    assert data["answers"][0]["constraints"] == ["warn one release"]
    failed = _new(root, "worker", "--stage", "review", "--summary", "stopped", "--problem", "fixture broken", "--tried", "rerun", "--recovery", "repair the fixture")  # fmt: skip
    assert failed["status"] == "failed"
    assert load_envelopes(unit).hold().blocked
    resolved = _new(root, "resolution", "--summary", "fixture repaired; tests pass", "--resolves", "worker-02.yaml")  # fmt: skip
    assert resolved["status"] == "completed"
    assert not load_envelopes(unit).hold()


@pytest.mark.parametrize(
    ("args", "code"),
    [
        (
            ("--kind", "worker", "--status", "completed", "--summary", "x", "--questions-file", "-"),
            "ENVELOPE_FLAG_INVALID",
        ),
        (("--kind", "question", "--summary", "x", "--questions-file", "-"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "review", "--summary", "x", "--questions-file", "-"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "worker", "--status", "failed", "--summary", "x"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "worker", "--summary", "x", "--recovery", "y"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "worker", "--summary", "x", "--effort", "max"), "ENVELOPE_FLAG_INVALID"),
        (("--kind", "worker", "--summary", "x"), "ENVELOPE_FLAG_INVALID"),  # a worker envelope names its stage
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
    out = _new(root, "worker", "--stage", "review", "--summary", "x", "--questions-file", "-", stdin="- { id: Q, title: t, prompt: p }\n")  # fmt: skip
    assert out["exit"] == 2 and "ENVELOPE_ITEMS_INVALID" in str(out["err"])
    _new(root, "worker", "--stage", "review", "--summary", "x", "--questions-file", "-", stdin=QUESTIONS)
    out = _new(root, "answer", "--summary", "x", "--answers-to", "worker-01.yaml", "--answers-file", "-", stdin="- { question: q1, choice: c, decision: d }\n")  # fmt: skip
    assert out["exit"] == 2 and "ENVELOPE_REFERENCE_INVALID" in str(out["err"])


# -- evaluation, requests and answers -----------------------------------------------------------------------------------


def _next(root: Path, *args: str) -> dict[str, object]:
    return json.loads(run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint", "--format", "json", *args).stdout)  # fmt: skip


def test_questions_are_choose_requests_answered_by_an_envelope(root: Path) -> None:
    _new(root, "worker", "--stage", "review", "--summary", "x", "--questions-file", "-", stdin=QUESTIONS)
    result = _next(root)
    requests = {r["id"]: r for r in result["requests"]}  # type: ignore[union-attr]
    q1 = requests["question:worker-01.q1"]
    assert (q1["kind"], q1["answer"], q1["context"]) == ("choose", "envelope", "proposal.md section 3")
    assert q1["target"] == {"type": "question", "name": "worker-01.yaml#q1", "stage": "review"}
    assert [o["id"] for o in q1["options"] if o["recommended"]] == ["a"]
    assert result["waiting"] == {"class": "human", "checks": ["question:worker-01.q1", "question:worker-01.q2"]}
    text = run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint").stdout
    assert '[PENDING_QUESTION: envelopes/worker-01.yaml id=q1 title="Storage format"]' in text
    assert (
        '[REQUEST: id=question:worker-01.q1 kind=choose title="Storage format" target=question:worker-01.yaml#q1'
        ' stage=review options=a,b recommended=a note=allowed answer=envelope context="proposal.md section 3"]' in text
    )
    refused = run_cli("answer", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint", "--request", "question:worker-01.q1", "--action", "accept", "--value", "a")  # fmt: skip
    assert refused.exit_code == 2 and "DECISION_INVALID" in refused.stderr and "envelope answer" in refused.stderr


@pytest.mark.parametrize("policy", ["ask", "auto"])
def test_a_hold_keeps_every_gate_from_passing(root: Path, policy: str) -> None:
    write_config(root, f'[workflow]\ndefault = "w"\n[workflow.approvals]\naccept = "{policy}"\n')
    unit = root / SIMPLE_UNIT
    _write(unit, "worker-01.yaml", _problem(stage="review"))
    for given in ((), ("--given", "accept")):
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
        assert [r["id"] for r in result["requests"]] == ["gate:accept"]  # type: ignore[union-attr]


def test_envelope_check_reports_the_hold(root: Path) -> None:
    unit = root / SIMPLE_UNIT
    _write(unit, "worker-01.yaml", _problem())
    _write(unit, "worker-02.yaml", _question())
    text = run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert text.exit_code == 0
    assert (
        "[ENVELOPE: envelopes/worker-01.yaml kind=worker seq=01 status=failed open_findings=0 problem=yes]"
        in text.stdout
    )
    assert "[BLOCKED: envelopes/worker-01.yaml" in text.stdout and "[PENDING_QUESTION: envelopes/worker-02.yaml id=q2" in text.stdout  # fmt: skip
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
    _write(unit, "worker-02.yaml", _question())
    tip = _commit(repo, "work")
    assert finish_guard(repo, "dev-x", base, tip) == [
        "docs/specs/x/envelopes/worker-01.yaml: unresolved problem: tests cannot start",
        "docs/specs/x/envelopes/worker-02.yaml: unanswered question q1: Format",
        "docs/specs/x/envelopes/worker-02.yaml: unanswered question q2: Scope",
    ]
    # Uncommitted envelopes neither block nor clear: the guard reads the tip.
    _write(unit, "resolution-01.yaml", {"kind": "resolution", "status": "completed", "resolves": "worker-01.yaml", "summary": "fixed"})  # fmt: skip
    assert len(finish_guard(repo, "dev-x", base, tip)) == 3
    answer = {"kind": "answer", "status": "completed", "answers_to": "worker-02.yaml"}
    _write(unit, "answer-01.yaml", {**answer, "answers": [{"question": "q1", "decision": "a"}, {"question": "q2", "decision": "b"}]})  # fmt: skip
    tip = _commit(repo, "resolve and answer")
    assert finish_guard(repo, "dev-x", base, tip) == []
    # Deleting a problem envelope does not clear it: a deleted file of a kept unit is read at the merge base.
    _git(repo, "switch", "-q", "main")
    _write(repo / "docs/specs/y", "worker-01.yaml", _problem())
    (repo / "docs/specs/y/spec.md").write_text("y\n")
    held_base = _commit(repo, "a held unit on the base")
    _git(repo, "switch", "-q", "-c", "dev-y")
    _git(repo, "rm", "-q", "docs/specs/y/envelopes/worker-01.yaml")
    assert finish_guard(repo, "dev-y", held_base, _commit(repo, "delete the problem")) == [
        "docs/specs/y/envelopes/worker-01.yaml: unresolved problem: tests cannot start"
    ]
    _git(repo, "rm", "-q", "-r", "docs/specs/y")
    assert finish_guard(repo, "dev-y", held_base, _commit(repo, "drop the unit")) == []
    # A malformed worker envelope holds: whether it reports a problem cannot be known.
    _write(
        repo / "docs/specs/z",
        "worker-01.yaml",
        {**_problem(), "problem": {"cause": "x", "recovery": "y", "severity": 1}},
    )
    malformed = finish_guard(repo, "dev-y", held_base, _commit(repo, "malformed"))
    assert len(malformed) == 1 and "docs/specs/z/envelopes/worker-01.yaml: malformed worker envelope" in malformed[0]
    # Git failures propagate (the guard runner refuses the merge): fail closed.
    with pytest.raises(GitError):
        finish_guard(repo, "dev-y", held_base, "0" * 40)


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


STAGED = """---
id: w
schema_version: 1
stages:
  - id: intent
    human_gate: intent
    exit: [anchor-exists]
  - id: build
    exit: [anchor-exists]
  - id: integrate
    human_gate: integration
    exit: [anchor-exists]
next:
  - { workflow: v }
---
"""


@pytest.fixture
def staged(tmp_path: Path) -> Path:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "w.md").write_text(STAGED)
    (defs / "v.md").write_text("---\nid: v\nschema_version: 1\nstages:\n  - id: s\n    exit: [anchor-exists]\n---\n")
    write_config(tmp_path, '[workflow]\ndefault = "w"\n[workflow.approvals]\nintent = "auto"\nhandoff = "auto"\n')
    assert run_cli("new", "-w", str(tmp_path), "u").exit_code == 0
    return tmp_path


def test_a_hold_keeps_the_gates_passed_before_it(staged: Path) -> None:
    unit = staged / SIMPLE_UNIT
    _write(unit, "worker-01.yaml", _problem(stage="build", workflow="w"))
    result = _next(staged)
    # intent passed before the problem was raised in build: the unit stays at integrate, not back at intent.
    assert result["done"] == ["intent", "build"] and result["stage"]["id"] == "integrate"  # type: ignore[index]
    assert result["gate"]["held"] is True  # type: ignore[index]
    # A problem without a stage of this workflow holds every gate.
    _write(unit, "worker-02.yaml", _problem(stage="elsewhere", workflow="w"))
    assert _next(staged)["stage"]["id"] == "intent"  # type: ignore[index]


def test_a_malformed_worker_envelope_holds_from_the_stage_it_states(staged: Path) -> None:
    unit = staged / SIMPLE_UNIT
    broken = {"cause": "x", "recovery": "y", "severity": 1}
    _write(unit, "worker-01.yaml", {**_problem(stage="build", workflow="w"), "problem": broken})
    result = _next(staged)
    assert result["done"] == ["intent", "build"] and result["stage"]["id"] == "integrate"  # type: ignore[index]
    assert result["blocked"] is True and result["gate"]["held"] is True  # type: ignore[index]
    assert result["malformed_workers"][0]["file"] == "envelopes/worker-01.yaml"  # type: ignore[index]
    text = run_cli("next", "-w", str(staged), "--unit", SIMPLE_UNIT, "--no-lint").stdout
    assert "[BLOCKED: envelopes/worker-01.yaml malformed=yes reason=" in text
    assert result["unmet"][0]["detail"] == "blocked by envelopes/worker-01.yaml"  # type: ignore[index]
    # Without a stage it states, or as YAML that is no mapping, it holds every gate.
    (unit / "envelopes/worker-01.yaml").write_text("- not a mapping\n")
    assert _next(staged)["stage"]["id"] == "intent"  # type: ignore[index]
    _write(unit, "worker-01.yaml", {"kind": "worker", "status": "completed", "summary": "no stage"})
    result = _next(staged)
    assert result["stage"]["id"] == "intent" and "names the stage" in result["malformed_workers"][0]["reason"]  # type: ignore[index]


def test_a_hold_keeps_the_handoff(staged: Path) -> None:
    write_config(staged, '[workflow]\ndefault = "w"\n[workflow.approvals]\nintent = "auto"\nintegration = "auto"\n')
    unit = staged / SIMPLE_UNIT
    assert _next(staged)["requests"][0]["id"] == "handoff"  # type: ignore[index]
    _write(unit, "worker-01.yaml", _question(stage="integrate", workflow="w"))
    result = _next(staged)
    assert result["complete"] is False  # the integrate gate is held by the question
    _write(unit, "answer-01.yaml", {"kind": "answer", "status": "completed", "answers_to": "worker-01.yaml", "answers": [{"question": "q1", "decision": "a"}]})  # fmt: skip
    result = _next(staged)
    assert result["complete"] is False and [r["id"] for r in result["requests"]] == ["question:worker-01.q2"]  # type: ignore[union-attr]
    refused = run_cli("handoff", "-w", str(staged), "--unit", SIMPLE_UNIT, "--no-lint")
    assert refused.exit_code != 0


def test_handoff_refuses_a_held_complete_unit(staged: Path) -> None:
    write_config(
        staged,
        '[workflow]\ndefault = "w"\n[workflow.approvals]\nintent = "auto"\nintegration = "auto"\nhandoff = "auto"\n',
    )
    unit = staged / SIMPLE_UNIT
    _write(unit, "worker-01.yaml", _problem())  # gates turned off are skipped; the handoff is still held
    write_config(
        staged,
        '[workflow]\ndefault = "w"\n[workflow.approvals]\nintent = "off"\nintegration = "off"\nhandoff = "auto"\n',
    )
    result = _next(staged)
    assert result["complete"] is True and result["requests"] == [] and result["blocked"] is True
    refused = run_cli("handoff", "-w", str(staged), "--unit", SIMPLE_UNIT, "--no-lint")
    assert refused.exit_code == 1 and "(HANDOFF_HELD)" in refused.stderr


# -- gate policies a definition narrows, and frontmatter alternatives -------------------------------------------------

NARROWED = """---
id: w
schema_version: 1
gates:
  accept: { policies: [ask] }
  integration: { answer: given, policies: [ask, auto] }
stages:
  - id: accept
    human_gate: accept
    exit: [frontmatter(task.md status planned|reviewing)]
  - id: integrate
    human_gate: integration
    exit: [anchor-exists]
---
"""


@pytest.fixture
def narrowed(tmp_path: Path) -> Path:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "w.md").write_text(NARROWED)
    write_config(tmp_path, '[workflow]\ndefault = "w"\n')
    assert run_cli("new", "-w", str(tmp_path), "u").exit_code == 0
    return tmp_path


@pytest.mark.parametrize(
    ("approvals", "ok"),
    [
        ("", True),
        ('accept = "ask"\n', True),
        ('accept = "auto"\n', False),
        ('integration = "auto"\n', True),
        ('integration = "off"\n', False),
    ],
)
def test_a_definition_narrows_the_policies_of_its_gates(narrowed: Path, approvals: str, ok: bool) -> None:
    write_config(narrowed, f'[workflow]\ndefault = "w"\n[workflow.approvals]\n{approvals}')
    result = run_cli("next", "-w", str(narrowed), "--unit", SIMPLE_UNIT, "--no-lint")
    if ok:
        assert result.exit_code == 0, result.stderr
        return
    assert result.exit_code == 2 and "(WORKFLOW_GATE_POLICY)" in result.stderr
    for command in (("requests",), ("answer", "--request", "gate:accept", "--action", "accept")):
        refused = run_cli(*command, "-w", str(narrowed), "--unit", SIMPLE_UNIT, "--no-lint")
        assert refused.exit_code == 2 and "WORKFLOW_GATE_POLICY" in refused.stderr


def test_narrowed_policies_show_and_frontmatter_takes_alternatives(narrowed: Path) -> None:
    shown = run_cli("show", "-w", str(narrowed), "w").stdout
    assert "[GATE: accept policy=ask policies=ask]" in shown
    assert "[GATE: integration policy=ask answer=given policies=ask,auto]" in shown
    result = _next(narrowed)
    assert result["stage"]["id"] == "accept" and result["unmet"][0]["name"] == "gate:accept"  # type: ignore[index]
    anchor = narrowed / SIMPLE_UNIT / "task.md"
    anchor.write_text(anchor.read_text().replace("status: planned", "status: rejected"))
    assert _next(narrowed)["unmet"][0]["detail"] == "status=rejected"  # type: ignore[index]


@pytest.mark.parametrize(
    ("gates", "reason"),
    [
        ("accept: { policies: [] }", "non-empty list"),
        ("accept: { policies: [auto] }", "must include ask"),
        ("accept: { policies: [ask, ask] }", "distinct"),
        ("accept: { policies: [ask, maybe] }", "distinct values of"),
        ("accept: { policy: [ask] }", "unknown keys"),
    ],
)
def test_malformed_gate_policies_are_definition_errors(tmp_path: Path, gates: str, reason: str) -> None:
    from devkit.workflow import DefinitionError, parse_definition

    text = f"---\nid: w\nschema_version: 1\ngates:\n  {gates}\nstages:\n  - id: a\n    human_gate: accept\n    exit: [anchor-exists]\n---\n"
    with pytest.raises(DefinitionError, match=reason):
        parse_definition(text)


def test_passed_gates_report_what_passed_them(staged: Path) -> None:
    result = _next(staged)  # intent = auto in the fixture
    assert result["passed_gates"] == [
        {"stage": "intent", "name": "intent", "policy": "auto", "satisfied": True, "source": "policy",
         "decision": None, "held": False}
    ]  # fmt: skip
    text = run_cli("next", "-w", str(staged), "--unit", SIMPLE_UNIT, "--no-lint", "--given", "integration").stdout
    assert "[GATE_PASSED: intent stage=intent policy=auto source=policy]" in text
    assert "[GATE_PASSED: integration stage=integrate policy=ask source=given]" in text


def test_a_worker_problem_lists_its_findings(root: Path) -> None:
    out = _new(root, "worker", "--stage", "review", "--summary", "range refused", "--problem", "boundary broken", "--recovery", "revert a.py", "--findings-file", "-", stdin="- { issue: a.py outside scope, evidence: a.py }\n")  # fmt: skip
    assert out["status"] == "failed" and out["open_findings"] == 1
    data = yaml.safe_load((root / SIMPLE_UNIT / "envelopes/worker-01.yaml").read_text())
    assert data["findings"][0]["issue"] == "a.py outside scope" and data["problem"]["cause"] == "boundary broken"


def test_a_worker_envelope_without_stage_is_refused_with_the_flag_to_add(root: Path) -> None:
    refused = run_cli("envelope", "worker", "-w", str(root), "--unit", SIMPLE_UNIT, "--summary", "x")
    assert refused.exit_code == 2 and "Missing option '--stage'" in refused.stderr
    loaded = load_envelopes(root / SIMPLE_UNIT)
    with pytest.raises(AuthoringError, match="names the stage") as caught:
        compose_envelope(unit_dir=root / SIMPLE_UNIT, envelopes=loaded, kind="worker", summary="x", effort="medium")
    assert "Pass --stage" in (caught.value.fix or "")
