from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit_dist.cli import cli as devkit_cli
from spec_support.proposals import accept
from spec_support.scope import CAP_A, SPEC, git, make_repo, write

from devkit_spec.features.proposals import CreateProposalUseCase
from devkit_spec.features.scope import Deadline, RegisterScopeUseCase, Source, open_session, own

SPEC_B = "specs/2026-10/20261002-b"


def _scope(root: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["spec", "scope", *args, "-w", str(root)])


def _json(result: Result) -> dict:
    return json.loads(result.stdout)


def _register(root: Path, spec: str) -> str:
    return RegisterScopeUseCase().execute(open_session(root), spec).token


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "repo")


@pytest.fixture
def worktrees(repo: Path, tmp_path: Path) -> tuple[Path, Path]:
    """Two linked worktrees of ``repo``: ``a`` runs ``SPEC``, ``b`` a bundle that also touches ``src/a``."""
    write(repo, f"{SPEC_B}/spec.md", "---\nid: SPEC-b\nstatus: in-progress\n---\n")
    write(repo, f"{SPEC_B}/tasks.md", "- [ ] **Task 1**: t\n  - **_Boundary**: `src/a/a.py`, `src/c/`\n")
    write(
        repo,
        f"{SPEC_B}/reconcile.md",
        f"---\nreconcile_id: REC-b\nstatus: pending\ntargets:\n  - file: {CAP_A}\n    resolution: modified\n---\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "b")
    a, b = tmp_path / "repo-wt-a", tmp_path / "repo-wt-b"
    git(repo, "worktree", "add", "-q", "-b", "a", str(a))
    git(repo, "worktree", "add", "-q", "-b", "b", str(b))
    return a, b


def test_help_lists_only_collect_and_release() -> None:
    result = CliRunner().invoke(devkit_cli, ["spec", "scope", "--help"])
    assert result.exit_code == 0, result.output
    commands = result.stdout.split("Commands:", 1)[1].split()
    named = {"collect", "release", "sweep", "register", "query", "compare", "update"}
    assert [word for word in commands if word in named] == ["collect", "release"], (
        "sweep stays hidden; the retired commands are gone"
    )
    assert CliRunner().invoke(devkit_cli, ["spec", "scope", "sweep", "--help"]).exit_code == 0


@pytest.mark.parametrize("command", ["register", "query", "compare", "update"])
def test_retired_commands_are_usage_errors(repo: Path, command: str) -> None:
    result = _scope(repo, command)
    assert result.exit_code == 2
    assert "No such command" in result.output and f"'{command}'" in result.output
    assert "[SCOPE_ACK" not in result.output


def test_release_and_sweep_after_creation_registration(worktrees: tuple[Path, Path], repo: Path) -> None:
    a, b = worktrees
    _register(a, SPEC)
    _register(b, SPEC_B)
    namespace = open_session(repo).location.namespace
    journal = repo / ".git/devkit-spec-scope" / namespace / "journal.jsonl"
    journal.write_text('{"event": "register", "task": "SPEC-s"}\n')  # an earlier version's journal
    before = journal.read_bytes()

    released = _scope(a, "release")
    assert released.stdout == "[SCOPE_RELEASE: SPEC-s released=yes registered=yes already=no revision=1]\n"
    assert _scope(a, "release").stdout == "[SCOPE_RELEASE: - released=no registered=no already=no revision=-]\n"
    data = _json(_scope(b, "release", "--task-id", "SPEC-b", "--format", "json"))
    assert (data["task"], data["released"], data["revision"]) == ("SPEC-b", True, 1)
    _register(b, SPEC_B)

    git(repo, "worktree", "remove", "--force", str(b))
    report = _scope(repo, "sweep")
    assert report.stdout.splitlines() == [
        "[SWEEP: SPEC-b verdict=stale reason=worktree-missing revision=1]",
        f"[SUMMARY: namespace={namespace} active=0 stale=1 unverifiable=0 error=0 removed=0]",
    ]
    moved = _scope(repo, "sweep", "--apply", "--expect", "SPEC-b=2", "--format", "json")
    assert moved.exit_code == 2 and _json(moved)["errors"][0]["code"] == "SPEC_SCOPE_STALE_REVISION"
    assert _json(moved)["results"][0]["reason"] == "stale-revision"
    applied = _scope(repo, "sweep", "--apply")
    assert (
        applied.exit_code == 0
        and "[SWEEP: SPEC-b verdict=removed reason=worktree-missing revision=1]" in applied.stdout
    )
    assert journal.read_bytes() == before, "release and sweep neither read nor write the journal"


def test_release_of_another_worktree_record_is_refused(worktrees: tuple[Path, Path]) -> None:
    a, b = worktrees
    _register(a, SPEC)
    _register(b, SPEC_B)
    result = _scope(a, "release", "--task-id", "SPEC-b", "--format", "json")
    assert result.exit_code == 2 and _json(result)["error"]["code"] == "SPEC_SCOPE_TOKEN_MISMATCH"


def test_option_errors(repo: Path) -> None:
    assert _json(_scope(repo, "sweep", "--expect", "x=1", "--format", "json"))["error"]["code"] == "ARGUMENT_INVALID"
    bad = _scope(repo, "sweep", "--apply", "--expect", "x", "--format", "json")
    assert _json(bad)["error"]["code"] == "ARGUMENT_INVALID"
    assert "query" not in _json(bad)["error"]["advisory"]["fix"]
    write(repo, ".devkit/config.toml", "[tool.spec.scope]\ntimeout = 0\n")
    assert _json(_scope(repo, "release", "--format", "json"))["error"]["code"] == "SPEC_CONFIG_INVALID"


def test_outside_git(tmp_path: Path) -> None:
    write(tmp_path, ".devkit/config.toml", "")
    result = _scope(tmp_path, "release", "--format", "json")
    assert result.exit_code == 2 and _json(result)["error"]["code"] == "SPEC_SCOPE_NOT_A_WORKTREE"


def test_an_unreadable_own_record_stops_release(repo: Path) -> None:
    _register(repo, SPEC)
    namespace_dir = next((repo / ".git/devkit-spec-scope").iterdir())
    record = namespace_dir / "SPEC-s.json"
    record.write_text(record.read_text() + "garbage")  # this worktree's own record, unreadable
    released = _scope(repo, "release")
    assert released.exit_code == 2 and "(SPEC_SCOPE_RECORD_INVALID)" in released.stderr
    assert (repo / ".git/devkit-spec-scope-token").exists()


def test_handoff_registers_inside_a_linked_worktree(repo: Path, tmp_path: Path) -> None:
    created = CreateProposalUseCase().execute(repo, "demo")
    accept(repo / created.path)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "proposal")
    linked = tmp_path / "repo-wt-demo"
    git(repo, "worktree", "add", "-q", "-b", "dev-demo", str(linked))
    result = CliRunner().invoke(devkit_cli, ["spec", "proposal", "handoff", "demo", "-w", str(linked)])
    assert result.exit_code == 0, result.output
    scope_lines = [line for line in result.stdout.splitlines() if line.startswith("[SCOPE: ")]
    assert len(scope_lines) == 1
    assert re.fullmatch(
        r"\[SCOPE: SPEC-demo namespace=\w{16} revision=1 scopes=\d+ unresolved=\d+ shared_path=\S+ token=\S+\]",
        scope_lines[0],
    )
    session = open_session(linked)
    mine = own(session)
    assert mine is not None and (mine.record.task_id, mine.record.revision) == ("SPEC-demo", 1)
    observed = {path.path for path in mine.record.scopes if path.source is Source.OBSERVED}
    assert any(path.startswith("specs/") for path in observed), "the uncommitted handoff output is observed"
    assert not (session.location.shared_path / session.location.namespace / "journal.jsonl").exists()
    records, _ = session.registry.query(session.location.namespace, Deadline(5))
    assert [item.task_id for item in records] == ["SPEC-demo"]


def test_handoff_in_the_base_checkout_does_not_register(repo: Path) -> None:
    created = CreateProposalUseCase().execute(repo, "demo")
    accept(repo / created.path)
    git(repo, "checkout", "-q", "-b", "dev-demo")  # a --no-worktree Development: the base checkout on its branch
    result = CliRunner().invoke(
        devkit_cli, ["spec", "proposal", "handoff", "demo", "-w", str(repo), "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    assert _json(result)["scope"] is None
    assert not (repo / ".git/devkit-spec-scope-token").exists()
