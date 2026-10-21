"""MCP tool registration for the proposal handoff application workflow."""

from pathlib import Path

from devkit_core.base.mcp import Confirmation, McpTool

from devkit_spec.features.proposals.usecases.native_handoff import HandoffService


def create_tools(root: Path) -> tuple[McpTool, ...]:
    from devkit_spec.features.proposals.mcp import plan_accept as plan_accept_mcp
    from devkit_spec.features.proposals.mcp import report as proposal_report_mcp

    service = HandoffService(root)

    async def handoff(arguments: dict, confirm: Confirmation) -> dict:
        return await service.handoff(arguments["slug"], arguments["report_uri"], confirm)

    return (
        McpTool(
            "spec_handoff",
            "Review an accepted proposal summary and exact live report URI in one native form, select activity effort defaulted from dev_effort, then explicitly approve starting local Development. Creates dev-<slug> and its worktree and runs proposal handoff only after approval. Decline, cancellation or unavailable confirmation makes no changes. Changed base or policy requires fresh review. Returns selected effort as run input; the caller continues in the returned worktree and records effort in its worker envelope. Does not approve or execute final merge.",
            {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$", "maxLength": 59},
                    "report_uri": {"type": "string", "minLength": 1},
                },
                "required": ["slug", "report_uri"],
                "additionalProperties": False,
            },
            handoff,
            destructive=True,
            open_world=True,
        ),
        *proposal_report_mcp.create_tools(root),
        *plan_accept_mcp.create_tools(root),
    )
