"""Locked append-only JSON Lines with interrupted-fragment recovery."""

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.core import file_lock, run_git_text

from devkit_adaptive.base.errors import LedgerFragmentIgnored, LedgerUnreadable, LedgerUnwritable
from devkit_adaptive.features.assignment.models.values import Event


class Ledger:
    def __init__(self, root: Path):
        self.directory = (
            Path(run_git_text(root, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
            / "devkit/adaptive"
        )
        self.path = self.directory / "ledger.jsonl"

    def read(self) -> tuple[list[Event], list[AdvisoryError], int]:
        try:
            raw = self.path.read_bytes() if self.path.exists() else b""
            end = raw.rfind(b"\n") + 1
            notices: list[AdvisoryError] = (
                [LedgerFragmentIgnored("ignored an unterminated final ledger fragment")] if raw[end:] else []
            )
            events = [json.loads(line) for line in raw[:end].splitlines()]
            known: set[str] = set()
            for event in events:
                if (
                    not isinstance(event, dict)
                    or event.get("schema") != 1
                    or event.get("event") not in {"assigned", "returned", "verified", "closed"}
                    or not isinstance(event.get("data"), dict)
                    or not isinstance(event.get("at"), str)
                    or not isinstance(event.get("id"), str)
                ):
                    raise ValueError("invalid event schema")
                if event["event"] == "assigned":
                    if event["id"] in known or event["data"].get("id") != event["id"]:
                        raise ValueError("invalid assignment event")
                    known.add(event["id"])
                elif event["id"] not in known:
                    raise ValueError("event precedes assignment")
            return events, notices, end
        except (OSError, ValueError, UnicodeError) as exc:
            raise LedgerUnreadable(f"cannot read ledger {self.path}: {exc}") from exc

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            with file_lock(self.directory / "lock", timeout=10):
                yield
        except OSError as exc:
            raise LedgerUnwritable(f"cannot write ledger {self.path}: {exc}") from exc

    def append(self, event: Event, end: int) -> None:
        try:
            with self.path.open("a+b") as output:
                output.truncate(end)
                output.write((json.dumps(event, separators=(",", ":"), ensure_ascii=True) + "\n").encode())
                output.flush()
                os.fsync(output.fileno())
        except OSError as exc:
            raise LedgerUnwritable(f"cannot append ledger {self.path}: {exc}") from exc
