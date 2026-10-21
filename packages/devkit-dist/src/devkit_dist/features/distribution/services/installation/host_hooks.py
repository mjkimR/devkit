"""Shared host hook configuration participates in the existing sync transaction."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from devkit_dist.features.distribution.models.content import Content
from devkit_dist.features.distribution.models.results import Action
from devkit_dist.features.distribution.services.installation.workspace import snapshot
from devkit_dist.features.host import adapter_for, plan_config
from devkit_dist.features.project.repositories.receipt import HostHookRecord


def plan_host_hooks(
    root: Path,
    previous: Sequence[HostHookRecord],
    desired: Sequence[HostHookRecord],
    changes: dict[str, Content | None],
    actions: list[Action],
) -> None:
    for host in sorted({record.host for record in (*previous, *desired)}):
        adapter = adapter_for(host)
        current = snapshot(root, adapter.config_path)
        raw = current.data if current else None
        updated = plan_config(
            host,
            raw,
            [record for record in previous if record.host == host],
            [record for record in desired if record.host == host],
        )
        if updated != raw:
            assert updated is not None
            changes[adapter.config_path] = Content(updated, current.mode if current else 0o644)
            actions.append(Action(adapter.config_path, "update" if current else "create"))
