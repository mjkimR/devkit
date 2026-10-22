"""Native tool adapters for proposal report publication and its template; no approval authority."""

from __future__ import annotations

import asyncio
from pathlib import Path

from devkit_core.base.mcp import Confirmation, McpTool

from devkit_spec.features.proposals.usecases.report import (
    PublishWorkspaceProposalReportUseCase,
    ReportTemplateUseCase,
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

    async def template(arguments: dict, _confirm: Confirmation) -> dict:
        text = await asyncio.to_thread(
            ReportTemplateUseCase().execute, root, arguments["slug"], arguments["source_sha"]
        )
        return {"proposal": f"PROP-{arguments['slug']}", "source_sha": arguments["source_sha"], "template": text}

    return (
        McpTool(
            "spec_proposal_report",
            "Publish a complete source-bound proposal review briefing in the workspace language. The body must"
            " complete the template from spec_proposal_report_template (CLI: devkit spec proposal report <slug>"
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
        McpTool(
            "spec_proposal_report_template",
            "Return the proposal review report template for the exact current committed Planning or accepted base"
            " SHA: frontmatter identity, localized mandatory sections, one decision block per PADR and the Planning"
            " envelopes and effort to account for. Complete every section with authored meaning, then publish it"
            " with spec_proposal_report. Read-only; publishes nothing.",
            {
                "type": "object",
                "properties": dict(_SOURCE),
                "required": ["slug", "source_sha"],
                "additionalProperties": False,
            },
            template,
            execution="read_only",
            read_only=True,
        ),
    )
