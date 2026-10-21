"""Native tool adapter for proposal report publication; no approval authority."""

from __future__ import annotations

import asyncio
from pathlib import Path

from devkit_core.base.mcp import Confirmation, McpTool

from devkit_spec.features.proposals.usecases.report import publish_workspace_report


def create_tools(root: Path) -> tuple[McpTool, ...]:
    async def report(arguments: dict, _confirm: Confirmation) -> dict:
        return await asyncio.to_thread(
            publish_workspace_report, root, arguments["slug"], arguments["source_sha"], arguments["body"]
        )

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
