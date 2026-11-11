from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
from devkit.advisory import ActionMode, AdvisoryError, Level
from spec_support.scope import CAP_A, SPEC, git, make_repo, write

from devkit_spec.base.errors import (
    ScopeNotAWorktreeError,
    ScopeSharedPathError,
    ScopeTimeoutError,
    ScopeTokenExistsError,
    ScopeTokenMismatchError,
)
from devkit_spec.features.policy.services.config import ScopeConfig
from devkit_spec.features.scope import (
    Deadline,
    Record,
    RegisterScopeUseCase,
    ReleaseScopeUseCase,
    Source,
    auto_register,
    default_namespace,
    locate,
    open_session,
    own,
)
from devkit_spec.features.scope.repositories import location as location_module
from devkit_spec.features.scope.repositories.location import SHARED_DIR, TOKEN_FILE, load_token, save_token
from devkit_spec.features.scope.usecases import flow


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "repo")


def test_locate_defaults_and_configuration(repo: Path, tmp_path: Path) -> None:
    location = locate(repo, ScopeConfig(), Deadline(10))
    assert location.shared_path == repo / ".git" / SHARED_DIR
    assert location.namespace == default_namespace(repo / ".git") and len(location.namespace) == 16
    assert location.token_path == repo / ".git" / TOKEN_FILE and not location.linked
    custom = locate(repo, ScopeConfig(shared_path=tmp_path / "shared", namespace="team"), Deadline(10))
    assert (custom.shared_path, custom.namespace) == (tmp_path / "shared", "team")
    linked = tmp_path / "repo-wt-x"
    git(repo, "worktree", "add", "-q", "-b", "x", str(linked))
    other = locate(linked, ScopeConfig(), Deadline(10))
    assert other.linked and (other.shared_path, other.namespace) == (location.shared_path, location.namespace)
    assert other.token_path.parent == repo / ".git/worktrees/repo-wt-x"
    outside = tmp_path / "plain"
    outside.mkdir()
    with pytest.raises(ScopeNotAWorktreeError):
        locate(outside, ScopeConfig(), Deadline(10))


def test_register_release_flow(repo: Path) -> None:
    session = open_session(repo)
    assert own(session) is None, "a worktree without a token owns no record"
    registered = RegisterScopeUseCase().execute(session, SPEC)
    stored = registered.record
    assert (stored.task_id, stored.base_revision, stored.base_ref, stored.worktree, stored.revision) == (
        "SPEC-s",
        git(repo, "rev-parse", "HEAD"),
        "",  # the base checkout itself has no base ref
        str(repo),
        1,
    )
    assert session.location.token_path.read_text().strip() == registered.token
    assert session.location.token_path.stat().st_mode & 0o777 == 0o600
    path = session.location.shared_path / session.location.namespace / "SPEC-s.json"
    data = json.loads(path.read_text())
    assert registered.token not in path.read_text()
    assert (data["schema_version"], data["last_request_id"], data["last_added"], data["last_removed"]) == (1, "", 0, 0)
    mine = own(session)
    assert mine is not None and mine.record == stored

    released = ReleaseScopeUseCase().execute(session)
    assert (released.task, released.revision, released.already) == ("SPEC-s", 1, False)
    assert not session.location.token_path.exists()
    assert ReleaseScopeUseCase().execute(session).registered is False, "releasing again changes nothing"
    assert not (session.location.shared_path / session.location.namespace / "journal.jsonl").exists()


def test_creation_records_declarations_and_dirty_paths_without_a_committed_range(repo: Path, tmp_path: Path) -> None:
    linked = tmp_path / "repo-wt-dev-s"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(linked))
    write(linked, "docs/decisions/ADR-new.md", "---\nid: ADR-new\n---\n")  # untracked handoff output
    write(linked, "src/b/b.py", "b = 2\n")
    git(linked, "add", "src/b/b.py")  # staged
    write(linked, "src/shared.py", "s = 2\n")  # unstaged
    write(linked, "notes/odd:name.md", "x\n")  # outside the path contract
    session = open_session(linked)
    record = RegisterScopeUseCase().execute(session, SPEC).record
    observed = [path.path for path in record.scopes if path.source is Source.OBSERVED]
    assert observed == ["docs/decisions/ADR-new.md", "src/b/b.py", "src/shared.py"]
    declared = {(path.source, path.path) for path in record.scopes if path.source is not Source.OBSERVED}
    assert (Source.DECLARED_CODE, "src/a") in declared and (Source.DECLARED_DOC, CAP_A) in declared
    reasons = [(item.value, item.reason, item.source) for item in record.unresolved]
    assert ("notes/odd:name.md", "invalid-path", Source.OBSERVED) in reasons, "an invalid dirty path is never dropped"
    assert not {item.reason for item in record.unresolved} & {
        "missing-base-ref",
        "missing-base-revision",
        "unknown-base-revision",
    }, "creation reads no committed range"
    assert (record.base_revision, record.base_ref) == (git(linked, "rev-parse", "HEAD"), "refs/heads/main")
    assert all(path.first_seen for path in record.scopes)


