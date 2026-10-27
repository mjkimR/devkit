"""A retained service whose loaded devkit code changed on disk refuses protected tools (SPEC-retained-runtime-receipt)."""

from __future__ import annotations

import asyncio
import importlib
import sys
from typing import Literal

import pytest
from devkit_core.base.mcp import McpTool
from devkit_core.core.plugins import iter_plugin_packages, load_subclasses
from devkit_dist.features.project.repositories.invocation import ExecutionBinding
from devkit_mcp.features.runtime.mcp.server import build_server
from fastmcp import Client

from .test_runtime import git

PACKAGE = "devkit_stale_fixture"
Execution = Literal["read_only", "preflight", "interactive", "approved_resume", "bounded_write"]


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    git(root, "init", "-b", "main")
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text("schema = 1\n")
    return root


@pytest.fixture
def loaded(tmp_path, monkeypatch):
    """A ``devkit_*`` package on ``sys.path`` whose ``model`` module is imported; ``unused`` never is."""
    source = tmp_path / "site" / PACKAGE
    source.mkdir(parents=True)
    (source / "__init__.py").write_text("")
    (source / "model.py").write_text("MEMBERS = ('SPEC',)\n")
    (source / "unused.py").write_text("VALUE = 1\n")
    monkeypatch.syspath_prepend(str(tmp_path / "site"))
    importlib.invalidate_caches()
    importlib.import_module(f"{PACKAGE}.model")
    yield source
    for name in [name for name in sys.modules if name == PACKAGE or name.startswith(f"{PACKAGE}.")]:
        del sys.modules[name]


def _tools(calls: list[str]) -> dict[str, McpTool]:
    def tool(name: str, execution: Execution) -> McpTool:
        async def invoke(arguments):
            calls.append(name)
            return {"ran": name}

        return McpTool(name, name, {"type": "object"}, invoke, execution=execution)

    return {
        "write": tool("write", "bounded_write"),
        "prepare": tool("prepare", "preflight"),
        "read": tool("read", "read_only"),
    }


def _call(server, name):
    async def call():
        async with Client(server, mode="legacy") as client:
            return await client.call_tool(name, {}, raise_on_error=False)

    return asyncio.run(call())


def test_changed_loaded_module_refuses_protected_tools(project, loaded):
    calls: list[str] = []
    server = build_server(_tools(calls), ExecutionBinding(project, project))
    assert not _call(server, "write").is_error
    (loaded / "model.py").write_text("MEMBERS = ('SPEC', 'USECASE')\n")
    for name in ("write", "prepare"):
        result = _call(server, name)
        assert result.is_error
        assert result.structured_content is not None
        error = result.structured_content["error"]
        assert error["code"] == "MCP_RUNTIME_STALE"
        assert error["advisory"]["mode"] == "INTERACTION"
        assert "Restart or reconnect" in error["advisory"]["fix"]
        assert any(f"{PACKAGE}.model" in detail for detail in error["advisory"]["details"])
    assert calls == ["write"]


def test_read_only_tools_and_unloaded_changes_are_not_refused(project, loaded):
    calls: list[str] = []
    server = build_server(_tools(calls), ExecutionBinding(project, project))
    (loaded / "unused.py").write_text("VALUE = 2\n")
    assert not _call(server, "write").is_error
    (loaded / "model.py").write_text("MEMBERS = ('SPEC', 'USECASE')\n")
    assert not _call(server, "read").is_error
    assert calls == ["write", "read"]


def test_plugins_loaded_after_start_are_not_stale(project, loaded, tmp_path):
    calls: list[str] = []
    server = build_server(_tools(calls), ExecutionBinding(project, project))
    plugin = tmp_path / "rules" / "demo"
    plugin.mkdir(parents=True)
    (plugin / "rule.py").write_text("class Demo:\n    pass\n")
    packages, failures = iter_plugin_packages(tmp_path / "rules")
    before = set(sys.modules)
    try:
        assert not failures
        assert load_subclasses(packages, object, namespace="devkit_rule").plugins
        assert any(name.startswith("devkit_rule_") for name in set(sys.modules) - before)
        assert not _call(server, "write").is_error
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]
    assert calls == ["write"]
