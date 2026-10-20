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
STATUS_SCHEMA = {
    "type": "object",
    "properties": {
        "request_id": {"type": "string"},
        "detail": {
            "type": "boolean",
            "default": False,
            "description": "Include the full retained validation request and diagnostics.",
        },
    },
    "required": ["request_id"],
    "additionalProperties": False,
}

REQUEST_SCHEMA = {
    **STATUS_SCHEMA,
    "properties": {"request_id": {"type": "string"}},
}


def create_tools(root: Path) -> tuple[McpTool, ...]:
    service = IntegrationService(root)

    def task(args: dict) -> Task:
        return Task(
            args["task_kind"], args["task_id"], args.get("unit"), json.dumps(args.get("claims", {}), sort_keys=True)
        )

    async def prepare(args: dict, _confirm: Confirmation) -> dict:
        return (await asyncio.to_thread(service.prepare, args["branch"], task(args))).compact_dict()

    async def integrate(args: dict, confirm: Confirmation) -> dict:
        return (await service.integrate(args["branch"], task(args), confirm)).compact_dict()

    async def resume(args: dict, _confirm: Confirmation) -> dict:
        return (await asyncio.to_thread(service.resume, args["request_id"])).compact_dict()

    async def status(args: dict, _confirm: Confirmation) -> dict:
        result = await asyncio.to_thread(service.inspect, args["request_id"])
        return result.to_dict() if args.get("detail", False) else result.compact_dict()

    return (
        McpTool(
            "integration_prepare",
            "Optional read-only preflight: inspect concise local integration scope and readiness without approval or Git mutations. Not required before integration_integrate, which prepares its own request. Use integration_status(detail=true) for full retained diagnostics.",
            TASK_SCHEMA,
            prepare,
            read_only=True,
        ),
        McpTool(
            "integration_integrate",
            'Prepare, request one host-native user confirmation, then perform local integration (a merge commit, or a fast-forward under [worktree] merge = "ff-only") and cleanup. No prior integration_prepare call or separate conversational approval is required. Returns concise scope and progress. '
            "Invoking this tool does not assert prior integration approval: before confirmation it only validates "
            "and prepares the exact scope, without merging, deleting branches, removing worktrees or running cleanup. "
            "Decline, cancellation or unavailable confirmation causes no integration changes. "
            "Only an explicit affirmative response through the host confirmation UI authorizes execution; "
            "tool-call permission and caller arguments do not grant that authority. "
            "Approval is bound to the prepared source commit, the confirmation target and, within this call only, its "
            "descendants, plus the cleanup scope; later target commits are merged in only when the merge is clean, the "
            "integration policy is unchanged and readiness passes again on the merged result; "
            "otherwise changed scope blocks execution with nothing changed on the target. "
            "After approval, effects may include advancing the base branch, removing the source worktree, "
            "deleting its local branch and running the listed scoped cleanup. "
            "No fetch, push, remote deletion or PR operations. Requires the configured readiness provider.",
            TASK_SCHEMA,
            integrate,
            destructive=True,
        ),
        McpTool(
            "integration_resume",
            "Resume only remaining steps of a request already approved in this server process, without a second confirmation, onto the target its approving call last built on (or the confirmation target); a later target needs a new integration_integrate. Returns concise progress and actionable errors; never supplies new approval or broadens cleanup. Inspect with integration_status before recovery when the outcome is uncertain.",
            REQUEST_SCHEMA,
            resume,
            destructive=True,
        ),
        McpTool(
            "integration_status",
            "Read-only retained progress and observed Git state, concise by default. Set detail=true for the full immutable request, evidence and cleanup revisions. Unknown request IDs require independent Git inspection.",
            STATUS_SCHEMA,
            status,
            read_only=True,
        ),
    )
