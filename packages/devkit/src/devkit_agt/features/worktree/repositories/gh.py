"""The one hardened ``gh`` runner and the parser of its ``--include`` HTTP output. Authentication stays with gh.

``run_gh`` never prompts, pages or colors, and never inherits a caller's repository selection: ``GH_REPO`` and Git's
repository variables are dropped and Git's global and system configuration are hidden, so an identity is always the
one the arguments name. ``http_response`` reads what ``gh api --include`` printed.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    """``gh``'s exit code (``127`` when gh is missing, ``None`` on timeout) and its decoded output."""

    returncode: int | None
    stdout: str = ""
    stderr: str = ""
    http_status: int | None = None


class Runner(Protocol):
    def __call__(self, cwd: Path, args: list[str]) -> CommandResult: ...


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: str


def run_gh(cwd: Path | None, args: list[str], *, timeout: float, input: bytes | None = None) -> CommandResult:
    """Run ``gh <args>`` in ``cwd`` (the process directory for ``None``) within ``timeout`` seconds.

    ``input`` is written to gh's standard input, which is ``/dev/null`` otherwise. The output is decoded with
    ``os.fsdecode``, so ``os.fsencode`` gives the bytes back.
    """
    env = {**os.environ, "GH_PROMPT_DISABLED": "1", "NO_COLOR": "1", "GH_PAGER": "cat"}
    # Repository discovery cannot inherit a caller's unrelated override.
    env.pop("GH_REPO", None)
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    try:
        result = subprocess.run(
            ["gh", *args],
            cwd=cwd,
            env=env,
            input=input,
            stdin=subprocess.DEVNULL if input is None else None,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return CommandResult(127)
    except subprocess.TimeoutExpired:
        return CommandResult(None)
    return CommandResult(result.returncode, os.fsdecode(result.stdout), os.fsdecode(result.stderr))


def http_response(output: str) -> HttpResponse | None:
    """The status, lower-cased headers and body of ``gh api --include`` output; ``None`` without an HTTP block.

    gh can print intermediate HTTP blocks: the last block owns the body.
    """
    raw = output.replace("\r\n", "\n")
    while raw.startswith("HTTP/"):
        header, separator, body = raw.partition("\n\n")
        if not separator:
            break
        lines = os.fsencode(header).decode("utf-8", "replace").splitlines()  # headers are text, never paths
        parts = lines[0].split()
        if len(parts) < 2 or not parts[1].isdigit():
            break
        if body.startswith("HTTP/"):
            raw = body
            continue
        headers = {
            key.lower(): value.strip() for line in lines[1:] if ":" in line for key, value in [line.split(":", 1)]
        }
        return HttpResponse(int(parts[1]), headers, body)
    return None
