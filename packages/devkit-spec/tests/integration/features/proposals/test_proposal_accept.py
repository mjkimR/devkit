"""``devkit spec proposal accept``: the one writer of an acceptance, also the direct acceptance of an eligible draft
(``ADR-direct-acceptance-command-and-handoff-guard``, ``ADR-eligibility-for-direct-acceptance``)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from click.testing import CliRunner, Result
from devkit_agt.features.workflow import Workspace, load_decisions, record_answer
from devkit_dist.cli import cli as devkit_cli
from spec_support.proposals import TODAY, write_workflow
from spec_support.scope import git, write

import devkit_spec
from devkit_spec.features.proposals import accept_proposal, create_proposal
from devkit_spec.features.proposals.usecases import accept as accept_module

PROPOSAL_DEFINITION = (
    Path(devkit_spec.__file__).parent / "bundles" / "spec" / "bundle" / "workflows" / "sdd-proposal.md"
).read_text(encoding="utf-8")
UNIT = "docs/proposals/PROP-{slug}"
SWEPT = """kind: feedback
stage: collect-feedback
workflow: sdd-proposal
segment: 0
created_at: '2026-10-13T00:00:00Z'
status: completed
summary: Swept the acceptance session; nothing observed.
findings: []
checks:
  swept: PASS recorded=0 duplicates=0
