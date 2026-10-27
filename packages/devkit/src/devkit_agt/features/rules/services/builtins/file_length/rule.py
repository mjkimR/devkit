from __future__ import annotations

from dataclasses import dataclass, field

from devkit_agt.features.rules.models.contracts import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins.base import BaseRule

DEFAULT_MAX_LINES = 400


@dataclass(frozen=True)
class FileLengthSettings:
    max_lines: int = DEFAULT_MAX_LINES
    extensions: list[str] = field(default_factory=lambda: [".md"])


class FileLengthRule(BaseRule):
    def __init__(self, max_lines: int = DEFAULT_MAX_LINES) -> None:
        super().__init__(
            id="RULE-file-length",
            name="file-length-check",
            description=f"Warn when a file exceeds line limits (default {max_lines} lines).",
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
            settings=FileLengthSettings(max_lines=max_lines),
            guide="guide.md",
        )

    def validate_settings(self, settings: FileLengthSettings) -> None:
        if settings.max_lines <= 0:
            raise ValueError("max_lines must be a positive integer")
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

            text = ctx.cache.read_text(p)
            lines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
            if lines > settings.max_lines:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=settings.max_lines + 1,
                        message=f"File exceeds line length limit ({lines} > {settings.max_lines} lines)",
                        remediation="Consider modularizing or splitting the document into smaller sections",
                        fixable=False,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )

        return violations
