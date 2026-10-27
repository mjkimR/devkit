from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit_dist.cli import cli as devkit_cli
from spec_support.proposals import accept
from spec_support.scope import CAP_A, CAP_PLANNED, SPEC, git, make_repo, write

from devkit_spec.features.proposals import create_proposal

SPEC_B = "specs/2026-10/20261002-b"


def _scope(root: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["spec", "scope", *args, "-w", str(root)])


def _json(result: Result) -> dict:
    return json.loads(result.stdout)


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


def test_compare_proposals_and_specs(repo: Path) -> None:
    result = _scope(repo, "compare", "--proposal", "one", "--proposal", "two", "--spec", SPEC)
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert lines[0] == "[PAIR: a=PROP-one b=PROP-two docs=1 code=0 unresolved=3]"
    assert lines[1] == f"[EVIDENCE: {CAP_PLANNED} a=PROP-one b=PROP-two kind=doc granularity=unknown]"
    assert "[PAIR: a=PROP-one b=SPEC-s docs=1 code=1 unresolved=6]" in lines
    assert (
        "[EVIDENCE: src/a a=PROP-one b=SPEC-s kind=code granularity=dir other=src/a source=candidate "
        "other_source=declared-code]"
    ) in lines
    assert "[DIFF: docs/capabilities/x/CAP-X-empty.md set=SPEC-s in=target-docs]" in lines
    assert f"[UNRESOLVED: {CAP_PLANNED} set=PROP-one reason=planned-doc]" in lines
    assert lines[-1] == "[SUMMARY: sets=3 pairs=3 overlapping=3]"
    assert not (repo / ".git/devkit-spec-scope").exists(), "compare never touches the registry"

    data = _json(_scope(repo, "compare", "--proposal", "one", "--spec", SPEC, "--format", "json"))
    assert data["summary"] == {"sets": 2, "pairs": 1, "overlapping": 1}
    assert data["sets"][1]["id"] == "SPEC-s" and data["pairs"][0]["a"] == "PROP-one"


def test_compare_input_errors(repo: Path) -> None:
    one = _scope(repo, "compare", "--proposal", "one", "--format", "json")
    assert one.exit_code == 2 and _json(one)["error"]["code"] == "ARGUMENT_INVALID"
    missing = _scope(repo, "compare", "--proposal", "one", "--proposal", "nope", "--format", "json")
    assert _json(missing)["error"]["code"] == "SPEC_PROPOSAL_NOT_FOUND"
    gone = _scope(repo, "compare", "--proposal", "one", "--spec", "specs/none", "--format", "json")
    assert _json(gone)["error"]["code"] == "SPEC_SCOPE_SPEC_NOT_FOUND"


