"""``devkit generated resolve|regen|check`` on real repositories, through the library and the command line."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.generated import (
    CommandFailedError,
    InputsConflictedError,
    OutputUndeclaredError,
    UnmergedError,
    check,
    regenerate,
    resolve,
    unmerged,
)
from devkit_core.core import ArgumentError
from devkit_dist.cli import cli
from testsupport.rules import git, init_repo, write

# out.txt concatenates the sources; count.txt, regenerated after it, counts its lines.
CONFIG = """[artifacts.gen]
paths = ["gen/out.txt"]
inputs = ["src/**"]
command = "mkdir -p gen && cat src/*.txt > gen/out.txt"

[artifacts.count]
paths = ["gen/count.txt"]
inputs = ["gen/out.txt"]
after = ["gen"]
command = "wc -l < gen/out.txt | tr -d ' ' > gen/count.txt"
"""


def attempt(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run Git where a nonzero exit (a merge that stops on conflicts) is expected."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")} | {"GIT_EDITOR": "true"}
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env, check=False)


def commit_all(root: Path, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = init_repo(tmp_path / "repo").resolve()
    write(root, ".devkit/generated.toml", CONFIG)
    write(root, "src/base.txt", "base\n")
    regenerate(root)
    commit_all(root, "generated")
    return root


def diverge(root: Path, ours: dict[str, str], theirs: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Commit ``theirs`` on branch ``other`` and ``ours`` on ``main``, regenerating on each, then merge ``other``."""
    git(root, "switch", "-q", "-c", "other")
    for rel, text in theirs.items():
        write(root, rel, text)
    regenerate(root)
    commit_all(root, "theirs")
    git(root, "switch", "-q", "main")
    for rel, text in ours.items():
        write(root, rel, text)
    regenerate(root)
    commit_all(root, "ours")
    return attempt(root, "merge", "--no-edit", "other")


def test_resolve_regenerates_the_conflicted_files_and_their_dependents_and_stages_them(repo: Path) -> None:
    merge = diverge(repo, {"src/a.txt": "a\n"}, {"src/b.txt": "b\n"})
    # Both sides counted 2 lines: count.txt merges cleanly, and is regenerated as gen's dependent.
    assert merge.returncode != 0 and set(unmerged(repo)) == {"gen/out.txt"}

    result = resolve(repo)

    assert (repo / "gen/out.txt").read_text() == "a\nb\nbase\n"
    assert (repo / "gen/count.txt").read_text() == "3\n"
    assert unmerged(repo) == {} and result.remaining == [] and result.notices == []
    assert [(item.id, item.conflicts) for item in result.artifacts] == [
        ("gen", ("gen/out.txt",)),
        ("count", ()),
    ]
    assert result.operation == "merge" and result.next_command == "git merge --continue"
    assert git(repo, "diff", "--name-only") == ""  # everything regenerated is staged
    assert attempt(repo, "merge", "--continue").returncode == 0


def test_a_conflicted_input_blocks_resolve_before_any_change(repo: Path) -> None:
    diverge(repo, {"src/base.txt": "ours\n"}, {"src/base.txt": "theirs\n"})
    before = (repo / "gen/out.txt").read_text()

    with pytest.raises(InputsConflictedError, match="nothing was changed") as caught:
        resolve(repo)

    assert caught.value.details == ("src/base.txt: read by gen",)
    assert (repo / "gen/out.txt").read_text() == before
    assert set(unmerged(repo)) == {"src/base.txt", "gen/out.txt"}


def test_an_artifact_without_inputs_is_blocked_by_any_other_conflict(repo: Path) -> None:
    write(repo, ".devkit/generated.toml", CONFIG.replace('inputs = ["src/**"]\n', ""))
    commit_all(repo, "no inputs")
    diverge(repo, {"README.md": "ours\n", "src/a.txt": "a\n"}, {"README.md": "theirs\n", "src/b.txt": "b\n"})
    with pytest.raises(InputsConflictedError) as caught:
        resolve(repo)
    assert caught.value.details == ("README.md: read by gen",)


