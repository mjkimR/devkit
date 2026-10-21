"""Resolved response-language preference."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PresentationLanguage:
    requested: str
    resolved: str
    source: str
    fallback: bool

    @property
    def approval_language(self) -> str:
        return "ko" if self.resolved == "ko" else "en"
