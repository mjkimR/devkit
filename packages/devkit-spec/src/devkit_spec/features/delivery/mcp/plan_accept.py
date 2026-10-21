"""MCP tool registration for the proposal plan_accept application workflow."""

from pathlib import Path

from devkit_core.base.mcp import Confirmation, McpTool

from devkit_spec.features.delivery.usecases.native_plan_accept import PlanAcceptUseCase


def create_tools(root: Path) -> tuple[McpTool, ...]:
    service = PlanAcceptUseCase(root)

    async def accept(arguments: dict, confirm: Confirmation) -> dict:
        return await service.execute(
            arguments["slug"], arguments["report_uri"], confirm, mode=arguments.get("mode", "accept_and_handoff")
        )

    return (
        McpTool(
            "spec_plan_accept",
            "Review an exact immutable proposal report; owning plan-accept=auto delegates acceptance and checked Planning merge. Otherwise approve accept_only "
            "or accept_and_handoff in one native form. Automatic handoff additionally requires proposal-handoff=auto. Binds source/base/policy/report/environment and returns "
            "partial effects for fresh approval. Local merge only; no remote publication authority.",
            {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$", "maxLength": 59},
                    "report_uri": {"type": "string"},
                    "mode": {
                        "type": "string",
                        "enum": ["accept_only", "accept_and_handoff"],
                        "default": "accept_and_handoff",
                        "description": "Operation scope; accept_only never starts Development, including under auto policy.",
                    },
                },
                "required": ["slug", "report_uri"],
                "additionalProperties": False,
            },
            accept,
            destructive=True,
            open_world=True,
        ),
    )