def test_other_conflicts_remain_with_a_warning_and_no_next_command(repo: Path) -> None:
    diverge(repo, {"README.md": "ours\n", "src/a.txt": "a\n"}, {"README.md": "theirs\n", "src/b.txt": "b\n"})

    result = resolve(repo)

    assert result.remaining == ["README.md"] and result.next_command is None
    assert [notice.code for notice in result.notices] == ["GENERATED_CONFLICTS_REMAIN"]
    assert result.notices[0].details == ("README.md",)
    assert (repo / "gen/out.txt").read_text() == "a\nb\nbase\n"


def test_a_side_that_deleted_the_file_is_seeded_as_deleted(repo: Path) -> None:
    write(
        repo,
        ".devkit/generated.toml",
        CONFIG.replace('seed = "ours"', "")
        + '\n[artifacts.gen2]\npaths = ["gen2.txt"]\ncommand = "test -e gen2.txt && echo kept > gen2.txt || true"\ninputs = ["src/**"]\nseed = "theirs"\n',
    )
    write(repo, "gen2.txt", "start\n")
    commit_all(repo, "gen2")
    git(repo, "switch", "-q", "-c", "other")
    git(repo, "rm", "-q", "gen2.txt")
    commit_all(repo, "theirs deletes")
    git(repo, "switch", "-q", "main")
    write(repo, "gen2.txt", "ours changed\n")
    commit_all(repo, "ours changes")
    assert attempt(repo, "merge", "--no-edit", "other").returncode != 0
    assert set(unmerged(repo)) == {"gen2.txt"}

    resolve(repo)

    assert not (repo / "gen2.txt").exists() and unmerged(repo) == {}
    assert git(repo, "status", "--porcelain") == "D  gen2.txt"


def test_a_failed_command_stops_with_its_log_and_stages_nothing(repo: Path) -> None:
    diverge(repo, {"src/a.txt": "a\n"}, {"src/b.txt": "b\n"})
    write(repo, ".devkit/generated.toml", CONFIG.replace("mkdir -p gen && cat", "echo broken >&2; exit 3; cat"))

    with pytest.raises(CommandFailedError) as caught:
        resolve(repo)

    assert caught.value.code == "GENERATED_COMMAND_FAILED"
    assert caught.value.details[0].startswith("exit=3  log=")
    assert "  | broken" in caught.value.details
    assert set(unmerged(repo)) == {"gen/out.txt"}


def test_a_command_writing_outside_its_files_is_refused(repo: Path) -> None:
    diverge(repo, {"src/a.txt": "a\n"}, {"src/b.txt": "b\n"})
    write(repo, ".devkit/generated.toml", CONFIG.replace("mkdir -p gen &&", "echo x > stray.txt && mkdir -p gen &&"))

    with pytest.raises(OutputUndeclaredError) as caught:
        resolve(repo)

    assert caught.value.details == ("stray.txt",)
    assert set(unmerged(repo)) == {"gen/out.txt"}


def test_a_dry_run_changes_nothing(repo: Path) -> None:
    diverge(repo, {"src/a.txt": "a\n"}, {"src/b.txt": "b\n"})
    before = (repo / "gen/out.txt").read_text()

    result = resolve(repo, dry_run=True)

    assert [item.id for item in result.artifacts] == ["gen", "count"] and result.next_command is None
    assert (repo / "gen/out.txt").read_text() == before and set(unmerged(repo)) == {"gen/out.txt"}


def test_resolve_continues_a_rebase(repo: Path) -> None:
    git(repo, "switch", "-q", "-c", "other")
    write(repo, "src/b.txt", "b\n")
    regenerate(repo)
    commit_all(repo, "theirs")
    git(repo, "switch", "-q", "main")
    write(repo, "src/a.txt", "a\n")
    regenerate(repo)
    commit_all(repo, "ours")
    assert attempt(repo, "rebase", "other").returncode != 0

    result = resolve(repo)

    assert result.operation == "rebase" and result.next_command == "git rebase --continue"
    assert (repo / "gen/out.txt").read_text() == "a\nb\nbase\n"


def test_resolve_without_conflicts_does_nothing(repo: Path) -> None:
    result = resolve(repo)
    assert result.artifacts == [] and result.remaining == [] and result.next_command is None


