"""Project worktree policy values and their duration grammar."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta

PERIOD = re.compile(r"([1-9][0-9]{0,3})([dw])")


@dataclass(frozen=True)
class WorktreeConfig:
    pull_request: str = "auto"
    delete_branch: bool = True
    setup: str | None = None
    stale_after: str = "14d"
    merge: str = "no-ff"


def parse_period(text: str) -> timedelta:
    """``<N>d`` or ``<N>w`` (``N`` from 1 to 9999) as a ``timedelta``; ``ValueError`` otherwise."""
    match = PERIOD.fullmatch(text)
    if match is None:
        raise ValueError(f"{text!r} is not <N>d or <N>w")
    days = int(match.group(1)) * (7 if match.group(2) == "w" else 1)
    return timedelta(days=days)