def test_two_worktrees_register_query_update_release_and_sweep(worktrees: tuple[Path, Path], repo: Path) -> None:
    a, b = worktrees
    first = _scope(a, "register", "--spec", SPEC)
    assert first.exit_code == 0, first.output
    match = re.fullmatch(
        r"\[SCOPE: SPEC-s namespace=(\w{16}) revision=1 scopes=\d+ unresolved=4 shared_path=(\S+) token=(\S+)\]\n",
        first.stdout,
    )
    assert match, first.stdout
    namespace, shared, token = match.groups()
    # Named relative to the workspace, never absolute.
    assert not Path(shared).is_absolute() and (a / shared).resolve() == (repo / ".git/devkit-spec-scope").resolve()
    second = _scope(b, "register", "--spec", SPEC_B, "--format", "json")
    assert second.exit_code == 0, second.output
    registered = _json(second)
    assert registered["namespace"] == namespace and registered["task"] and registered["token"]
    # A compact registration: no record internals or timestamps.
    assert not {"record", "token_hash", "updated_at"} & set(registered)

    query = _scope(a, "query")
    assert query.exit_code == 0, query.output
    assert token not in query.stdout, "the token is printed by register only"
    lines = query.stdout.splitlines()
    assert lines[0].startswith("[RECORD: SPEC-s revision=1 worktree=. ") and lines[0].endswith("own=yes]")
    assert lines[1].startswith("[RECORD: SPEC-b revision=1 ") and lines[1].endswith("own=no]")
    assert lines[2] == "[PAIR: a=SPEC-s b=SPEC-b docs=1 code=1 unresolved=4]"
    assert (
        "[EVIDENCE: src/a a=SPEC-s b=SPEC-b kind=code granularity=dir other=src/a/a.py source=declared-code other_source=declared-code]"
        in lines
    )
    assert lines[-1] == f"[SUMMARY: namespace={namespace} records=2 pairs=1 overlapping=1 problems=0]"
    from_base = _scope(repo, "query")
    assert "[PAIR: a=SPEC-b b=SPEC-s docs=1 code=1 unresolved=4]" in from_base.stdout.splitlines()
    planned = _scope(repo, "query", "--spec", SPEC_B)
    assert "[PAIR: a=SPEC-b b=SPEC-s docs=1 code=1 unresolved=4]" in planned.stdout.splitlines()

    write(b, "src/a/a.py", "a = 'b'\n")
    write(b, "src/c/new.py", "c = 1\n")
    update = _scope(b, "update", "--spec", SPEC_B)
    assert update.exit_code == 0, update.output
    ack = update.stdout.splitlines()[-1]
    assert re.fullmatch(
        r"\[SCOPE_ACK: status=applied revision=2 added=2 removed=0 overlaps=1 unresolved=0 request_id=\S+\]", ack
    )
    data = _json(_scope(b, "update", "--spec", SPEC_B, "--format", "json"))
    assert data["ack"]["status"] == "applied" and data["ack"]["revision"] == 3 and data["pairs"][0]["b"] == "SPEC-s"

    released = _scope(a, "release")
    assert released.stdout == "[SCOPE_RELEASE: SPEC-s released=yes registered=yes already=no revision=1]\n"
    assert _scope(a, "release").stdout == "[SCOPE_RELEASE: - released=no registered=no already=no revision=-]\n"

    git(repo, "worktree", "remove", "--force", str(b))
    report = _scope(repo, "sweep")
    assert report.stdout.splitlines() == [
        "[SWEEP: SPEC-b verdict=stale reason=worktree-missing revision=3]",
        f"[SUMMARY: namespace={namespace} active=0 stale=1 unverifiable=0 error=0 removed=0]",
    ]
    moved = _scope(repo, "sweep", "--apply", "--expect", "SPEC-b=2", "--format", "json")
    assert moved.exit_code == 2 and _json(moved)["errors"][0]["code"] == "SPEC_SCOPE_STALE_REVISION"
    assert _json(moved)["results"][0]["reason"] == "stale-revision"
    applied = _scope(repo, "sweep", "--apply")
    assert (
        applied.exit_code == 0
        and "[SWEEP: SPEC-b verdict=removed reason=worktree-missing revision=3]" in applied.stdout
    )

    history = _scope(repo, "query", "--history", "--task", "b")
    events = [line.split()[1] for line in history.stdout.splitlines() if line.startswith("[EVENT:")]
    assert events == ["register", "update", "update", "sweep", "sweep", "sweep"]
    assert history.stdout.splitlines()[-1] == f"[SUMMARY: namespace={namespace} events=6 problems=0]"
    by_id = _json(_scope(repo, "query", "--history", "--task", "SPEC-s", "--format", "json"))
    assert [event["event"] for event in by_id["events"]] == ["register", "release"]


def test_declared_code_replaces_candidates_and_observed_paths_still_overlap(
    worktrees: tuple[Path, Path], repo: Path
) -> None:
    # AC-01, AC-04: SPEC-b declares src/a/a.py and src/c/; its target's entrypoints (src/a/, src/shared.py) drop out.
    a, b = worktrees
    assert _scope(b, "register", "--spec", SPEC_B).exit_code == 0
    write(b, "src/b/b.py", "b = 'b'\n")  # outside SPEC-b's boundary and outside every target's entrypoints
    git(b, "commit", "-q", "-am", "b")
    assert _scope(b, "update", "--spec", SPEC_B).exit_code == 0
    own = _json(_scope(b, "query", "--format", "json"))["own"]
    scopes = {(item["path"], item["source"]) for item in own["scopes"] if item["path"].startswith("src/")}
    assert scopes == {("src/a/a.py", "declared-code"), ("src/c", "declared-code"), ("src/b/b.py", "observed")}

    assert _scope(a, "register", "--spec", SPEC).exit_code == 0
    lines = _scope(a, "query").stdout.splitlines()
    assert "[PAIR: a=SPEC-s b=SPEC-b docs=1 code=2 unresolved=4]" in lines
    assert (
        "[EVIDENCE: src/b a=SPEC-s b=SPEC-b kind=code granularity=dir other=src/b/b.py source=declared-code "
        "other_source=observed]"
    ) in lines
    assert not [line for line in lines if "source=candidate" in line]


