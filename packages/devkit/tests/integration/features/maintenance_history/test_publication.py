from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

import pytest
from devkit_agt.features.maintenance_history.models.errors import (
    AuthorityMissing,
    BranchForeign,
    BranchMissing,
    Deferred,
    EvidenceChanged,
    PublishFailed,
    PublishUnknown,
    RecordCollision,
    RunMissing,
)
from devkit_agt.features.maintenance_history.models.records import ROOT_COMMIT, run_path
from devkit_agt.features.maintenance_history.repositories.github import Response
from devkit_agt.features.maintenance_history.repositories.local import read_record, write_record
from devkit_agt.features.maintenance_history.services.publication import GitHubHistory, publish, update
from devkit_agt.features.maintenance_history.services.runs import finish, start
from testsupport.history import FakeGitHub


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for args in (("init", "-q"), ("config", "user.name", "Test"), ("config", "user.email", "test@example.invalid")):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    (root / "tracked").write_text("initial")
    subprocess.run(["git", "-C", str(root), "add", "tracked"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "initial"], check=True)
    return root


def ready(repo: Path, tmp_path: Path, name: str = "one") -> Path:
    report = tmp_path / (name + ".md")
    result = start(
        repo,
        repository="owner/repo",
        playbook="weekly-report",
        scope=name,
        into=tmp_path / "runs",
        report=report,
        zone="UTC",
        supersedes=(),
        prior_runs=(),
    )
    run = Path(result.data["path"])
    report.write_text("safe report " + name)
    finish(run, outcome="completed", result="no findings", report=None, applied_commits=(), follow_ups=())
    return run


def history(fake: FakeGitHub) -> GitHubHistory:
    return GitHubHistory("owner/repo", "maintenance-history", fake)


def test_initialize_validate_foreign_and_authority() -> None:
    fake = FakeGitHub()
    with pytest.raises(AuthorityMissing):
        history(fake).initialize("")
    assert not fake.calls
    result = history(fake).initialize("simulated test authority")
    assert result.data["head_sha"] == ROOT_COMMIT
    count = sum(call[0] == "POST" for call in fake.calls)
    history(fake).initialize("simulated test authority")
    assert count == sum(call[0] == "POST" for call in fake.calls)
    fake.head = "a" * 40
    with pytest.raises(BranchForeign):
        history(fake).initialize("simulated test authority")


def test_atomic_publish_duplicate_get_list_and_immutable_record(repo: Path, tmp_path: Path) -> None:
    fake = FakeGitHub()
    history(fake).initialize("simulated")
    run = ready(repo, tmp_path)
    refs = subprocess.check_output(["git", "-C", str(repo), "for-each-ref"])
    index = (repo / ".git/index").read_bytes()
    frozen = read_record(run)
    result = publish(history(fake), run, "simulated", (), "owner/repo")
    assert len(fake.indexes()) == 1
    assert fake.indexes()[0]["result"] == "no findings"
    posts = sum(call[0] in ("POST", "PATCH") for call in fake.calls)
    assert publish(history(fake), run, "simulated", (), "owner/repo").data == result.data
    assert posts == sum(call[0] in ("POST", "PATCH") for call in fake.calls)
    path = run_path(run.name) + "/record.json"
    published = json.loads(fake.files()[path])
    assert "publication" not in published and "attempts" not in published
    assert published["report"] == frozen["report"]
    fetched = history(fake).get(run.name, "report.md")
    assert base64.b64decode(fetched.data["content"]) == Path(frozen["report"]["path"]).read_bytes()
    assert history(fake).listing("weekly-report", None, None, False, 20).data["count"] == 1
    assert index == (repo / ".git/index").read_bytes()
    assert refs == subprocess.check_output(["git", "-C", str(repo), "for-each-ref"])


def test_interleaved_writers_rebuild_index_without_losing_either(repo: Path, tmp_path: Path) -> None:
    fake = FakeGitHub()
    history(fake).initialize("simulated")
    first, second = ready(repo, tmp_path, "first"), ready(repo, tmp_path, "second")

    def interleave(method: str, path: str, payload: dict | None) -> Response | None:
        if method == "PATCH":
            fake.hook = None
            publish(history(fake), second, "simulated", (), "owner/repo")
        return None

    fake.hook = interleave
    publish(history(fake), first, "simulated", (), "owner/repo")
    assert {line["run_id"] for line in fake.indexes()} == {first.name, second.name}
    assert run_path(first.name) + "/record.json" in fake.files()
    assert run_path(second.name) + "/record.json" in fake.files()


