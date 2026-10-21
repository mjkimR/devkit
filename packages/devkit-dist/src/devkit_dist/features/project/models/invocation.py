"""Executor context required by transports without depending on live project readers."""

from pathlib import Path
from typing import Protocol


class InvocationBinding(Protocol):
    workspace: Path
    executor: Path
    common: Path
    identity: tuple[int, int]
    terminal_removal: Path | None

    def environment(self, *, terminal: bool = False) -> str: ...
    def guard(self, *, terminal: bool = False) -> None: ...
