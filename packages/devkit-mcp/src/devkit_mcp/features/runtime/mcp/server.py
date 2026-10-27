"""FastMCP stdio transport. Tool approval never substitutes for scoped confirmation.

The server records the installed devkit source when it starts and refuses every call
other than ``read_only`` with ``MCP_RUNTIME_STALE`` once a loaded devkit module no
longer matches it.
"""

from __future__ import annotations

import json
from contextlib import nullcontext
from importlib.metadata import version
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.base.mcp import McpTool
from devkit_dist.features.host.models.errors import HostMcpError, HostMcpInputError
from devkit_dist.features.project.models.invocation import InvocationBinding
from devkit_dist.features.project.usecases.invocation import execution_binding, guard_execution, invocation
from fastmcp import FastMCP
from fastmcp.tools import Tool, ToolResult
from jsonschema import Draft202012Validator
from mcp_types import TextContent, ToolAnnotations
from pydantic import PrivateAttr

from devkit_mcp.features.runtime.usecases.discovery import load_tools
from devkit_mcp.features.runtime.usecases.loaded_code import GuardLoadedCodeUseCase, RecordLoadedCodeUseCase


class _DevkitTool(Tool):
    _service: McpTool = PrivateAttr()
    _binding: InvocationBinding | None = PrivateAttr()
    _profile: str = PrivateAttr()
    _loaded_code: GuardLoadedCodeUseCase = PrivateAttr()

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        result: dict[str, Any]

        try:
            if (self._profile == "read-only" and self._service.execution != "read_only") or not Draft202012Validator(
                self._service.input_schema
            ).is_valid(arguments):
                raise HostMcpInputError("unknown tool or invalid arguments; inspect the tool's input schema")
            if self._service.execution == "read_only":
                with invocation(self._binding) if self._binding is not None else nullcontext():
                    result = await self._service.invoke(arguments)
            else:
                self._loaded_code.execute()
                with invocation(self._binding) if self._binding is not None else nullcontext():
                    guard_execution()
                    result = await self._service.invoke(arguments)
            if not isinstance(result, dict):
                raise HostMcpError("service returned a non-object result")
        except AdvisoryError as exc:
            result = {"error": exc.to_dict()}
        except Exception as exc:
            result = {"error": HostMcpError(f"service execution failed ({type(exc).__name__})").to_dict()}

        return ToolResult(
            content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False))],
            structured_content=result,
            is_error=bool(result.get("error") or result.get("errors")),
        )


def build_server(
    tools: dict[str, McpTool], binding: InvocationBinding | None = None, *, profile: str = "local"
) -> FastMCP:
    mcp = FastMCP("devkit", version=version("devkit-mcp"))
    loaded_code = GuardLoadedCodeUseCase(RecordLoadedCodeUseCase().execute())

    for service in tools.values():
        if profile == "read-only" and service.execution != "read_only":
            continue
        tool = _DevkitTool(
            name=service.name,
            description=service.description,
            parameters=service.input_schema,
            annotations=ToolAnnotations(
                read_only_hint=service.read_only,
                destructive_hint=service.destructive,
                open_world_hint=service.open_world,
            ),
        )
        tool._service = service
        tool._binding = binding
        tool._profile = profile
        tool._loaded_code = loaded_code
        mcp.add_tool(tool)

    return mcp


def serve(root: Path, configuration_workspace: Path, *, profile: str = "local") -> None:
    """Run a local stdio server; stdout belongs exclusively to the MCP protocol."""
    server = build_server(load_tools(root), execution_binding(configuration_workspace, root), profile=profile)
    server.run(transport="stdio", show_banner=False)