def test_a_dirty_path_timeout_fails_the_registration(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    linked = tmp_path / "repo-wt-dev-s"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(linked))
    session = open_session(linked)
    listing = flow.dirty

    def expired(root: Path, deadline: Deadline) -> list[str]:
        return listing(root, Deadline(0))  # the command's deadline runs out while Git lists the dirty paths

    monkeypatch.setattr(flow, "dirty", expired)
    with pytest.raises(ScopeTimeoutError):
        RegisterScopeUseCase().execute(session, SPEC)
    assert not session.location.token_path.exists()
    assert session.registry.query(session.location.namespace, Deadline(5))[0] == [], "nothing is registered"


def test_second_registration_in_a_worktree_is_refused(repo: Path) -> None:
    session = open_session(repo)
    RegisterScopeUseCase().execute(session, SPEC, "first")
    with pytest.raises(ScopeTokenExistsError):
        RegisterScopeUseCase().execute(session, SPEC, "second")
    assert [item.task_id for item in session.registry.query(session.location.namespace, Deadline(5))[0]] == ["first"]


def test_a_registration_that_loses_the_token_race_is_rolled_back(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    session = open_session(repo)
    namespace = session.location.namespace
    winner, _ = session.registry.register(Record(namespace=namespace, task_id="first", worktree=str(repo)), Deadline(5))

    def raced(path: Path, token: str) -> None:  # the concurrent registration saves its token first
        save_token(path, winner)
        save_token(path, token)

    monkeypatch.setattr(flow, "save_token", raced)
    with pytest.raises(ScopeTokenExistsError) as raised:
        RegisterScopeUseCase().execute(session, SPEC, "second")
    assert raised.value.details == ()
    records = session.registry.query(namespace, Deadline(5))[0]
    assert [(item.task_id, item.shared_worktree) for item in records] == [("first", False)], (
        "the losing record is removed and the winner no longer shares the worktree"
    )
    mine = own(session)
    assert mine is not None and mine.record.task_id == "first", "the winner keeps its token"


def test_token_files_are_complete_or_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    path = tmp_path / "git" / TOKEN_FILE
    path.parent.mkdir()
    stale, fresh, other = (path.parent / name for name in (f".{TOKEN_FILE}-ab_12cd3", f".{TOKEN_FILE}-zz99yy00", ".x"))
    for leftover in (stale, fresh, other):
        leftover.write_text("live-token\n")
    old = time.time() - 3600
    os.utime(stale, (old, old))
    os.utime(other, (old, old))
    assert load_token(path) is None
    assert not stale.exists() and fresh.exists() and other.exists(), "only old files of the temp pattern are removed"
    path.write_text("partial")
    assert load_token(path) is None, "a token without its newline is incomplete"
    path.unlink()

    def no_links(*args: object) -> None:
        raise OSError(1, "Operation not permitted")

    monkeypatch.setattr(location_module.os, "link", no_links)
    save_token(path, "one")
    assert load_token(path) == "one" and path.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        save_token(path, "two")
    monkeypatch.undo()

    session = open_session(repo)
    session.location.token_path.write_text("")  # an interrupted save without hard links
    with pytest.raises(ScopeTokenExistsError):
        RegisterScopeUseCase().execute(session, SPEC)
    assert ReleaseScopeUseCase().execute(session).registered is False and not session.location.token_path.exists()
    assert RegisterScopeUseCase().execute(session, SPEC).record.task_id == "SPEC-s"


def test_save_token_is_exclusive(tmp_path: Path) -> None:
    path = tmp_path / "git" / TOKEN_FILE
    save_token(path, "one")
    with pytest.raises(FileExistsError):
        save_token(path, "two")
    assert path.read_text() == "one\n" and path.stat().st_mode & 0o777 == 0o600
    assert [entry.name for entry in path.parent.iterdir()] == [TOKEN_FILE], "no temporary file is left"


def test_a_failed_rollback_is_a_detail_of_the_original_error(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    session = open_session(repo)

    def unwritable(path: Path, token: str) -> None:
        raise PermissionError("read-only git directory")

    monkeypatch.setattr(flow, "save_token", unwritable)
    with pytest.raises(ScopeSharedPathError) as raised:
        RegisterScopeUseCase().execute(session, SPEC)
    assert raised.value.details == ()
    assert session.registry.query(session.location.namespace, Deadline(5))[0] == [], "the record is rolled back"

    def timed_out(*args: object) -> None:
        raise ScopeTimeoutError("waiting for the namespace lock exceeded the scope timeout of 5s")

    monkeypatch.setattr(session.registry, "release", timed_out)
    with pytest.raises(ScopeSharedPathError) as raised:
        RegisterScopeUseCase().execute(session, SPEC)
    assert "read-only git directory" in raised.value.message, "the original error is kept"
    assert len(raised.value.details) == 1 and "SPEC-s could not be removed" in raised.value.details[0]
    assert "scope timeout" in raised.value.details[0]


def test_release_of_a_named_task(repo: Path) -> None:
    session = open_session(repo)
    # Without a token nothing of this worktree is registered: release succeeds and changes nothing (its --help).
    nothing = ReleaseScopeUseCase().execute(session, "SPEC-s")
    assert (nothing.registered, nothing.already) == (False, False)
    RegisterScopeUseCase().execute(session, SPEC)
    session.registry.register(
        Record(namespace=session.location.namespace, task_id="SPEC-x", worktree="/wt/x"), Deadline(5)
    )
    with pytest.raises(ScopeTokenMismatchError):
        ReleaseScopeUseCase().execute(session, "SPEC-x")
    assert ReleaseScopeUseCase().execute(session, "SPEC-nope").already and session.location.token_path.exists()
    assert ReleaseScopeUseCase().execute(session, "SPEC-s").task == "SPEC-s"


def test_an_unreadable_own_record_keeps_the_token(repo: Path) -> None:
    session = open_session(repo)
    RegisterScopeUseCase().execute(session, SPEC)
    path = session.location.shared_path / session.location.namespace / "SPEC-s.json"
    path.write_text(path.read_text() + "trailing garbage")  # still names the token hash
    for call in (
        lambda: ReleaseScopeUseCase().execute(session),
        lambda: ReleaseScopeUseCase().execute(session, "SPEC-s"),
        lambda: own(session),
    ):
        with pytest.raises(AdvisoryError) as raised:
            call()
        error = raised.value
        assert (error.code, error.level, error.mode) == (
            "SPEC_SCOPE_RECORD_INVALID",
            Level.ERROR,
            ActionMode.INTERACTION,
        )
        assert error.target_files == (session.location.shown(path),) and error.details == ("SPEC-s.json: parse",)
        assert "token is kept" in error.message
    assert session.location.token_path.exists(), "the token of a record that cannot be read is kept"


def test_unrelated_unreadable_records_do_not_block_release(repo: Path) -> None:
    session = open_session(repo)
    RegisterScopeUseCase().execute(session, SPEC)
    directory = session.location.shared_path / session.location.namespace
    (directory / "SPEC-other.json").write_text("{not json")  # another task's corrupt record
    assert ReleaseScopeUseCase().execute(session, "SPEC-gone").already and session.location.token_path.exists()
    with pytest.raises(AdvisoryError) as raised:
        ReleaseScopeUseCase().execute(session, "SPEC-other")  # that task's own record file is the unreadable one
    assert raised.value.target_files == (session.location.shown(directory / "SPEC-other.json"),)
    released = ReleaseScopeUseCase().execute(session, "SPEC-s")
    assert (released.task, released.already) == ("SPEC-s", False) and not session.location.token_path.exists()

    RegisterScopeUseCase().execute(session, SPEC)
    (directory / "SPEC-s.json").unlink()  # the record is gone: the token is orphaned
    assert own(session) is None, "an orphaned token owns no record"
    released = ReleaseScopeUseCase().execute(session)
    assert released.already and not session.location.token_path.exists(), "the orphaned token is removed"


def test_a_shared_worktree_is_a_creation_notice(repo: Path) -> None:
    session = open_session(repo)
    session.registry.register(
        Record(namespace=session.location.namespace, task_id="SPEC-x", worktree=str(repo)), Deadline(5)
    )
    registered = RegisterScopeUseCase().execute(session, SPEC)
    assert [notice.code for notice in registered.notices] == ["SPEC_SCOPE_SHARED_WORKTREE"]


def test_auto_register_only_in_a_linked_worktree_at_either_level(repo: Path, tmp_path: Path) -> None:
    assert auto_register(repo, SPEC) is None, "the base checkout never registers"
    linked = tmp_path / "repo-wt-s"
    git(repo, "worktree", "add", "-q", "-b", "s", str(linked))
    registered = auto_register(linked, SPEC)
    assert registered is not None and registered.notices == []
    assert registered.record.worktree == str(linked)
    session = open_session(linked)
    assert not (session.location.shared_path / session.location.namespace / "journal.jsonl").exists()
    assert auto_register(linked, SPEC) is None, "automatic registration failures are silent"

    for level in ("required", "auto"):
        write(linked, ".devkit/config.toml", f'[tool.spec]\nworktree = "{level}"\n')
        ReleaseScopeUseCase().execute(session)
        assert auto_register(linked, SPEC) is not None, level
    plain = tmp_path / "plain"
    write(plain, ".devkit/config.toml", "")
    assert auto_register(plain, "specs/x") is None
