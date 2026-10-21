"""Read-only filesystem assertion helpers."""

import builtins
import io
import os

import pytest


def guard_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    original_open = os.open
    original_io = io.open
    original_builtin = builtins.open

    def fail(*args: object, **kwargs: object):
        pytest.fail(f"query attempted filesystem mutation: {args}")

    def os_read(path, flags, *args, **kwargs):
        if os.fspath(path) == os.devnull:
            return original_open(path, flags, *args, **kwargs)
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        return original_open(path, flags, *args, **kwargs)

    def checked_open(original):
        def read(path, mode="r", *args, **kwargs):
            assert not any(flag in mode for flag in "wax+")
            return original(path, mode, *args, **kwargs)

        return read

    monkeypatch.setattr(os, "open", os_read)
    monkeypatch.setattr(io, "open", checked_open(original_io))
    monkeypatch.setattr(builtins, "open", checked_open(original_builtin))
    for name in ("mkdir", "unlink", "remove", "rename", "replace"):
        monkeypatch.setattr(os, name, fail)
