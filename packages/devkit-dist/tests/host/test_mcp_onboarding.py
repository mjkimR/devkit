"""Project registration ownership, clean-tree behavior and interrupted transaction recovery."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from devkit.host import registrations as r


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Fixture")
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text("schema = 1\n")
    (root / ".devkit/.gitignore").write_text("transient/\n")
    git(root, "add", ".devkit")
    git(root, "commit", "-m", "fixture")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))
    monkeypatch.setattr(r, "collisions", lambda *args: [])
    launch = r.LaunchDescriptor("/retained/python", ("-m", "devkit", "mcp", "serve"), str(root), str(root), "local")
    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [SimpleNamespace(load=lambda: lambda *a, **k: launch)])
    return root


def test_registration_converges_and_uninstall_removes_only_owned(repo, monkeypatch):
    planned = r.plan(repo, ["codex", "claude"])
    assert not (repo / ".mcp.json").exists()  # planning is read-only
    r.apply(planned)
    assert git(repo, "status", "--porcelain") == ""
    snapshots = {name: (repo / name).read_bytes() for name in [*r.DESTINATIONS.values(), r.LEDGER]}
    assert r.plan(repo, ["codex", "claude"]).changes == []
    assert snapshots == {name: (repo / name).read_bytes() for name in snapshots}
    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [])
    r.apply(r.plan(repo, ["codex", "claude"]))
    assert r._entry("codex", (repo / ".codex/config.toml").read_bytes()) is None
    assert r._entry("claude", (repo / ".mcp.json").read_bytes()) is None
    assert git(repo, "status", "--porcelain") == ""
    assert b"/.mcp.json" in (repo / ".git/info/exclude").read_bytes()


@pytest.mark.parametrize("tracked,ignored", [(True, False), (True, True), (False, False)])
def test_tracked_and_visible_foreign_destinations_are_unchanged(repo, tracked, ignored):
    target = repo / ".mcp.json"
    raw = b'{"foreign": "kept"}\n'
    target.write_bytes(raw)
    if tracked:
        git(repo, "add", ".mcp.json")
        git(repo, "commit", "-m", "host-owned")
    if ignored:
        (repo / ".git/info/exclude").write_text("/.mcp.json\n")
    planned = r.plan(repo, ["claude"])
    assert planned.notices[0].code == "MCP_REGISTRATION_UNAVAILABLE"
    r.apply(planned)
    assert target.read_bytes() == raw


def test_ignored_foreign_settings_mode_and_noop_preserved(repo):
    target = repo / ".mcp.json"
    (repo / ".git/info/exclude").write_text("/.mcp.json\n")
    target.write_text('{"mcpServers":{"foreign":{"command":"other"}},"metadata":true}')
    target.chmod(0o640)
    r.apply(r.plan(repo, ["claude"]))
    content = target.read_bytes()
    assert json.loads(content)["mcpServers"]["foreign"] == {"command": "other"}
    assert target.stat().st_mode & 0o777 == 0o640
    r.apply(r.plan(repo, ["claude"]))
    assert target.read_bytes() == content


@pytest.mark.parametrize("edit", ["edited", "missing", "unowned", "duplicate", "malformed"])
def test_conflicts_fail_before_writes(repo, edit):
    target = repo / ".mcp.json"
    (repo / ".git/info/exclude").write_text("/.mcp.json\n")
    if edit in {"edited", "missing"}:
        r.apply(r.plan(repo, ["claude"]))
    values = {
        "edited": '{"mcpServers":{"devkit":{"command":"edited"}}}',
        "missing": "{}",
        "unowned": '{"mcpServers":{"devkit":{"command":"/retained/python"}}}',
        "duplicate": '{"mcpServers":{},"mcpServers":{}}',
        "malformed": "{",
    }
    target.write_text(values[edit])
    with pytest.raises(r.RegistrationError):
        r.plan(repo, ["claude", "codex"])
    assert not (repo / ".codex/config.toml").exists()


def test_absent_owned_destination_is_recreated(repo):
    r.apply(r.plan(repo, ["claude"]))
    (repo / ".mcp.json").unlink()
    r.apply(r.plan(repo, ["claude"]))
    assert r._entry("claude", (repo / ".mcp.json").read_bytes()) is not None


def test_foreign_linked_worktree_prevents_new_exclusion(repo, tmp_path):
    other = tmp_path / "linked"
    git(repo, "worktree", "add", "-b", "dev-task", str(other))
    (other / ".mcp.json").write_text("{}")
    before = (repo / ".git/info/exclude").read_bytes()
    planned = r.plan(repo, ["claude"])
    assert planned.notices and not planned.changes
    r.apply(planned)
    assert (repo / ".git/info/exclude").read_bytes() == before
    assert ".mcp.json" in git(other, "status", "--porcelain")


def test_external_edit_or_git_index_change_aborts(repo):
    planned = r.plan(repo, ["claude"])
    (repo / ".mcp.json").write_text("{}")
    with pytest.raises(r.RegistrationError):
        r.apply(planned)
    assert (repo / ".mcp.json").read_text() == "{}"


def test_interrupted_transaction_recovers_exact_previous_bytes(repo, monkeypatch):
    planned = r.plan(repo, ["codex", "claude"])
    original = r._write

    def fail(path, value, anchor):
        if path == repo / ".codex/config.toml":
            raise OSError("fixture interruption")
        original(path, value, anchor)

    monkeypatch.setattr(r, "_write", fail)
    with pytest.raises(OSError):
        r.apply(planned)
    assert (repo / r.JOURNAL).exists()
    monkeypatch.setattr(r, "_write", original)
    r.recover(repo)
    assert not (repo / r.JOURNAL).exists()
    assert not (repo / ".mcp.json").exists()
    r.apply(r.plan(repo, ["codex", "claude"]))
    assert not r.plan(repo, ["codex", "claude"]).changes


def test_locked_validation_never_writes(repo):
    planned = r.plan(repo, ["claude"])
    with pytest.raises(r.RegistrationError):
        r.apply(planned, locked=True)
    assert not (repo / ".mcp.json").exists()


def test_optout_and_agent_removal(repo):
    r.apply(r.plan(repo, ["codex", "claude"]))
    r.apply(r.plan(repo, ["claude"]))
    assert r._entry("codex", (repo / ".codex/config.toml").read_bytes()) is None
    (repo / ".devkit/config.local.toml").write_text("[mcp]\nregister=false\n")
    r.apply(r.plan(repo, ["claude"]))
    assert r._entry("claude", (repo / ".mcp.json").read_bytes()) is None


def test_unloadable_provider_is_not_uninstall(repo, monkeypatch):
    r.apply(r.plan(repo, ["claude"]))

    def fail():
        raise ImportError("fixture")

    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [SimpleNamespace(load=fail)])
    with pytest.raises(r.RegistrationError, match="not uninstall"):
        r.plan(repo, ["claude"])
    assert r._entry("claude", (repo / ".mcp.json").read_bytes()) is not None


def test_symlink_and_malformed_ledger_refuse(repo, tmp_path):
    (repo / ".mcp.json").symlink_to(tmp_path / "foreign")
    with pytest.raises(r.RegistrationError):
        r.plan(repo, ["claude"])
    (repo / ".mcp.json").unlink()
    ledger = repo / r.LEDGER
    ledger.parent.mkdir(parents=True)
    ledger.write_text("{}")
    with pytest.raises(r.RegistrationError):
        r.plan(repo, ["claude"])