"""
NOTE = "direct acceptance, Planning skipped: the contract is settled; task_kind feature confirmed"


def _repo(tmp_path: Path, *, config: str = "") -> Path:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, ".devkit/config.toml", config)
    write_workflow(root, "sdd-proposal", PROPOSAL_DEFINITION)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "init")
    return root


def _draft(root: Path, slug: str = "small", *, intent: bool = True, swept: bool = True) -> Path:
    """A bound draft with its plan-intent recorded and its acceptance session swept; returns proposal.md."""
    created = create_proposal(root, slug, today=TODAY)
    assert created.workflow == "sdd-proposal"
    if intent:
        ws = Workspace(root, lint=None, ancestor=None)
        record_answer(ws, ws.resolve_unit(UNIT.format(slug=slug)), "gate:plan-intent", "accept", by="user", lint=False)
    if swept:
        write(root, f"{UNIT.format(slug=slug)}/envelopes/feedback-01.yaml", SWEPT)
    return root / created.path


def _edit(proposal: Path, old: str, new: str) -> None:
    text = proposal.read_text(encoding="utf-8")
    assert old in text
    proposal.write_text(text.replace(old, new, 1), encoding="utf-8")


def _accept(root: Path, slug: str, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["spec", "proposal", "accept", slug, "--by", "user", *args, "-w", str(root)])


def _error(result: Result) -> dict[str, Any]:
    """The JSON error with its advisory fields (``mode``, ``details``, ``target_files``) merged in."""
    assert result.exit_code == 2, result.output
    error = json.loads(result.stdout)["error"]
    return {**error, **error["advisory"], "details": error["advisory"].get("details", [])}


def _snapshot(root: Path, slug: str) -> dict[str, bytes]:
    unit = root / UNIT.format(slug=slug)
    return {path.relative_to(unit).as_posix(): path.read_bytes() for path in sorted(unit.rglob("*")) if path.is_file()}


def _plan_accepts(root: Path, slug: str) -> list[dict[str, object]]:
    decisions = load_decisions(root / UNIT.format(slug=slug)).records
    return [
        yaml.safe_load((root / UNIT.format(slug=slug) / record.file).read_text(encoding="utf-8"))
        for record in decisions
        if record.request == "gate:plan-accept"
    ]


def test_a_direct_acceptance_writes_the_status_and_records_the_gate(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)

    result = _accept(root, "small", "--direct", "--note", "the contract is settled")

    assert result.exit_code == 0, result.output
    [record] = _plan_accepts(root, "small")
    assert (record["action"], record["by"], record["note"], record["stage"]) == (
        "accept",
        "user",
        NOTE,
        "direction-handoff",
    )
    assert "status: accepted" in proposal.read_text(encoding="utf-8")
    unit = UNIT.format(slug="small")
    assert result.stdout == (
        f"[ACCEPTED: PROP-small form=direct path={unit}/proposal.md status=accepted"
        f" decision={unit}/decisions/02-gate-plan-accept.yaml]\n"
    )
    ws = Workspace(root, lint=None, ancestor=None)
    assert ws.evaluate_unit(ws.resolve_unit(unit), lint=False).complete


def test_every_failed_condition_is_listed_and_nothing_is_written(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root, intent=False)
    _edit(proposal, "status: draft", "status: draft\nneeds_decompose: true\nsupersedes: PROP-older")
    _edit(proposal, "task_kind: feature", "task_kind: chore")
    write(
        root,
        f"{UNIT.format(slug='small')}/envelopes/worker-01.yaml",
        "kind: worker\nstage: spike\nworkflow: sdd-proposal\nsegment: 0\ncreated_at: '2026-10-13T00:00:00Z'\n"
        "status: failed\nsummary: stopped\nfindings: []\nproblem:\n  cause: the tool broke\n  recovery: rerun\n",
    )
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "draft")
    git(root, "update-ref", "refs/remotes/origin/plan-small", "HEAD")  # fetched from a remote
    before = _snapshot(root, "small")

    error = _error(_accept(root, "small", "--direct", "--note", "settled", "--format", "json"))

    assert error["code"] == "SPEC_PROPOSAL_NOT_ELIGIBLE" and error["mode"] == "INTERACTION"
    details = error["details"]
    assert [line.split(":", 1)[0] for line in details] == ["blocking"] * 5 + ["pending"]
    for expected in ("needs_decompose", "supersedes: PROP-older", "origin/plan-small", "'chore'", "the tool broke"):
        assert any(expected in line for line in details), expected
    assert "gate:plan-intent" in details[-1]
    assert _snapshot(root, "small") == before


@pytest.mark.parametrize("place", ["linked", "detached", "dev-branch", "plan-branch", "not-origin-head"])
def test_a_direct_acceptance_runs_only_on_the_base_checkout(tmp_path: Path, place: str) -> None:
    root = _repo(tmp_path)
    _draft(root)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "draft")
    where = root
    if place == "linked":
        where = tmp_path / "linked"
        git(root, "worktree", "add", "-q", "-b", "elsewhere", str(where))
    elif place == "detached":
        git(root, "checkout", "-q", "--detach")
    elif place == "dev-branch":
        git(root, "checkout", "-q", "-b", "dev-small")
    elif place == "plan-branch":
        git(root, "checkout", "-q", "-b", "plan-other")
    else:
        git(root, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        git(root, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    before = _snapshot(where, "small")

    error = _error(_accept(where, "small", "--direct", "--note", "settled", "--format", "json"))

    assert error["code"] == "SPEC_PROPOSAL_NOT_ELIGIBLE"
    expected = {
        "linked": "linked worktree",
        "detached": "detached HEAD",
        "dev-branch": "activity branch dev-small",
        "plan-branch": "activity branch plan-other",
        "not-origin-head": "integration base trunk",
    }[place]
    assert any(expected in line for line in error["details"])
    assert _snapshot(where, "small") == before


def test_the_base_branch_is_the_origin_head_target(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    git(root, "checkout", "-q", "-b", "trunk")
    _draft(root)
    git(root, "update-ref", "refs/remotes/origin/trunk", "HEAD")
    git(root, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    assert _accept(root, "small", "--direct", "--note", "settled").exit_code == 0


def test_without_origin_head_the_main_worktrees_branch_is_the_base(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    git(root, "checkout", "-q", "-b", "hand-made")
    _draft(root)
    assert _accept(root, "small", "--direct", "--note", "settled").exit_code == 0


@pytest.mark.parametrize("hold", ["question", "malformed"])
def test_a_pending_question_or_a_malformed_worker_holds_it(tmp_path: Path, hold: str) -> None:
    root = _repo(tmp_path)
    _draft(root)
    head = (
        "kind: worker\nstage: intent-proposal\nworkflow: sdd-proposal\nsegment: 0\ncreated_at: '2026-10-13T00:00:00Z'\n"
    )
    body = (
        "status: needs_input\nsummary: asks\nfindings: []\nquestions:\n  - id: scope\n    title: Which scope?\n    prompt: Pick the scope.\n"
        if hold == "question"
        else "status: [broken\n"
    )
    write(root, f"{UNIT.format(slug='small')}/envelopes/worker-01.yaml", head + body)
    before = _snapshot(root, "small")
    error = _error(_accept(root, "small", "--direct", "--note", "settled", "--format", "json"))
    assert error["code"] == "SPEC_PROPOSAL_NOT_ELIGIBLE"
    expected = "unanswered question scope" if hold == "question" else "malformed worker envelope"
    assert any(line.startswith("blocking: envelope hold:") and expected in line for line in error["details"])
    assert _snapshot(root, "small") == before


def test_the_check_reports_a_pending_intent_and_writes_nothing(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root, intent=False)
    before = _snapshot(root, "small")

    result = _accept(root, "small", "--direct", "--check", "--note", "settled")

    assert result.exit_code == 0, result.output
    assert result.stdout == (
        "[ACCEPT_CHECK: PROP-small form=direct path=docs/proposals/PROP-small/proposal.md eligible=yes"
        " pending=gate:plan-intent]\n"
    )
    assert _snapshot(root, "small") == before
    _edit(proposal, "status: draft", "status: draft\nneeds_decompose: true")
    error = _error(_accept(root, "small", "--direct", "--check", "--note", "settled", "--format", "json"))
    assert error["code"] == "SPEC_PROPOSAL_NOT_ELIGIBLE"
    assert [line.split(":", 1)[0] for line in error["details"]] == ["blocking", "pending"]
    # The write itself still requires the intent recorded.
    _edit(proposal, "\nneeds_decompose: true", "")
    error = _error(_accept(root, "small", "--direct", "--note", "settled", "--format", "json"))
    assert error["code"] == "SPEC_PROPOSAL_NOT_ELIGIBLE" and _plan_accepts(root, "small") == []


def test_an_eligible_check_without_pending_conditions(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _draft(root)
    checked = accept_proposal(root, "small", by="user", note="settled", direct=True, check=True)
    assert (checked.form, checked.checked, checked.pending, checked.status) == ("direct", True, (), "draft")
    assert checked.to_dict()["decision"] is None


def test_a_refusal_of_the_workflow_restores_the_status(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root, swept=False)
    before = proposal.read_bytes()

    error = _error(_accept(root, "small", "--direct", "--note", "settled", "--format", "json"))

    assert error["code"] == "SPEC_PROPOSAL_GATE_NOT_OPEN"
    assert any("envelope-check-pass(feedback swept)" in line for line in error["details"])
    assert proposal.read_bytes() == before and _plan_accepts(root, "small") == []


def test_the_sweep_switched_off_by_policy_lets_the_gate_open(tmp_path: Path) -> None:
    root = _repo(tmp_path, config='[workflow.stages]\ncollect-feedback = "off"\n')
    _draft(root, swept=False)
    assert _accept(root, "small", "--direct", "--note", "settled").exit_code == 0
    assert len(_plan_accepts(root, "small")) == 1


def test_a_proposal_with_crlf_line_endings_is_accepted(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)
    proposal.write_bytes(proposal.read_bytes().replace(b"\n", b"\r\n"))
    before = proposal.read_bytes()
    accept_proposal(root, "small", by="user", note="settled", direct=True)
    assert proposal.read_bytes() == before.replace(b"status: draft", b"status: accepted", 1)


def test_any_failure_after_the_status_write_restores_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)
    before = proposal.read_bytes()

    def fail(*args: object, **kwargs: object) -> object:
        raise OSError("disk full")

    monkeypatch.setattr(accept_module, "record_answer", fail)
    with pytest.raises(OSError, match="disk full"):
        accept_proposal(root, "small", by="user", note="settled", direct=True)
    assert proposal.read_bytes() == before and _plan_accepts(root, "small") == []


def test_a_failure_while_collecting_the_reasons_still_restores(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root, swept=False)  # the gate does not open
    before = proposal.read_bytes()

    def fail(*args: object, **kwargs: object) -> list[str]:
        raise OSError("unit unreadable")

    monkeypatch.setattr(accept_module, "_not_open_details", fail)
    with pytest.raises(OSError, match="unit unreadable"):
        accept_proposal(root, "small", by="user", note="settled", direct=True)
    assert proposal.read_bytes() == before and _plan_accepts(root, "small") == []


def test_the_status_line_keeps_its_comment(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)
    before = proposal.read_text(encoding="utf-8")
    accept_proposal(root, "small", by="user", note="settled", direct=True)
    # Only the value changes: the scaffolded comment and every other line stay.
    assert proposal.read_text(encoding="utf-8") == before.replace("status: draft", "status: accepted", 1)


def test_the_planning_form_on_its_branch(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)
    _edit(proposal, "status: draft", "status: reviewing")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "review")
    git(root, "checkout", "-q", "-b", "elsewhere")
    error = _error(_accept(root, "small", "--note", "after review", "--format", "json"))
    assert error["code"] == "SPEC_PROPOSAL_WRONG_WORKTREE" and "status: reviewing" in proposal.read_text()

    git(root, "checkout", "-q", "-b", "plan-small")
    result = _accept(root, "small", "--note", "after review")

    assert result.exit_code == 0, result.output
    assert "form=planning" in result.stdout and "status: accepted" in proposal.read_text(encoding="utf-8")
    assert [record["note"] for record in _plan_accepts(root, "small")] == ["after review"]


@pytest.mark.parametrize("case", ["draft", "reviewing-direct", "rejected", "recorded", "single-file", "unbound"])
def test_forms_the_command_does_not_accept(tmp_path: Path, case: str) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)
    slug, args = "small", ["--direct", "--note", "settled"]
    if case == "draft":
        args = []
    elif case == "reviewing-direct":
        _edit(proposal, "status: draft", "status: reviewing")
    elif case == "rejected":
        _edit(proposal, "status: draft", "status: rejected")
    elif case == "recorded":
        accept_proposal(root, "small", by="user", note="settled", direct=True)
    elif case == "single-file":
        slug = "solo"
        write(root, "docs/proposals/PROP-solo.md", "---\nid: PROP-solo\nstatus: draft\n---\n\n# Solo\n")
    else:
        _edit(proposal, "workflow: sdd-proposal\n", "")
    before = _snapshot(root, "small")

    error = _error(_accept(root, slug, *args, "--format", "json"))

    assert error["code"] == "SPEC_PROPOSAL_ACCEPT_REFUSED"
    assert _snapshot(root, "small") == before


def test_a_direct_acceptance_without_its_record_is_repaired(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)
    _edit(proposal, "status: draft", "status: accepted")
    before = proposal.read_bytes()

    result = _accept(root, "small", "--direct", "--note", "settled")

    assert result.exit_code == 0, result.output
    assert "form=repair" in result.stdout and proposal.read_bytes() == before
    assert [record["note"] for record in _plan_accepts(root, "small")] == [
        NOTE.replace("the contract is settled", "settled")
    ]


def test_a_planning_acceptance_without_its_record_is_not_repaired(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root)
    _edit(proposal, "status: draft", "status: accepted")
    write(
        root,
        f"{UNIT.format(slug='small')}/envelopes/worker-01.yaml",
        "kind: worker\nstage: direction-handoff\nworkflow: sdd-proposal\nsegment: 0\n"
        "created_at: '2026-10-13T00:00:00Z'\nstatus: completed\nsummary: Planning done\nfindings: []\n",
    )
    error = _error(_accept(root, "small", "--direct", "--note", "settled", "--format", "json"))
    assert error["code"] == "SPEC_PROPOSAL_NOT_ELIGIBLE"
    assert any("worker envelope" in line for line in error["details"])
    assert _plan_accepts(root, "small") == []


def test_arguments_are_refused_before_the_proposal_is_read(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _draft(root)
    before = _snapshot(root, "small")
    policy = CliRunner().invoke(
        devkit_cli,
        ["spec", "proposal", "accept", "small", "--by", "policy", "--direct", "--note", "x", "-w", str(root)],
    )
    assert policy.exit_code == 2 and "--by" in policy.output
    error = _error(_accept(root, "small", "--direct", "--note", "  ", "--format", "json"))
    assert error["code"] == "ARGUMENT_INVALID" and error["target_files"] == ["--note"]
    error = _error(_accept(root, "missing", "--direct", "--note", "  ", "--format", "json"))
    assert error["code"] == "ARGUMENT_INVALID"  # before the proposal is looked up
    assert _snapshot(root, "small") == before


@pytest.mark.parametrize("intent", ["ask", "auto"])
def test_policy_direct_acceptance_records_authority_and_status(tmp_path: Path, intent: str) -> None:
    root = _repo(tmp_path, config=f'[workflow.approvals]\nplan-accept = "auto"\nplan-intent = "{intent}"\n')
    proposal = _draft(root, intent=intent == "ask")
    result = CliRunner().invoke(
        devkit_cli,
        ["spec", "proposal", "accept", "small", "--by", "policy", "--direct", "--note", "settled", "-w", str(root)],
    )
    assert result.exit_code == 0, result.output
    [record] = _plan_accepts(root, "small")
    assert (record["action"], record["by"], record["stage"]) == ("accept", "policy", "direction-handoff")
    assert "status: accepted" in proposal.read_text()
    workspace = Workspace(root, lint=None, ancestor=None)
    assert workspace.evaluate_unit(workspace.resolve_unit(UNIT.format(slug="small")), lint=False).complete


def test_policy_cannot_accept_when_owning_policy_requires_user(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _draft(root)
    before = _snapshot(root, "small")
    result = CliRunner().invoke(
        devkit_cli,
        ["spec", "proposal", "accept", "small", "--by", "policy", "--direct", "--note", "settled", "-w", str(root)],
    )
    assert result.exit_code == 2
    assert "ARGUMENT_INVALID" in result.stderr
    assert _snapshot(root, "small") == before
    assert not _plan_accepts(root, "small")
