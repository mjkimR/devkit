from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli as devkit_cli
from spec_support.delivery import _cli, _make_synced_repo, _start_worktree
from spec_support.scope import git

from devkit_spec.features.delivery.cli.proposals import proposal_group


@pytest.fixture(scope="module")
def proposal_seed_template(synced_template: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    seed_root = tmp_path_factory.mktemp("proposal-seed-template")
    repo = _make_synced_repo(seed_root, synced_template)
    _cli(repo, "sync")
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "Record complete consumer installation")
    wt = _start_worktree(repo, "plan-idea", seed_root / "seed-planning")
    unit = "docs/proposals/PROP-idea"
    _cli(wt, "spec", "proposal", "new", "idea", "--title", "Idea", "--summary", "Review this idea.")
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "feedback",
        "--stage",
        "collect-feedback",
        "--summary",
        "Observed sweep complete.",
        "--check",
        "swept=PASS",
    )
    anchor = wt / unit / "proposal.md"
    anchor.write_text(anchor.read_text().replace("status: draft", "status: reviewing"))
    git(wt, "add", "-A")
    git(wt, "commit", "-m", "Planning complete")
    git(repo, "worktree", "remove", "--force", str(wt))
    return repo


@pytest.fixture
def pending(tmp_path: Path, proposal_seed_template: Path):
    repo = tmp_path / "repo"
    shutil.copytree(proposal_seed_template, repo, symlinks=True)
    wt = tmp_path / "planning"
    git(repo, "worktree", "add", "-q", str(wt), "plan-idea")
    git(repo, "config", "branch.plan-idea.devkitWorktree", "true")
    git(repo, "config", "branch.plan-idea.devkitBase", "main")
    shutil.copytree(repo / ".devkit/managed", wt / ".devkit/managed", dirs_exist_ok=True)
    return repo, wt


