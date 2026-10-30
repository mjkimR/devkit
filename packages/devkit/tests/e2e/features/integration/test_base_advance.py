"""The approving call absorbs target commits that land after its own preparation (``SPEC-integration-follow-ups``),
and preparation checks the prospective merge of a target that moved before it (``SPEC-integration-merge-moved-target``).
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path

import devkit_agt.features.integration.usecases.service as service_module
import pytest
from devkit.advisory import ActionMode, Actor
from devkit_agt.features.integration import IntegrationService, ProviderError, Task
from devkit_agt.features.integration.models.errors import ReceiptConflictError
from devkit_agt.features.integration.repositories.receipts import check_merge
from devkit_agt.features.worktree import (
    CommitFailedError,
    GitUnsupportedError,
    MergeConflictError,
    MergeNotFastForwardError,
)
from devkit_core.core.locks import file_lock
from testsupport.rules import git, write

TASK = Task("session", "fixture-task")
LOCK = ".git/devkit-integration.lock"


def commit(root: Path, rel: str, text: str = "x\n") -> str:
    write(root, rel, text)
    git(root, "add", ".")
    git(root, "commit", "-qm", f"change {rel}")
    return git(root, "rev-parse", "HEAD")


def integrate(service: IntegrationService, action=None):
    """One Host-approved CLI invocation; ``action`` runs after the call's own preparation, before its build."""
    digest = service.prepare("dev-demo", TASK).request.digest
    if action is not None:
        prepare = service.prepare

        def prepared(*args, **kwargs):
            result = prepare(*args, **kwargs)
            action()
            return result

        service.prepare = prepared  # type: ignore[method-assign]
    return service.execute_cli("dev-demo", TASK, expected_digest=digest)


def test_clean_advance_after_preparation_lands_a_merge_commit(repo, ready_provider, monkeypatch):
    base, worktree = repo
    tip, target = git(worktree, "rev-parse", "HEAD"), git(base, "rev-parse", "HEAD")
    guards = []
    original = service_module.run_finish_guards
    monkeypatch.setattr(service_module, "run_finish_guards", lambda *args: guards.append(args[2:]) or original(*args))
    moved = []
    result = integrate(IntegrationService(base), lambda: moved.append(commit(base, "theirs.txt")))
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
    result = integrate(IntegrationService(base), lambda: moved.append(commit(base, "README.md", "theirs\n")))
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
    refused = integrate(service, lambda: moved.append(commit(base, "theirs.txt")))
    assert refused.status == "blocked" and refused.errors[0].code == "WORKTREE_MERGE_NOT_FF"
    assert git(base, "rev-parse", "HEAD") == moved[0] and worktree.exists()
    git(base, "reset", "-q", "--hard", "HEAD~1")
    result = integrate(IntegrationService(base))
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
    result = integrate(IntegrationService(base))
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

    result = integrate(IntegrationService(base), sync)
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
    result = integrate(IntegrationService(base), lambda: moved.append(commit(base, ".devkit/config.toml", config)))
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

    result = integrate(IntegrationService(base), action)
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

            from devkit_agt.features.integration import Evidence

            return replace(value, evidence=(*value.evidence, Evidence("EXTRA", "changed")))
        return value

    monkeypatch.setattr(type(ready_provider), "check", check)
    result = integrate(IntegrationService(base))
    assert result.status == "blocked" and result.errors[0].code == "INTEGRATION_REQUEST_STALE"
    assert worktree.exists()


def test_prepared_scope_states_the_target_and_the_disclosure(repo):
    base, _ = repo
    request = IntegrationService(base).prepare("dev-demo", TASK).request
    scope = request.approval_scope()
    assert scope["readiness"] == {"disclosure": "fixture checks on the merged result only"}
    assert scope["target"] == {"branch": "main", "sha": request.context.finish.target_sha}
    assert scope["merge_method"] == "no-ff" and scope["already_merged"] is False


