"""MCP adapter for source-bound proposal report publication; no approval authority."""

from __future__ import annotations

import asyncio
from pathlib import Path

from devkit_core.base.mcp import Confirmation, McpTool

from devkit_spec.features.proposals.usecases.report import (
    PublishWorkspaceProposalReportUseCase,
)

_SOURCE = {
    "slug": {"type": "string"},
    "source_sha": {"type": "string"},
}


def create_tools(root: Path) -> tuple[McpTool, ...]:
    async def report(arguments: dict, _confirm: Confirmation) -> dict:
        artifact = await asyncio.to_thread(
            PublishWorkspaceProposalReportUseCase().execute,
            root,
            arguments["slug"],
            arguments["source_sha"],
            arguments["body"],
        )
        return artifact.receipt_dict()

    return (
        McpTool(
            "spec_proposal_report",
            "Publish a complete source-bound proposal review briefing in the workspace language. The body must"
            " complete the template from the CLI command `devkit spec proposal report <slug>"
            " --source-sha <sha> --template): its frontmatter identity, localized sections, every PADR with its"
            " decision fields and every Planning envelope and effort. Returns exact immutable URI and metadata"
            " without echoing Markdown. Does not approve lifecycle effects.",
            {
                "type": "object",
                "properties": {**_SOURCE, "body": {"type": "string"}},
                "required": ["slug", "source_sha", "body"],
                "additionalProperties": False,
            },
            report,
            execution="bounded_write",
        ),
    )
