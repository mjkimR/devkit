"""Read-only installation and observation status, separate from host trust and execution permissions."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError

from devkit_dist.features.host.models.errors import HookConflictError, HookDispatchError, HookMissingError
from devkit_dist.features.host.services.configuration import adapter_for, parse_config
from devkit_dist.features.host.services.observation import last_observation, safe_path
from devkit_dist.features.host.usecases.runner import load_definition, load_handler
from devkit_dist.features.project.repositories.receipt import load_receipt


@dataclass
class HostStatus:
    host: str
    hooks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "hooks": self.hooks,
            "ok": not self.errors,
            "runtime_on_path": shutil.which("devkit") is not None,
            "trust": "unknown",
            "execution_permissions": "unknown",
            "errors": [error.to_dict() for error in self.errors],
            "notices": [],
        }


def inspect_host(root: Path, host: str = "codex", *, check_handlers: bool = True) -> HostStatus:
    adapter = adapter_for(host)
    report = HostStatus(host)
    safe_path(root, ".devkit/installation.json")
    receipt = load_receipt(root)
    if receipt is None:
        return report
    records = [record for record in receipt.host_hooks if record.host == host]
    if not records:
        return report
    path = safe_path(root, adapter.config_path)
    config = parse_config(path.read_bytes() if path.exists() else None, adapter.config_path)
    for record in records:
        item: dict[str, Any] = {"asset": record.asset, "event": record.event, "state": "ok", "last_received": None}
        try:
            count = config.get("hooks", {}).get(record.event, []).count(adapter.group(record))
            if count != 1:
                error = HookMissingError if not path.exists() else HookConflictError
                raise error("hook registration is missing, edited or duplicated", target_files=[adapter.config_path])
            hook = load_definition(root, receipt, record.asset)
            if hook.host != host or adapter.record(record.asset, hook) != record:
                raise HookDispatchError("hook definition and receipt registration differ; run devkit sync")
            if check_handlers:
                load_handler(hook.handler)
            item["last_received"] = last_observation(root, host, record.asset)
        except AdvisoryError as exc:
            item["state"] = "invalid"
            report.errors.append(exc)
        except OSError as exc:
            item["state"] = "invalid"
            report.errors.append(HookDispatchError(f"cannot inspect hook files ({type(exc).__name__})"))
        report.hooks.append(item)
    return report
