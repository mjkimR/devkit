"""Bounded gh API transport with response status and header preservation."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any, Protocol

from ..models.errors import GhUnavailable, TransportFailure
from ..models.records import canonical


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict[str, str]
    body: Any


class Runner(Protocol):
    def __call__(self, method: str, endpoint: str, payload: dict[str, Any] | None, timeout: float) -> Response: ...


def run_gh(method: str, endpoint: str, payload: dict[str, Any] | None, timeout: float) -> Response:
    args = ["gh", "api", "--include", "--method", method, "-H", "Accept: application/vnd.github+json", endpoint]
    if payload is not None:
        args += ["--input", "-"]
    try:
        completed = subprocess.run(
            args,
            input=canonical(payload) if payload is not None else None,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GhUnavailable("gh is unavailable") from exc
    raw = completed.stdout.replace(b"\r\n", b"\n")
    # gh --include can print intermediate HTTP blocks; the last block owns the body.
    while raw.startswith(b"HTTP/"):
        header, separator, body = raw.partition(b"\n\n")
        if not separator:
            break
        lines = header.decode("utf-8", "replace").splitlines()
        status = int(lines[0].split()[1])
        headers = {
            key.lower(): value.strip() for line in lines[1:] if ":" in line for key, value in [line.split(":", 1)]
        }
        if body.startswith(b"HTTP/"):
            raw = body
            continue
        try:
            content = json.loads(body) if body.strip() else None
        except ValueError:
            content = body.decode("utf-8", "replace")
        return Response(status, headers, content)
    try:
        authenticated = subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=15, check=False)
    except subprocess.TimeoutExpired as exc:
        raise TransportFailure("Cannot verify gh authentication during a transport failure") from exc
    if authenticated.returncode:
        raise GhUnavailable("gh is not authenticated", f"gh exit={completed.returncode}")
    raise TransportFailure("Authenticated gh returned no HTTP response")
