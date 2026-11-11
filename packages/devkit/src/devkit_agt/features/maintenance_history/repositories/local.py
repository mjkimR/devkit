"""Run-directory storage; no writes outside the selected run directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from devkit_core.core.files import atomic_write_bytes

from ..models.errors import InputError
from ..models.records import canonical, run_parts


def write_record(run: Path, record: dict[str, Any]) -> None:
    """Replace ``record.json`` in ``run`` atomically, readable and writable by its owner only."""
    atomic_write_bytes(run / "record.json", canonical(record), mode=0o600)


def read_record(run: Path) -> dict[str, Any]:
    try:
        record = json.loads((run / "record.json").read_bytes())
        if not isinstance(record, dict) or not isinstance(record.get("run_id"), str):
            raise ValueError("record is not a run object")
        run_parts(record["run_id"])
        if run.name != record["run_id"]:
            raise ValueError("run directory and record ID differ")
        return record
    except (OSError, ValueError, TypeError) as exc:
        raise InputError(
            "Cannot read history run record", type(exc).__name__, target_files=[str(run / "record.json")]
        ) from exc
