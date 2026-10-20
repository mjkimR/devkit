"""SDK-backed stdio transport. Tool approval never substitutes for a service's scoped confirmation."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
from contextlib import nullcontext
from importlib.metadata import version
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit.core.mcp import ConfirmationReply, McpTool
from devkit.core.mcp_context import ExecutionBinding, guard_execution, invocation
from devkit.host.errors import HostConfirmationError, HostMcpError, HostMcpInputError
from jsonschema import Draft202012Validator
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from devkit_mcp.services import load_tools


def build_server(
    tools: dict[str, McpTool], binding: ExecutionBinding | None = None, *, profile: str = "local"
) -> Server:
    server = Server("devkit", version=version("devkit-mcp"))

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema,
                annotations=types.ToolAnnotations(
                    readOnlyHint=tool.read_only, destructiveHint=tool.destructive, openWorldHint=tool.open_world
                ),
            )
            for tool in tools.values()
            if profile != "read-only" or tool.execution == "read_only"
        ]

    @server.call_tool(validate_input=False)
    async def call_tool(name: str, arguments: dict) -> types.CallToolResult:
        async def confirm(message: str, schema: dict) -> ConfirmationReply:
            if binding is not None:
                binding.guard()
            guard_execution()
            context = server.request_context
            capability = (
                context.session.client_params.capabilities.elicitation if context.session.client_params else None
            )
            if capability is None or capability.form is None:
                raise HostConfirmationError(
                    "client did not advertise native form elicitation; no authority was granted"
                )
            try:
                result = await context.session.elicit_form(message, schema, related_request_id=context.request_id)
                if binding is not None:
                    binding.guard()
                guard_execution()
                return ConfirmationReply(result.action, result.content or {})
            except AdvisoryError:
                raise
            except Exception as exc:
                raise HostConfirmationError(
                    f"native confirmation failed ({type(exc).__name__}); no authority was granted"
                ) from exc

        try:
            tool = tools.get(name)
            if tool is None or not Draft202012Validator(tool.input_schema).is_valid(arguments):
                raise HostMcpInputError("unknown tool or invalid arguments; inspect the tool's input schema")
            if profile == "read-only" and tool.execution != "read_only":
                raise HostMcpInputError("tool is not available in the read-only profile")
            if tool.execution == "read_only":
                result = await tool.invoke(arguments, confirm)
            else:
                with invocation(binding) if binding is not None else nullcontext():
                    guard_execution()
                    result = await tool.invoke(arguments, confirm)
            if not isinstance(result, dict):
                raise HostMcpError("service returned a non-object result")
        except AdvisoryError as exc:
            result = {"error": exc.to_dict()}
        except Exception as exc:
            result = {"error": HostMcpError(f"service execution failed ({type(exc).__name__})").to_dict()}
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))],
            structuredContent=result,
            isError=bool(result.get("error") or result.get("errors")),
        )

    return server


def serve(root: Path, configuration_workspace: Path, *, profile: str = "local") -> None:
    """Run a local stdio server; stdout belongs exclusively to the MCP SDK."""
    server = build_server(load_tools(root), ExecutionBinding(configuration_workspace, root), profile=profile)

    async def run() -> None:
        async with stdio_server() as (read, write):
            # The SDK captured the real output stream; library prints cannot corrupt the wire.
            with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
                await server.run(read, write, server.create_initialization_options())

    asyncio.run(run())
