"""Bounded, derived read-notice delivery memos under the existing project lock."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Sequence
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.core import atomic_write_bytes, file_lock

from devkit_agt.features.rules.models.errors import ReadSessionExpiredNotice, ReadSessionUnavailableNotice

MAX_AGE = 24 * 60 * 60
MAX_FINGERPRINTS = 2048


def suppress(
    root: Path, token: str, fingerprints: Sequence[str], *, now: float | None = None
) -> tuple[set[str], AdvisoryError | None]:
    """Return duplicate fingerprints; failure never hides a consideration."""
    now = time.time() if now is None else now
    try:
        directory = root / ".devkit/transient/rules/read-notices"
        cursor = root
        for component in directory.relative_to(root).parts:
            cursor = cursor / component
            if cursor.is_symlink():
                raise ValueError("memo directory is a symlink")
        directory.mkdir(parents=True, exist_ok=True)
        key = hashlib.sha256(token.encode()).hexdigest()
        path = directory / (key + ".json")
        if path.is_symlink():
            raise ValueError("memo is a symlink")
        with file_lock(root / ".devkit/transient/lock", timeout=0):
            if path.exists():
                if path.stat().st_size > 300000:
                    raise ValueError("memo exceeds bounded state")
                data = json.loads(path.read_text())
                created, entries = data["created"], data["fingerprints"]
                if (
                    not isinstance(created, (float, int))
                    or not isinstance(entries, list)
                    or len(entries) > MAX_FINGERPRINTS
                ):
                    raise ValueError("invalid memo")
                if any(
                    not isinstance(e, str) or len(e) != 64 or any(c not in "0123456789abcdef" for c in e)
                    for e in entries
                ):
                    raise ValueError("invalid fingerprints")
            else:
                created, entries = now, []
            if created > now or now - created >= MAX_AGE or len(entries) >= MAX_FINGERPRINTS:
                return set(), ReadSessionExpiredNotice("read session expired; use a fresh token for suppression")
            existing = set(entries)
            incoming = set(fingerprints)
            if len(existing | incoming) > MAX_FINGERPRINTS:
                return set(), ReadSessionExpiredNotice("read session fingerprint bound reached; use a fresh token")
            duplicates = existing & incoming
            payload = {"created": created, "fingerprints": sorted(existing | incoming)}
            atomic_write_bytes(path, json.dumps(payload, separators=(",", ":")).encode())
            return duplicates, None
    except (OSError, ValueError, KeyError, TypeError, AdvisoryError):
        return set(), ReadSessionUnavailableNotice("read session memo unavailable; all considerations are returned")


def source_fingerprint(path: Path | None, identity: str) -> str:
    try:
        content = path.read_bytes() if path is not None else identity.encode()
    except OSError:
        content = identity.encode()
    return hashlib.sha256(content).hexdigest()
