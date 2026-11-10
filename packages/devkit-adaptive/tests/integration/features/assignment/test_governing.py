"""Constraint IDs and paths resolve in the assignee's worktree."""

import subprocess


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def assigned(call, *args):
    return call("new", "--owner", "o", "--goal", "g", *args)["assignment"]


def document(path, identifier="CAP-TEST-one", alias="CAP-TEST-alias"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\nid: {identifier}\naliases: [{alias}]\ntitle: Test\nstatus: active\nsummary: "Fixture"\n---\n# Fixture\n'
    )


def test_governing_alias_paths_and_none(repo, call):
    document(repo / "docs/capabilities/test/CAP-TEST-one.md")
    (repo / "docs/notes.md").write_text("notes")
    value = assigned(call, "--governing", "CAP-TEST-alias", "--governing", "docs/notes.md")
    assert value["governing"] == ["CAP-TEST-one", "docs/notes.md"]
    assert assigned(call, "--governing", "none")["governing"] == []
    assert assigned(call)["governing"] == []


def test_unresolved_duplicate_and_other_worktree(repo, call, tmp_path):
    result = call(
        "new",
        "--owner",
        "o",
        "--goal",
        "g",
        "--governing",
        "CAP-NOPE-missing",
        "--governing",
        "docs/absent.md",
        expected=2,
    )
    assert result["error"]["code"] == "ADAPTIVE_GOVERNING_UNRESOLVED"
    assert "unknown-id" in str(result) and "missing-path" in str(result)
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-qb", "dev", str(linked))
    main_doc = repo / "docs/capabilities/test/CAP-TEST-one.md"
    document(main_doc)
    result = call(
        "new", "--owner", "o", "--goal", "g", "--worktree", str(linked), "--governing", "CAP-TEST-one", expected=2
    )
    assert result["error"]["code"] == "ADAPTIVE_GOVERNING_UNRESOLVED"
    assert assigned(call, "--worktree", str(linked), "--governing", str(main_doc))["governing"] == [str(main_doc)]
    document(repo / "docs/capabilities/test/duplicate.md")
    assert "duplicate-id" in str(call("new", "--owner", "o", "--goal", "g", "--governing", "CAP-TEST-one", expected=2))
