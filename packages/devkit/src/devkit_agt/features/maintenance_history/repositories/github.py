"""Bounded gh API transport with response status and header preservation, on the worktree feature's hardened
``run_gh``."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Protocol

from devkit_agt.features.worktree.repositories.gh import http_response
from devkit_agt.features.worktree.repositories.gh import run_gh as gh

from ..models.errors import GhUnavailable, TransportFailure
from ..models.records import canonical

AUTH_TIMEOUT = 15.0  # seconds for the `gh auth status` that classifies a response-less failure


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict[str, str]
    body: Any


class Runner(Protocol):
    def __call__(self, method: str, endpoint: str, payload: dict[str, Any] | None, timeout: float) -> Response: ...


def run_gh(method: str, endpoint: str, payload: dict[str, Any] | None, timeout: float) -> Response:
    """One ``gh api`` request; ``GhUnavailable`` when gh is missing or logged out, ``subprocess.TimeoutExpired`` when
    it does not answer within ``timeout``, ``TransportFailure`` when authenticated gh printed no HTTP response."""
    args = ["api", "--include", "--method", method, "-H", "Accept: application/vnd.github+json", endpoint]
    if payload is not None:
        args += ["--input", "-"]
    completed = gh(None, args, timeout=timeout, input=canonical(payload) if payload is not None else None)
    if completed.returncode == 127:
        raise GhUnavailable("gh is unavailable")
    if completed.returncode is None:
        raise subprocess.TimeoutExpired(["gh", *args], timeout)
    response = http_response(completed.stdout)
    if response is not None:
        body = os.fsencode(response.body)
        try:
            content = json.loads(body) if body.strip() else None
        except ValueError:
            content = body.decode("utf-8", "replace")
        return Response(response.status, response.headers, content)
    authenticated = gh(None, ["auth", "status"], timeout=AUTH_TIMEOUT)
    if authenticated.returncode is None:
        raise TransportFailure("Cannot verify gh authentication during a transport failure")
    if authenticated.returncode:
        raise GhUnavailable("gh is not authenticated", f"gh exit={completed.returncode}")
    raise TransportFailure("Authenticated gh returned no HTTP response")
