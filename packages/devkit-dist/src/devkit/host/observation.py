"""Metadata-only observer used to verify the installed hook path."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from devkit.core.files import atomic_write_bytes
from devkit.core.paths import normalize_relpath
from devkit.host.errors import HookDispatchError
from devkit.host.hooks import HookEvent, HookResponse


def safe_path(root: Path, relative: str) -> Path:
    """Host configuration and observation state never follow symlinked components."""
    path = root
    for part in normalize_relpath(relative, canonical=True).parts:
        path /= part
        if path.is_symlink():
            raise HookDispatchError("host path contains a symlink", target_files=[relative])
    if path.exists() and not path.is_file():
        raise HookDispatchError("host path is not a regular file", target_files=[relative])
    return path


def observation_path(root: Path, host: str, asset: str) -> Path:
    bundle, name = asset.split(":")
    return safe_path(root, f".devkit/transient/host/{host}/{bundle}/{name}.json")


def observe(event: HookEvent) -> HookResponse:
    """Record only which hook ran and when; no session IDs, cwd, prompts, arguments or transcripts."""
    data = {"host": event.host, "asset": event.asset, "event": event.name, "received_at": datetime.now(UTC).isoformat()}
    atomic_write_bytes(observation_path(event.root, event.host, event.asset), json.dumps(data).encode(), mode=0o600)
    return HookResponse()


def last_observation(root: Path, host: str, asset: str) -> dict[str, str] | None:
    path = observation_path(root, host, asset)
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_bytes())
        if (
            not isinstance(value, dict)
            or set(value) != {"host", "asset", "event", "received_at"}
            or value["host"] != host
            or value["asset"] != asset
            or not isinstance(value["received_at"], str)
            or not isinstance(value["event"], str)
        ):
            raise ValueError("invalid observation")
        datetime.fromisoformat(value["received_at"])
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise HookDispatchError("invalid hook observation metadata", target_files=[str(path)]) from exc
    return value
