"""Discover installed tool services without importing domain services from the host layer."""

from __future__ import annotations

import contextlib
import os
import re
from importlib import metadata
from pathlib import Path
from typing import get_args, get_type_hints

from devkit_core.base.mcp import McpTool
from devkit_core.core.extensions import ExtensionFailed, call_extensions
from devkit_dist.features.host.models.errors import HostMcpError

SERVICE_GROUP = "devkit.host.services"
NAME = re.compile(r"[a-zA-Z0-9_-]{1,64}\Z")
# The execution classes ``McpTool.execution`` declares.
EXECUTIONS = frozenset(get_args(get_type_hints(McpTool)["execution"]))


def load_tools(root: Path) -> dict[str, McpTool]:
    """Every tool the ``devkit.host.services`` entry points declare for ``root``, by name.

    Raises ``HostMcpError`` naming the first service that cannot be listed, loaded or called (``SystemExit``
    included), or that declares something other than a tuple of ``McpTool`` with valid, unique names; a failure to
    list the group names ``discovery``. A service's standard output is discarded.
    """
    tools: dict[str, McpTool] = {}

    def call(entry: metadata.EntryPoint) -> None:
        with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
            declared = entry.load()(root)
        if not isinstance(declared, tuple) or not all(isinstance(tool, McpTool) for tool in declared):
            raise TypeError("service must return a tuple of McpTool")
        for tool in declared:
            if not NAME.fullmatch(tool.name) or tool.name in tools or tool.execution not in EXECUTIONS:
                raise TypeError("invalid or duplicate tool name")
            tools[tool.name] = tool

    for outcome in call_extensions(SERVICE_GROUP, call, fail_fast=True):
        if isinstance(outcome, ExtensionFailed):
            error = outcome.error
            raise HostMcpError(f"MCP service {outcome.name} cannot load ({type(error).__name__})") from error
    return tools