def test_regen_refuses_unmerged_paths_and_rewrites_in_place(repo: Path) -> None:
    write(repo, "src/c.txt", "c\n")
    result = regenerate(repo, ["gen"])
    assert [(item.id, item.changed) for item in result.artifacts] == [
        ("gen", ("gen/out.txt",)),
        ("count", ("gen/count.txt",)),
    ]
    assert git(repo, "diff", "--cached", "--name-only") == ""

    commit_all(repo, "c")
    diverge(repo, {"src/base.txt": "ours\n"}, {"src/base.txt": "theirs\n"})
    with pytest.raises(UnmergedError):
        regenerate(repo)


def test_check_reports_stale_artifacts_and_leaves_the_checkout_alone(repo: Path) -> None:
    assert check(repo).stale == []
    write(repo, "src/c.txt", "c\n")
    commit_all(repo, "stale")
    write(repo, "README.md", "dirty\n")

    result = check(repo)

    assert [item.id for item in result.stale] == ["gen", "count"]
    assert result.commit == git(repo, "rev-parse", "HEAD")
    assert git(repo, "status", "--porcelain") == "M README.md"
    assert len(git(repo, "worktree", "list").splitlines()) == 1
    skipped = [item.id for item in result.artifacts if item.skipped]
    assert skipped == ["devkit-receipt"]  # optional: no receipt is tracked
    assert check(repo, rev="HEAD~1").stale == []


def test_check_names_an_artifact_registered_only_in_the_working_tree(repo: Path) -> None:
    write(repo, ".devkit/generated.toml", CONFIG + '\n[artifacts.extra]\npaths = ["gen/extra.txt"]\ncommand = "true"\n')

    with pytest.raises(ArgumentError) as raised:
        check(repo, ["extra"])

    assert "registered in the working tree but not at HEAD: extra" in str(raised.value)
    fix = raised.value.fix or ""
    assert ".devkit/generated.toml" in fix and "--rev" in fix
    with pytest.raises(ArgumentError, match="unknown or disabled generated artifacts: missing"):
        check(repo, ["missing"])
    write(repo, ".devkit/generated.toml", "[artifacts.gen\n")  # mid-edit: the committed registry still holds
    with pytest.raises(ArgumentError, match="unknown or disabled generated artifacts: missing"):
        check(repo, ["missing"])


def invoke(*args: str):
    return CliRunner().invoke(cli, ["generated", *args])


def test_the_commands_print_sentinels_and_check_exits_1_when_stale(repo: Path) -> None:
    listed = invoke("list", "-w", str(repo))
    assert listed.exit_code == 0
    assert '[GENERATED: gen source=project seed=ours paths=gen/out.txt command="mkdir -p gen' in listed.stdout

    assert invoke("check", "-w", str(repo)).stdout.splitlines()[-1].startswith("[SUMMARY: commit=")
    write(repo, "src/c.txt", "c\n")
    commit_all(repo, "stale")
    stale = invoke("check", "gen", "-w", str(repo))
    assert stale.exit_code == 1
    assert "[GENERATED_STALE: gen changed=1]" in stale.stdout
    assert "(GENERATED_STALE)" in stale.stderr and "devkit generated regen gen count" in stale.stderr

    diverge(repo, {"src/a.txt": "a\n"}, {"src/b.txt": "b\n"})
    resolved = invoke("resolve", "-w", str(repo))
    assert resolved.exit_code == 0, resolved.output
    assert resolved.stdout.splitlines() == [
        "[GENERATED_RESOLVED: gen conflicts=1 changed=1]",
        "[GENERATED_RESOLVED: count conflicts=0 changed=1]",
        "[SUMMARY: operation=merge artifacts=2 remaining=0 dry_run=no]",
        "[NEXT_CMD: git merge --continue]",
    ]
    again = json.loads(invoke("resolve", "-w", str(repo), "--format", "json").stdout)
    assert again == {
        "operation": "merge",
        "dry_run": False,
        "artifacts": [],
        "remaining": [],
        "next_command": "git merge --continue",
        "notices": [],
    }
