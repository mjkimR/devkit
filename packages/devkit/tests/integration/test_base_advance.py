"""Approved integrations absorb target commits that land during the confirmation (``SPEC-integration-follow-ups``)."""

from __future__ import annotations

import asyncio
import hashlib
import json
import threading
import time
from pathlib import Path

import pytest
from devkit.core import LockHeldError
from devkit.core.errors import GitError
from devkit.core.locks import file_lock
from devkit.core.mcp import ConfirmationReply
from devkit.integration import IntegrationService, ProviderError, Task
from devkit.integration import service as service_module
from devkit.integration.receipts import check_merge
from devkit.worktree import CommitFailedError, MergeNotFastForwardError, merging
from testsupport.rules import git, write

TASK = Task("session", "fixture-task")
LOCK = ".git/devkit-integration.lock"


def commit(root: Path, rel: str, text: str = "x\n") -> str:
    write(root, rel, text)
    git(root, "add", ".")
    git(root, "commit", "-qm", f"change {rel}")
    return git(root, "rev-parse", "HEAD")


def approve_after(action=None):
    async def confirm(message: str, _schema: dict) -> ConfirmationReply:
        confirm.messages.append(message)
        if action is not None:
            action()
        return ConfirmationReply("accept", {"approve": True})

    confirm.messages = []
    return confirm


def integrate(service: IntegrationService, confirm):
    return asyncio.run(service.integrate("dev-demo", TASK, confirm))


def test_clean_advance_during_confirmation_lands_a_merge_commit(repo, ready_provider, monkeypatch):
    base, worktree = repo
    tip, target = git(worktree, "rev-parse", "HEAD"), git(base, "rev-parse", "HEAD")
    guards = []
    original = service_module.run_finish_guards
    monkeypatch.setattr(service_module, "run_finish_guards", lambda *args: guards.append(args[2:]) or original(*args))
    moved = []
    result = integrate(IntegrationService(base), approve_after(lambda: moved.append(commit(base, "theirs.txt"))))
    assert result.status == "completed", result.errors
    head = git(base, "rev-parse", "HEAD")
    assert git(base, "rev-parse", "HEAD^1", "HEAD^2").split() == [moved[0], tip]
    assert set(git(base, "ls-tree", "--name-only", "HEAD").split()) >= {"theirs.txt", "ready.txt"}
    assert result.build() == {"confirmation_target": target, "build_target": moved[0], "result": head}
    built = ready_provider.calls[-1]
    assert built.finish.target_sha == moved[0] and built.result_sha == head
    assert guards[-1] == (target, tip)  # merge-base(build target, source) and the source tip
    assert not worktree.exists()


def test_conflicting_advance_changes_nothing(repo):
    base, worktree = repo
    commit(worktree, "README.md", "ours\n")
    moved = []
    result = integrate(
        IntegrationService(base), approve_after(lambda: moved.append(commit(base, "README.md", "theirs\n")))
    )
    assert result.status == "blocked" and result.errors[0].code == "WORKTREE_MERGE_CONFLICT"
    assert result.steps["merge"] == "failed" and "Merge the target branch into the task branch" in (
        result.errors[0].fix or ""
    )
    assert git(base, "rev-parse", "HEAD") == moved[0] and worktree.exists() and git(base, "status", "--porcelain") == ""


def test_ff_only_in_the_source_policy_fast_forwards_and_refuses_an_advance(repo):
    base, worktree = repo
    commit(worktree, ".devkit/config.toml", '[integration]\nprovider = "fixture"\n[worktree]\nmerge = "ff-only"\n')
    tip = git(worktree, "rev-parse", "HEAD")
    service = IntegrationService(base)
    assert service.prepare("dev-demo", TASK).request.approval_scope()["merge_method"] == "ff-only"
    moved = []
    refused = integrate(service, approve_after(lambda: moved.append(commit(base, "theirs.txt"))))
    assert refused.status == "blocked" and refused.errors[0].code == "WORKTREE_MERGE_NOT_FF"
    assert git(base, "rev-parse", "HEAD") == moved[0] and worktree.exists()
    git(base, "reset", "-q", "--hard", "HEAD~1")
    result = integrate(IntegrationService(base), approve_after())
    assert result.status == "completed" and git(base, "rev-parse", "HEAD") == tip


def test_target_moved_between_build_and_fast_forward_changes_nothing(repo, monkeypatch):
    base, worktree = repo
    original = service_module.build_result
    moved = []

    def build(*args, **kw):
        value = original(*args, **kw)
        moved.append(commit(base, "racing.txt"))
        return value

    monkeypatch.setattr(service_module, "build_result", build)
    result = integrate(IntegrationService(base), approve_after())
    assert result.status == "blocked" and result.errors[0].code == "INTEGRATION_TARGET_MOVED"
    assert result.steps["merge"] == "not_run" and git(base, "rev-parse", "HEAD") == moved[0] and worktree.exists()