def test_lost_ref_response_then_retry_inspects_without_republishing(repo: Path, tmp_path: Path) -> None:
    fake = FakeGitHub()
    history(fake).initialize("simulated")
    run = ready(repo, tmp_path)

    def lost(method: str, path: str, payload: dict | None) -> Response | None:
        if method == "PATCH":
            assert payload
            fake.head = payload["sha"]
            fake.hook = None
            raise subprocess.TimeoutExpired("gh", 30)
        return None

    fake.hook = lost
    with pytest.raises(PublishUnknown):
        publish(history(fake), run, "simulated", (), "owner/repo")
    assert read_record(run)["publication"] == "unknown"
    mutations = sum(call[0] in ("POST", "PATCH") for call in fake.calls)
    publish(history(fake), run, "simulated", (), "owner/repo")
    assert read_record(run)["publication"] == "published"
    assert mutations == sum(call[0] in ("POST", "PATCH") for call in fake.calls)


@pytest.mark.parametrize(
    ("method", "target", "status", "headers"),
    [
        ("GET", "", 403, {"x-ratelimit-remaining": "0"}),
        ("POST", "git/blobs", 502, {}),
        ("GET", "", 429, {"retry-after": "120"}),
    ],
)
def test_rate_limit_and_object_failures_defer(
    repo: Path, tmp_path: Path, method: str, target: str, status: int, headers: dict[str, str]
) -> None:
    fake = FakeGitHub()
    history(fake).initialize("simulated")
    run = ready(repo, tmp_path)
    fake.hook = lambda current, path, payload: (
        Response(status, headers, {}) if current == method and path == target else None
    )
    with pytest.raises(Deferred):
        publish(history(fake), run, "simulated", (), "owner/repo")
    assert read_record(run)["publication"] == "pending"
    assert fake.head == ROOT_COMMIT


def test_permission_missing_branch_collision_and_changed_evidence(repo: Path, tmp_path: Path) -> None:
    fake = FakeGitHub()
    run = ready(repo, tmp_path)
    with pytest.raises(BranchMissing):
        publish(history(fake), run, "simulated", (), "owner/repo")
    assert history(fake).listing("weekly-report", None, None, False, 20).data["count"] == 0
    with pytest.raises(RunMissing):
        history(fake).get(run.name, "record.json")
    history(fake).initialize("simulated")
    fake.hook = lambda method, path, payload: Response(404, {}, {}) if path == "" else None
    with pytest.raises(PublishFailed):
        publish(history(fake), run, "simulated", (), "owner/repo")
    fake.hook = None
    publish(history(fake), run, "simulated", (), "owner/repo")
    path = run_path(run.name) + "/record.json"
    fake.files()[path] = b"different"
    with pytest.raises(RecordCollision):
        publish(history(fake), run, "simulated", (), "owner/repo")
    Path(read_record(run)["report"]["path"]).write_text("changed")
    calls = len(fake.calls)
    with pytest.raises(EvidenceChanged):
        publish(history(fake), run, "simulated", (), "owner/repo")
    assert len(fake.calls) == calls


def test_amendment_unknown_retry_and_two_in_one_second(repo: Path, tmp_path: Path) -> None:
    fake = FakeGitHub()
    history(fake).initialize("simulated")
    run = ready(repo, tmp_path)
    publish(history(fake), run, "simulated", (), "owner/repo")
    original = fake.files()[run_path(run.name) + "/record.json"]

    def lost(method: str, path: str, payload: dict | None) -> Response | None:
        if method == "PATCH":
            assert payload
            fake.head = payload["sha"]
            fake.hook = None
            raise subprocess.TimeoutExpired("gh", 30)
        return None

    fake.hook = lost
    with pytest.raises(PublishUnknown):
        update(history(fake), run, "simulated", "integrated", ("a" * 40,))
    fixed = read_record(run)["updates"][0]["file"]
    update(history(fake), run, "simulated", "integrated", ("a" * 40,))
    assert read_record(run)["updates"][0]["file"] == fixed
    update(history(fake), run, "simulated", "stopped", ())
    changes = read_record(run)["updates"]
    assert len(changes) == 2 and changes[0]["file"] != changes[1]["file"]
    assert fake.files()[run_path(run.name) + "/record.json"] == original
    assert (
        history(fake).listing("weekly-report", None, None, False, 20).data["runs"][0]["integration_state"] == "stopped"
    )


