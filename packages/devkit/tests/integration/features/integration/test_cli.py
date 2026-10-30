from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import replace
from pathlib import Path

import devkit_agt.features.worktree.usecases.lifecycle as lifecycle
import pytest
from click.testing import CliRunner
from devkit_agt.features.integration import IntegrationService
from devkit_agt.features.integration.cli import cli
from devkit_agt.features.integration.models.contracts import Task
from devkit_agt.features.worktree import RemoveFailedError
from testsupport.rules import git

from .test_pull_request import FakeGitHub


def test_lifecycle_mcp_service_registration_is_removed():
    pyproject = Path(__file__).resolve().parents[4] / "pyproject.toml"
    entries = tomllib.loads(pyproject.read_text("utf-8"))["project"].get("entry-points", {})
    assert "devkit.host.services" not in entries


def test_integrate_cli_executes_after_host_conversation(repo):
    base, worktree = repo
    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--expected-digest",
            IntegrationService(base).prepare("dev-demo", Task("session", "fixture")).request.digest,
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "completed"
    assert payload["authority"] == "host-conversation"
    assert not worktree.exists()


def test_integrate_cli_reads_automatic_authority_from_base(repo):
    base, worktree = repo
    config = base / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\ndev-integration = "auto"\n')
    from testsupport.rules import git

    git(base, "add", ".devkit/config.toml")
    git(base, "commit", "-qm", "enable automatic integration")
    # The source worktree follows the configured base before the operation is prepared.
    git(worktree, "merge", "-q", "main")
    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["authority"] == "policy"
    assert not worktree.exists()


def test_integrate_cli_executes_pull_request_route(repo, tmp_path, ready_provider, monkeypatch):
    base, worktree = repo
    original_check = ready_provider.check
    monkeypatch.setattr(
        ready_provider,
        "check",
        lambda context: replace(original_check(context), landed_check="devkit rules check"),
    )
    remote = tmp_path / "remote.git"
    git(base, "init", "--bare", str(remote))
    git(base, "remote", "add", "origin", str(remote))
    git(base, "push", "-u", "origin", "main")
    service = IntegrationService(base)
    fake = FakeGitHub(base, remote)
    service.github = fake
    monkeypatch.setattr("devkit_agt.features.integration.cli.IntegrationService", lambda _root: service)

    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--route",
            "pull-request",
            "--expected-digest",
            service.prepare("dev-demo", Task("session", "fixture"), "pull-request").request.digest,
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "completed"
    assert payload["authority"] == "host-conversation"
    assert payload["request"]["route"] == "pull-request"
    assert fake.merge_calls == 1 and not worktree.exists()


def test_integrate_cli_retries_observed_cleanup_without_merging_twice(repo, monkeypatch):
    base, worktree = repo
    original_remove = lifecycle._remove
    remove_attempts = 0

    def fail_once(root, path):
        nonlocal remove_attempts
        remove_attempts += 1
        if remove_attempts == 1:
            raise RemoveFailedError("temporary permission failure")
        return original_remove(root, path)

    monkeypatch.setattr(lifecycle, "_remove", fail_once)
    service = IntegrationService(base)
    monkeypatch.setattr("devkit_agt.features.integration.cli.IntegrationService", lambda _root: service)
    base_before = git(base, "rev-parse", "HEAD")

    def invoke():
        return CliRunner().invoke(
            cli,
            [
                "integrate",
                "dev-demo",
                "--task-kind",
                "session",
                "--task-id",
                "fixture",
                "--expected-digest",
                service.prepare("dev-demo", Task("session", "fixture")).request.digest,
                "--workspace-root",
                str(base),
                "--format",
                "json",
            ],
        )

    first = invoke()
    assert first.exit_code == 1, first.output
    first_payload = json.loads(first.output)
    assert first_payload["status"] == "partial"
    assert first_payload["steps"]["merge"] == "completed"
    assert worktree.exists()
    landed = git(base, "rev-parse", "HEAD")
    assert landed != base_before

    second = invoke()
    assert second.exit_code == 0, second.output
    second_payload = json.loads(second.output)
    assert second_payload["status"] == "completed"
    assert second_payload["steps"]["merge"] == "skipped"
    assert git(base, "rev-parse", "HEAD") == landed
    assert remove_attempts == 2
    assert not worktree.exists()


