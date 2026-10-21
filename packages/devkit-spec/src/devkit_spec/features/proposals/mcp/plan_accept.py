"""MCP tool registration for the proposal plan_accept application workflow."""

from pathlib import Path

from devkit_core.base.mcp import Confirmation, McpTool

from devkit_spec.features.proposals.usecases.native_plan_accept import PlanAcceptService


def create_tools(root: Path) -> tuple[McpTool, ...]:
    service = PlanAcceptService(root)

    async def accept(arguments: dict, confirm: Confirmation) -> dict:
        return await service.accept(arguments["slug"], arguments["report_uri"], confirm)

    return (
        McpTool(
            "spec_plan_accept",
            "Review an exact immutable proposal report and explicitly approve accept_only "
            "or accept_and_handoff in one native form. Binds source/base/policy/report/environment and returns "
            "partial effects for fresh approval. Local merge only; no remote publication authority.",
            {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$", "maxLength": 59},
                    "report_uri": {"type": "string"},
                },
                "required": ["slug", "report_uri"],
                "additionalProperties": False,
            },
            accept,
            destructive=True,
            open_world=True,
        ),
    )
