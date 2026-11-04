"""Run-directory storage; no writes outside the selected run directory."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from ..models.errors import InputError
from ..models.records import canonical, run_parts


def write_record(run: Path, record: dict[str, Any]) -> None:
    with tempfile.NamedTemporaryFile(dir=run, prefix=".record-", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(canonical(record))
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, run / "record.json")
    finally:
        temporary.unlink(missing_ok=True)


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
