"""The immutable source-bound handoff disclosure."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HandoffPreview:
    root: Path
    slug: str
    head: str
    base_branch: str
    worktree: str
    setup: str | None
    policy: str
    title: str
    summary: str
    plan: str
    effort: str
    report_uri: str = ""
    existing: bool = False

    def message(self, language: str = "en") -> str:
        from devkit_spec.features.proposals.models.approval import message

        return message(self, language)