def test_already_merged_branch_is_a_cleanup_only_request(repo):
    base, worktree = repo
    git(base, "merge", "-q", "--no-ff", "-m", "chore(merge): integrate dev-demo into main", "dev-demo")
    head = git(base, "rev-parse", "HEAD")
    service = IntegrationService(base)
    assert service.prepare("dev-demo", TASK).request.approval_scope()["already_merged"] is True
    result = integrate(service)
    assert result.status == "completed" and result.steps["merge"] == "skipped"
    assert result.request.approval_scope()["already_merged"] is True and result.build_target is None
    assert git(base, "rev-parse", "HEAD") == head and not worktree.exists()
    assert "refs/heads/dev-demo" not in git(base, "show-ref")


def test_moved_target_before_preparation_lands_a_merge_without_a_base_merge(repo, ready_provider, monkeypatch):
    """``ADR-moved-target-merge``: the source need not contain a conflict-free moved target."""
    base, worktree = repo
    tip, cut = git(worktree, "rev-parse", "HEAD"), git(base, "rev-parse", "HEAD")
    moved = commit(base, "theirs.txt")
    guards = []
    original = service_module.run_finish_guards
    monkeypatch.setattr(service_module, "run_finish_guards", lambda *args: guards.append(args[2:]) or original(*args))
    service = IntegrationService(base)
    request = service.prepare("dev-demo", TASK).request
    prepared = ready_provider.calls[-1]
    assert request.context.result_sha is None and request.context.finish.target_sha == moved
    assert prepared.result_sha is not None and prepared.finish.target_sha == moved
    assert git(base, "rev-parse", f"{prepared.result_sha}^1", f"{prepared.result_sha}^2").split() == [moved, tip]
    assert guards[-1] == (cut, tip)  # merge-base(target, source) and the source tip
    assert prepared.result_sha not in git(base, "for-each-ref", "--format=%(objectname)")
    result = integrate(service)
    assert result.status == "completed", result.errors
    head = git(base, "rev-parse", "HEAD")
    assert git(base, "rev-parse", "HEAD^1", "HEAD^2").split() == [moved, tip]
    assert result.build() == {"confirmation_target": moved, "build_target": moved, "result": head}
    assert result.request.context.finish.source_sha == tip and not worktree.exists()


