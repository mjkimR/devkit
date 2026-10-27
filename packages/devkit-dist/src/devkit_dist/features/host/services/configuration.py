"""Pure shared-file planning: own exact matcher groups, preserve all foreign entries."""

from __future__ import annotations

import copy
import json
from collections.abc import Sequence
from typing import Any

from devkit_dist.features.host.models.errors import HookConflictError, HookDefinitionError, HostConfigError
from devkit_dist.features.host.models.hooks import SUPPORTED_HOSTS, HookDefinition, parse_hook
from devkit_dist.features.host.repositories.adapters.codex import CodexAdapter
from devkit_dist.features.project.repositories.receipt import HostHookRecord


def adapter_for(host: str) -> CodexAdapter:
    if host not in SUPPORTED_HOSTS:
        raise HookDefinitionError(f"unsupported host: {host}; supported: codex")
    return CodexAdapter()


def read_hook(raw: bytes, target: str) -> HookDefinition:
    hook = parse_hook(raw, target)
    try:
        adapter_for(hook.host).validate(hook, target)
    except HookDefinitionError as exc:
        if not exc.target_files:
            exc.target_files = (target,)
        raise
    return hook


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key")
        out[key] = value
    return out


def parse_config(raw: bytes | None, target: str) -> dict[str, Any]:
    try:
        data = json.loads(raw, object_pairs_hook=_unique, parse_constant=_invalid_constant) if raw is not None else {}
        if not isinstance(data, dict):
            raise ValueError("expected an object")
        hooks = data.get("hooks", {})
        if not isinstance(hooks, dict) or any(
            not isinstance(groups, list) or any(not isinstance(group, dict) for group in groups)
            for groups in hooks.values()
        ):
            raise ValueError("hooks must map event names to arrays of matcher groups")
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise HostConfigError(
            "host hook configuration must be an unambiguous JSON object", target_files=[target]
        ) from exc
    return data


def _invalid_constant(value: str) -> Any:
    raise ValueError("non-JSON constant")


def plan_config(
    host: str, raw: bytes | None, previous: Sequence[HostHookRecord], desired: Sequence[HostHookRecord]
) -> bytes | None:
    """Replace recorded groups atomically with sync's other writes; absent whole files can be restored.

    A missing/edited/duplicated owned group in an existing file is a conflict. We cannot identify a group after
    its command was edited, so never silently re-add it beside the edited command. Unowned identical groups
    are conflicts too: adopting them would authorize their later removal.
    """
    adapter = adapter_for(host)
    data = parse_config(raw, adapter.config_path)
    updated = copy.deepcopy(data)
    hooks = updated.setdefault("hooks", {})
    if raw is not None:
        for record in previous:
            groups = hooks.get(record.event, [])
            expected = adapter.group(record)
            if groups.count(expected) != 1:
                raise HookConflictError(
                    "a recorded hook group is missing, edited or duplicated", target_files=[adapter.config_path]
                )
            groups.remove(expected)
            if not groups:
                hooks.pop(record.event, None)
    for record in desired:
        groups = hooks.setdefault(record.event, [])
        group = adapter.group(record)
        if group in groups:
            raise HookConflictError(
                "an identical hook group exists without receipt ownership", target_files=[adapter.config_path]
            )
        groups.append(group)
    if updated == data or (raw is None and not desired):
        return raw
    return (json.dumps(updated, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
