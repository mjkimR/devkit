"""Records of ``git status --porcelain=v1 -z``."""

from __future__ import annotations

from collections.abc import Iterator


def status_records(raw: bytes) -> Iterator[tuple[bytes, bytes]]:
    """Each ``XY <path>`` record of ``raw`` as ``(XY, path)``.

    A rename or copy (``R`` or ``C`` in either column) is followed by one more field, its source path, which is
    not a record of its own and is skipped. Fields too short to be a record (the trailing empty one) are skipped.
    """
    fields = iter(raw.split(b"\0"))
    for entry in fields:
        status = entry[:2]
        if b"R" in status or b"C" in status:
            next(fields, None)
        if len(entry) > 3:
            yield status, entry[3:]
