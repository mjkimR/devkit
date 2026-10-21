"""Native tool adapter for proposal report publication; no approval authority."""

from __future__ import annotations

import asyncio
from pathlib import Path

from devkit.core import run_git
from devkit.core.mcp import Confirmation, McpTool
from devkit.core.mcp_context import guard_execution
from devkit.worktree import find, locate

from devkit_spec.proposal_report import publish


def create_tools(root: Path) -> tuple[McpTool, ...]:
    async def report(arguments: dict, _confirm: Confirmation) -> dict:
        guard_execution()

        def produce() -> dict:
            guard_execution()
            position = locate(root)
            selected = root
            if not position.linked and run_git(root, "rev-parse", "HEAD").decode().strip() != arguments["source_sha"]:
                selected = find(position, f"plan-{arguments['slug']}")
            return publish(selected, arguments["slug"], arguments["source_sha"], arguments["body"]).to_dict()

        return await asyncio.to_thread(produce)

    return (
        McpTool(
            "spec_proposal_report",
            "Publish a complete source-bound proposal review briefing in the workspace language. Returns exact immutable URI, metadata and Markdown. Does not approve lifecycle effects.",
            {
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "source_sha": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["slug", "source_sha", "body"],
                "additionalProperties": False,
            },
            report,
            execution="bounded_write",
        ),
    )