def test_list_two_year_shards_and_supersession(repo: Path, tmp_path: Path) -> None:
    fake = FakeGitHub()
    history(fake).initialize("simulated")
    one, two = ready(repo, tmp_path, "one"), ready(repo, tmp_path, "two")
    old = read_record(one)
    old_id = old["run_id"].replace("-2026", "-2025")
    renamed = one.with_name(old_id)
    one.rename(renamed)
    old["run_id"] = old_id
    write_record(renamed, old)
    newer = read_record(two)
    newer["supersedes"] = [old_id]
    write_record(two, newer)
    publish(history(fake), renamed, "simulated", (), "owner/repo")
    publish(history(fake), two, "simulated", (), "owner/repo")
    assert len(history(fake).listing("weekly-report", None, None, True, 20).data["runs"]) == 2
    result = history(fake).listing("weekly-report", None, None, False, 20)
    assert [item["run_id"] for item in result.data["runs"]] == [two.name]
    assert history(fake).listing("weekly-report", "missing", None, False, 20).data["count"] == 0


def test_empty_repository_and_read_timeout(repo: Path, tmp_path: Path) -> None:
    from devkit_agt.features.maintenance_history.models.errors import RepositoryEmpty

    fake = FakeGitHub()
    fake.hook = lambda method, path, payload: (
        Response(409, {}, {}) if method == "POST" and path == "git/trees" else None
    )
    with pytest.raises(RepositoryEmpty):
        history(fake).initialize("simulated")
    fake.hook = None
    history(fake).initialize("simulated")
    run = ready(repo, tmp_path)

    def timeout(method: str, path: str, payload: dict | None) -> Response | None:
        if method == "GET":
            raise subprocess.TimeoutExpired("gh", 30)
        return None

    fake.hook = timeout
    with pytest.raises(Deferred):
        publish(history(fake), run, "simulated", (), "owner/repo")
    assert read_record(run)["publication"] == "pending"


def test_three_races_defer_without_losing_other_writers(repo: Path, tmp_path: Path) -> None:
    fake = FakeGitHub()
    history(fake).initialize("simulated")
    run = ready(repo, tmp_path)

    def race(method: str, path: str, payload: dict | None) -> Response | None:
        if method == "PATCH":
            assert fake.head
            current = fake.commits[fake.head]
            other = str(len(fake.calls)).zfill(40)
            fake.commits[other] = current | {"parents": [fake.head]}
            fake.head = other
            return Response(422, {}, {})
        return None

    fake.hook = race
    with pytest.raises(Deferred):
        publish(history(fake), run, "simulated", (), "owner/repo")
    assert len([call for call in fake.calls if call[0] == "PATCH"]) == 3
    assert read_record(run)["publication"] == "pending"


def test_frozen_extra_selection_and_unregistered_file_refused_before_network(repo: Path, tmp_path: Path) -> None:
    from devkit_agt.features.maintenance_history.models.errors import InputError

    fake = FakeGitHub()
    history(fake).initialize("simulated")
    report = tmp_path / "report.md"
    extra = tmp_path / "extra.txt"
    report.write_text("safe")
    extra.write_text("safe evidence")
    started = start(
        repo,
        repository="owner/repo",
        playbook="weekly-report",
        scope="extra",
        into=tmp_path / "runs",
        report=report,
        zone="UTC",
        supersedes=(),
        prior_runs=(),
    )
    run = Path(started.data["path"])
    finish(run, outcome="interrupted", result=None, report=None, applied_commits=(), follow_ups=(), files=(extra,))
    unknown = tmp_path / "unknown.txt"
    unknown.write_text("safe")
    count = len(fake.calls)
    with pytest.raises(InputError):
        publish(history(fake), run, "simulated", (unknown,), "owner/repo")
    assert count == len(fake.calls)
    publish(history(fake), run, "simulated", (extra,), "owner/repo")
    assert fake.files()[run_path(run.name) + "/extra.txt"] == b"safe evidence"
    assert fake.indexes()[0]["outcome"] == "interrupted"
