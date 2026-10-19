"""Receipt-bound dispatch from a native host event to an installed service handler."""

from __future__ import annotations

import contextlib
import os
from collections.abc import Callable
from importlib import metadata
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast

from devkit.core.receipt import Receipt, load_receipt, verified_asset_file
from devkit.host.configuration import adapter_for, parse_config, read_hook
from devkit.host.errors import HookDispatchError
from devkit.host.hooks import HookDefinition, HookEvent, HookResponse
from devkit.host.observation import safe_path

HANDLER_GROUP = "devkit.host.handlers"
Handler = Callable[[HookEvent], HookResponse]


def load_handler(name: str) -> Handler:
    entries = sorted(metadata.entry_points(group=HANDLER_GROUP, name=name), key=lambda item: item.value)
    if len(entries) != 1:
        raise HookDispatchError(f"handler {name} requires exactly one installed {HANDLER_GROUP} entry point")
    try:
        with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
            handler = entries[0].load()
    except Exception as exc:
        # Do not copy exception messages: a handler can include event input or secrets in them.
        raise HookDispatchError(f"handler {name} could not load ({type(exc).__name__})") from exc
    if not callable(handler):
        raise HookDispatchError(f"handler {name} is not callable")
    return cast(Handler, handler)


def load_definition(root: Path, receipt: Receipt, key: str) -> HookDefinition:
    assets = [asset for asset in receipt.assets("hook") if f"{asset.bundle}:{asset.id}" == key]
    if len(assets) != 1 or len(assets[0].paths) != 1:
        raise HookDispatchError("hook must name one selected, single-file hook asset")
    asset = assets[0]
    path = verified_asset_file(root, asset.paths[0], receipt, asset)
    raw = path.read_bytes()
    recorded = receipt.file(asset.paths[0])
    if recorded is not None and not recorded.matches(raw):
        raise HookDispatchError("hook source changed while reading it")
    return read_hook(raw, asset.paths[0])


def dispatch(root: Path, host: str, asset: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the native event and installed registration, then invoke one trusted package handler.

    Host timeouts bound the whole command, including imports and service execution. This advisory hook path
    supplies context only; it does not return permission decisions or perform integration dispatch.
    """
    adapter = adapter_for(host)
    if safe_path(root, ".devkit/transient/sync-journal.json").exists():
        raise HookDispatchError("recover the interrupted sync before running host hooks")
    safe_path(root, ".devkit/installation.json")
    receipt = load_receipt(root)
    if receipt is None:
        raise HookDispatchError("no synchronized project receipt")
    hook = load_definition(root, receipt, asset)
    record = adapter.record(asset, hook)
    if hook.host != host or record not in receipt.host_hooks or host not in receipt.selection.agents:
        raise HookDispatchError("hook definition and receipt registration differ; run devkit sync")
    if payload.get("hook_event_name") != hook.event:
        raise HookDispatchError("native event does not match the installed hook event")
    config_path = safe_path(root, adapter.config_path)
    config = parse_config(config_path.read_bytes() if config_path.exists() else None, adapter.config_path)
    if config.get("hooks", {}).get(record.event, []).count(adapter.group(record)) != 1:
        raise HookDispatchError("installed hook registration is missing, edited or duplicated")
    handler = load_handler(hook.handler)
    event = HookEvent(host, hook.event, root, asset, MappingProxyType(payload))
    try:
        with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
            result = handler(event)
    except Exception as exc:
        raise HookDispatchError(f"handler {hook.handler} failed ({type(exc).__name__})") from exc
    if not isinstance(result, HookResponse):
        raise HookDispatchError(f"handler {hook.handler} must return HookResponse")
    return adapter.response(hook.event, result)
