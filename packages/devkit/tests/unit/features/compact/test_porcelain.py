"""``devkit_agt.features.compact.status_records``: ``git status --porcelain=v1 -z`` records."""

from __future__ import annotations

from devkit_agt.features.compact import status_records


def test_renames_and_copies_skip_their_source_field() -> None:
    raw = b"R  new.txt\0old.txt\0 M edited.txt\0C  copy.txt\0orig.txt\0RM moved.txt\0was.txt\0?? fresh.txt\0"
    assert list(status_records(raw)) == [
        (b"R ", b"new.txt"),
        (b" M", b"edited.txt"),
        (b"C ", b"copy.txt"),
        (b"RM", b"moved.txt"),
        (b"??", b"fresh.txt"),
    ]


def test_empty_output_has_no_records() -> None:
    assert list(status_records(b"")) == []
