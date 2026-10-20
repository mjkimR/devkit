"""Transport-independent execution binding and installed SDK capability behavior."""

from __future__ import annotations

import shutil
import subprocess
from types import SimpleNamespace

import pytest
from devkit.core.mcp import McpTool
from devkit.core.mcp_context import (
    ExecutionBinding,
    McpInteractiveError,
    McpWorkspaceError,
    capture_terminal_removal,
    guard_execution,
    invocation,
)
from devkit_mcp import configuration, services
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
