"""Dependency-free MCP service contracts. The SDK remains an optional transport dependency."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal

Invocation = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class McpTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    invoke: Invocation
    execution: Literal["read_only", "preflight", "interactive", "approved_resume", "bounded_write"] = "interactive"
    read_only: bool = False
    destructive: bool = False
    open_world: bool = False
