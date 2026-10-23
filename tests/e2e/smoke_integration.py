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

from devkit_agt.features.worktree import locate, start
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROVIDER = """
from pathlib import Path
from devkit_core.core.git import run_git
from devkit_agt.features.integration import Evidence, Readiness

def check(context):
    plan = context.finish
    value = run_git(Path(plan.base), "show", f"{plan.source_sha}:ready.txt").strip()
    return Readiness(plan.source_sha, plan.target_sha, (Evidence("SMOKE_CHECK_PASSED", plan.source_sha),),
                     () if value == b"ready" else ("smoke fixture is not ready",),
                     result_sha=context.result_sha, disclosure="smoke fixture check only")
"""


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


async def conversation(root: Path, worktree: Path, prepared_digest: str) -> None:
    args = ["-m", "devkit_dist", "mcp", "serve", "--workspace-root", str(root), "--configuration-workspace", str(root)]
    params = StdioServerParameters(command=sys.executable, args=args)
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write, read_timeout_seconds=timedelta(seconds=30)) as session,
    ):
        await session.initialize()
        tools = await session.list_tools()
        names = {tool.name for tool in tools.tools}
        assert not names.intersection(
            {"integration_prepare", "integration_integrate", "integration_status", "integration_resume"}
        )
        assert {"shared_put", "shared_get"} <= names
        tip = git(worktree, "rev-parse", "HEAD")
        before = git(root, "rev-parse", "HEAD")
        assert worktree.exists() and before == git(root, "rev-parse", "HEAD")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "devkit_dist",
                "integration",
                "integrate",
                "dev-smoke",
                "--task-kind",
                "session",
                "--task-id",
                "installed-fixture",
                "--expected-digest",
                prepared_digest,
                "--workspace-root",
                str(root),
                "--format",
                "json",
            ],
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        integrated = json.loads(result.stdout)
        assert integrated["status"] == "completed", integrated
        assert integrated["authority"] == "host-conversation"
        assert not worktree.exists() and git(root, "rev-parse", "HEAD^1", "HEAD^2").split() == [before, tip]


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
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "devkit_dist",
                    "integration",
                    "prepare",
                    "dev-smoke",
                    "--task-kind",
                    "session",
                    "--task-id",
                    "installed-fixture",
                    "-w",
                    str(root),
                    "--format",
                    "json",
                ],
                text=True,
                capture_output=True,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            prepared = json.loads(result.stdout)
            assert prepared["status"] == "prepared"
            asyncio.run(conversation(root, worktree, prepared["request"]["digest"]))
    finally:
        module.unlink(missing_ok=True)
        shutil.rmtree(metadata, ignore_errors=True)


if __name__ == "__main__":
    main()