def test_update_failure_prints_the_ack_then_the_error(repo: Path) -> None:
    result = _scope(repo, "update", "--spec", SPEC)
    assert result.exit_code == 2
    assert re.fullmatch(
        r"\[SCOPE_ACK: status=failed revision=0 added=0 removed=0 overlaps=0 unresolved=0 request_id=\S+\]\n",
        result.stdout,
    )
    assert "(SPEC_SCOPE_TOKEN_MISSING)" in result.stderr
    data = _json(_scope(repo, "update", "--spec", SPEC, "--format", "json"))
    assert data["ack"]["status"] == "failed" and data["errors"][0]["code"] == "SPEC_SCOPE_TOKEN_MISSING"
    # Off an activity branch the fix lists the bundles to choose from instead of a bare placeholder.
    assert f"candidate: uv run devkit spec scope register --spec {SPEC}" in data["errors"][0]["advisory"]["details"]
    git(repo, "checkout", "-q", "-b", "dev-s")
    exact = _json(_scope(repo, "update", "--spec", SPEC, "--format", "json"))["errors"][0]["advisory"]["fix"]
    assert f"`uv run devkit spec scope register --spec {SPEC}`" in exact


def test_register_errors(repo: Path) -> None:
    missing = _scope(repo, "register", "--format", "json")
    assert _json(missing)["error"]["code"] == "ARGUMENT_INVALID"
    assert _json(_scope(repo, "register", "--spec", "specs/none", "--format", "json"))["error"]["code"] == (
        "SPEC_SCOPE_SPEC_NOT_FOUND"
    )
    assert _scope(repo, "register", "--spec", SPEC).exit_code == 0
    again = _scope(repo, "register", "--spec", SPEC, "--format", "json")
    assert _json(again)["error"]["code"] == "SPEC_SCOPE_TOKEN_EXISTS"


def test_option_errors(repo: Path) -> None:
    assert _json(_scope(repo, "query", "--task", "x", "--format", "json"))["error"]["code"] == "ARGUMENT_INVALID"
    assert _json(_scope(repo, "sweep", "--expect", "x=1", "--format", "json"))["error"]["code"] == "ARGUMENT_INVALID"
    bad = _scope(repo, "sweep", "--apply", "--expect", "x", "--format", "json")
    assert _json(bad)["error"]["code"] == "ARGUMENT_INVALID"
    write(repo, ".devkit/config.toml", "[tool.spec.scope]\ntimeout = 0\n")
    assert _json(_scope(repo, "query", "--format", "json"))["error"]["code"] == "SPEC_CONFIG_INVALID"


def test_outside_git(tmp_path: Path) -> None:
    write(tmp_path, ".devkit/config.toml", "")
    result = _scope(tmp_path, "query", "--format", "json")
    assert result.exit_code == 2 and _json(result)["error"]["code"] == "SPEC_SCOPE_NOT_A_WORKTREE"


def test_history_reports_unreadable_lines(repo: Path) -> None:
    assert _scope(repo, "query", "--history").stdout.splitlines()[-1].endswith("events=0 problems=0]")
    assert _json(_scope(repo, "query", "--history", "--format", "json"))["events"] == []
    _scope(repo, "register", "--spec", SPEC)
    journal = next((repo / ".git/devkit-spec-scope").glob("*/journal.jsonl"))
    with journal.open("a") as handle:
        handle.write("not json\n")
    result = _scope(repo, "query", "--history")
    assert result.exit_code == 0 and result.stdout.splitlines()[-1].endswith("events=1 problems=1]")
    assert "(SPEC_SCOPE_JOURNAL_LINE_INVALID)" in result.stderr
    assert _scope(repo, "query", "--history", "--strict").exit_code == 1


def test_journal_unavailable_keeps_stdout_and_exit(repo: Path) -> None:
    namespace_dir = repo / ".git/devkit-spec-scope"
    register = _scope(repo, "register", "--spec", SPEC)
    journal = next(namespace_dir.glob("*/journal.jsonl"))
    journal.unlink()
    journal.mkdir()
    released = _scope(repo, "release")
    assert released.exit_code == 0 and released.stdout.startswith("[SCOPE_RELEASE: SPEC-s released=yes")
    assert released.stderr.count("(SPEC_SCOPE_JOURNAL_UNAVAILABLE)") == 1
    assert register.exit_code == 0


def test_unreadable_record_is_a_warning(repo: Path) -> None:
    _scope(repo, "register", "--spec", SPEC)
    namespace_dir = next((repo / ".git/devkit-spec-scope").iterdir())
    (namespace_dir / "broken.json").write_text("{")
    result = _scope(repo, "query")
    assert result.exit_code == 0 and result.stdout.splitlines()[-1].endswith("problems=1]")
    assert "(SPEC_SCOPE_RECORD_INVALID)" in result.stderr


