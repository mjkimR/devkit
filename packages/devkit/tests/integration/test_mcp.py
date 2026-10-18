"""Real SDK client/server conversations over stdio; no OpenAI API or native UI is simulated as verified."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import timedelta

import pytest
from click.testing import CliRunner
from devkit.cli import cli
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from testsupport.rules import git

SCRIPT = """
import sys
from pathlib import Path
from types import SimpleNamespace
from importlib import metadata
from devkit.integration import Evidence, Readiness
from devkit.host.mcp.server import serve

class Provider:
    def check(self, context):
        plan = context.finish
        return Readiness(plan.source_sha, plan.target_sha, (Evidence("FIXTURE_CHECK_PASSED", plan.source_sha),))

provider = Provider()
original = metadata.entry_points
def entries(**kw):
    if kw.get("group") == "devkit.integration.readiness":
        return [SimpleNamespace(name="fixture", value="fixture:provider", dist=None, load=lambda: provider)] if kw.get("name") == "fixture" else []
    if kw.get("group") == "devkit.post_finish":
        return []
    return original(**kw)
metadata.entry_points = entries
serve(Path(sys.argv[1]))
"""


@pytest.mark.parametrize(
    "action,content,expected",
    [
        ("accept", {"approve": True}, "completed"),
        ("accept", {"approve": False}, "not_approved"),
        ("decline", None, "declined"),
        ("cancel", None, "cancelled"),
    ],
)
def test_native_protocol_confirmation_binds_to_real_git_scope(repo, action, content, expected):
    base, worktree = repo
    source, target = git(worktree, "rev-parse", "HEAD"), git(base, "rev-parse", "HEAD")
    refs_before = git(base, "show-ref")
    messages = []

    async def confirm(context, params):
        assert git(base, "show-ref") == refs_before and worktree.exists()
        messages.append(params.message)
        return types.ElicitResult(action=action, content=content)

    async def run():
        params = StdioServerParameters(command=sys.executable, args=["-c", SCRIPT, str(base)])
        async with (
            stdio_client(params) as (read, write),
            ClientSession(
                read, write, read_timeout_seconds=timedelta(seconds=20), elicitation_callback=confirm
            ) as session,
        ):
            await session.initialize()
            tools = await session.list_tools()
            assert {tool.name for tool in tools.tools} == {
                "integration_prepare",
                "integration_integrate",
                "integration_resume",
                "integration_status",
            }
            integration = next(tool for tool in tools.tools if tool.name == "integration_integrate")
            assert integration.annotations is not None
            assert integration.annotations.readOnlyHint is False
            assert integration.annotations.destructiveHint is True
            assert integration.annotations.openWorldHint is False
            assert integration.description is not None
            for guarantee in (
                "does not assert prior integration approval",
                "before confirmation it only validates",
                "Decline, cancellation or unavailable confirmation",
                "host confirmation UI authorizes execution",
                "changed scope blocks execution",
                "No fetch, push, remote deletion or PR operations",
            ):
                assert guarantee in integration.description
            result = await session.call_tool(
                "integration_integrate", {"branch": "dev-demo", "task_kind": "session", "task_id": "sdk-fixture"}
            )
            assert result.structuredContent is not None
            assert result.structuredContent["status"] == expected, result
            return result.structuredContent

    result = asyncio.run(run())
    assert len(messages) == 1 and source in messages[0] and target in messages[0] and str(worktree) in messages[0]
    if expected == "completed":
        assert not worktree.exists() and git(base, "rev-parse", "HEAD") == source
        assert result["authority"] == "mcp-elicitation"
    else:
        assert worktree.exists() and git(base, "show-ref") == refs_before
        assert result["authority"] == "none"


def test_client_without_forms_and_caller_approval_flags_cannot_execute(repo):
    base, worktree = repo
    refs_before = git(base, "show-ref")

    async def run():
        params = StdioServerParameters(command=sys.executable, args=["-c", SCRIPT, str(base)])
        async with (
            stdio_client(params) as (read, write),
            ClientSession(read, write, read_timeout_seconds=timedelta(seconds=20)) as session,
        ):
            await session.initialize()
            arguments = {"branch": "dev-demo", "task_kind": "session", "task_id": "fixture"}
            invalid = await session.call_tool("integration_integrate", arguments | {"approved": True})
            assert invalid.structuredContent is not None
            assert invalid.structuredContent["error"]["code"] == "HOST_MCP_ARGUMENT_INVALID"
            result = await session.call_tool("integration_integrate", arguments)
            assert result.structuredContent is not None
            assert result.structuredContent["status"] == "blocked"
            assert result.structuredContent["errors"][0]["code"] == "HOST_CONFIRMATION_UNAVAILABLE"

    asyncio.run(run())
    assert worktree.exists() and git(base, "show-ref") == refs_before


def test_manual_configuration_is_inspectable_and_does_not_write_host_settings(repo):
    base, _ = repo
    result = CliRunner().invoke(cli, ["host", "mcp", "config", "-w", str(base), "--format", "json"])
    assert result.exit_code == 0
    value = json.loads(result.stdout)
    assert value["transport"] == "stdio" and value["args"][-1] == str(base)
    assert value["inspect_command"] == "codex mcp get devkit --json"
    assert not (base / ".codex").exists()