@pytest.mark.parametrize("mode", ["accept_only", "accept_and_handoff"])
def test_accept_cli_commits_and_merges_exact_reviewed_plan(pending, mode):
    repo, planning = pending
    result = CliRunner().invoke(
        proposal_group,
        [
            "accept-plan",
            "idea",
            "--by",
            "user",
            "--mode",
            mode,
            "--effort",
            "low",
            "-w",
            str(repo),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "accepted" and payload["verification"] == "pending"
    assert payload["handoff_status"] == "not_started"
    assert payload["acceptance_authority"] == "user"
    assert payload["integration"]["authority"] == "host-conversation"
    assert "ui_action" not in payload["integration"]
    assert "acceptance_commit" in payload["completed_steps"]
    assert "status: accepted" in (repo / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert not planning.exists() and not git(repo, "branch", "--list", "dev-idea")
    assert payload["continuation"]["handoff_authorized"] is (mode == "accept_and_handoff")


def test_accept_cli_refuses_invalid_mode(pending):
    repo, planning = pending
    before = git(repo, "show-ref")
    result = CliRunner().invoke(
        proposal_group,
        ["accept-plan", "idea", "--by", "user", "--mode", "invalid_mode", "-w", str(repo)],
    )
    assert result.exit_code == 2
    assert "Invalid value for '--mode'" in result.output
    assert git(repo, "show-ref") == before and planning.exists()


@pytest.mark.parametrize("output_format", ["json", "text"])
def test_accept_cli_uses_plan_accept_auto_when_development_remains_ask(pending, output_format):
    repo, planning = pending
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\nplan-accept = "auto"\ndev-integration = "ask"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Delegate proposal acceptance to policy")
    git(planning, "merge", "--no-edit", "main")

    result = CliRunner().invoke(
        proposal_group,
        [
            "accept-plan",
            "idea",
            "--by",
            "policy",
            "--mode",
            "accept_and_handoff",
            "--effort",
            "high",
            "-w",
            str(repo),
            "--format",
            output_format,
        ],
    )

    assert result.exit_code == 0, result.output
    if output_format == "json":
        payload = json.loads(result.stdout)
        assert payload["status"] == "accepted" and payload["acceptance_authority"] == "policy"
        assert payload["mode"] == "accept_only" and payload["requested_mode"] == "accept_and_handoff"
        assert payload["continuation"]["handoff_authorized"] is False
        assert "command" not in payload["continuation"]
    else:
        assert "mode=accept_only" in result.stdout and "mode=accept_and_handoff" not in result.stdout


def test_accept_cli_withdraws_its_writes_when_the_commit_gate_refuses(pending, tmp_path):
    repo, planning = pending
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "pre-commit").write_text("#!/bin/sh\necho 'RULE-example refused the staged tree' >&2\nexit 1\n")
    (hooks / "pre-commit").chmod(0o755)
    git(repo, "config", "core.hooksPath", str(hooks))
    before = git(repo, "show-ref")

    result = CliRunner().invoke(
        proposal_group,
        ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "-w", str(repo), "--format", "json"],
    )

    # Nothing was done: the command fails outright with one error document (ARCH-08-1 section 4).
    assert result.exit_code == 2, result.output
    error = json.loads(result.output)["error"]
    assert error["code"] == "SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED" and error["advisory"]["mode"] == "INPUT_ERROR"
    assert error["advisory"]["details"] == ["RULE-example refused the staged tree"]
    assert error["advisory"]["target_files"] == ["plan-idea"]
    text = CliRunner().invoke(
        proposal_group, ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "-w", str(repo)]
    )
    assert text.exit_code == 2 and text.stdout == ""
    assert "SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED" in text.stderr
    assert git(planning, "status", "--porcelain") == ""
    assert "status: reviewing" in (planning / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert git(repo, "show-ref") == before


def _accept_json(root: Path, *args: str) -> dict:
    result = CliRunner().invoke(proposal_group, ["accept-plan", "idea", *args, "-w", str(root), "--format", "json"])
    assert result.exit_code == 2, result.output
    return json.loads(result.output)["error"]


# SPEC-split-composed-proposal-accept AC-03
def test_accept_and_handoff_without_effort_is_refused_by_the_use_case(pending):
    repo, planning = pending
    before = git(repo, "show-ref")
    error = _accept_json(repo, "--by", "user", "--mode", "accept_and_handoff")
    assert error["code"] == "SPEC_PROPOSAL_APPROVAL_REPLY_INVALID"
    assert error["advisory"]["target_files"] == ["--effort"]
    assert git(repo, "show-ref") == before and planning.exists()


def test_a_policy_acceptance_is_never_redirected_to_the_user(pending):
    repo, planning = pending
    # Under plan-accept=ask the policy refusal wins, even off the base checkout.
    for root in (repo, planning):
        error = _accept_json(root, "--by", "policy", "--mode", "accept_only")
        assert error["code"] == "SPEC_PROPOSAL_POLICY_NOT_AUTO" and "--by user" not in json.dumps(error)
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\nplan-accept = "auto"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Delegate proposal acceptance to policy")
    git(planning, "merge", "--no-edit", "main")
    # Off the base checkout the fix keeps the caller's own --by policy command.
    error = _accept_json(planning, "--by", "policy", "--mode", "accept_only")
    assert error["code"] == "SPEC_PROPOSAL_WRONG_WORKTREE"
    assert "uv run devkit spec proposal accept-plan idea --by policy --mode accept_only" in error["advisory"]["fix"]
    assert "--by user" not in json.dumps(error) and "<" not in error["advisory"]["fix"]


def _advance(repo: Path, rel: str, text: str | None, *gate: str) -> str:
    """Commit a change to ``rel`` on the base (``None`` deletes it) and return the moved target; ``gate`` passes
    ``--no-verify`` for a commit another writer made without this repository's gate."""
    if text is None:
        git(repo, "rm", "-q", rel)
    else:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
        git(repo, "add", rel)
    git(repo, "commit", *gate, "-m", f"Change {rel} on the base")
    return git(repo, "rev-parse", "HEAD")


def test_accept_cli_integrates_a_moved_target_without_a_base_merge(pending):
    """``SPEC-integration-merge-moved-target``: the landed merge has the moved target and the acceptance commit."""
    repo, planning = pending
    source = git(planning, "rev-parse", "HEAD")
    moved = _advance(repo, "docs/unrelated.md", "Unrelated base change.\n")
    result = CliRunner().invoke(
        proposal_group,
        ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "-w", str(repo), "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "accepted", json.dumps(payload, indent=2)
    acceptance = payload["acceptance_sha"]
    assert git(repo, "rev-parse", f"{acceptance}^") == source  # the acceptance commit's only parent: no base merge
    assert git(repo, "rev-parse", "HEAD^1", "HEAD^2").split() == [moved, acceptance]
    assert payload["landed_sha"] == git(repo, "rev-parse", "HEAD") and payload["target_sha"] == moved
    assert payload["verification"] == "pending"


def test_accept_cli_text_names_the_merged_target_and_the_disclosure(pending):
    repo, _ = pending
    moved = _advance(repo, "docs/unrelated.md", "Unrelated base change.\n")
    result = CliRunner().invoke(
        proposal_group, ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "-w", str(repo)]
    )
    assert result.exit_code == 0, result.output
    line = result.stdout.splitlines()[0]
    assert line.startswith("[ACCEPTED: PROP-idea ") and f" target_sha={moved} " in line
    assert f" landed_sha={git(repo, 'rev-parse', 'HEAD')} " in line
    assert "verification=pending handoff=not_started" in line


def test_accept_cli_refuses_a_target_change_to_the_proposal_before_the_acceptance_commit(pending):
    repo, planning = pending
    source = git(planning, "rev-parse", "HEAD")
    _advance(repo, "docs/proposals/PROP-idea/note.md", "A base note.\n", "--no-verify")
    error = _accept_json(repo, "--by", "user", "--mode", "accept_only")
    assert error["code"] == "SPEC_PROPOSAL_APPROVAL_NOT_READY", json.dumps(error, indent=2)
    details = error["advisory"]["details"]
    assert any("the target changed docs/proposals/PROP-idea" in line for line in details), details
    assert "Merge the target into plan-idea" in error["advisory"]["fix"]
    assert git(planning, "rev-parse", "HEAD") == source
    assert "status: reviewing" in (planning / "docs/proposals/PROP-idea/proposal.md").read_text()


def test_accept_cli_refuses_reference_drift_on_the_prospective_result(pending):
    repo, planning = pending
    cited = "docs/capabilities/delivery/CAP-DLV-cited.md"
    _advance(
        repo,
        cited,
        '---\nid: CAP-DLV-cited\ntitle: Cited\nsummary: "A capability the proposal cites."\nstatus: active\n'
        "area: delivery\ncreated: 2026-10-01\nupdated: 2026-10-01\n---\n\n# [CAP-DLV-cited] Cited\n\n"
        "## 1. Overview\nCited capability.\n",
    )
    git(planning, "merge", "--no-edit", "main")
    anchor = planning / "docs/proposals/PROP-idea/proposal.md"
    anchor.write_text(anchor.read_text() + "\nThis builds on `CAP-DLV-cited`.\n")
    git(planning, "commit", "-am", "Cite the capability")
    _advance(repo, cited, None)
    result = CliRunner().invoke(
        proposal_group,
        ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "-w", str(repo), "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["verification"] == "pending" and payload["status"] == "accepted"


def _refuse_handoff_commit(repo: Path, tmp_path: Path) -> None:
    """Only the handoff commit on dev-idea is refused; the acceptance commit on plan-idea passes."""
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "pre-commit").write_text(
        '#!/bin/sh\n[ "$(git rev-parse --abbrev-ref HEAD)" = dev-idea ] || exit 0\n'
        "echo 'RULE-example refused the handoff' >&2\nexit 1\n"
    )
    (hooks / "pre-commit").chmod(0o755)
    git(repo, "config", "core.hooksPath", str(hooks))


def test_acceptance_yields_before_handoff_evaluation(pending, monkeypatch):
    from devkit_spec.features.delivery.usecases import native_handoff

    repo, _ = pending
    monkeypatch.setattr(native_handoff, "prepare", lambda *a, **kw: pytest.fail("old-process handoff evaluated"))
    result = CliRunner().invoke(
        proposal_group,
        [
            "accept-plan",
            "idea",
            "--by",
            "user",
            "--mode",
            "accept_and_handoff",
            "--effort",
            "high",
            "-w",
            str(repo),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "accepted" and payload["verification"] == "pending"
    assert payload["handoff_status"] == "not_started" and "handoff" not in payload["completed_steps"]
    assert "commit" not in payload and "worktree" not in payload
    assert payload["continuation"]["activity_effort"] == "high"
    assert payload["continuation"]["mode"] == "accept_and_handoff"
    assert payload["continuation"]["handoff_authorized"] is True
    assert payload["continuation"]["landed_sha"] == git(repo, "rev-parse", "HEAD")
    assert "spec proposal handoff idea --effort high" in payload["next_action"]
    assert "fresh process" in payload["next_action"]


def test_acceptance_text_reports_pending_verification_and_fresh_continuation(pending, tmp_path):
    repo, _ = pending
    _refuse_handoff_commit(repo, tmp_path)
    result = CliRunner().invoke(
        proposal_group,
        ["accept-plan", "idea", "--by", "user", "--mode", "accept_and_handoff", "--effort", "low", "-w", str(repo)],
    )
    assert result.exit_code == 0, result.output
    assert "verification=pending handoff=not_started" in result.stdout
    assert "commit=" not in result.stdout and "[NEXT_ACTION:" in result.stdout
    assert "SPEC_HANDOFF_COMMIT_REFUSED" not in result.stderr


QUESTION = """\
- id: q1
  title: Storage format
  prompt: Which storage format?
  context: The format decides the migration.
  options:
    - {id: a, description: Keep YAML, recommended: true}
    - {id: b, description: Move to JSON, recommended: false}
  allow_note: true
"""


# SPEC-git-operator-planning-completion-route AC-05 (GOP-03)
def test_a_question_recorded_at_direction_handoff_holds_the_composed_acceptance(pending):
    repo, planning = pending
    unit = "docs/proposals/PROP-idea"
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\nplan-accept = "auto"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Delegate proposal acceptance to policy")
    git(planning, "merge", "--no-edit", "main")
    # Under plan-accept=auto a reviewing proposal reads as complete before any acceptance ran.
    shown = CliRunner().invoke(devkit_cli, ["workflow", "next", "--unit", unit, "-w", str(planning)])
    assert shown.exit_code == 0, shown.output
    assert "[STAGE: - complete=yes]" in shown.stdout
    head = git(planning, "rev-parse", "HEAD")
    recorded = CliRunner().invoke(
        devkit_cli,
        [
            *("workflow", "envelope", "worker", "--unit", unit, "--stage", "direction-handoff"),
            *("--summary", "Planning ends with one open question.", "--effort", "low", "--head", head),
            *("--questions-file", "-", "-w", str(planning)),
        ],
        input=QUESTION,
    )
    assert recorded.exit_code == 0, recorded.output
    git(planning, "add", "-A")
    git(planning, "commit", "-m", "Record the Planning return")
    before = git(repo, "show-ref")

    error = _accept_json(repo, "--by", "policy", "--mode", "accept_only")

    assert error["code"] == "SPEC_PROPOSAL_APPROVAL_NOT_READY", json.dumps(error, indent=2)
    assert any(line.startswith("hold: ") for line in error["advisory"]["details"]), error["advisory"]["details"]
    assert git(repo, "show-ref") == before
    assert "status: reviewing" in (planning / unit / "proposal.md").read_text()
    assert not list((planning / unit / "decisions").glob("*gate-plan-accept*"))
    assert git(repo, "branch", "--list", "dev-idea") == ""


# SPEC-git-operator-planning-completion-route AC-06; SPEC-split-composed-proposal-accept AC-02, AC-04
@pytest.mark.parametrize(
    "args",
    [
        ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "--check"],
        ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "--direct"],
        ["accept-plan", "idea", "--by", "user", "--mode", "accept_only", "--note", "why"],
        ["accept-plan", "idea", "--by", "user"],
        ["accept", "idea", "--by", "user", "--mode", "accept_only"],
        ["accept", "idea", "--by", "user", "--effort", "low"],
    ],
)
def test_each_acceptance_form_refuses_the_other_forms_options(pending, args):
    repo, planning = pending
    before = git(repo, "show-ref")

    result = CliRunner().invoke(proposal_group, [*args, "-w", str(repo)])

    assert result.exit_code == 2 and result.stdout == "", result.output
    assert "No such option" in result.stderr or "Missing option '--mode'" in result.stderr, result.stderr
    assert git(repo, "show-ref") == before
    assert "status: reviewing" in (planning / "docs/proposals/PROP-idea/proposal.md").read_text()


@pytest.fixture
def cleanup_fails_once(monkeypatch):
    import devkit_agt.features.worktree.usecases.lifecycle as lifecycle
    from devkit_agt.features.worktree import RemoveFailedError

    original = lifecycle._remove
    attempts = []

    def remove(root, path):
        attempts.append(path)
        if len(attempts) == 1:
            raise RemoveFailedError("temporary cleanup refusal")
        return original(root, path)

    monkeypatch.setattr(lifecycle, "_remove", remove)
    return attempts


@pytest.mark.parametrize("output_format", ["json", "text"])
def test_partial_acceptance_retains_landed_revision_and_authorized_continuation(
    pending, cleanup_fails_once, output_format
):
    repo, planning = pending
    result = CliRunner().invoke(
        proposal_group,
        [
            "accept-plan",
            "idea",
            "--by",
            "user",
            "--mode",
            "accept_and_handoff",
            "--effort",
            "high",
            "-w",
            str(repo),
            "--format",
            output_format,
        ],
    )
    assert result.exit_code == 1, result.output
    landed = git(repo, "rev-parse", "HEAD")
    assert planning.exists() and len(cleanup_fails_once) == 1
    if output_format == "json":
        payload = json.loads(result.stdout)
        assert payload["status"] == "needs_recovery" and payload["landed_sha"] == landed
        assert payload["verification"] == "pending" and payload["handoff_status"] == "not_started"
        assert payload["requested_mode"] == payload["mode"] == "accept_and_handoff"
        assert payload["continuation"] == {
            "mode": "accept_and_handoff",
            "activity_effort": "high",
            "unit": "docs/proposals/PROP-idea",
            "landed_sha": landed,
            "authority": "host-conversation",
            "handoff_authorized": True,
            "command": "uv run devkit spec proposal handoff idea --effort high",
        }
        assert "remaining cleanup" in payload["next_action"] and "final checks" in payload["next_action"]
    else:
        assert f"landed_sha={landed}" in result.stdout
        assert "verification=pending handoff=not_started" in result.stdout
        assert "remaining cleanup" in result.stdout and "final checks" in result.stdout


def test_cleanup_only_acceptance_retry_keeps_actual_no_ff_landing(pending, cleanup_fails_once):
    repo, planning = pending
    args = [
        "accept-plan",
        "idea",
        "--by",
        "user",
        "--mode",
        "accept_and_handoff",
        "--effort",
        "high",
        "-w",
        str(repo),
        "--format",
        "json",
    ]
    first = CliRunner().invoke(proposal_group, args)
    assert first.exit_code == 1, first.output
    landed = git(repo, "rev-parse", "HEAD")
    source = git(planning, "rev-parse", "HEAD")
    assert landed != source and len(git(repo, "rev-list", "--parents", "-n", "1", landed).split()) == 3
    second = CliRunner().invoke(proposal_group, args)
    assert second.exit_code == 0, second.output
    payload = json.loads(second.stdout)
    assert payload["status"] == "accepted" and payload["landed_sha"] == landed
    assert payload["integration"]["steps"]["merge"] == "skipped"
    assert payload["continuation"]["landed_sha"] == landed and payload["continuation"]["activity_effort"] == "high"
    assert git(repo, "rev-parse", "HEAD") == landed and not planning.exists()
    assert len(cleanup_fails_once) == 2