def test_handoff_registers_inside_a_linked_worktree(repo: Path, tmp_path: Path) -> None:
    created = create_proposal(repo, "demo")
    accept(repo / created.path)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "proposal")
    linked = tmp_path / "repo-wt-demo"
    git(repo, "worktree", "add", "-q", "-b", "dev-demo", str(linked))
    result = CliRunner().invoke(devkit_cli, ["spec", "proposal", "handoff", "demo", "-w", str(linked)])
    assert result.exit_code == 0, result.output
    scope_lines = [line for line in result.stdout.splitlines() if line.startswith("[SCOPE: ")]
    assert len(scope_lines) == 1 and scope_lines[0].startswith("[SCOPE: SPEC-demo namespace=")
    assert " token=" in scope_lines[0]
    query = _scope(linked, "query")
    assert query.stdout.splitlines()[0].startswith("[RECORD: SPEC-demo revision=1") and "own=yes" in query.stdout
    history = _json(_scope(linked, "query", "--history", "--format", "json"))
    assert history["events"][0]["source"] == "handoff" and history["events"][0]["slug"] == "demo"


def test_handoff_in_the_base_checkout_does_not_register(repo: Path) -> None:
    created = create_proposal(repo, "demo")
    accept(repo / created.path)
    git(repo, "checkout", "-q", "-b", "dev-demo")  # a --no-worktree Development: the base checkout on its branch
    result = CliRunner().invoke(
        devkit_cli, ["spec", "proposal", "handoff", "demo", "-w", str(repo), "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    assert _json(result)["scope"] is None
    assert not (repo / ".git/devkit-spec-scope-token").exists()


def test_query_lists_the_records_when_this_worktree_record_may_be_unreadable(repo: Path) -> None:
    _scope(repo, "register", "--spec", SPEC)
    namespace_dir = next((repo / ".git/devkit-spec-scope").iterdir())
    own = namespace_dir / "SPEC-s.json"
    (namespace_dir / "broken.json").write_text("{")  # another task's corrupt record
    own.unlink()  # this worktree's token is orphaned
    result = _scope(repo, "query")
    assert result.exit_code == 0 and result.stdout.splitlines()[-1].endswith(
        "records=0 pairs=0 overlapping=0 problems=1]"
    )
    assert "(SPEC_SCOPE_RECORD_INVALID)" in result.stderr

    _scope(repo, "release")
    _scope(repo, "register", "--spec", SPEC)
    own.write_text(own.read_text() + "garbage")  # this worktree's own record, unreadable
    result = _scope(repo, "query", "--format", "json")
    assert result.exit_code == 0, result.output
    data = _json(result)
    assert data["own"] is None and data["summary"]["problems"] == 2
    [notice] = data["notices"]
    assert notice["code"] == "SPEC_SCOPE_RECORD_INVALID"
    assert any(
        "this worktree's record is not among the readable records" in line for line in notice["advisory"]["details"]
    )
    released = _scope(repo, "release")
    assert released.exit_code == 2 and "(SPEC_SCOPE_RECORD_INVALID)" in released.stderr


@pytest.mark.parametrize("args", [(), ("--spec", SPEC), ("--history",)])
@pytest.mark.parametrize("registered", [False, True])
def test_query_cli_never_writes(
    repo: Path, monkeypatch: pytest.MonkeyPatch, args: tuple[str, ...], registered: bool
) -> None:
    import os

    from spec_support.scope_read_access import guard_writes

    from devkit_spec.features.scope.usecases.flow import open_session

    if registered:
        result = _scope(repo, "register", "--spec", SPEC)
        assert result.exit_code == 0, result.output
    session = open_session(repo)
    token_temp = session.location.token_path.parent / ".devkit-spec-scope-token-abcdefgh"
    token_temp.write_text("old token fragment")
    os.utime(token_temp, (0, 0))
    with monkeypatch.context() as guarded:
        guard_writes(guarded)
        result = _scope(repo, "query", *args, "--format", "json")
        assert result.exit_code == 0, result.output
    assert token_temp.read_text() == "old token fragment"


@pytest.mark.parametrize("option", [("--limit", "10"), ("--cursor", "invalid")])
def test_history_options_require_history(repo: Path, option: tuple[str, str]) -> None:
    result = _scope(repo, "query", *option, "--format", "json")
    assert result.exit_code == 2 and _json(result)["error"]["code"] == "ARGUMENT_INVALID"


def test_history_pages_are_recent_bounded_and_stable_across_appends(repo: Path) -> None:
    _scope(repo, "register", "--spec", SPEC)
    journal = next((repo / ".git/devkit-spec-scope").glob("*/journal.jsonl"))
    events = [{"event": "update", "task": "SPEC-s", "revision": i} for i in range(1, 124)]
    journal.write_text("".join(json.dumps(event) + "\n" for event in events))
    first = _json(_scope(repo, "query", "--history", "--format", "json"))
    assert [e["revision"] for e in first["events"]] == list(range(74, 124))
    assert first["pagination"]["limit"] == 50 and first["pagination"]["total"] == 123
    with journal.open("a") as handle:
        handle.write(json.dumps({"event": "update", "task": "SPEC-s", "revision": 124}) + "\n")
    second = _json(
        _scope(repo, "query", "--history", "--cursor", first["pagination"]["next_cursor"], "--format", "json")
    )
    assert [e["revision"] for e in second["events"]] == list(range(24, 74))
    last = _json(
        _scope(repo, "query", "--history", "--cursor", second["pagination"]["next_cursor"], "--format", "json")
    )
    assert [e["revision"] for e in last["events"]] == list(range(1, 24))
    assert last["pagination"]["next_cursor"] is None


def test_history_filter_precedes_pagination_and_cursor_is_bound_to_filter(repo: Path) -> None:
    _scope(repo, "register", "--spec", SPEC)
    journal = next((repo / ".git/devkit-spec-scope").glob("*/journal.jsonl"))
    events = [{"event": "update", "task": "SPEC-s" if i % 2 else "SPEC-b", "revision": i} for i in range(1, 10)]
    journal.write_text("".join(json.dumps(event) + "\n" for event in events) + "not json\n")
    first = _scope(repo, "query", "--history", "--task", "SPEC-s", "--limit", "2", "--format", "json")
    assert first.exit_code == 0
    data = _json(first)
    assert data["notices"][0]["code"] == "SPEC_SCOPE_JOURNAL_LINE_INVALID"
    assert [e["revision"] for e in data["events"]] == [7, 9]
    assert data["pagination"]["total"] == 5 and data["summary"]["problems"] == 1
    cursor = data["pagination"]["next_cursor"]
    next_page = _json(
        _scope(repo, "query", "--history", "--task", "SPEC-s", "--limit", "2", "--cursor", cursor, "--format", "json")
    )
    assert [e["revision"] for e in next_page["events"]] == [3, 5]
    wrong_filter = _scope(repo, "query", "--history", "--task", "SPEC-b", "--cursor", cursor, "--format", "json")
    assert wrong_filter.exit_code == 2 and _json(wrong_filter)["error"]["code"] == "ARGUMENT_INVALID"
    with journal.open("w") as handle:
        handle.write(json.dumps(events[-1]) + "\n")
    stale = _scope(repo, "query", "--history", "--task", "SPEC-s", "--cursor", cursor, "--format", "json")
    assert stale.exit_code == 2 and _json(stale)["error"]["code"] == "ARGUMENT_INVALID"


@pytest.mark.parametrize("limit", ["0", "101"])
def test_history_rejects_out_of_range_limit(repo: Path, limit: str) -> None:
    assert _scope(repo, "query", "--history", "--limit", limit).exit_code == 2


def test_history_text_pages_like_list_and_names_the_next_command(repo: Path) -> None:
    _scope(repo, "register", "--spec", SPEC)
    journal = next((repo / ".git/devkit-spec-scope").glob("*/journal.jsonl"))
    events = [{"event": "update", "task": "SPEC-s", "revision": i, "worktree": str(repo)} for i in range(1, 4)]
    journal.write_text("".join(json.dumps(event) + "\n" for event in events))
    lines = _scope(repo, "query", "--history", "--limit", "2").stdout.splitlines()
    assert all(" worktree=. " in line or line.endswith("worktree=.]") for line in lines[:2])
    cursor = _json(_scope(repo, "query", "--history", "--limit", "2", "--format", "json"))["pagination"]["next_cursor"]
    assert lines[2] == f"[PAGE: total=3 limit=2 count=2 next={cursor}]"
    assert lines[3] == f"[NEXT_CMD: uv run devkit spec scope query --history -w {repo} --limit 2 --cursor {cursor}]"


def test_query_with_the_registered_bundle_is_no_self_pair(repo: Path) -> None:
    _scope(repo, "register", "--spec", SPEC)
    git(repo, "worktree", "add", "-q", str(repo.parent / "other"), "-b", "other")
    result = _scope(repo.parent / "other", "query", "--spec", SPEC, "--format", "json")
    assert result.exit_code == 0, result.output
    assert [(pair["a"], pair["b"]) for pair in _json(result)["pairs"]] == []