def _receipt(files: dict[str, bytes]) -> str:
    data = {
        "schema": 1,
        "packages": [],
        "selection": {"agents": [], "presets": {}},
        "assets": [],
        "files": {
            name: {"sha256": hashlib.sha256(content).hexdigest(), "mode": 420}
            for name, content in sorted(files.items())
        },
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def test_receipt_and_asset_only_advance_is_absorbed(repo):
    base, _worktree = repo

    def sync():
        write(base, "bundle/skill.md", "v2\n")
        write(base, ".devkit/installation.json", _receipt({"bundle/skill.md": b"v2\n"}))
        git(base, "add", ".")
        git(base, "commit", "-qm", "sync bundle")

    result = integrate(IntegrationService(base), approve_after(sync))
    assert result.status == "completed", result.errors
    assert git(base, "show", "HEAD:bundle/skill.md") == "v2"


@pytest.mark.parametrize(
    "config",
    [
        '[integration]\nprovider = "fixture"\n[worktree]\ndelete_branch = false\n',
        '[integration]\nprovider = "fixture"\n[worktree]\nmerge = "ff-only"\n',
        '[integration]\nprovider = "fixture"\n[worktree]\npull_request = "required"\n',
        '[integration]\nprovider = "other"\n',
        '[integration]\nprovider = "fixture"\n[workflow.approvals]\ndev-integration = "auto"\n',
    ],
)
def test_policy_advance_is_stale(repo, config):
    base, worktree = repo
    moved = []
    result = integrate(
        IntegrationService(base), approve_after(lambda: moved.append(commit(base, ".devkit/config.toml", config)))
    )
    assert result.status == "blocked" and result.errors[0].code == "INTEGRATION_REQUEST_STALE"
    assert git(base, "rev-parse", "HEAD") == moved[0] and worktree.exists()


def test_merge_that_leaves_a_receipt_record_inconsistent_is_refused(tmp_path, repo):
    base, worktree = repo
    lines = b"one\ntwo\nthree\nfour\nfive\n"
    write(base, "managed.md", lines)
    write(base, ".devkit/installation.json", _receipt({"managed.md": lines}))
    git(base, "add", ".")
    git(base, "commit", "-qm", "receipt")
    git(worktree, "merge", "-q", "main")
    ours = lines.replace(b"one", b"ONE")
    write(worktree, "managed.md", ours)
    write(worktree, ".devkit/installation.json", _receipt({"managed.md": ours}))
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "re-sync")
    moved = []

    def action():
        return moved.append(commit(base, "managed.md", lines.replace(b"five", b"FIVE").decode()))

    result = integrate(IntegrationService(base), approve_after(action))
    assert result.status == "blocked" and result.errors[0].code == "INTEGRATION_RECEIPT_CONFLICT"
    assert list(result.errors[0].target_files) == ["managed.md"]
    assert git(base, "rev-parse", "HEAD") == moved[0] and worktree.exists()


def test_receipt_check_skips_untracked_and_parent_inconsistencies(repo):
    base, _ = repo
    write(base, ".devkit/installation.json", _receipt({".claude/x.md": b"a\n", "stale.md": b"recorded\n"}))
    write(base, "stale.md", "different\n")  # already inconsistent on the parent
    git(base, "add", ".")
    git(base, "commit", "-qm", "receipt")
    head = git(base, "rev-parse", "HEAD")
    check_merge(base, head, (head, git(base, "rev-parse", "HEAD~1")))
    write(base, ".devkit/installation.json", "{broken")
    git(base, "commit", "-qam", "broken receipt")
    with pytest.raises(Exception) as raised:
        check_merge(base, git(base, "rev-parse", "HEAD"), (head,))
    assert getattr(raised.value, "code", "") == "INTEGRATION_RECEIPT_CONFLICT"


@pytest.mark.parametrize("disclosure", ["", "two\nlines", "x" * 201])
def test_missing_or_malformed_disclosure_fails_closed(repo, ready_provider, disclosure):
    base, _ = repo
    ready_provider.disclosure = disclosure
    with pytest.raises(ProviderError):
        IntegrationService(base).prepare("dev-demo", TASK)


def test_changed_source_bound_evidence_at_the_build_is_stale(repo, ready_provider, monkeypatch):
    base, worktree = repo
    original = type(ready_provider).check

    def check(self, context):
        value = original(self, context)
        if context.result_sha is not None:
            from dataclasses import replace

            from devkit.integration import Evidence

            return replace(value, evidence=(*value.evidence, Evidence("EXTRA", "changed")))
        return value

    monkeypatch.setattr(type(ready_provider), "check", check)
    result = integrate(IntegrationService(base), approve_after())
    assert result.status == "blocked" and result.errors[0].code == "INTEGRATION_REQUEST_STALE"
    assert worktree.exists()


def test_confirmation_text_states_the_conditions_and_the_disclosure(repo):
    base, _ = repo
    request = IntegrationService(base).prepare("dev-demo", TASK).request
    message = request.confirmation_message()
    lines = message.splitlines()
    assert lines[0] == 'Approve local integration of "dev-demo" into "main" with a merge commit?'
    assert (
        "only if the merge is clean, the integration policy is unchanged and readiness provider"
        ' "fixture" passes again on the merged result; otherwise nothing changes on the target.'
    ) in message.replace("\n", " ")
    assert 'Result check: "fixture checks on the merged result only"' in lines
    assert f'Target: "main" @ {request.context.finish.target_sha} (at confirmation)' in lines
    assert request.to_dict()["merge_method"] == "no-ff"


