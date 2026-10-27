"""Executor context required by transports without depending on live project readers, and the agent-facing form of a
devkit command named in output.

A consumer has devkit through its project environment, so every command an advisory, sentinel or next-step field
suggests is ``uv run devkit ...`` (``ADR-keep-uv-run-as-the-agent-facing-devkit-invocation``).
"""

from pathlib import Path
from typing import Protocol


class InvocationBinding(Protocol):
    workspace: Path
    executor: Path
    common: Path
    identity: tuple[int, int]
    terminal_removal: Path | None

    def environment(self, *, terminal: bool = False) -> str: ...
    def guard(self, *, terminal: bool = False) -> None: ...


AGENT_INVOCATION = "uv run devkit"


def devkit_command(arguments: str) -> str:
    """``arguments`` as the command an agent runs: ``devkit_command("sync")`` is ``uv run devkit sync``."""
    return f"{AGENT_INVOCATION} {arguments}"
