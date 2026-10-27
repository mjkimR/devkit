from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from devkit_agt.features.rules import (
    COMMIT_INDEX_VARIABLE,
    SnapshotError,
    commit_index,
    git_snapshot,
    materialize_snapshot,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    (root / "docs").mkdir()
    (root / "docs/a.md").write_text("# A\n")
    (root / "run.sh").write_text("#!/bin/sh\n")
    (root / "run.sh").chmod(0o755)
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "init")
    return root


def test_staged_snapshot_ignores_unstaged_edits_and_untracked_files(repo: Path, tmp_path: Path) -> None:
    (repo / "docs/a.md").write_text("# A staged\n")
    (repo / "docs/new.md").write_text("new\n")
    _git(repo, "add", "docs")
    (repo / "docs/a.md").write_text("# A unstaged\n")
    (repo / "untracked.md").write_text("x\n")
    (repo / ".env").write_text("SECRET=1\n")

    snapshot = git_snapshot(repo, staged=True)
    assert snapshot.mode == "staged"
    assert snapshot.changed == ("docs/a.md", "docs/new.md")
    assert snapshot.deleted == ()
    assert {name for name, _, _ in snapshot.files} == {"docs/a.md", "docs/new.md", "run.sh"}

    out = tmp_path / "out"
    materialize_snapshot(snapshot, out)
    assert (out / "docs/a.md").read_text() == "# A staged\n"
    assert (out / "run.sh").stat().st_mode & 0o111
    assert not (out / "untracked.md").exists() and not (out / ".env").exists()


def test_staged_snapshot_reports_deleted_paths(repo: Path) -> None:
    _git(repo, "rm", "-q", "run.sh")
    snapshot = git_snapshot(repo, staged=True)
    assert snapshot.deleted == ("run.sh",)
    assert snapshot.changed == ()


