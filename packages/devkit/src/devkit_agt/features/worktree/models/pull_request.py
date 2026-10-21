"""Bound GitHub repository identity."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Repository:
    remote: str
    fetch_url: str
    push_url: str
    host: str
    name: str
    delete_on_merge: bool

    def public_scope(self) -> dict[str, Any]:
        return {"remote": self.remote, "repository": self.selector, "delete_on_merge": self.delete_on_merge}

    @property
    def selector(self) -> str:
        return f"{self.host}/{self.name}"