def test_integrate_cli_refuses_source_changed_after_preparation(repo):
    base, worktree = repo
    task = Task("session", "fixture")
    prepared = IntegrationService(base).prepare("dev-demo", task)
    reviewed_digest = prepared.request.digest
    reviewed_source = prepared.request.context.finish.source_sha
    before = git(base, "rev-parse", "HEAD")
    (worktree / "after-approval.txt").write_text("Changed after conversational approval\n")
    git(worktree, "add", "after-approval.txt")
    git(worktree, "commit", "-qm", "Advance source after approval")
    assert git(worktree, "rev-parse", "HEAD") != reviewed_source

    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--expected-digest",
            reviewed_digest,
            "-w",
            str(base),
        ],
    )

    assert result.exit_code == 2, result.output
    assert "INTEGRATION_REQUEST_STALE" in result.output
    assert git(base, "rev-parse", "HEAD") == before
    assert worktree.exists()


def test_integrate_cli_requires_prepared_scope_under_ask(repo):
    base, worktree = repo
    before = git(base, "show-ref")
    result = CliRunner().invoke(
        cli, ["integrate", "dev-demo", "--task-kind", "session", "--task-id", "fixture", "-w", str(base)]
    )
    assert result.exit_code == 2, result.output
    assert "INTEGRATION_AUTHORITY_REQUIRED" in result.output
    assert "--expected-digest" in result.output
    assert git(base, "show-ref") == before
    assert worktree.exists()


def test_integrate_cli_refuses_target_changed_after_preparation(repo):
    base, worktree = repo
    reviewed_digest = IntegrationService(base).prepare("dev-demo", Task("session", "fixture")).request.digest
    git(base, "merge", "--ff-only", "dev-demo")
    before = git(base, "show-ref")
    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--expected-digest",
            reviewed_digest,
            "-w",
            str(base),
        ],
    )
    assert result.exit_code == 2, result.output
    assert "INTEGRATION_REQUEST_STALE" in result.output
    assert git(base, "show-ref") == before
    assert worktree.exists()


def _integrate_args(base, *extra):
    return ["integrate", "dev-demo", "--task-kind", "session", "--task-id", "fixture", *extra, "-w", str(base)]


def test_ask_without_digest_asks_the_user_with_the_exact_command(repo):
    base, _ = repo
    digest = IntegrationService(base).prepare("dev-demo", Task("session", "fixture")).request.digest
    result = CliRunner().invoke(cli, [*_integrate_args(base), "--format", "json"])
    assert result.exit_code == 2, result.output
    advisory = json.loads(result.output)["error"]["advisory"]
    assert advisory["code"] == "INTEGRATION_AUTHORITY_REQUIRED" and advisory["mode"] == "INTERACTION"
    # [FIX] re-presents the scope; integrating it is only for after the user approved it, a detail.
    assert advisory["fix"] == "uv run devkit integration prepare dev-demo --task-kind session --task-id fixture"
    assert advisory["details"] == [
        "after the user approves the scope prepare shows: uv run devkit integration integrate dev-demo"
        f" --task-kind session --task-id fixture --expected-digest {digest}"
    ]
    assert advisory["what_to_report"]


def test_a_stale_digest_asks_the_user_again_with_the_current_digest(repo):
    base, _ = repo
    digest = IntegrationService(base).prepare("dev-demo", Task("session", "fixture")).request.digest
    result = CliRunner().invoke(cli, [*_integrate_args(base, "--expected-digest", "0" * 64), "--format", "json"])
    assert result.exit_code == 2, result.output
    advisory = json.loads(result.output)["error"]["advisory"]
    assert advisory["code"] == "INTEGRATION_REQUEST_STALE" and advisory["mode"] == "INTERACTION"
    assert advisory["fix"] == "uv run devkit integration prepare dev-demo --task-kind session --task-id fixture"
    assert advisory["details"][0].endswith(f"--expected-digest {digest}")


