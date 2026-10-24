"""FastMCP adapts devkit tools while preserving native confirmation rules."""

from __future__ import annotations

import asyncio

from devkit_core.base.mcp import McpTool
from devkit_core.core.git import run_git
from devkit_dist.features.project.repositories.invocation import ExecutionBinding
from devkit_mcp.features.runtime.mcp.server import build_server
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult
from mcp_types import ElicitRequestFormParams


def _project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    run_git(root, "init", "-b", "main")
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text("schema = 1\n")
    return root


def _interactive_tool(calls: list[dict]):
    async def invoke(arguments, confirm):
        reply = await confirm(
            "Approve this operation",
            {"type": "object", "properties": {"approve": {"type": "boolean"}}},
        )
        calls.append({"action": reply.action, **reply.content})
        return {"confirmed": reply.content.get("approve", False)}

    return McpTool("confirm", "Confirm an operation", {"type": "object"}, invoke)


def test_native_form_confirmation_acceptance_and_decline(tmp_path):
    project = _project(tmp_path)
    calls: list[dict] = []
    server = build_server({"confirm": _interactive_tool(calls)}, ExecutionBinding(project, project))

    async def approve_handler(message, response_type, request, context):
        assert message == "Approve this operation"
        assert isinstance(request, ElicitRequestFormParams)
        return ElicitResult(action="accept", content={"approve": True})

    async def decline_handler(message, response_type, request, context):
        return ElicitResult(action="decline")

    async def exercise(handler):
        async with Client(server, mode="legacy", elicitation_handler=handler) as client:
            return await client.call_tool("confirm", {}, raise_on_error=False)

    accepted, declined = asyncio.run(exercise(approve_handler)), asyncio.run(exercise(decline_handler))
    assert not accepted.is_error
    assert accepted.structured_content == {"confirmed": True}
    assert not declined.is_error
    assert declined.structured_content == {"confirmed": False}
    assert calls == [{"action": "accept", "approve": True}, {"action": "decline"}]


def test_missing_native_form_capability_fails_closed(tmp_path):
    project = _project(tmp_path)
    calls: list[dict] = []
    server = build_server({"confirm": _interactive_tool(calls)}, ExecutionBinding(project, project))

    async def exercise():
        async with Client(server, mode="legacy") as client:
            return await client.call_tool("confirm", {}, raise_on_error=False)

    result = asyncio.run(exercise())
    assert result.is_error
    assert result.structured_content is not None
    assert result.structured_content["error"]["code"] == "HOST_CONFIRMATION_UNAVAILABLE"
    assert calls == []
