"""Transport-independent execution binding and installed SDK capability behavior."""

from __future__ import annotations

import shutil
import subprocess
from types import SimpleNamespace

import pytest
from devkit_core.base.mcp import McpTool
from devkit_dist.features.project.repositories.invocation import (
    ExecutionBinding,
    McpInteractiveError,
    McpWorkspaceError,
    capture_terminal_removal,
    guard_execution,
)
from devkit_dist.features.project.usecases.invocation import invocation
from devkit_mcp.features.runtime.usecases import configuration
from devkit_mcp.features.runtime.usecases import discovery as services
from mcp import types


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


@pytest.fixture
def clones(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    git(base, "init", "-b", "main")
    git(base, "config", "user.name", "Fixture")
    git(base, "config", "user.email", "fixture@example.invalid")
    (base / ".devkit").mkdir()
    (base / ".devkit/config.toml").write_text("schema = 1\n")
    git(base, "add", ".devkit")
    git(base, "commit", "-m", "fixture")
    task = tmp_path / "task"
    git(base, "worktree", "add", "-b", "dev-task", str(task))
    return base, task


def cloud(root):
    (root / ".devkit/config.local.toml").write_text('[execution]\nenvironment="cloud"\n')


def test_owning_workspace_not_executor_controls_execution(clones):
    base, task = clones
    binding = ExecutionBinding(task, base)
    cloud(base)
    with invocation(binding):
        guard_execution()
        cloud(task)
        with pytest.raises(McpInteractiveError):
            guard_execution()
    with pytest.raises(McpInteractiveError), invocation(binding):
        guard_execution()


def test_missing_or_wrong_workspace_fails_closed(clones):
    base, task = clones
    binding = ExecutionBinding(task, base)
    with invocation(binding):
        shutil.rmtree(task)
        with pytest.raises(McpWorkspaceError):
            guard_execution()
    with pytest.raises(McpWorkspaceError), invocation(binding):
        pass


def test_terminal_cleanup_exception_is_exact_and_cannot_resume(clones):
    base, task = clones
    binding = ExecutionBinding(task, base)
    with invocation(binding):
        capture_terminal_removal(task)
        git(base, "worktree", "remove", str(task))
        guard_execution(terminal=True)
        with pytest.raises(McpWorkspaceError):
            guard_execution()  # cannot merge or push after self-removal
    with pytest.raises(McpWorkspaceError), invocation(binding):
        guard_execution(terminal=True)


def test_cloud_blocks_terminal_capture(clones):
    base, task = clones
    binding = ExecutionBinding(task, base)
    with invocation(binding):
        cloud(task)
        with pytest.raises(McpInteractiveError):
            capture_terminal_removal(task)


def test_linked_interpreter_lexical_path_is_rejected(clones):
    _, task = clones
    candidate = task / ".venv/bin/python"
    candidate.parent.mkdir(parents=True)
    candidate.symlink_to(shutil.which("python3"))
    assert configuration._linked_source(candidate)


def test_service_classification_is_separate_from_annotations(monkeypatch, tmp_path):
    async def call(args, confirm):
        return {}

    tool = McpTool("fixture", "fixture", {"type": "object"}, call, read_only=True)
    assert tool.execution == "interactive"
    monkeypatch.setattr(
        services.metadata,
        "entry_points",
        lambda **kw: [SimpleNamespace(name="fixture", value="fixture:create", load=lambda: lambda root: (tool,))],
    )
    assert services.load_tools(tmp_path)["fixture"] is tool
    monkeypatch.setattr(
        services.metadata,
        "entry_points",
        lambda **kw: [SimpleNamespace(name="fixture", value="fixture:create", load=lambda: lambda root: (tool, tool))],
    )
    with pytest.raises(Exception, match="cannot load"):
        services.load_tools(tmp_path)


@pytest.mark.parametrize("capability,form", [({}, False), ({"form": {}}, True), ({"url": {}}, False)])
def test_installed_sdk_normalizes_form_capability(capability, form):
    parsed = types.ClientCapabilities.model_validate({"elicitation": capability})
    assert parsed.elicitation is not None
    assert (parsed.elicitation.form is not None) is form


def test_probe_reports_advisory_and_candidate_rejects_removable_dependency(clones, monkeypatch):
    import json
    import sys

    base, task = clones
    probe = subprocess.run([sys.executable, "-c", configuration.PROBE], capture_output=True, text=True, check=True)
    import devkit.advisory

    assert devkit.advisory.__file__ in json.loads(probe.stdout)["paths"]
    candidate = base / "python"
    candidate.touch()
    dependency = task / "packages/devkit-advisory/src/devkit/advisory/__init__.py"
    monkeypatch.setattr(configuration.metadata, "entry_points", lambda **kw: [])
    monkeypatch.setattr(configuration.metadata, "version", lambda name: "1.0")
    original_run = subprocess.run
    monkeypatch.setattr(
        configuration.subprocess,
        "run",
        lambda *a, **kw: (
            SimpleNamespace(
                returncode=0,
                stdout=json.dumps({"version": "1.0", "services": [], "prefix": str(base), "paths": [str(dependency)]}),
            )
            if "-c" in a[0]
            else original_run(*a, **kw)
        ),
    )
    with pytest.raises(configuration.RuntimeUnavailable):
        configuration.descriptor(task, executable=str(candidate))


@pytest.mark.parametrize("operation", ["registration", "locked"])
def test_child_sync_rechecks_original_owner_after_lock(clones, operation):
    import json
    import os
    import sys

    from devkit_dist.features.project.repositories.invocation import CONSTRAINT_ENV, constraint_environment

    base, task = clones
    with invocation(ExecutionBinding(base, base)):
        restricted = constraint_environment()
    assert set(json.loads(restricted[CONSTRAINT_ENV])) == {"workspace", "common", "identity"}
    script = """
import json, sys
from contextlib import contextmanager
from pathlib import Path
from devkit.advisory import AdvisoryError
from devkit_dist.features.distribution.usecases import sync
owner, target = Path(sys.argv[1]), Path(sys.argv[2])
@contextmanager
def lock(*args, **kwargs):
    (owner / ".devkit/config.local.toml").write_text('[execution]\\nenvironment="cloud"\\n')
    yield
sync.registrations.clone_lock = lock
sync.registrations.apply = lambda *a, **k: (_ for _ in ()).throw(AssertionError("registration mutation"))
sync.commit_locked = lambda *a, **k: (_ for _ in ()).throw(AssertionError("asset mutation"))
try:
    if sys.argv[3] == "registration": sync.sync_registrations(target)
    else: sync.sync_project(target, [], locked=True)
except AdvisoryError as exc:
    print(json.dumps({"code": exc.code}))
else:
    raise AssertionError("owner cloud transition was ignored")
"""
    completed = subprocess.run(
        [sys.executable, "-c", script, str(base), str(task), operation],
        env={**os.environ, **restricted},
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(completed.stdout)["code"] == "MCP_INTERACTIVE_UNAVAILABLE"
    assert not (task / ".devkit/config.local.toml").exists()
    assert not (task / ".mcp.json").exists()


def test_constraint_never_inherits_terminal_removal_authority(clones, monkeypatch):
    from devkit_dist.features.project.repositories.invocation import constraint_environment

    base, task = clones
    with invocation(ExecutionBinding(task, base)):
        restricted = constraint_environment()
        capture_terminal_removal(task)
        git(base, "worktree", "remove", str(task))
        guard_execution(terminal=True)
    for key, value in restricted.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(McpWorkspaceError):
        guard_execution(terminal=True)


def test_cloud_transition_stops_transaction_writes_and_retains_journal(clones, monkeypatch):
    from devkit_dist.features.distribution.models.content import Content
    from devkit_dist.features.distribution.services.installation import transaction

    base, task = clones
    original = transaction.replace_file

    def write_then_change(path, content):
        original(path, content)
        if path == task / transaction.JOURNAL:
            cloud(base)

    monkeypatch.setattr(transaction, "replace_file", write_then_change)
    with invocation(ExecutionBinding(base, base)), pytest.raises(McpInteractiveError):
        transaction.apply_changes(task, {"asset.txt": Content(b"must not be written", 0o644)})
    assert not (task / "asset.txt").exists()
    assert (task / transaction.JOURNAL).exists()