def test_automatic_policy_refusing_the_pull_request_route_stays_blocked(repo):
    base, _ = repo
    config = base / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\ndev-integration = "auto"\n')
    result = CliRunner().invoke(cli, [*_integrate_args(base, "--route", "pull-request"), "--format", "json"])
    advisory = json.loads(result.output)["error"]["advisory"]
    assert (advisory["code"], advisory["mode"]) == ("INTEGRATION_AUTHORITY_REQUIRED", "BLOCKED")


def test_not_ready_is_an_input_error_keeping_the_reasons(repo, ready_provider):
    base, worktree = repo
    ready_provider.allowed = False
    result = CliRunner().invoke(
        cli,
        ["prepare", "dev-demo", "--task-kind", "session", "--task-id", "fixture", "-w", str(base), "--format", "json"],
    )
    assert result.exit_code == 2, result.output
    advisory = json.loads(result.output)["error"]["advisory"]
    assert (advisory["code"], advisory["mode"]) == ("INTEGRATION_NOT_READY", "INPUT_ERROR")
    assert advisory["details"] == ["finish the fixture checks"] and advisory["target_files"] == [str(worktree)]
    assert "commit the final changes and prepare a new" in advisory["fix"]


def test_task_argument_errors_target_the_flag(repo):
    base, _ = repo
    result = CliRunner().invoke(
        cli,
        ["prepare", "dev-demo", "--task-kind", "session", "--task-id", "fixture", "--claims", "[]", "-w", str(base)],
    )
    assert result.exit_code == 2 and "[TARGET] --claims" in result.output, result.output


def test_prepare_shows_the_approval_scope(repo):
    base, worktree = repo
    args = ["prepare", "dev-demo", "--task-kind", "session", "--task-id", "fixture", "-w", str(base)]
    payload = json.loads(CliRunner().invoke(cli, [*args, "--format", "json"]).output)
    request = payload["request"]
    assert request["pull_request"] is None and request["worktree"] == {"path": str(worktree), "remove": True}
    assert request["readiness"] == {"disclosure": "fixture checks on the merged result only"}
    assert "common_dir" not in json.dumps(payload) and "policy_digest" not in json.dumps(payload)
    text = CliRunner().invoke(cli, args).output.splitlines()
    assert text[0].startswith("[INTEGRATION_PREPARED: ")
    assert f" target_sha={request['target']['sha']} " in text[0]
    assert text[1] == (
        "[INTEGRATION_SCOPE: worktree_remove=yes delete_branch=yes cleanup=- seeded=- "
        'disclosure="fixture checks on the merged result only"]'
    )


def test_integrate_text_lists_effects_as_pairs(repo):
    base, _ = repo
    digest = IntegrationService(base).prepare("dev-demo", Task("session", "fixture")).request.digest
    result = CliRunner().invoke(cli, _integrate_args(base, "--expected-digest", digest))
    assert result.exit_code == 0, result.output
    line = result.output.splitlines()[0]
    assert line.endswith(
        "effects=merge:completed,worktree_remove:completed,branch_delete:completed,marker_clear:skipped,"
        "post_finish:completed]"
    ), line


