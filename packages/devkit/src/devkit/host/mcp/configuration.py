"""Inspectable manual Codex MCP setup; never writes user settings or trust state."""

import json
import shlex
import sys
from pathlib import Path


def configuration(root: Path) -> dict:
    command = str(Path(sys.executable).absolute())
    args = ["-m", "devkit", "host", "mcp", "serve", "--workspace-root", str(root.resolve())]
    return {
        "host": "codex",
        "server": "devkit",
        "transport": "stdio",
        "command": command,
        "args": args,
        "add_command": shlex.join(["codex", "mcp", "add", "devkit", "--", command, *args]),
        "inspect_command": "codex mcp get devkit --json",
        "remove_command": "codex mcp remove devkit",
        "toml": "[mcp_servers.devkit]\ncommand = " + json.dumps(command) + "\nargs = " + json.dumps(args) + "\n",
        "trust": "host-managed",
        "execution_permissions": "host-managed",
    }
