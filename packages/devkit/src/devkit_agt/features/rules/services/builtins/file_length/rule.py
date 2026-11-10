from __future__ import annotations

import re
from contextlib import suppress
from dataclasses import dataclass, field

from devkit_core.core import FrontmatterError

from devkit_agt.features.rules.models.contracts import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins.base import BaseRule

DEFAULT_MAX_BYTES = 48 * 1024
_CONSOLIDATED_FEEDBACK_ID = re.compile(
    r"FB-consolidated-[a-z0-9]+(?:-[a-z0-9]+)*-(?:resolved|promoted|dismissed|forwarded)"
)


def _is_consolidated_record(header: dict[str, object] | None) -> bool:
    if header is None:
        return False
    identity, aliases = header.get("id"), header.get("aliases")
    if not isinstance(identity, str) or not identity.strip() or not isinstance(aliases, list):
        return False
    if not all(isinstance(alias, str) and alias.strip() for alias in aliases):
        return False
    count = len(set(aliases))
    return (identity.startswith("ADR-") and count >= 2) or (
        _CONSOLIDATED_FEEDBACK_ID.fullmatch(identity) is not None and count >= 1
    )


@dataclass(frozen=True)
class FileLengthSettings:
    max_bytes: int = DEFAULT_MAX_BYTES
    extensions: list[str] = field(default_factory=lambda: [".md"])
    consolidated_max_bytes: int | None = None


class FileLengthRule(BaseRule):
    def __init__(self, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
        super().__init__(
            id="RULE-file-length",
            name="file-length-check",
            description=f"Warn when a file exceeds byte limits (default {max_bytes} bytes).",
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
            settings=FileLengthSettings(max_bytes=max_bytes),
            guide="guide.md",
        )

    def validate_settings(self, settings: FileLengthSettings) -> None:
        if settings.max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        if settings.consolidated_max_bytes is not None and settings.consolidated_max_bytes <= 0:
            raise ValueError("consolidated_max_bytes must be a positive integer")
        for ext in settings.extensions:
            if len(ext) < 2 or not ext.startswith(".") or any(c in ext for c in "/\\*?[]"):
                raise ValueError(f"extensions must be literal dot-prefixed extensions, got {ext!r}")

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        files = ctx.cache.find_files(ctx.workspace_root, extensions=None)
        for p in files:
            rel = ctx.cache.relative_name(p)
            if not ctx.is_file_targeted(rel):
                continue
            settings: FileLengthSettings = ctx.settings(self, rel)
            if p.suffix not in settings.extensions:
                continue

            size = len(ctx.cache.read_bytes(p))
            limit = settings.max_bytes
            consolidated = False
            if size > limit and settings.consolidated_max_bytes is not None and p.suffix == ".md":
                # Header validation belongs to document rules; preserve the ordinary finding on invalid headers.
                with suppress(FrontmatterError):
                    consolidated = _is_consolidated_record(ctx.cache.get_frontmatter(p))
                if consolidated:
                    limit = max(limit, settings.consolidated_max_bytes)
            if size > limit:
                remediation = (
                    "Review the consolidation group by topic while preserving every retained decision or outcome"
                    if consolidated
                    else "Consider modularizing or splitting the document into smaller sections"
                )
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=1,
                        message=f"File exceeds byte budget ({size} > {limit} bytes)",
                        remediation=remediation,
                        fixable=False,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )

        return violations