def test_partial_cleanup_warning_exits_zero_and_errors_print_last(repo, monkeypatch):
    from devkit.advisory import AdvisoryError, Level
    from devkit_agt.features.integration.models.contracts import IntegrationResult

    base, _ = repo
    request = IntegrationService(base).prepare("dev-demo", Task("session", "fixture")).request
    warning = AdvisoryError("cleanup remains", code="INTEGRATION_CLEANUP_INCOMPLETE", level=Level.WARNING)

    def fake(status, errors=()):
        result = IntegrationResult(request, status=status)
        result.notices.append(warning)
        result.errors.extend(errors)
        monkeypatch.setattr("devkit_agt.features.integration.cli.IntegrateUseCase.execute", lambda *_a, **_k: result)

    fake("partial")
    assert CliRunner().invoke(cli, _integrate_args(base)).exit_code == 0
    assert CliRunner().invoke(cli, _integrate_args(base, "--strict")).exit_code == 1

    fake("blocked", [AdvisoryError("refused", code="INTEGRATION_TARGET_MOVED", guardrail=True)])
    result = CliRunner().invoke(cli, _integrate_args(base, "--strict"))
    assert result.exit_code == 2, result.output  # --strict never lowers 2 to 1
    stderr = result.stderr
    assert stderr.index("[WARN]") < stderr.index("[ERROR]")


def test_prepare_inside_the_worktree_fixes_with_the_same_command_on_the_base(repo):
    base, worktree = repo
    result = CliRunner().invoke(
        cli, ["prepare", "dev-demo", "--task-kind", "session", "--task-id", "fixture", "-w", str(worktree)]
    )
    assert result.exit_code == 2 and "(WORKTREE_RUN_FROM_BASE)" in result.output, result.output
    assert (
        f"[FIX]    uv run devkit integration prepare dev-demo --task-kind session --task-id fixture -w {base}\n"
        in result.output
    )


@pytest.mark.parametrize("command", ["prepare", "integrate"])
def test_missing_session_claims_retries_same_command(repo, ready_provider, monkeypatch, command):
    from devkit_agt.features.integration import Evidence

    base, worktree = repo
    original = ready_provider.check
    claims = '{"task_kind":"feature","effort":"low","review":true,"tests":true,"lint":true}'

    def check(context):
        result = original(context)
        if context.task.claims_json == "{}":
            return replace(
                result,
                evidence=(*result.evidence, Evidence("SESSION_CLAIMS_INVALID", "--claims")),
                reasons=("session claims require task_kind",),
            )
        return result

    monkeypatch.setattr(ready_provider, "check", check)
    digest = IntegrationService(base).prepare("dev-demo", Task("session", "fixture", claims_json=claims)).request.digest
    args = [command, "dev-demo", "--task-kind", "session", "--task-id", "fixture", "-w", str(base), "--format", "json"]
    if command == "integrate":
        args += ["--expected-digest", digest]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 2, result.output
    advisory = json.loads(result.output)["error"]["advisory"]
    assert advisory["code"] == "INTEGRATION_NOT_READY"
    assert advisory["target_files"] == ["--claims"]
    assert "--claims" in advisory["fix"] and "same" in advisory["fix"]
    assert "commit" not in advisory["fix"] and "prepare a new" not in advisory["fix"]
    assert worktree.exists()
    retried = CliRunner().invoke(cli, [*args, "--claims", claims])
    assert retried.exit_code == 0, retried.output
    payload = json.loads(retried.output)
    assert payload["request"]["digest"] == digest
    assert payload["status"] == ("prepared" if command == "prepare" else "completed")


def test_missing_claims_do_not_hide_source_readiness_failure(repo, ready_provider, monkeypatch):
    from devkit_agt.features.integration import Evidence

    base, _worktree = repo
    original = ready_provider.check
    ready_provider.allowed = False

    def check(context):
        result = original(context)
        if context.task.claims_json == "{}":
            return replace(
                result,
                evidence=(*result.evidence, Evidence("SESSION_CLAIMS_INVALID", "--claims")),
                reasons=(*result.reasons, "claims input is incomplete"),
            )
        return result

    monkeypatch.setattr(ready_provider, "check", check)
    args = [
        "prepare",
        "dev-demo",
        "--task-kind",
        "session",
        "--task-id",
        "fixture",
        "-w",
        str(base),
        "--format",
        "json",
    ]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 2, result.output
    advisory = json.loads(result.output)["error"]["advisory"]
    assert advisory["details"] == ["finish the fixture checks", "claims input is incomplete"]
    assert "resolve any other reported readiness conditions" in advisory["fix"]
    claims = '{"task_kind":"feature","effort":"low","review":true,"tests":true,"lint":true}'
    retried = CliRunner().invoke(cli, [*args, "--claims", claims])
    assert retried.exit_code == 2, retried.output
    advisory = json.loads(retried.output)["error"]["advisory"]
    assert advisory["details"] == ["finish the fixture checks"]
    assert "commit the final changes and prepare a new" in advisory["fix"]


