"""Exercise installed integration/MCP wheels with a disposable, explicitly installed readiness fixture."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from datetime import timedelta
from pathlib import Path

from devkit.worktree import locate, start
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

PROVIDER = """
from pathlib import Path
from devkit.core.git import run_git
from devkit.integration import Evidence, Readiness

def check(context):
    plan = context.finish
    value = run_git(Path(plan.base), "show", f"{plan.source_sha}:ready.txt").strip()
    return Readiness(plan.source_sha, plan.target_sha, (Evidence("SMOKE_CHECK_PASSED", plan.source_sha),),
                     () if value == b"ready" else ("smoke fixture is not ready",),
                     result_sha=context.result_sha, disclosure="smoke fixture check only")
"""


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


async def conversation(root: Path, worktree: Path) -> None:
    approvals: list[str] = []

    async def confirm(context, params):
        approvals.append(params.message)
        return types.ElicitResult(action="accept", content={"approve": len(approvals) == 2})

    args = ["-m", "devkit", "host", "mcp", "serve", "-w", str(root)]
    params = StdioServerParameters(command=sys.executable, args=args)
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write, read_timeout_seconds=timedelta(seconds=30), elicitation_callback=confirm) as session,
    ):
        await session.initialize()
        tools = await session.list_tools()
        assert "integration_integrate" in {tool.name for tool in tools.tools}
        request = {"branch": "dev-smoke", "task_kind": "session", "task_id": "installed-fixture"}
        tip = git(worktree, "rev-parse", "HEAD")
        before = git(root, "rev-parse", "HEAD")
        preview = await session.call_tool("integration_prepare", request)
        assert preview.structuredContent is not None and preview.structuredContent["status"] == "prepared"
        refused = await session.call_tool(
            "integration_resume", {"request_id": preview.structuredContent["request"]["id"]}
        )
        assert (
            refused.structuredContent is not None
            and refused.structuredContent["error"]["code"] == "INTEGRATION_AUTHORITY_REQUIRED"
        )
        nonapproved = await session.call_tool("integration_integrate", request)
        assert nonapproved.structuredContent is not None and nonapproved.structuredContent["status"] == "not_approved"
        assert worktree.exists() and git(root, "rev-parse", "HEAD") == before
        approved = await session.call_tool("integration_integrate", request)
        assert approved.structuredContent is not None and approved.structuredContent["status"] == "completed", approved
        assert len(approvals) == 2 and tip in approvals[1] and before in approvals[1]
        assert not worktree.exists() and git(root, "rev-parse", "HEAD^1", "HEAD^2").split() == [before, tip]
        assert approved.structuredContent["request"]["network_operations"] == "excluded"
        assert "context" not in approved.structuredContent["request"]
        assert "SMOKE_CHECK_PASSED" not in approvals[1]
        request_id = approved.structuredContent["request"]["id"]
        inspected = await session.call_tool("integration_status", {"request_id": request_id})
        assert inspected.structuredContent is not None and "context" not in inspected.structuredContent["request"]
        detailed = await session.call_tool("integration_status", {"request_id": request_id, "detail": True})
        assert detailed.structuredContent is not None and detailed.structuredContent["request"]["readiness"]["evidence"]
        resumed = await session.call_tool("integration_resume", {"request_id": request_id})
        assert resumed.structuredContent is not None and resumed.structuredContent["status"] == "completed"
        assert len(approvals) == 2


def main() -> None:
    site = Path(sysconfig.get_paths()["purelib"])
    module = site / "devkit_smoke_readiness.py"
    metadata = site / "devkit_smoke_readiness-0.0.0.dist-info"
    assert not module.exists() and not metadata.exists()
    try:
        module.write_text(PROVIDER)
        metadata.mkdir()
        (metadata / "METADATA").write_text("Metadata-Version: 2.1\nName: devkit-smoke-readiness\nVersion: 0.0.0\n")
        (metadata / "entry_points.txt").write_text("[devkit.integration.readiness]\nsmoke = devkit_smoke_readiness\n")
        with tempfile.TemporaryDirectory(prefix="integration-", dir=sys.argv[1]) as temporary:
            root = Path(temporary) / "repo"
            root.mkdir()
            git(root, "init", "-qb", "main")
            git(root, "config", "user.name", "devkit smoke")
            git(root, "config", "user.email", "smoke@example.test")
            (root / ".devkit").mkdir()
            (root / ".devkit/config.toml").write_text('[integration]\nprovider = "smoke"\n')
            git(root, "add", ".")
            git(root, "commit", "-qm", "configure fixture")
            worktree = start(locate(root), "dev-smoke").path
            (worktree / "ready.txt").write_text("ready\n")
            git(worktree, "add", ".")
            git(worktree, "commit", "-qm", "ready fixture")
            result = subprocess.check_output(
                [
                    sys.executable,
                    "-m",
                    "devkit",
                    "integration",
                    "prepare",
                    "dev-smoke",
                    "--task-kind",
                    "session",
                    "--task-id",
                    "fixture",
                    "-w",
                    str(root),
                    "--format",
                    "json",
                ],
                text=True,
            )
            assert json.loads(result)["status"] == "prepared"
            asyncio.run(conversation(root, worktree))
    finally:
        module.unlink(missing_ok=True)
        shutil.rmtree(metadata, ignore_errors=True)


if __name__ == "__main__":
    main()
