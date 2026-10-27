"""Project registration ownership, clean-tree behavior and interrupted transaction recovery."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from devkit_dist.features.host.usecases import registrations as r


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
    launch = r.LaunchDescriptor(
        "/retained/python", ("-m", "devkit_dist", "mcp", "serve"), str(root), str(root), "local"
    )
    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [SimpleNamespace(load=lambda: lambda *a, **k: launch)])
    return root


def test_registration_converges_and_uninstall_removes_only_owned(repo, monkeypatch):
    planned = r.plan(repo, ["codex", "claude", "antigravity"])
    assert not (repo / ".mcp.json").exists()  # planning is read-only
    assert not (repo / ".agents/mcp_config.json").exists()
    r.apply(planned)
    assert git(repo, "status", "--porcelain") == ""
    snapshots = {name: (repo / name).read_bytes() for name in [*r.DESTINATIONS.values(), r.LEDGER]}
    assert r.plan(repo, ["codex", "claude", "antigravity"]).changes == []
    assert snapshots == {name: (repo / name).read_bytes() for name in snapshots}
    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [])
    r.apply(r.plan(repo, ["codex", "claude", "antigravity"]))
    assert r._entry("codex", (repo / ".codex/config.toml").read_bytes()) is None
    assert r._entry("claude", (repo / ".mcp.json").read_bytes()) is None
    assert r._entry("antigravity", (repo / ".agents/mcp_config.json").read_bytes()) is None
    assert git(repo, "status", "--porcelain") == ""
    assert b"/.mcp.json" in (repo / ".git/info/exclude").read_bytes()
    assert b"/.agents/mcp_config.json" in (repo / ".git/info/exclude").read_bytes()


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


def _interrupt_after_host(repo, monkeypatch):
    original = r._write

    def fail(path, value, anchor):
        if path == repo / r.LEDGER:
            raise OSError("fixture interruption")
        original(path, value, anchor)

    monkeypatch.setattr(r, "_write", fail)
    with pytest.raises(OSError):
        r.apply(r.plan(repo, ["claude"]))
    monkeypatch.setattr(r, "_write", original)


def test_recovery_refuses_newly_tracked_destination(repo, monkeypatch):
    _interrupt_after_host(repo, monkeypatch)
    git(repo, "add", "-f", ".mcp.json")
    before = (repo / ".mcp.json").read_bytes()
    with pytest.raises(r.RegistrationError, match="Git eligibility"):
        r.recover(repo)
    assert (repo / ".mcp.json").read_bytes() == before
    assert (repo / r.JOURNAL).exists()


def test_recovery_retains_exclusion_used_by_linked_checkout(repo, monkeypatch, tmp_path):
    other = tmp_path / "linked"
    git(repo, "worktree", "add", "-b", "dev-linked", str(other))
    _interrupt_after_host(repo, monkeypatch)
    r.apply(r.plan(other, ["claude"]))
    other_bytes = (other / ".mcp.json").read_bytes()
    r.recover(repo)
    assert not (repo / ".mcp.json").exists()
    assert (other / ".mcp.json").read_bytes() == other_bytes
    assert r._ignored(other, ".mcp.json")
    assert "/.mcp.json" in r._ledger(repo)["excludes"]
    assert not (repo / r.JOURNAL).exists()


def test_recovery_interruption_is_repeatable(repo, monkeypatch):
    _interrupt_after_host(repo, monkeypatch)
    original = r._write

    def fail(path, value, anchor):
        if path == repo / ".mcp.json":
            raise OSError("recovery interruption")
        original(path, value, anchor)

    monkeypatch.setattr(r, "_write", fail)
    with pytest.raises(OSError):
        r.recover(repo)
    monkeypatch.setattr(r, "_write", original)
    r.recover(repo)
    assert not (repo / r.JOURNAL).exists()
    assert not (repo / ".mcp.json").exists()
    assert "/.mcp.json" in r._ledger(repo)["excludes"]


def test_claude_code_selection_uses_the_claude_adapter(repo):
    r.apply(r.plan(repo, ["claude-code"]))
    assert (repo / ".mcp.json").is_file()
    assert r.inspect(repo, ["claude-code"])["project"]["claude"]["state"] == "owned"


def test_antigravity_selection_uses_the_antigravity_adapter(repo):
    r.apply(r.plan(repo, ["antigravity"]))
    assert (repo / ".agents/mcp_config.json").is_file()
    assert r.inspect(repo, ["antigravity"])["project"]["antigravity"]["state"] == "owned"
    assert b"/.agents/mcp_config.json" in (repo / ".git/info/exclude").read_bytes()


def test_inspect_lists_a_refused_plan_under_errors_not_notices(repo):
    (repo / r.JOURNAL).parent.mkdir(parents=True, exist_ok=True)
    (repo / r.JOURNAL).write_text("{}")
    result = r.inspect(repo, ["claude"])
    assert [error.code for error in result["errors"]] == ["MCP_REGISTRATION_INTERRUPTED"]
    assert result["notices"] == []
    assert r.inspect(repo.parent, [])["errors"] == []  # nothing to inspect is no problem


def test_actions_name_each_path_and_create_for_a_new_file(repo):
    planned = r.plan(repo, ["claude"])
    assert planned.actions == [
        (".git/info/exclude", "update"),
        (".mcp.json", "create"),
        (r.LEDGER, "create"),
    ]
    r.apply(planned)
    (repo / ".devkit/config.local.toml").write_text("[mcp]\nregister=false\n")
    assert dict(r.plan(repo, ["claude"]).actions)[".mcp.json"] == "update"


def test_actions_name_a_linked_worktree_exclusion_by_its_absolute_path(repo, tmp_path):
    other = tmp_path / "linked"
    git(repo, "worktree", "add", "-b", "dev-actions", str(other))
    paths = [path for path, _ in r.plan(other, ["claude"]).actions]
    assert str((repo / ".git/info/exclude").resolve()) in paths


def test_unregistered_hosts_reports_desired_registration_absent_from_the_checkout(repo, monkeypatch):
    def refuse_load(**kw):
        return [SimpleNamespace(load=lambda: pytest.fail("the provider must not be loaded"))]

    monkeypatch.setattr(r.metadata, "entry_points", refuse_load)
    assert r.unregistered_hosts(repo, ["claude-code", "codex", "cursor"]) == ["claude", "codex"]
    launch = r.LaunchDescriptor("/retained/python", ("-m", "x"), str(repo), str(repo), "local")
    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [SimpleNamespace(load=lambda: lambda *a, **k: launch)])
    r.apply(r.plan(repo, ["claude"]))
    assert r.unregistered_hosts(repo, ["claude-code", "codex"]) == ["codex"]
    (repo / ".devkit/config.local.toml").write_text("[mcp]\nregister=false\n")
    assert r.unregistered_hosts(repo, ["codex"]) == []


def test_unregistered_hosts_is_empty_without_a_provider_or_git(repo, monkeypatch, tmp_path):
    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [])
    assert r.unregistered_hosts(repo, ["claude"]) == []
    plain = tmp_path / "plain"
    (plain / ".devkit").mkdir(parents=True)
    (plain / ".devkit/config.toml").write_text("schema = 1\n")
    monkeypatch.setattr(r.metadata, "entry_points", lambda **kw: [SimpleNamespace()])
    assert r.unregistered_hosts(plain, ["claude"]) == []


def test_unregistered_hosts_skips_a_tracked_destination(repo):
    (repo / ".mcp.json").write_text("{}\n")
    git(repo, "add", ".mcp.json")
    git(repo, "commit", "-m", "host-owned")
    assert r.unregistered_hosts(repo, ["claude"]) == []


def test_each_registration_condition_has_its_own_code_mode_and_target(repo, tmp_path):
    from devkit.advisory import ActionMode

    r.apply(r.plan(repo, ["claude"]))
    (repo / ".mcp.json").write_text('{"mcpServers":{"devkit":{"command":"edited"}}}')
    with pytest.raises(r.RegistrationError) as edited:
        r.plan(repo, ["claude"])
    assert edited.value.code == "MCP_REGISTRATION_CONFLICT" and edited.value.mode is ActionMode.INTERACTION
    assert edited.value.target_files == (".mcp.json",)
    for error in (
        r.RegistrationError("x"),
        r.RegistrationUnavailable("x"),
        r.RuntimeUnavailable("x"),
        r.LedgerUnignored("x"),
    ):
        assert "independently authorized" not in (error.fix or "") and "PATH" not in (error.fix or "")
    runtime = r.RuntimeUnavailable("x")
    assert runtime.mode is ActionMode.INPUT_ERROR and runtime.target_files == ("--executable",)
    ledger = r.LedgerUnignored("x")
    assert ledger.mode is ActionMode.AUTO and ledger.fix == "uv run devkit sync"
    (repo / r.JOURNAL).write_text("{}")
    with pytest.raises(r.RegistrationError) as interrupted:
        r.plan(repo, ["claude"])
    assert interrupted.value.mode is ActionMode.AUTO and interrupted.value.fix == "uv run devkit sync"


def test_unsupported_host_and_retained_exclusions_have_their_own_codes(repo):
    planned = r.plan(repo, ["claude", "cursor"])
    assert [notice.code for notice in planned.notices] == ["MCP_HOST_UNSUPPORTED"]
    r.apply(planned)
    removed = r.plan(repo, [], remove=True)
    assert [notice.code for notice in removed.notices] == ["MCP_EXCLUSIONS_RETAINED"]
    r.apply(removed)
    # Retained lines were reported when they were left; an unchanged rerun repeats nothing.
    assert r.plan(repo, [], remove=True).notices == []


def test_tracked_destination_targets_the_file(repo):
    (repo / ".mcp.json").write_text("{}")
    git(repo, "add", ".mcp.json")
    git(repo, "commit", "-q", "-m", "tracked")
    (notice,) = r.plan(repo, ["claude"]).notices
    assert notice.code == "MCP_REGISTRATION_UNAVAILABLE" and notice.target_files == (".mcp.json",)