def test_ci_snapshot_uses_merge_base(repo: Path) -> None:
    _git(repo, "checkout", "-q", "-b", "feature")
    (repo / "docs/b.md").write_text("# B\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "feature")
    _git(repo, "checkout", "-q", "main")
    (repo / "docs/c.md").write_text("# C\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "main moves on")
    _git(repo, "checkout", "-q", "feature")
    (repo / "docs/b.md").write_text("# B unstaged\n")

    snapshot = git_snapshot(repo, staged=False, base="main")
    assert snapshot.mode == "ci"
    assert snapshot.changed == ("docs/b.md",)
    assert snapshot.base == _git(repo, "merge-base", "main", "feature")


def test_unborn_branch_compares_against_empty_tree(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    (root / "a.md").write_text("a\n")
    _git(root, "add", "a.md")
    snapshot = git_snapshot(root, staged=True)
    assert snapshot.changed == ("a.md",)


def test_snapshot_errors_outside_git_and_for_bad_base(tmp_path: Path, repo: Path) -> None:
    with pytest.raises(SnapshotError, match="not inside a Git work tree"):
        git_snapshot(tmp_path, staged=True)
    with pytest.raises(SnapshotError, match="merge-base failed"):
        git_snapshot(repo, staged=False, base="nope/nope")


def test_snapshot_root_must_be_the_toplevel(repo: Path) -> None:
    with pytest.raises(SnapshotError, match="top level"):
        git_snapshot(repo / "docs", staged=True)


def test_materialize_symlinks_submodules_and_backslash_names(repo: Path, tmp_path: Path) -> None:
    (repo / "docs/latest.md").symlink_to("a.md")
    (repo / "docs/escape.md").symlink_to("../../outside.md")
    (repo / "a\\b.txt").write_text("odd but valid on POSIX\n")
    _git(repo, "add", ".")
    head = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-index", "--add", "--cacheinfo", f"160000,{head},vendor/sub")

    snapshot = git_snapshot(repo, staged=True)
    assert snapshot.changed == ("a\\b.txt",)  # symlinks and submodules are not evaluation targets
    modes = {name: mode for name, _, mode in snapshot.files}
    assert modes["docs/latest.md"] == "120000" and modes["vendor/sub"] == "160000"

    out = tmp_path / "out"
    materialize_snapshot(snapshot, out)
    assert (out / "docs/latest.md").is_symlink() and (out / "docs/latest.md").read_text() == "# A\n"
    assert not (out / "docs/escape.md").exists() and not (out / "docs/escape.md").is_symlink()
    assert (out / "vendor/sub").is_dir()
    assert (out / "a\\b.txt").read_text() == "odd but valid on POSIX\n"


def test_changed_and_deleted_from_one_diff(repo: Path) -> None:
    (repo / "docs/a.md").write_text("# A2\n")
    (repo / "docs/new.md").write_text("new\n")
    _git(repo, "rm", "-q", "run.sh")
    _git(repo, "add", ".")
    snapshot = git_snapshot(repo, staged=True)
    assert snapshot.changed == ("docs/a.md", "docs/new.md")
    assert snapshot.deleted == ("run.sh",)
    assert "changed=2 deleted=1" in snapshot.describe()


def test_materialize_streams_large_and_many_blobs(repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import devkit_agt.features.rules.repositories.workspace.snapshot as snapshot_module

    monkeypatch.setattr(snapshot_module, "_CHUNK", 4096)  # many chunk boundaries inside one blob
    big = bytes(range(256)) * 4099 + b"\n\n"  # binary, newlines, not a multiple of the chunk size
    (repo / "big.bin").write_bytes(big)
    many = repo / "many"
    many.mkdir()
    for index in range(3000):  # object names exceed a pipe buffer: the writer must not block the reader
        (many / f"f{index:04d}.txt").write_text(f"{index}\n")
    (repo / "empty.txt").write_bytes(b"")
    _git(repo, "add", ".")

    out = tmp_path / "out"
    materialize_snapshot(git_snapshot(repo, staged=True), out)
    assert (out / "big.bin").read_bytes() == big
    assert (out / "empty.txt").read_bytes() == b""
    assert (out / "many/f2999.txt").read_text() == "2999\n"
    assert len(list((out / "many").iterdir())) == 3000


def test_materialize_reports_a_missing_object(repo: Path, tmp_path: Path) -> None:
    import dataclasses

    snapshot = git_snapshot(repo, staged=True)
    bogus = dataclasses.replace(snapshot, files=(("ghost.md", "0" * 40, "100644"),))
    with pytest.raises(SnapshotError, match="missing") as info:
        materialize_snapshot(bogus, tmp_path / "out")
    assert info.value.code == "RULES_SNAPSHOT_FAILED"


def test_materialize_reports_a_git_failure_and_a_timeout(repo: Path, tmp_path: Path) -> None:
    from devkit_agt.features.rules.repositories.workspace.snapshot import _BlobReader

    snapshot = git_snapshot(repo, staged=True)
    gone = tmp_path / "gone"
    gone.mkdir()
    reader = _BlobReader(gone, [sha for _, sha, _ in snapshot.files])  # not a repository: git exits nonzero
    with pytest.raises(SnapshotError, match="cat-file failed"):
        reader.header("docs/a.md", snapshot.files[0][1])
    reader.close()

    import time

    # More output than a pipe holds and nobody reading it: Git cannot finish before the watchdog kills it.
    slow = _BlobReader(repo, [snapshot.files[0][1]] * 5000, timeout=0.0)
    deadline = time.monotonic() + 10
    while not slow._timed_out and time.monotonic() < deadline:
        time.sleep(0.01)
    with pytest.raises(SnapshotError, match="timed out"):
        slow.finish()
    slow.close()


def test_a_watchdog_firing_after_a_clean_exit_does_not_fail_the_run(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from devkit_agt.features.rules.repositories.workspace.snapshot import _BlobReader

    snapshot = git_snapshot(repo, staged=True)
    name, sha, _ = snapshot.files[0]
    reader = _BlobReader(repo, [sha], timeout=60.0)
    try:
        reader.read(name, reader.header(name, sha))
        wait = reader._process.wait

        def wait_then_fire(*args: object, **kwargs: object) -> int:
            returncode = wait()
            reader._timed_out = "no progress reading its output for 60.0s"  # the watchdog fires before finish stops it
            return returncode

        monkeypatch.setattr(reader._process, "wait", wait_then_fire)
        reader.finish()  # Git exited 0: every object was delivered
    finally:
        reader.close()


def test_the_blob_reader_timeout_counts_idle_time_and_the_limit_bounds_the_whole_run(repo: Path) -> None:
    import time

    from devkit_agt.features.rules.repositories.workspace.snapshot import _BlobReader

    snapshot = git_snapshot(repo, staged=True)
    blobs = [(name, sha) for name, sha, _ in snapshot.files] * 4
    # Reading steadily for longer than the idle timeout in all succeeds: every read resets it.
    steady = _BlobReader(repo, [sha for _, sha in blobs], timeout=0.5)
    try:
        started = time.monotonic()
        for name, sha in blobs:
            time.sleep(0.1)
            steady.read(name, steady.header(name, sha))
        assert time.monotonic() - started > 0.5
        steady.finish()
    finally:
        steady.close()

    bounded = _BlobReader(repo, [blobs[0][1]] * 5000, timeout=60.0, limit=0.0)  # cannot finish unread
    deadline = time.monotonic() + 10
    while not bounded._timed_out and time.monotonic() < deadline:
        time.sleep(0.01)
    with pytest.raises(SnapshotError, match=r"timed out \(not finished after 0.0s\)"):
        bounded.finish()
    bounded.close()


def test_commit_index_applies_only_to_its_own_repository(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
    monkeypatch.delenv(COMMIT_INDEX_VARIABLE, raising=False)
    assert commit_index(repo) is None

    index = str((repo / ".git/index.lock").resolve())
    monkeypatch.setenv(COMMIT_INDEX_VARIABLE, index)
    assert commit_index(repo) == index

    other = tmp_path / "other"
    other.mkdir()
    subprocess.run(["git", "init", "-q", str(other)], check=True)
    assert commit_index(other) is None  # a test suite's own repository keeps its default index

    monkeypatch.setenv("GIT_INDEX_FILE", index)
    assert commit_index(repo) is None  # Git's own variable already applies
