"""Host-neutral hook definitions and service handler contracts."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit.host.errors import HookDefinitionError

NAME = re.compile(r"[a-z][a-z0-9-]*\Z")


@dataclass(frozen=True)
class HookDefinition:
    host: str
    event: str
    handler: str
    matcher: str = ""
    timeout: int = 10


@dataclass(frozen=True)
class HookEvent:
    """The host's input; handlers must not persist prompts, tool inputs or transcripts."""

    host: str
    name: str
    root: Path
    asset: str
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class HookResponse:
    """Optional context from an advisory service; grants no execution authority."""

    additional_context: str | None = None


def parse_hook(raw: bytes, target: str) -> HookDefinition:
    """Read one declarative TOML hook. Host capabilities are validated by its adapter."""
    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise HookDefinitionError("hook source must be UTF-8 TOML", target_files=[target]) from exc
    required = {"host", "event", "handler"}
    if required - data.keys() or data.keys() - required - {"matcher", "timeout"}:
        raise HookDefinitionError(
            "hook fields: host, event, handler, optional matcher and timeout", target_files=[target]
        )
    if any(not isinstance(data[key], str) or not data[key] for key in required):
        raise HookDefinitionError("host, event and handler must be nonempty strings", target_files=[target])
    if not NAME.fullmatch(data["host"]) or not NAME.fullmatch(data["handler"]):
        raise HookDefinitionError("host and handler must be lowercase slugs", target_files=[target])
    matcher, timeout = data.get("matcher", ""), data.get("timeout", 10)
    if not isinstance(matcher, str) or type(timeout) is not int or not 1 <= timeout <= 600:
        raise HookDefinitionError(
            "matcher must be a string; timeout must be an integer from 1 to 600", target_files=[target]
        )
    return HookDefinition(data["host"], data["event"], data["handler"], matcher, timeout)