def test_moved_target_cli_merges_and_states_the_merged_target_and_disclosure(repo):
    """``SPEC-integration-merge-moved-target``: no base merge, and the result names what it merged and checked."""
    base, worktree = repo
    tip = git(worktree, "rev-parse", "HEAD")
    (base / "theirs.txt").write_text("theirs\n")
    git(base, "add", "theirs.txt")
    git(base, "commit", "-qm", "advance the target")
    moved = git(base, "rev-parse", "HEAD")
    prepared = CliRunner().invoke(
        cli, ["prepare", "dev-demo", "--task-kind", "session", "--task-id", "fixture", "-w", str(base)]
    )
    assert prepared.exit_code == 0, prepared.output
    first = prepared.output.splitlines()[0]
    assert f" target_sha={moved} " in first
    digest = first.split(" digest=", 1)[1].split(" ", 1)[0]
    result = CliRunner().invoke(cli, _integrate_args(base, "--expected-digest", digest))
    assert result.exit_code == 0, result.output
    head = git(base, "rev-parse", "HEAD")
    line = result.output.splitlines()[0]
    assert f" target_sha={moved} build_target={moved} result={head} " in line
    assert ' disclosure="fixture checks on the merged result only" effects=' in line
    assert git(base, "rev-parse", "HEAD^1", "HEAD^2").split() == [moved, tip]


def test_receipt_only_conflict_cli_states_the_seeded_artifact(repo):
    """``SPEC-generated-conflicts-in-prepared-merge``: prepare and integrate name the artifact kept from one side."""
    base, worktree = repo

    def receipt(root, side):
        # An untracked projection's record: the merged receipt parses and leaves no tracked record inconsistent.
        record = {".agents/skill.md": {"sha256": hashlib.sha256(side.encode()).hexdigest(), "mode": 420}}
        data = {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": record}
        (root / ".devkit").mkdir(exist_ok=True)
        (root / ".devkit/installation.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        git(root, "add", ".devkit/installation.json")
        git(root, "commit", "-qm", f"receipt {side}")
        return (root / ".devkit/installation.json").read_text()

    receipt(base, "base")
    git(worktree, "merge", "-q", "main")
    receipt(worktree, "source")
    target = receipt(base, "target")
    args = ["prepare", "dev-demo", "--task-kind", "session", "--task-id", "fixture", "-w", str(base)]
    prepared = CliRunner().invoke(cli, args)
    assert prepared.exit_code == 0, prepared.output
    lines = prepared.output.splitlines()
    assert " seeded=devkit-receipt disclosure=" in lines[1]
    assert "(INTEGRATION_GENERATED_SEEDED)" in prepared.output
    assert "devkit generated regen devkit-receipt" in prepared.output
    payload = json.loads(CliRunner().invoke(cli, [*args, "--format", "json"]).output)
    assert payload["generated"]["seeded"] == [
        {"id": "devkit-receipt", "paths": [".devkit/installation.json"], "seed": "ours", "kept": "target"}
    ]
    assert payload["generated"]["regenerate"].endswith("devkit generated regen devkit-receipt")
    assert [notice["code"] for notice in payload["notices"]] == ["INTEGRATION_GENERATED_SEEDED"]
    digest = lines[0].split(" digest=", 1)[1].split(" ", 1)[0]
    result = CliRunner().invoke(cli, _integrate_args(base, "--expected-digest", digest))
    assert result.exit_code == 0, result.output
    assert " seeded=devkit-receipt disclosure=" in result.output.splitlines()[0]
    assert git(base, "show", "HEAD:.devkit/installation.json") == target.rstrip("\n")
