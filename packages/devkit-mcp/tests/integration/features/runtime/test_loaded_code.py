"""A retained service whose loaded devkit code changed on disk refuses protected tools (SPEC-retained-runtime-receipt)."""

from __future__ import annotations

import asyncio
import importlib
import sys

import pytest
from devkit_core.base.mcp import McpTool
from devkit_dist.features.project.repositories.invocation import ExecutionBinding
from devkit_mcp.features.runtime.mcp.server import build_server
from mcp import types

from .test_runtime import git

PACKAGE = "devkit_stale_fixture"


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
    def tool(name: str, execution: str) -> McpTool:
        async def invoke(arguments, confirm):
            calls.append(name)
            return {"ran": name}

        return McpTool(name, name, {"type": "object"}, invoke, execution=execution)

    return {
        "write": tool("write", "bounded_write"),
        "prepare": tool("prepare", "preflight"),
        "read": tool("read", "read_only"),
    }


def _call(server, name):
    result = asyncio.run(
        server.request_handlers[types.CallToolRequest](
            types.CallToolRequest(method="tools/call", params=types.CallToolRequestParams(name=name, arguments={}))
        )
    )
    return result.root


def test_changed_loaded_module_refuses_protected_tools(project, loaded):
    calls: list[str] = []
    server = build_server(_tools(calls), ExecutionBinding(project, project))
    assert not _call(server, "write").isError
    (loaded / "model.py").write_text("MEMBERS = ('SPEC', 'USECASE')\n")
    for name in ("write", "prepare"):
        result = _call(server, name)
        assert result.isError
        error = result.structuredContent["error"]
        assert error["code"] == "MCP_RUNTIME_STALE"
        assert error["mode"] == "BLOCKED"
        assert "Restart or reconnect" in error["fix"]
        assert any(f"{PACKAGE}.model" in detail for detail in error["details"])
    assert calls == ["write"]


def test_read_only_tools_and_unloaded_changes_are_not_refused(project, loaded):
    calls: list[str] = []
    server = build_server(_tools(calls), ExecutionBinding(project, project))
    (loaded / "unused.py").write_text("VALUE = 2\n")
    assert not _call(server, "write").isError
    (loaded / "model.py").write_text("MEMBERS = ('SPEC', 'USECASE')\n")
    assert not _call(server, "read").isError
    assert calls == ["write", "read"]
