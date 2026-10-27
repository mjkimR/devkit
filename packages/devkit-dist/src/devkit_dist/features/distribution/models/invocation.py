"""The agent-facing form of a devkit command named in a ``[FIX]`` or ``[DETAIL]`` line.

A consumer has devkit through its project environment, so every suggested command is ``uv run devkit ...``
(``ADR-keep-uv-run-as-the-agent-facing-devkit-invocation``).
"""

AGENT_INVOCATION = "uv run devkit"


def devkit_command(arguments: str) -> str:
    """``arguments`` as the command an agent runs: ``devkit_command("sync")`` is ``uv run devkit sync``."""
    return f"{AGENT_INVOCATION} {arguments}"
