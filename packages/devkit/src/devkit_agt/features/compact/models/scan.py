"""Immutable command output scan results."""

from __future__ import annotations

from dataclasses import dataclass, field

from devkit.advisory import Level


@dataclass(frozen=True)
class ToolWarning:
    """A warning a tool printed: its message and the first location it named (``""`` when none)."""

    message: str
    location: str = ""


@dataclass(frozen=True)
class Failure:
    """A test the output names as failed: its node ID, ``failed`` or ``error`` (setup, teardown or
    collection), and the message printed with it (``""`` when none)."""

    test: str
    kind: str
    message: str = ""


@dataclass(frozen=True)
class RelayedAdvisory:
    """An advisory block a nested ``devkit`` command printed, as it was printed."""

    level: Level
    text: str


@dataclass(frozen=True)
class Omitted:
    """What did not fit a budget: items per kind, characters of the excerpt."""

    summaries: int = 0
    failures: int = 0
    warnings: int = 0
    advisories: int = 0
    output: int = 0

    def __bool__(self) -> bool:
        return any((self.summaries, self.failures, self.warnings, self.advisories, self.output))


@dataclass(frozen=True)
class Scan:
    """The bounded view of one command's output.

    ``output`` is the excerpt: the output without the relayed advisory blocks,
    its head and its tail with a marker line where characters were left out,
    filtered lines removed.
    """

    summaries: tuple[str, ...] = ()
    failures: tuple[Failure, ...] = ()  # failed tests no line of the excerpt names
    warnings: tuple[ToolWarning, ...] = ()
    advisories: tuple[RelayedAdvisory, ...] = ()
    output: str = ""
    omitted: Omitted = field(default_factory=Omitted)
    filtered: int = 0  # lines filtered out of the excerpt, overwritten progress states included
    last_lines: tuple[str, ...] = ()  # the excerpt's last non-blank lines, within LAST_LINES and LAST_BUDGET
    read: int = 0  # characters read, the whole output
