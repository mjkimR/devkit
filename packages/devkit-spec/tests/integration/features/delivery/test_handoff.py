"""The shared handoff operation preserves successful writes and registration recovery."""

from pathlib import Path

import pytest
from spec_support.proposals import TODAY, accept
from spec_support.scope import git, make_repo

from devkit_spec.base.errors import HandoffStaleError
from devkit_spec.features.delivery.usecases.handoff import handoff_and_register
from devkit_spec.features.proposals import create_proposal
from devkit_spec.features.scope import load_token, open_session


@pytest.fixture
def accepted_worktree(tmp_path: Path) -> Path:
    repo = make_repo(tmp_path / "repo")
    proposal = create_proposal(repo, "handoff", today=TODAY)
    accept(repo / proposal.path)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "accepted proposal")
    linked = tmp_path / "repo-wt-dev-handoff"
    git(repo, "worktree", "add", "-q", "-b", "dev-handoff", str(linked))
    return linked


def test_handoff_registers_after_writing_spec_and_preserves_notices(accepted_worktree: Path) -> None:
    root = accepted_worktree
    session = open_session(root)
    (session.location.shared_path / session.location.namespace / "journal.jsonl").mkdir(parents=True)
    observed = []

    def before_registration() -> None:
        assert not (root / "docs/proposals/PROP-handoff/proposal.md").exists()
        assert (root / "specs/2026-10/20261013-handoff/spec.md").is_file()
        assert load_token(open_session(root).location.token_path) is None
        observed.append("handoff-complete")

    completed = handoff_and_register(root, "handoff", today=TODAY, before_registration=before_registration)
    handed, registered = completed.handoff, completed.registered
    assert observed == ["handoff-complete"]
    assert registered is not None
    assert registered.record.spec == handed.dir
    assert load_token(registered.location.token_path) == registered.token
    assert any(notice.code == "SPEC_PROPOSAL_UNBOUND" for notice in handed.notices)
    assert "SPEC_SCOPE_JOURNAL_UNAVAILABLE" not in [notice.code for notice in handed.notices]
    assert registered.notices == []
    assert "SPEC_SCOPE_JOURNAL_UNAVAILABLE" not in [notice.code for notice in completed.notices]


def test_registration_failure_is_silent_after_a_successful_handoff(accepted_worktree: Path) -> None:
    root = accepted_worktree
    session = open_session(root)
    session.location.token_path.write_text("existing-token\n")

    completed = handoff_and_register(root, "handoff", today=TODAY)
    handed, registered = completed.handoff, completed.registered

    assert registered is None
    assert (root / handed.dir / "spec.md").is_file()
    assert not (root / "docs/proposals/PROP-handoff/proposal.md").exists()
    assert load_token(session.location.token_path) == "existing-token"
    codes = [notice.code for notice in completed.notices]
    assert "SPEC_SCOPE_REGISTER_FAILED" not in codes
    assert "SPEC_PROPOSAL_UNBOUND" in codes
    assert all(not code.startswith("SPEC_SCOPE_") for code in codes)


def test_guard_refusal_keeps_handoff_without_starting_registration(accepted_worktree: Path) -> None:
    root = accepted_worktree

    def cancelled() -> None:
        assert (root / "specs/2026-10/20261013-handoff/spec.md").is_file()
        raise HandoffStaleError("the invocation was cancelled after handoff")

    with pytest.raises(HandoffStaleError):
        handoff_and_register(root, "handoff", today=TODAY, before_registration=cancelled)

    session = open_session(root)
    assert load_token(session.location.token_path) is None
    assert session.registry.query(session.location.namespace, session.deadline) == ([], [])
    assert (root / "specs/2026-10/20261013-handoff/spec.md").is_file()
    assert not (root / "docs/proposals/PROP-handoff/proposal.md").exists()


def test_native_handoff_suppresses_registration_diagnostics(
    accepted_worktree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from devkit_agt.features.worktree import locate

    from devkit_spec.features.delivery.usecases import native_handoff
    from devkit_spec.features.proposals.models.handoff import HandoffPreview

    root = accepted_worktree
    base = locate(root).base
    session = open_session(root)
    (session.location.shared_path / session.location.namespace / "journal.jsonl").mkdir(parents=True)
    preview = HandoffPreview(
        base,
        "handoff",
        git(root, "rev-parse", "HEAD"),
        "main",
        str(root),
        None,
        "",
        "Handoff",
        "",
        "",
        "medium",
        existing=True,
    )
    monkeypatch.setattr(native_handoff, "prepare", lambda *args: preview)
    monkeypatch.setattr(native_handoff, "_prepare", lambda *args, **kwargs: (None, None))
    captured = []

    def complete(root: Path, slug: str, **kwargs):
        completed = handoff_and_register(root, slug, today=TODAY, **kwargs)
        captured.append(completed)
        return completed

    monkeypatch.setattr(native_handoff, "handoff_and_register", complete)
    result = native_handoff.HandoffUseCase(base)._execute(preview, "medium")

    completed = captured[0]
    assert result["status"] == "handed_off", result
    assert result["errors"] == []
    assert result["handoff"] == completed.handoff.to_dict()
    assert result["notices"] == [notice.to_dict() for notice in completed.notices]
    assert [notice["code"] for notice in result["handoff"]["notices"]] == ["SPEC_PROPOSAL_UNBOUND"]
    assert [notice["code"] for notice in result["notices"]] == [
        "SPEC_PROPOSAL_UNBOUND",
    ]
    assert completed.registered is not None
    assert result["scope_token"] == completed.registered.token


def test_cli_handoff_json_suppresses_registration_diagnostics(accepted_worktree: Path) -> None:
    import json

    from click.testing import CliRunner
    from devkit_dist.cli import cli

    root = accepted_worktree
    session = open_session(root)
    (session.location.shared_path / session.location.namespace / "journal.jsonl").mkdir(parents=True)
    result = CliRunner().invoke(cli, ["spec", "proposal", "handoff", "handoff", "-w", str(root), "--format", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert [notice["code"] for notice in payload["notices"]] == [
        "SPEC_PROPOSAL_UNBOUND",
    ]
    assert payload["scope"]["token"] == load_token(session.location.token_path)
    assert payload["spec"] == "SPEC-handoff"


@pytest.mark.parametrize("output", ["json", "text"])
@pytest.mark.parametrize("strict", [False, True])
def test_cli_handoff_registration_failure_preserves_primary_exit(
    accepted_worktree: Path, output: str, strict: bool
) -> None:
    from click.testing import CliRunner
    from devkit_dist.cli import cli

    session = open_session(accepted_worktree)
    session.location.token_path.write_text("already-owned\n")
    args = ["spec", "proposal", "handoff", "handoff", "-w", str(accepted_worktree), "--format", output]
    if strict:
        args.append("--strict")
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result.output
    assert "SPEC_SCOPE_" not in result.output and "SCOPE_ACK" not in result.output