def test_moved_target_conflict_refuses_at_prepare_with_nothing_changed(repo):
    base, worktree = repo
    tip = commit(worktree, "README.md", "ours\n")
    moved = commit(base, "README.md", "theirs\n")
    before = git(base, "show-ref")
    with pytest.raises(MergeConflictError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert "resolve the conflict" in (raised.value.fix or "") and "never rebase" in (raised.value.fix or "")
    assert git(base, "show-ref") == before and git(base, "rev-parse", "HEAD") == moved
    assert git(base, "rev-parse", "dev-demo") == tip and worktree.exists()
    assert git(worktree, "status", "--porcelain") == "" and git(base, "status", "--porcelain") == ""


@pytest.mark.parametrize(
    ("config", "branch_kept"),
    [
        ('[integration]\nprovider = "fixture"\n[workflow.approvals]\ndev-integration = "auto"\n', False),
        ('[integration]\nprovider = "fixture"\n[worktree]\ndelete_branch = false\n', True),
    ],
)
def test_moved_target_that_changed_integration_policy_integrates(repo, config, branch_kept):
    base, worktree = repo
    commit(base, ".devkit/config.toml", config)
    result = integrate(IntegrationService(base))
    assert result.status == "completed", result.errors
    assert ("refs/heads/dev-demo" in git(base, "show-ref")) is branch_kept and not worktree.exists()
    assert result.authority == ("policy" if "auto" in config else "host-conversation")


def test_moved_target_that_leaves_a_receipt_record_inconsistent_refuses_at_prepare(repo):
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
    moved = commit(base, "managed.md", lines.replace(b"five", b"FIVE").decode())
    with pytest.raises(ReceiptConflictError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert list(raised.value.target_files) == ["managed.md"] and "prepare again" in (raised.value.fix or "")
    assert git(base, "rev-parse", "HEAD") == moved and worktree.exists()


def test_moved_target_digest_does_not_depend_on_identity_or_time_zone(repo, monkeypatch):
    base, worktree = repo
    commit(base, "theirs.txt")
    digest = IntegrationService(base).prepare("dev-demo", TASK).request.digest
    monkeypatch.setenv("TZ", "Pacific/Kiritimati")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Someone Else")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "else@example.invalid")
    assert IntegrationService(base).prepare("dev-demo", TASK).request.digest == digest
    result = IntegrationService(base).execute_cli("dev-demo", TASK, expected_digest=digest)
    assert result.status == "completed", result.errors
    assert not worktree.exists()


def test_moved_target_under_ff_only_still_refuses_at_prepare(repo):
    base, worktree = repo
    commit(worktree, ".devkit/config.toml", '[integration]\nprovider = "fixture"\n[worktree]\nmerge = "ff-only"\n')
    moved = commit(base, "theirs.txt")
    with pytest.raises(MergeNotFastForwardError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert raised.value.actor is Actor.TOOL and raised.value.mode is ActionMode.AUTO
    fix = raised.value.fix or ""
    assert "never rebase" in fix and "rebase or merge" not in fix
    assert git(base, "rev-parse", "HEAD") == moved and worktree.exists()


def test_moved_target_needs_merge_tree_support(repo, monkeypatch):
    import devkit_agt.features.worktree.services.merging as merging

    base, _ = repo
    commit(base, "theirs.txt")
    monkeypatch.setattr(merging, "git_version", lambda _base: (2, 37))
    with pytest.raises(GitUnsupportedError):
        IntegrationService(base).prepare("dev-demo", TASK)


def test_moved_target_without_identity_is_refused_before_the_confirmation(repo):
    base, _ = repo
    commit(base, "theirs.txt")
    git(base, "config", "user.name", "")
    with pytest.raises(CommitFailedError):
        IntegrationService(base).prepare("dev-demo", TASK)


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
    result = integrate(IntegrationService(base))
    thread.join()
    assert result.status == "completed"


def test_lock_held_past_the_wait_changes_nothing_and_names_the_rerun(repo, monkeypatch):
    base, worktree = repo
    monkeypatch.setattr(service_module, "LOCK_WAIT", 0.2)
    before = git(base, "show-ref")
    service = IntegrationService(base)
    with file_lock(base / LOCK):
        started = time.monotonic()
        result = integrate(service)
        assert result.status == "blocked" and result.errors[0].code == "LOCK_HELD"
        assert "devkit integration integrate" in (result.errors[0].fix or "") and git(base, "show-ref") == before
        assert time.monotonic() - started < 5
    assert integrate(IntegrationService(base)).status == "completed" and not worktree.exists()


def test_cleanup_accepts_later_commits_on_the_base_after_the_merge(repo, monkeypatch):
    import devkit_agt.features.worktree.usecases.lifecycle as lifecycle
    from devkit_agt.features.worktree import RemoveFailedError

    base, worktree = repo
    original = lifecycle._remove

    def deny(_base, _path):
        raise RemoveFailedError("permission denied")

    monkeypatch.setattr(lifecycle, "_remove", deny)
    service = IntegrationService(base)
    result = integrate(service)
    assert result.status == "partial" and result.steps["merge"] == "completed"
    commit(base, "later.txt")
    monkeypatch.setattr(lifecycle, "_remove", original)
    assert integrate(IntegrationService(base)).status == "completed" and not worktree.exists()


def test_post_merge_metadata_rewrite_completes_cleanup(repo):
    base, worktree = repo
    hook = base / ".git/hooks/post-merge"
    hook.write_text("#!/bin/sh\ngit -c core.hooksPath=/dev/null commit --amend -qm 'rewritten metadata'\n")
    hook.chmod(0o755)
    result = integrate(IntegrationService(base))
    assert result.status == "completed", result.errors
    assert result.result_sha == git(base, "rev-parse", "HEAD")
    assert not worktree.exists()


@pytest.mark.parametrize("mutation", ["content", "parents", "source", "policy"])
def test_post_merge_mutation_preserves_task(repo, mutation):
    base, worktree = repo
    scripts = {
        "content": "echo changed > ready.txt\ngit add ready.txt\ngit commit --amend -qm changed",
        "parents": 'replacement=$(git commit-tree HEAD^{tree} -p HEAD^2 -p HEAD^1 -m reordered)\ngit update-ref refs/heads/main "$replacement"',
        "source": "git commit --amend -qm rewritten\ngit update-ref refs/heads/dev-demo HEAD",
        "policy": "git commit --amend -qm rewritten\nprintf '\n[workflow.approvals]\ndev-integration = \"auto\"\n' >> .devkit/config.toml",
    }
    hook = base / ".git/hooks/post-merge"
    hook.write_text("#!/bin/sh\n" + scripts[mutation] + "\n")
    hook.chmod(0o755)
    service = IntegrationService(base)
    result = integrate(service)
    assert result.status in {"blocked", "partial"}
    assert result.errors[0].code == "INTEGRATION_REQUEST_STALE"
    assert worktree.exists()
    assert git(base, "rev-parse", "--verify", "refs/heads/dev-demo")


def test_post_merge_metadata_rewrite_then_a_fresh_call_completes_cleanup(repo, monkeypatch):
    import devkit_agt.features.worktree.usecases.lifecycle as lifecycle
    from devkit_agt.features.worktree import RemoveFailedError

    base, worktree = repo
    hook = base / ".git/hooks/post-merge"
    hook.write_text("#!/bin/sh\ngit -c core.hooksPath=/dev/null commit --amend -qm rewritten\n")
    hook.chmod(0o755)
    original = lifecycle._remove

    def deny(_base, _path):
        raise RemoveFailedError("permission denied")

    monkeypatch.setattr(lifecycle, "_remove", deny)
    service = IntegrationService(base)
    result = integrate(service)
    assert result.status == "partial" and result.steps["merge"] == "completed"
    assert result.result_sha == git(base, "rev-parse", "HEAD")
    commit(base, "later.txt")
    monkeypatch.setattr(lifecycle, "_remove", original)
    assert integrate(IntegrationService(base)).status == "completed" and not worktree.exists()


def _projection(side: str) -> str:
    """A receipt whose only record is an untracked projection's, so ``check_merge`` has nothing tracked to compare."""
    return _receipt({".agents/skill.md": side.encode()})


def _diverge(base: Path, worktree: Path, files: dict[str, tuple[str, str, str]]) -> tuple[str, str]:
    """Commit each file's base text on the target and merge it into the branch, then the source and target texts."""
    for side, root in ((0, base), (1, worktree), (2, base)):
        if side == 1:
            git(worktree, "merge", "-q", "main")
        for rel, texts in files.items():
            write(root, rel, texts[side])
        git(root, "add", ".")
        git(root, "commit", "-qm", f"side {side}")
    return git(worktree, "rev-parse", "HEAD"), git(base, "rev-parse", "HEAD")


def test_receipt_only_conflict_is_seeded_from_the_target_and_disclosed(repo, ready_provider):
    """``ADR-generated-conflicts-in-prepared-merge``: prepare and integrate land one seeded tree and disclose it."""
    base, worktree = repo
    receipt = ".devkit/installation.json"
    tip, moved = _diverge(
        base, worktree, {receipt: (_projection("base"), _projection("source"), _projection("target"))}
    )
    service = IntegrationService(base)
    prepared = service.prepare("dev-demo", TASK)
    prospective = ready_provider.calls[-1].result_sha
    assert prospective is not None
    assert git(base, "show", f"{prospective}:{receipt}") == _projection("target").rstrip("\n")
    assert [(item.id, item.paths, item.seed, item.kept) for item in prepared.seeded] == [
        ("devkit-receipt", (receipt,), "ours", "target")
    ]
    generated = prepared.compact_dict()["generated"]
    assert generated["regenerate"].endswith("devkit generated regen devkit-receipt")
    (notice,) = prepared.notices
    assert notice.code == "INTEGRATION_GENERATED_SEEDED" and notice.target_files == (receipt,)
    assert "devkit generated regen devkit-receipt" in (notice.fix or "") and "commit" in (notice.fix or "")
    result = integrate(service)
    assert result.status == "completed", result.errors
    assert git(base, "rev-parse", "HEAD^1", "HEAD^2").split() == [moved, tip]
    assert git(base, "rev-parse", "HEAD^{tree}") == git(base, "rev-parse", f"{prospective}^{{tree}}")
    assert result.compact_dict()["generated"] == generated
    assert [item.code for item in result.notices] == ["INTEGRATION_GENERATED_SEEDED"]


def test_project_artifact_seeded_from_the_source(repo):
    base, worktree = repo
    write(base, ".devkit/generated.toml", "[artifacts.lock]\npaths = ['uv.lock']\ncommand = 'true'\nseed = 'theirs'\n")
    git(base, "add", ".")
    git(base, "commit", "-qm", "register the lock")
    _diverge(base, worktree, {"uv.lock": ("base\n", "source\n", "target\n")})
    result = integrate(IntegrationService(base))
    assert result.status == "completed", result.errors
    assert git(base, "show", "HEAD:uv.lock") == "source"
    assert result.compact_dict()["generated"]["seeded"] == [
        {"id": "lock", "paths": ["uv.lock"], "seed": "theirs", "kept": "source"}
    ]


@pytest.mark.parametrize(
    ("other", "detail"),
    [
        ("README.md", "README.md: owned by no generated artifact"),
        ("AGENTS.md", "AGENTS.md: read by devkit-receipt"),
    ],
)
def test_receipt_conflict_beside_another_conflict_refuses_with_nothing_changed(repo, other, detail):
    base, worktree = repo
    tip, moved = _diverge(
        base,
        worktree,
        {
            ".devkit/installation.json": (_projection("base"), _projection("source"), _projection("target")),
            other: ("base\n", "source\n", "target\n"),
        },
    )
    before = git(base, "show-ref")
    with pytest.raises(MergeConflictError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert raised.value.details == (detail,) and "Merge the target branch" in (raised.value.fix or "")
    assert git(base, "show-ref") == before and git(base, "rev-parse", "HEAD") == moved
    assert git(base, "rev-parse", "dev-demo") == tip and worktree.exists()
    assert git(worktree, "status", "--porcelain") == "" and git(base, "status", "--porcelain") == ""


def test_seeded_receipt_that_leaves_a_record_inconsistent_refuses(repo, ready_provider):
    base, worktree = repo
    lines = b"one\ntwo\n"
    ours = b"ONE\ntwo\n"
    receipt = _receipt({"managed.md": lines})
    tip, moved = _diverge(
        base,
        worktree,
        {
            "managed.md": (lines.decode(), ours.decode(), lines.decode()),
            ".devkit/installation.json": (
                receipt,
                _receipt({"managed.md": ours}),
                receipt.replace('"mode": 420', '"mode": 493'),
            ),
        },
    )
    with pytest.raises(ReceiptConflictError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert list(raised.value.target_files) == ["managed.md"]
    prospective = ready_provider.calls[-1].result_sha
    assert git(base, "show", f"{prospective}:.devkit/installation.json") == git(
        base, "show", f"{moved}:.devkit/installation.json"
    )
    assert git(base, "rev-parse", "HEAD") == moved and git(base, "rev-parse", "dev-demo") == tip


def test_registry_committed_at_the_target_decides(repo):
    base, worktree = repo
    write(base, ".devkit/generated.toml", "[artifacts.devkit-receipt]\nenabled = false\n")
    git(base, "add", ".")
    git(base, "commit", "-qm", "disable the receipt artifact")
    _diverge(
        base,
        worktree,
        {".devkit/installation.json": (_projection("base"), _projection("source"), _projection("target"))},
    )
    with pytest.raises(MergeConflictError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert raised.value.details == (".devkit/installation.json: owned by no generated artifact",)


class _Lifecycle:
    """The part of an acceptance lifecycle a preparation reads before the build refuses."""

    approval_gate = "dev-integration"


@pytest.mark.parametrize("composed", ["lifecycle", "fresh preparation"])
def test_composed_acceptance_preparation_settles_no_conflict(repo, composed):
    """Composed acceptance prepares with its lifecycle (and re-prepares with ``settle_generated=False``) without a
    settler, so a receipt-only conflict still refuses with nothing changed."""
    base, worktree = repo
    tip, moved = _diverge(
        base,
        worktree,
        {".devkit/installation.json": (_projection("base"), _projection("source"), _projection("target"))},
    )
    before = git(base, "show-ref")
    service = IntegrationService(base)
    with pytest.raises(MergeConflictError):
        if composed == "lifecycle":
            service._prepare("dev-demo", TASK, lifecycle=_Lifecycle())  # type: ignore[arg-type]
        else:
            service._prepare("dev-demo", TASK, settle_generated=False)
    assert git(base, "show-ref") == before and git(base, "rev-parse", "HEAD") == moved
    assert git(base, "rev-parse", "dev-demo") == tip and git(base, "status", "--porcelain") == ""
