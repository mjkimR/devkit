"""The integration service exposed through host-owned MCP transport and native confirmation."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from devkit.host.mcp import Confirmation, McpTool
from devkit.integration.models import Task
from devkit.integration.service import IntegrationService

TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "branch": {"type": "string"},
        "task_kind": {"type": "string", "enum": ["unit", "session"]},
        "task_id": {"type": "string", "minLength": 1, "maxLength": 256},
        "unit": {"type": "string"},
        "claims": {
            "type": "object",
            "description": "Provider-specific caller declarations; never approval authority. Exclude secrets and transcripts.",
        },
    },
    "required": ["branch", "task_kind", "task_id"],
    "additionalProperties": False,
}
REQUEST_SCHEMA = {
    "type": "object",
    "properties": {"request_id": {"type": "string"}},
    "required": ["request_id"],
    "additionalProperties": False,
}


def create_tools(root: Path) -> tuple[McpTool, ...]:
    service = IntegrationService(root)

    def task(args: dict) -> Task:
        return Task(
            args["task_kind"], args["task_id"], args.get("unit"), json.dumps(args.get("claims", {}), sort_keys=True)
        )

    async def prepare(args: dict, _confirm: Confirmation) -> dict:
        return (await asyncio.to_thread(service.prepare, args["branch"], task(args))).to_dict()

    async def integrate(args: dict, confirm: Confirmation) -> dict:
        return (await service.integrate(args["branch"], task(args), confirm)).to_dict()

    async def resume(args: dict, _confirm: Confirmation) -> dict:
        return (await asyncio.to_thread(service.resume, args["request_id"])).to_dict()

    async def status(args: dict, _confirm: Confirmation) -> dict:
        return (await asyncio.to_thread(service.inspect, args["request_id"])).to_dict()

    return (
        McpTool(
            "integration_prepare",
            "Inspect an exact local FF integration request and provider readiness without approval or Git mutations.",
            TASK_SCHEMA,
            prepare,
            read_only=True,
        ),
        McpTool(
            "integration_integrate",
            "Request host-native user confirmation, then perform the approved local FF integration and cleanup. "
            "Invoking this tool does not assert prior integration approval: before confirmation it only validates "
            "and prepares the exact scope, without merging, deleting branches, removing worktrees or running cleanup. "
            "Decline, cancellation or unavailable confirmation causes no integration changes. "
            "Only an explicit affirmative response through the host confirmation UI authorizes execution; "
            "tool-call permission and caller arguments do not grant that authority. "
            "Approval is bound to the prepared source and target commits and cleanup scope; changed scope blocks execution. "
            "After approval, effects may include advancing the base branch, removing the source worktree, "
            "deleting its local branch and running the listed scoped cleanup. "
            "No fetch, push, remote deletion or PR operations. Requires the configured readiness provider.",
            TASK_SCHEMA,
            integrate,
            destructive=True,
        ),
        McpTool(
            "integration_resume",
            "Inspect and finish the remaining scope of a request already approved in this server process. Never supplies new approval or broadens cleanup.",
            REQUEST_SCHEMA,
            resume,
            destructive=True,
        ),
        McpTool(
            "integration_status",
            "Inspect retained request progress and current Git refs before recovery. Unknown request IDs require independent Git inspection.",
            REQUEST_SCHEMA,
            status,
            read_only=True,
        ),
    )
