"""Recorded authority, repository identity and lifecycle acceptance scenarios."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest
from devkit_adaptive.features.assignment.repositories.ledger import Ledger


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def assigned(call, *args):
    return call("new", "--owner", "host", "--goal", "deliver", *args)["assignment"]


def returned(call, identifier="a1", *args):
    return call("return", identifier, "--status", "completed", *args)


def test_shared_ledger_and_unchanged_status(repo, call, tmp_path):
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-qb", "dev", str(linked))
    before = {root: git(root, "status", "--porcelain") for root in (repo, linked)}
    value = assigned(call, "--worktree", str(linked), "--write", "src/a", "--check", "tests")
    assert value["base"] == git(linked, "rev-parse", "HEAD")
    assert call("list", root=linked)["assignments"][0]["id"] == value["id"]
    assert before == {root: git(root, "status", "--porcelain") for root in before}
    shown = call("show", "a1")
    assert shown["assignment"]["checks"] == [{"name": "tests", "command": None}]
    assert "[GRANT: commit=no]" in call("show", "a1", text=True)


def test_overlap_and_sequenced_exemption(repo, call):
    assigned(call, "--write", "src/a")
    before = Ledger(repo).path.read_bytes()
    for scope in ("src/a/x.py", "."):
        error = call("new", "--owner", "o", "--goal", "g", "--write", scope, expected=2)
        assert error["error"]["code"] == "ADAPTIVE_SCOPE_OVERLAP"
        assert Ledger(repo).path.read_bytes() == before
    assigned(call, "--write", "src/ab")
    assigned(call, "--write", "src/a", "--depends-on", "a1")


@pytest.mark.parametrize("commit", [False, True])
def test_clean_return_and_checks(repo, call, commit):
    assigned(call, "--write", "src", "--check", "tests", *(["--commit"] if commit else []))
    (repo / "src/a").write_text("changed\n")
    if commit:
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "change")
    returned(call, "a1", "--check", "tests=pass")
    verified = call("verify", "a1", "--strict")
    assert verified["result"] == "pass"
    assert verified["checks"]["commit"]["status"] == ("not-applicable" if commit else "pass")
    call("close", "a1", "--outcome", "integrated")
    assert call("list")["assignments"] == []
    assert call("list", "--all")["assignments"][0]["observed"] is None


@pytest.mark.parametrize("kind", ["committed-rename", "dirty-rename", "untracked"])
def test_scope_violations(repo, call, kind):
    assigned(call, "--write", "src", "--commit")
    if kind == "untracked":
        (repo / "outside").write_text("outside")
    else:
        git(repo, "mv", "src/a", "outside")
        if kind == "committed-rename":
            git(repo, "commit", "-qm", "rename")
    returned(call)
    result = call("verify", "a1", expected=1)
    assert result["result"] == "fail"
    assert any(item["path"] == "outside" for item in result["checks"]["scope"]["outside"])
    assert "ADAPTIVE_SCOPE_VIOLATION" in {item["code"] for item in result["errors"]}
    assert call("show", "a1")["assignment"]["status"] == "rejected"


def test_diverged_final_and_head_moved(repo, call):
    assigned(call, "--write", ".", "--commit")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "--orphan", "other")
    git(repo, "commit", "-qm", "unrelated")
    returned(call)
    result = call("verify", "a1", expected=1)
    assert result["checks"]["base"]["status"] == "fail"
    assert result["checks"]["scope"]["status"] == "not-run"
    returned(call, "a1", "--final", base)
    assert call("verify", "a1", expected=1)["checks"]["head"]["status"] == "fail"


@pytest.mark.parametrize(
    "outcome,code", [(None, "ADAPTIVE_CHECK_OUTCOME_MISSING"), ("skipped", "ADAPTIVE_CHECK_NOT_PASSED")]
)
def test_missing_and_nonpassing_checks(repo, call, outcome, code):
    assigned(call, "--check", "tests", "--check", "lint")
    returned(call, "a1", "--check", "tests=pass", *(["--check", f"lint={outcome}"] if outcome else []))
    assert code in {item["code"] for item in call("verify", "a1", expected=1)["errors"]}


def test_commit_grant_and_strict_uncommitted(repo, call):
    assigned(call, "--write", "src")
    git(repo, "commit", "--allow-empty", "-qm", "unexpected")
    returned(call)
    assert "ADAPTIVE_COMMIT_NOT_GRANTED" in {item["code"] for item in call("verify", "a1", expected=1)["errors"]}
    call("close", "a1", "--outcome", "abandoned", "--reason", "retry")
    assigned(call, "--write", "src", "--commit")
    (repo / "src/a").write_text("dirty")
    returned(call, "a2")
    result = call("verify", "a2", "--strict", expected=1)
    assert result["result"] == "pass"
    assert result["notices"][0]["code"] == "ADAPTIVE_UNCOMMITTED_CHANGES"


def test_nesting_children_and_scope(repo, call):
    assigned(call, "--write", "src", "--commit")
    error = call("new", "--owner", "o", "--goal", "g", "--parent", "a1", "--write", "docs", expected=2)
    assert error["error"]["code"] == "ADAPTIVE_AUTHORITY_NOT_NARROWED"
    assigned(call, "--parent", "a1", "--write", "src/a")
    error = call("new", "--owner", "o", "--goal", "g", "--parent", "a2", expected=2)
    assert error["error"]["code"] == "ADAPTIVE_NESTING_DEPTH"
    returned(call)
    assert call("verify", "a1", expected=1)["checks"]["children"]["status"] == "fail"
    assert (
        call("close", "a1", "--outcome", "abandoned", "--reason", "stop", expected=2)["error"]["code"]
        == "ADAPTIVE_CHILDREN_OUTSTANDING"
    )
    call("close", "a2", "--outcome", "abandoned", "--reason", "stop")
    call("verify", "a1")


def test_retry_return_close_and_history(repo, call):
    assigned(call, "--check", "tests")
    returned(call)
    call("verify", "a1", expected=1)
    assert call("close", "a1", "--outcome", "integrated", expected=2)["error"]["code"] == "ARGUMENT_INVALID"
    returned(call, "a1", "--check", "tests=pass")
    call("verify", "a1")
    shown = call("show", "a1")
    assert sum(event["event"] == "returned" for event in shown["events"]) == 2
    call("return", "a1", "--status", "needs_input")
    result = call("close", "a1", "--outcome", "integrated", "--reason", "host review", "--strict", expected=1)
    assert result["notices"][0]["code"] == "ADAPTIVE_CLOSED_UNVERIFIED"
    assert call("verify", "a1", expected=2)["error"]["code"] == "ADAPTIVE_ASSIGNMENT_CLOSED"


def test_list_observations_missing_moved_and_untouched(repo, call, tmp_path):
    assigned(call)
    observed = call("list")["assignments"][0]["observed"]
    assert observed["attention"] == ["no-changes"]
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-qb", "dev", str(linked))
    assigned(call, "--worktree", str(linked), "--commit")
    git(linked, "commit", "--allow-empty", "-qm", "one")
    assert call("list")["assignments"][1]["observed"]["commits"] == 1
    linked.rename(tmp_path / "moved")
    missing = call("list")["assignments"][1]["observed"]
    assert missing["attention"] == ["worktree-missing"]
    assert missing["head"] is None


def test_preexisting_dirty_and_nested_repository(repo, call):
    (repo / "old").write_text("preexisting")
    assigned(call, "--write", "vendor")
    nested = repo / "vendor/x"
    nested.mkdir(parents=True)
    git(nested, "init", "-q")
    returned(call)
    result = call("verify", "a1")
    assert result["changed_paths"]["preexisting_dirty"] == ["old"]
    assert result["notices"][0]["code"] == "ADAPTIVE_PREEXISTING_DIRTY"


def test_fragment_repair_invalid_line_and_concurrency(repo, call):
    assigned(call)
    ledger = Ledger(repo)
    with ledger.path.open("ab") as stream:
        stream.write(b'{"partial":')
    assert call("list")["notices"][0]["code"] == "ADAPTIVE_LEDGER_FRAGMENT_IGNORED"
    assigned(call)
    assert call("list")["notices"] == []
    args = [
        sys.executable,
        "-m",
        "devkit_dist",
        "adaptive",
        "assignment",
        "new",
        "--owner",
        "o",
        "--goal",
        "g",
        "-w",
        str(repo),
        "--format",
        "json",
    ]

    def run(_):
        return subprocess.run(args, text=True, capture_output=True)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, range(2)))
    assert all(result.returncode == 0 for result in results), results
    assert len({json.loads(result.stdout)["assignment"]["id"] for result in results}) == 2
    for line in ledger.path.read_text().splitlines():
        json.loads(line)
    with ledger.path.open("ab") as stream:
        stream.write(b"invalid\n")
    assert call("list", expected=2)["error"]["code"] == "ADAPTIVE_LEDGER_UNREADABLE"


@pytest.mark.parametrize(
    "args",
    [
        ("list",),
        ("show", "a1"),
        ("verify", "a1"),
        ("return", "a1", "--status", "completed"),
        ("close", "a1", "--outcome", "abandoned", "--reason", "x"),
        ("new", "--owner", "o", "--goal", "g"),
    ],
)
def test_nonrepository_refused(repo, call, tmp_path, args):
    assert call(*args, root=tmp_path, expected=2)["error"]["code"] == "ADAPTIVE_REPOSITORY_UNSUPPORTED"


def test_unborn_and_bare_worktree(repo, call, tmp_path):
    unborn = tmp_path / "unborn"
    unborn.mkdir()
    git(unborn, "init", "-q")
    assert call("list", root=unborn)["assignments"] == []
    assert (
        call("new", "--owner", "o", "--goal", "g", root=unborn, expected=2)["error"]["code"]
        == "ADAPTIVE_REVISION_UNRESOLVED"
    )
    bare = tmp_path / "bare.git"
    git(repo, "clone", "--bare", str(repo), str(bare))
    linked = tmp_path / "bare-linked"
    git(bare, "worktree", "add", str(linked))
    assigned(lambda *args: call(*args, root=linked))
    assert (bare / "devkit/adaptive/ledger.jsonl").is_file()
    assert call("list", root=linked)["summary"]["open"] == 1


def test_invalid_inputs_do_not_append(repo, call):
    for args in [
        ("--id", "BAD"),
        ("--write", "*.py"),
        ("--write", "../escape"),
        ("--check", "=x"),
        ("--governing", "none", "--governing", "docs/x"),
    ]:
        assert call("new", "--owner", "o", "--goal", "g", *args, expected=2)["error"]["code"] == "ARGUMENT_INVALID"
    assert not Ledger(repo).path.exists()


def test_ledger_unwritable_reports_unrecorded(repo, call):
    directory = Ledger(repo).directory
    directory.parent.mkdir(parents=True)
    directory.write_text("blocks creation")
    result = call("new", "--owner", "o", "--goal", "g", expected=2)
    assert result["error"]["code"] == "ADAPTIVE_LEDGER_UNWRITABLE"


def test_readonly_parent_does_not_grant_commit(repo, call):
    assigned(call, "--write", "src")
    result = call("new", "--owner", "o", "--goal", "g", "--parent", "a1", "--commit", expected=2)
    assert result["error"]["code"] == "ADAPTIVE_AUTHORITY_NOT_NARROWED"


def test_symlink_scope_is_normalized_and_both_rename_names_observed(repo, call):
    (repo / "alias").symlink_to("src", target_is_directory=True)
    value = assigned(call, "--write", "alias")
    assert value["write"] == ["src"]
    (repo / "src/a").write_text("changed")
    returned(call)
    assert call("verify", "a1")["result"] == "pass"


@pytest.mark.parametrize("flag,code", [("--id", "ARGUMENT_INVALID"), ("--base", "ADAPTIVE_REVISION_UNRESOLVED")])
def test_explicit_empty_new_identity_does_not_append(repo, call, flag, code):
    assert call("new", "--owner", "o", "--goal", "g", flag, "", expected=2)["error"]["code"] == code
    assert not Ledger(repo).path.exists()


@pytest.mark.parametrize("value", ["^HEAD", "-h", "--all"])
def test_option_like_or_negated_revision_is_unresolved(repo, call, value):
    result = call("new", "--owner", "o", "--goal", "g", "--base", value, expected=2)
    assert result["error"]["code"] == "ADAPTIVE_REVISION_UNRESOLVED"
    assert not Ledger(repo).path.exists()
    assert assigned(call, "--base", "HEAD")["base"] == git(repo, "rev-parse", "HEAD")


def test_explicit_empty_final_does_not_append(repo, call):
    assigned(call)
    before = Ledger(repo).path.read_bytes()
    result = call("return", "a1", "--status", "completed", "--final", "", expected=2)
    assert result["error"]["code"] == "ADAPTIVE_REVISION_UNRESOLVED"
    assert Ledger(repo).path.read_bytes() == before


def test_list_reports_unreadable_worktree_and_exits_zero(repo, call, tmp_path):
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-qb", "dev", str(linked))
    assigned(call, "--worktree", str(linked))
    git(linked, "switch", "-q", "--orphan", "orphan")
    observed = call("list")["assignments"][0]["observed"]
    assert observed["worktree_state"] == "present"
    assert observed["attention"] == ["worktree-unreadable"]
    assert (observed["head"], observed["commits"], observed["dirty"]) == (None, None, None)
    assert "attention=worktree-unreadable" in call("list", text=True)


def test_given_final_resolves_in_assignment_worktree(repo, call, tmp_path):
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-qb", "dev", str(linked))
    assigned(call, "--worktree", str(linked), "--commit")
    git(linked, "commit", "--allow-empty", "-qm", "work")
    final = returned(call, "a1", "--final", "HEAD")["assignment"]["return"]["final"]
    assert final == git(linked, "rev-parse", "HEAD") != git(repo, "rev-parse", "HEAD")
    linked.rename(tmp_path / "moved")
    head = git(repo, "rev-parse", "HEAD")
    assert returned(call, "a1", "--final", "main")["assignment"]["return"]["final"] == head


def test_malformed_event_data_is_unreadable(repo, call):
    assigned(call)
    with Ledger(repo).path.open("ab") as stream:
        stream.write(b'{"schema":1,"at":"x","event":"verified","id":"a1","data":{}}\n')
    assert call("list", expected=2)["error"]["code"] == "ADAPTIVE_LEDGER_UNREADABLE"


@pytest.mark.parametrize("missing", ["status", "worktree", "base", "depends_on", "dirty_at_assign"])
def test_assigned_event_missing_recorded_field_is_unreadable(repo, call, missing):
    assigned(call)
    path = Ledger(repo).path
    event = json.loads(path.read_bytes())
    del event["data"][missing]
    path.write_text(json.dumps(event) + "\n")
    for command in (("list",), ("show", "a1")):
        assert call(*command, expected=2)["error"]["code"] == "ADAPTIVE_LEDGER_UNREADABLE"


def test_symlink_loop_scope_is_argument_error(repo, call):
    (repo / "loop").symlink_to("loop")
    assert call("new", "--owner", "o", "--goal", "g", "--write", "loop", expected=2)["error"]["code"] == (
        "ARGUMENT_INVALID"
    )
    assert not Ledger(repo).path.exists()


def test_transaction_body_oserror_is_not_ledger_unwritable(repo):
    with pytest.raises(FileNotFoundError), Ledger(repo).transaction():
        raise FileNotFoundError("body")
