"""Discover installed tool services without importing domain services from the host layer."""

from __future__ import annotations

import contextlib
import os
import re
from importlib import metadata
from pathlib import Path

from devkit.core.mcp import McpTool
from devkit.host.errors import HostMcpError

SERVICE_GROUP = "devkit.host.services"
NAME = re.compile(r"[a-zA-Z0-9_-]{1,64}\Z")


def load_tools(root: Path) -> dict[str, McpTool]:
    tools: dict[str, McpTool] = {}
    for entry in sorted(metadata.entry_points(group=SERVICE_GROUP), key=lambda item: (item.name, item.value)):
        try:
            with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
                declared = entry.load()(root)
            if not isinstance(declared, tuple) or not all(isinstance(tool, McpTool) for tool in declared):
                raise TypeError("service must return a tuple of McpTool")
            for tool in declared:
                if (
                    not NAME.fullmatch(tool.name)
                    or tool.name in tools
                    or tool.execution not in {"read_only", "preflight", "interactive", "approved_resume"}
                ):
                    raise TypeError("invalid or duplicate tool name")
                tools[tool.name] = tool
        except Exception as exc:
            raise HostMcpError(f"MCP service {entry.name} cannot load ({type(exc).__name__})") from exc
    return tools
