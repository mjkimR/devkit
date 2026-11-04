from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from devkit_agt.features.maintenance_history.models.errors import (
    EvidenceChanged,
    InputError,
    ReportMismatch,
    SecretFound,
    SnapshotFailed,
)
from devkit_agt.features.maintenance_history.models.records import ROOT_COMMIT, ROOT_README, canonical
from devkit_agt.features.maintenance_history.repositories.local import read_record
from devkit_agt.features.maintenance_history.repositories.snapshot import capture
from devkit_agt.features.maintenance_history.services.runs import evidence, finish, start


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "--no-optional-locks", "-C", str(root), *args], stderr=subprocess.DEVNULL)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")
    (root / "tracked.txt").write_text("initial\n")
    git(root, "add", "tracked.txt")
    git(root, "commit", "-qm", "initial")
    return root


def begin(root: Path, into: Path, report: Path) -> Path:
    result = start(
        root,
        repository="owner/repo",
        playbook="weekly-report",
        scope="test",
        into=into,
        report=report,
        zone="UTC",
        supersedes=(),
        prior_runs=(),
    )
    return Path(result.data["path"])


def close(run: Path, **kwargs: object) -> None:
    finish(run, outcome="completed", result=None, report=None, applied_commits=(), follow_ups=(), **kwargs)  # type: ignore[arg-type]


def test_snapshot_preserves_index_refs_and_reports_dirty_identity(repo: Path) -> None:
    (repo / "tracked.txt").write_text("changed\n")
    (repo / "untracked.bin").write_bytes(b"\x00new")
    index = (repo / ".git/index").read_bytes()
    refs = git(repo, "for-each-ref")
    status = git(repo, "status", "--porcelain")
    one, diff = capture(repo, [])
    git(repo, "config", "diff.algorithm", "patience")
    git(repo, "config", "diff.noprefix", "true")
    two, _ = capture(repo, [])
    assert one["inspected_tree"] == two["inspected_tree"]
    assert diff is not None and hashlib.sha256(diff).hexdigest() == one["diff_digest"]
    assert index == (repo / ".git/index").read_bytes()
    assert refs == git(repo, "for-each-ref")
    assert status == git(repo, "status", "--porcelain")
    (repo / "tracked.txt").write_text("changed again\n")
    three, _ = capture(repo, [])
    assert three["inspected_tree"] != one["inspected_tree"]
    assert three["diff_digest"] != one["diff_digest"]


def test_global_excludes_change_snapshot_identity(repo: Path, tmp_path: Path) -> None:
    excluded = tmp_path / "ignores"
    excluded.write_text("")
    git(repo, "config", "core.excludesfile", str(excluded))
    (repo / "hidden.txt").write_text("hide me")
    first, _ = capture(repo, [])
    assert first == capture(repo, [])[0]
    excluded.write_text("hidden.txt\n")
    second, _ = capture(repo, [])
    assert first["inspected_tree"] != second["inspected_tree"]
    assert second["dirty"] is False


@pytest.mark.parametrize("inside", [True, False])
def test_run_and_report_never_count_as_drift(repo: Path, tmp_path: Path, inside: bool) -> None:
    into = repo / "runs" if inside else tmp_path / "runs"
    report = repo / "report.md" if inside else tmp_path / "report.md"
    run = begin(repo, into, report)
    report.write_text("# report\n")
    close(run)
    record = read_record(run)
    assert not record["dirty"]
    assert not record["drifted_at_finish"]
    assert record["inspected_tree"] == git(repo, "rev-parse", "HEAD^{tree}").decode().strip()
    assert record["diff_digest"] is None


def test_finish_refuses_mismatch_and_secrets_without_freezing(repo: Path, tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    run = begin(repo, tmp_path / "runs", report)
    with pytest.raises(ReportMismatch):
        finish(run, outcome="completed", result=None, report=tmp_path / "other.md", applied_commits=(), follow_ups=())
    report.write_text("token=" + "ghp_" + "X" * 36)
    with pytest.raises(SecretFound):
        close(run)
    assert read_record(run)["finished_at"] is None
    report.write_text("safe")
    close(run)
    report.write_text("changed")
    with pytest.raises(EvidenceChanged):
        evidence(run, read_record(run), ())


def test_freeze_extra_files_and_require_registered_selection(repo: Path, tmp_path: Path) -> None:
    report, extra = tmp_path / "report.md", tmp_path / "extra.txt"
    run = begin(repo, tmp_path / "runs", report)
    report.write_text("safe")
    extra.write_text("evidence")
    close(run, files=(extra,))
    record = read_record(run)
    frozen = canonical(record)
    assert evidence(run, record, (extra,))["extra.txt"] == b"evidence"
    assert canonical(record) == frozen
    assert "extra.txt" not in evidence(run, record, ())
    with pytest.raises(InputError):
        evidence(run, record, (report,))
    extra.write_text("changed")
    with pytest.raises(EvidenceChanged):
        evidence(run, record, (extra,))


def test_finish_warns_on_actual_content_drift(repo: Path, tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    run = begin(repo, tmp_path / "runs", report)
    (repo / "tracked.txt").write_text("changed")
    report.write_text("safe")
    result = finish(run, outcome="failed", result="test failure", report=None, applied_commits=(), follow_ups=())
    assert [item.code for item in result.notices] == ["HISTORY_RUN_DRIFTED"]
    assert read_record(run)["outcome"] == "failed"


def test_failed_clean_filter_writes_no_run(repo: Path, tmp_path: Path) -> None:
    git(repo, "config", "filter.broken.clean", "false")
    git(repo, "config", "filter.broken.required", "true")
    (repo / ".gitattributes").write_text("*.txt filter=broken\n")
    (repo / "tracked.txt").write_text("changed")
    with pytest.raises(SnapshotFailed):
        begin(repo, tmp_path / "runs", tmp_path / "report.md")
    assert not (tmp_path / "runs").exists()


def test_canonical_bytes_and_frozen_root_match_git_objects(repo: Path, tmp_path: Path) -> None:
    assert canonical({"z": 1, "a": "é"}) == canonical({"a": "é", "z": 1})
    blob = subprocess.check_output(["git", "hash-object", "--stdin"], input=ROOT_README).strip()
    # The full root object is independently hashed by git; no local ref/index update.
    person = b"devkit maintenance history <maintenance-history@devkit.invalid> 946684800 +0000"
    tree_bytes = b"100644 README.md\0" + bytes.fromhex(blob.decode())
    tree_sha = subprocess.check_output(["git", "hash-object", "-t", "tree", "--stdin"], input=tree_bytes).strip()
    commit = (
        b"tree "
        + tree_sha
        + b"\nauthor "
        + person
        + b"\ncommitter "
        + person
        + b"\n\nInitialize devkit maintenance history\n"
    )
    actual = subprocess.check_output(["git", "hash-object", "-t", "commit", "--stdin"], input=commit).decode().strip()
    assert actual == ROOT_COMMIT
    assert json.loads(canonical({"root": ROOT_COMMIT}))["root"] == actual
