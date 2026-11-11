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
    # ``read_only`` runs unguarded and advertises the read-only hint; every other tool is a guarded write.
    execution: Literal["read_only", "bounded_write"] = "bounded_write"
    destructive: bool = False
    open_world: bool = False
