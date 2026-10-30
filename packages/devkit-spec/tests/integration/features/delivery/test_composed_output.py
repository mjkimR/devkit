"""The composed ``proposal accept --mode`` and ``proposal handoff --effort`` print their outcome by the agent-output
contract (``ARCH-08-1-agent-output``): the status decides the exit code before ``--strict``, a stopped outcome never
prints the success kind, errors come last with every advisory field, and the next step reaches text output too."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode
from devkit_dist.cli import cli as devkit_cli

from devkit_spec.base.errors import HandoffStaleError
from devkit_spec.features.delivery.usecases import native_handoff, native_plan_accept

WARNING = {
    "code": "WORKTREE_SETUP_SLOW",
    "level": "WARNING",
    "message": "setup took long",
    "exit_code": 0,
    "advisory": {"code": "WORKTREE_SETUP_SLOW", "level": "WARNING", "mode": "CONTINUE"},
}


def _stale() -> dict[str, Any]:
    error = HandoffStaleError("the new worktree no longer contains the reviewed base commit", "moved", retry_after="1m")
    return error.to_dict()


def _handoff(monkeypatch: pytest.MonkeyPatch, result: dict[str, Any]) -> None:
    monkeypatch.setattr(native_handoff.HandoffUseCase, "execute", lambda self, slug, effort: result)


def _accept(monkeypatch: pytest.MonkeyPatch, result: dict[str, Any]) -> None:
    monkeypatch.setattr(native_plan_accept.PlanAcceptUseCase, "execute", lambda self, slug, **kwargs: result)


def _run(tmp_path: Path, *args: str):
    return CliRunner().invoke(devkit_cli, ["spec", "proposal", *args, "-w", str(tmp_path)])


def test_a_completed_handoff_prints_its_next_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _handoff(
        monkeypatch,
        {
            "status": "handed_off",
            "worktree": {"path": "/abs/dev-idea", "created": True},
            "handoff": {"spec": "SPEC-idea", "dir": "specs/x", "errors": [], "notices": []},
            "next_command": "uv run devkit workflow next --unit specs/x",
            "authority": "host-conversation",
            "commit": "a" * 40,
            "errors": [],
            "notices": [WARNING],
        },
    )
    result = _run(tmp_path, "handoff", "idea", "--effort", "low")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[HANDOFF: PROP-idea status=handed_off spec=SPEC-idea dir=specs/x worktree=dev-idea effort=low"
        f" authority=host-conversation commit={'a' * 40}]",
        "[NEXT_CMD: uv run devkit workflow next --unit specs/x]",
    ]
    strict = CliRunner().invoke(
        devkit_cli, ["spec", "proposal", "handoff", "--strict", "idea", "--effort", "low", "-w", str(tmp_path)]
    )
    assert strict.exit_code == 1  # the warning under --strict


def test_a_stopped_handoff_prints_its_own_kind_and_errors_last(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stale = _stale()
    _handoff(
        monkeypatch,
        {
            "status": "needs_recovery",
            "worktree": {"path": "/abs/dev-idea", "created": True},
            "errors": [stale],
            "notices": [WARNING],
            "authority": "host-conversation",
        },
    )
    result = CliRunner().invoke(
        devkit_cli, ["spec", "proposal", "handoff", "--strict", "idea", "--effort", "low", "-w", str(tmp_path)]
    )
    assert result.exit_code == 1, result.output
    assert result.stdout.startswith("[HANDOFF_STOPPED: PROP-idea status=needs_recovery")
    assert "[HANDOFF: " not in result.stdout
    assert result.stderr.index("[WARN]") < result.stderr.index("[ERROR]")
    assert "[DETAIL] moved" in result.stderr and "[WHEN]   Not before: 1m" in result.stderr


def test_a_blocked_acceptance_that_did_nothing_is_the_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stale = _stale()
    _accept(monkeypatch, {"status": "blocked", "completed_steps": [], "errors": [stale], "notices": [WARNING]})
    # --strict never turns the failure (2) into a warning exit (1).
    text = _run(tmp_path, "accept", "--strict", "idea", "--by", "user", "--mode", "accept_only")
    assert text.exit_code == 2, text.output
    assert text.stdout == "" and "SPEC_HANDOFF_STALE" in text.stderr
    data = _run(tmp_path, "accept", "idea", "--by", "user", "--mode", "accept_only", "--format", "json")
    assert data.exit_code == 2
    document = json.loads(data.stdout)
    assert document["error"]["code"] == "SPEC_HANDOFF_STALE"
    assert [notice["code"] for notice in document["notices"]] == ["WORKTREE_SETUP_SLOW"]


def test_a_stopped_acceptance_reads_the_handoff_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stale = _stale()
    _accept(
        monkeypatch,
        {
            "status": "needs_recovery",
            "completed_steps": ["acceptance_commit", "merge"],
            "errors": [],
            "handoff": {"errors": [stale], "notices": []},
            "acceptance_authority": "user",
            "next_action": "Inspect preserved handoff effects",
        },
    )
    result = _run(tmp_path, "accept", "idea", "--by", "user", "--mode", "accept_and_handoff", "--effort", "low")
    assert result.exit_code == 1, result.output
    assert result.stdout.splitlines() == [
        "[ACCEPTED_STOPPED: PROP-idea status=needs_recovery mode=accept_and_handoff authority=user"
        " completed=acceptance_commit,merge commit=-]",
        '[NEXT_ACTION: "Inspect preserved handoff effects"]',
    ]
    assert "SPEC_HANDOFF_STALE" in result.stderr


def test_a_refusal_renders_every_error_and_always_exits_2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_spec.base.errors import ProposalInPlanningError

    first = ProposalInPlanningError("first", exit_code=ExitCode.FINDINGS).to_dict()  # its own exit code is 1
    second = _stale()
    _accept(monkeypatch, {"status": "blocked", "completed_steps": [], "errors": [first, second]})
    text = _run(tmp_path, "accept", "idea", "--by", "user", "--mode", "accept_only")
    assert text.exit_code == 2 and text.stdout == ""
    assert text.stderr.index("(SPEC_PROPOSAL_IN_PLANNING)") < text.stderr.index("(SPEC_HANDOFF_STALE)")
    data = _run(tmp_path, "accept", "idea", "--by", "user", "--mode", "accept_only", "--format", "json")
    assert data.exit_code == 2
    document = json.loads(data.stdout)
    assert document["error"]["code"] == "SPEC_HANDOFF_STALE"
    assert [error["code"] for error in document["errors"]] == ["SPEC_PROPOSAL_IN_PLANNING"]


# SPEC-git-operator-result-readiness AC-02
def test_a_refused_handoff_commit_names_its_next_action_not_the_nested_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from devkit_spec.base.errors import HandoffCommitRefusedError

    refused = HandoffCommitRefusedError("refused", "hook output", target_files=["specs/x/spec.md"], fix="Commit there")
    _handoff(
        monkeypatch,
        {
            "status": "needs_recovery",
            "worktree": {"path": "/abs/dev-idea", "created": True},
            # The plain handoff's own next command stays in its nested result; the stopped outcome must not print it.
            "handoff": {"spec": "SPEC-idea", "dir": "specs/x", "next_command": "uv run devkit workflow next --unit x"},
            "commit": None,
            "next_action": "Commit there",
            "authority": "host-conversation",
            "errors": [refused.to_dict()],
            "notices": [],
        },
    )
    result = _run(tmp_path, "handoff", "idea", "--effort", "low")
    assert result.exit_code == 1, result.output
    assert result.stdout.splitlines() == [
        "[HANDOFF_STOPPED: PROP-idea status=needs_recovery spec=SPEC-idea dir=specs/x worktree=dev-idea effort=low"
        " authority=host-conversation commit=-]",
        '[NEXT_ACTION: "Commit there"]',
    ]
    assert "(SPEC_HANDOFF_COMMIT_REFUSED)" in result.stderr and "[TARGET] specs/x/spec.md" in result.stderr


# SPEC-git-operator-result-readiness AC-03
def test_a_combined_acceptance_prints_the_handoff_commit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _accept(
        monkeypatch,
        {
            "status": "handed_off",
            "completed_steps": ["acceptance_commit", "merge", "worktree_setup", "handoff", "handoff_commit"],
            "commit": "b" * 40,
            "handoff": {"next_command": "uv run devkit workflow next --unit specs/x", "errors": [], "notices": []},
            "acceptance_authority": "user",
            "errors": [],
        },
    )
    result = _run(tmp_path, "accept", "idea", "--by", "user", "--mode", "accept_and_handoff", "--effort", "low")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[ACCEPTED: PROP-idea status=handed_off mode=accept_and_handoff authority=user"
        f" completed=acceptance_commit,merge,worktree_setup,handoff,handoff_commit commit={'b' * 40}]",
        "[NEXT_CMD: uv run devkit workflow next --unit specs/x]",
    ]
