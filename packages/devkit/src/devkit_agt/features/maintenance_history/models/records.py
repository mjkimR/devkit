"""Canonical record encoding and history identities."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from devkit.advisory import AdvisoryError

from .errors import InputError

PLAYBOOKS = ("weekly-report", "drift-reconciliation", "review-refactor", "performance-pass")
RUN_ID = re.compile(r"(weekly-report|drift-reconciliation|review-refactor|performance-pass)-(\d{8}T\d{6}Z)-[0-9a-f]{8}")
IDENTITY = {"name": "devkit maintenance history", "email": "maintenance-history@devkit.invalid"}
ROOT_DATE = "2000-01-01T00:00:00Z"
ROOT_README = b"# devkit maintenance history\n\nHistory marker: devkit-maintenance-history-v1\nRuns: runs/<playbook>/<run-id>/; indexes: index/<playbook>/<year>.jsonl\nNever merge this branch into a code branch.\n"
LOCAL_FIELDS = frozenset(
    {"destination", "authority", "attempts", "publication", "history_commit", "updates", "published_files"}
)


def canonical(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n"
    ).encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_sha(kind: str, data: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(data)}\0".encode() + data).hexdigest()


ROOT_TREE = git_sha("tree", b"100644 README.md\0" + bytes.fromhex(git_sha("blob", ROOT_README)))
_ROOT_PERSON = b"devkit maintenance history <maintenance-history@devkit.invalid> 946684800 +0000"
ROOT_COMMIT = git_sha(
    "commit",
    b"tree "
    + ROOT_TREE.encode()
    + b"\nauthor "
    + _ROOT_PERSON
    + b"\ncommitter "
    + _ROOT_PERSON
    + b"\n\nInitialize devkit maintenance history\n",
)


def run_parts(run_id: str) -> tuple[str, str]:
    match = RUN_ID.fullmatch(run_id)
    if not match:
        raise InputError("Invalid history run ID")
    return match[1], match[2][:4]


def run_path(run_id: str) -> str:
    playbook, _ = run_parts(run_id)
    return f"runs/{playbook}/{run_id}"


def safe_file(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value or any(ord(c) < 32 for c in value):
        raise InputError("Published file must be a safe relative path")
    return str(path)


def published_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in LOCAL_FIELDS}


@dataclass
class HistoryResult:
    kind: str
    data: dict[str, Any]
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.data | {"notices": [notice.to_dict() for notice in self.notices]}