def test_already_merged_branch_is_a_cleanup_only_request(repo):
    base, worktree = repo
    git(base, "merge", "-q", "--no-ff", "-m", "chore(merge): integrate dev-demo into main", "dev-demo")
    head = git(base, "rev-parse", "HEAD")
    service = IntegrationService(base)
    confirm = approve_after()
    result = integrate(service, confirm)
    assert confirm.messages[0].startswith('Approve cleanup of "dev-demo", already merged into "main"?')
    assert "nothing is merged; only the cleanup below runs" in confirm.messages[0]
    assert result.status == "completed" and result.steps["merge"] == "skipped"
    assert result.request.approval_scope()["already_merged"] is True and result.build_target is None
    assert git(base, "rev-parse", "HEAD") == head and not worktree.exists()
    assert "refs/heads/dev-demo" not in git(base, "show-ref")


def test_diverged_branch_is_refused_with_a_sha_preserving_fix(repo):
    base, _ = repo
    commit(base, "theirs.txt")
    with pytest.raises(MergeNotFastForwardError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    fix = raised.value.fix or ""
    assert "never rebase" in fix and "rebase or merge" not in fix


def test_missing_identity_is_refused_before_the_confirmation(repo):
    base, _ = repo
    git(base, "config", "user.name", "")
    with pytest.raises(CommitFailedError):
        IntegrationService(base).prepare("dev-demo", TASK)


def test_lock_released_within_the_wait_lets_the_build_run(repo, monkeypatch):
    base, _ = repo
    monkeypatch.setattr(service_module, "LOCK_WAIT", 10.0)
    held, release = threading.Event(), threading.Event()

    def hold():
        with file_lock(base / LOCK):
            held.set()
            release.wait(5)

    thread = threading.Thread(target=hold)
    thread.start()
    held.wait(5)
    threading.Timer(0.5, release.set).start()
    result = integrate(IntegrationService(base), approve_after())
    thread.join()
    assert result.status == "completed"


def test_lock_held_past_the_wait_changes_nothing_and_names_resume(repo, monkeypatch):
    base, worktree = repo
    monkeypatch.setattr(service_module, "LOCK_WAIT", 0.2)
    before = git(base, "show-ref")
    service = IntegrationService(base)
    with file_lock(base / LOCK):
        started = time.monotonic()
        result = integrate(service, approve_after())
        assert result.status == "blocked" and result.errors[0].code == "LOCK_HELD"
        assert "integration_resume" in (result.errors[0].fix or "") and git(base, "show-ref") == before
        with pytest.raises(LockHeldError):
            service.resume(result.request.id)
        assert time.monotonic() - started < 5
    assert service.resume(result.request.id).status == "completed" and not worktree.exists()


def test_resume_never_absorbs_a_later_target(repo, monkeypatch):
    base, worktree = repo
    monkeypatch.setattr(service_module, "LOCK_WAIT", 0.2)
    service = IntegrationService(base)
    with file_lock(base / LOCK):
        result = integrate(service, approve_after())
    moved = commit(base, "later.txt")
    resumed = service.resume(result.request.id)
    assert resumed.status == "blocked" and resumed.errors[0].code == "INTEGRATION_REQUEST_STALE"
    assert git(base, "rev-parse", "HEAD") == moved and worktree.exists()


def test_resume_after_a_build_continues_only_onto_the_last_build_target(repo, monkeypatch):
    base, worktree = repo
    original = merging.run_git

    def deny(root, *args, **kw):
        if args[0] == "merge":
            raise GitError("permission denied", returncode=128, stderr="denied")
        return original(root, *args, **kw)

    monkeypatch.setattr(merging, "run_git", deny)
    service = IntegrationService(base)
    result = integrate(service, approve_after())
    assert result.errors[0].code == "WORKTREE_MERGE_FAILED" and result.build_target is not None
    monkeypatch.setattr(merging, "run_git", original)
    moved = commit(base, "later.txt")
    resumed = service.resume(result.request.id)
    assert resumed.status == "blocked" and resumed.errors[0].code == "INTEGRATION_REQUEST_STALE"
    assert git(base, "rev-parse", "HEAD") == moved and worktree.exists()


def test_cleanup_accepts_later_commits_on_the_base_after_the_merge(repo, monkeypatch):
    from devkit.worktree import RemoveFailedError, lifecycle

    base, worktree = repo
    original = lifecycle._remove

    def deny(_base, _path):
        raise RemoveFailedError("permission denied")

    monkeypatch.setattr(lifecycle, "_remove", deny)
    service = IntegrationService(base)
    result = integrate(service, approve_after())
    assert result.status == "partial" and result.steps["merge"] == "completed"
    commit(base, "later.txt")
    monkeypatch.setattr(lifecycle, "_remove", original)
    assert service.resume(result.request.id).status == "completed" and not worktree.exists()
