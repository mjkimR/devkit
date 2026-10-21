"""Adapter selection from explicit workspace configuration and installed factories."""

from __future__ import annotations

import os
from importlib import metadata
from pathlib import Path

from devkit.core.local_config import read_effective_config
from devkit.shared.api import SharedArtifactAdapter
from devkit.shared.errors import AdapterError
from devkit.shared.local import LocalAdapter, discover

GROUP = "devkit.shared.adapters"


def adapter(workspace: Path) -> SharedArtifactAdapter:
    configured = read_effective_config(workspace).values["shared"]["adapter"]
    selected = os.environ.get("DEVKIT_SHARED_ADAPTER", configured)
    context = discover(workspace)
    entries = list(metadata.entry_points(group=GROUP))
    names = [entry.name for entry in entries]
    if "local" in names or len(set(names)) != len(names):
        raise AdapterError("duplicate or reserved adapter registration")
    if selected == "local":
        return LocalAdapter(context)
    matches = [entry for entry in entries if entry.name == selected]
    if len(matches) != 1:
        raise AdapterError("selected adapter is not installed")
    try:
        instance = matches[0].load()(context)
        if (
            not isinstance(instance, SharedArtifactAdapter)
            or instance.adapter_id != selected
            or not isinstance(instance.repository_namespace, str)
            or not instance.repository_namespace
            or any(not callable(getattr(instance, name, None)) for name in ("put", "get", "list", "sweep"))
        ):
            raise TypeError("invalid adapter implementation")
        return instance
    except Exception as exc:
        raise AdapterError(f"adapter factory failed: {type(exc).__name__}") from exc
