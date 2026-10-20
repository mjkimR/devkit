"""Verify a retained runtime without installing packages or searching arbitrary interpreters."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from devkit.core.git import run_git
from devkit.core.local_config import read_effective_config
from devkit.host.registrations import LaunchDescriptor, RuntimeUnavailable, common_dir

# A probe only imports the transport and inspects service module specs; no service factory or host is launched.
PROBE = """
import importlib.util, importlib.metadata, json, sys
import devkit_mcp.server
entries = list(importlib.metadata.entry_points(group="devkit.host.services"))
modules = ["devkit_mcp", "devkit.core", "devkit.advisory"] + [e.value.split(":")[0] for e in entries]
paths = []
for name in modules:
    spec = importlib.util.find_spec(name)
    if spec is None: raise RuntimeError("missing service module")
    paths += ([spec.origin] if spec.origin else list(spec.submodule_search_locations or []))
# Include all imported runtime dependency modules, including editable SDK/schema dependencies.
paths += [m.__file__ for m in tuple(sys.modules.values()) if getattr(m, "__file__", None)]
print(json.dumps({"prefix": sys.prefix, "paths": paths,
    "services": sorted((e.name, e.value, e.dist.name, e.dist.version) for e in entries),
    "version": importlib.metadata.version("devkit-mcp")}))
"""


def _linked_source(path: Path) -> bool:
    return any((parent / ".git").is_file() for parent in (path, *path.parents))


def descriptor(root: Path, *, executable: str | None = None, environment: str | None = None) -> LaunchDescriptor | None:
    root = root.resolve()
    common = common_dir(root)
    if common is None:
        raise RuntimeUnavailable("a retained runtime requires a Git checkout")
    output = run_git(root, "worktree", "list", "--porcelain", "-z").decode()
    worktrees = [Path(part[9:]).resolve() for part in output.split("\0") if part.startswith("worktree ")]
    if not worktrees:
        raise RuntimeUnavailable("the retained base checkout is unavailable")
    executor = worktrees[0]
    if common_dir(executor) != common:
        raise RuntimeUnavailable("retained executor is not from the owning clone")
    tasks = worktrees[1:]
    candidates = (
        [Path(executable).absolute()]
        if executable
        else [Path(sys.executable).absolute(), executor / ".venv/bin/python"]
    )
    required = sorted(
        (e.name, e.value, (e.dist.name if e.dist else ""), (e.dist.version if e.dist else ""))
        for e in metadata.entry_points(group="devkit.host.services")
    )
    selected = None
    for candidate in dict.fromkeys(candidates):
        if (
            not candidate.is_file()
            or _linked_source(candidate)
            or any(candidate.is_relative_to(task) for task in tasks)
        ):
            continue
        try:
            proc = subprocess.run(
                [str(candidate), "-c", PROBE],
                cwd=executor,
                capture_output=True,
                text=True,
                timeout=15,
                env={k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}},
            )
            data = json.loads(proc.stdout) if proc.returncode == 0 else {}
            if (
                data.get("version") != metadata.version("devkit-mcp")
                or [tuple(row) for row in data.get("services", [])] != required
            ):
                continue
            paths = [Path(data["prefix"]).absolute(), *(Path(path).absolute() for path in data["paths"])]
            if any(_linked_source(path) for path in paths):
                continue
            if any(
                path.is_relative_to(task) or path.resolve().is_relative_to(task) for path in paths for task in tasks
            ):
                continue
            selected = candidate
            break
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
            continue
    if selected is None:
        raise RuntimeUnavailable(
            "no verified retained interpreter/import installation with the same services is available"
        )
    profile = (
        "read-only"
        if (environment or read_effective_config(root).values["execution"]["environment"]) == "cloud"
        else "local"
    )
    if profile == "read-only":
        from devkit_mcp.services import load_tools

        if not any(tool.execution == "read_only" for tool in load_tools(executor).values()):
            return None
    args = (
        "-m",
        "devkit",
        "mcp",
        "serve",
        "--workspace-root",
        str(executor),
        "--configuration-workspace",
        str(root),
        "--profile",
        profile,
    )
    return LaunchDescriptor(str(selected), args, str(executor), str(root), profile)
