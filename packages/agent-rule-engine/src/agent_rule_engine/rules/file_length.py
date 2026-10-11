from __future__ import annotations

from agent_rule_engine.models import Phase, RuleContext, Severity, Violation
from agent_rule_engine.rules.base import BaseRule

DEFAULT_MAX_LINES = 400


class FileLengthRule(BaseRule):
    def __init__(self, max_lines: int = DEFAULT_MAX_LINES) -> None:
        super().__init__(
            id="RULE-file-length",
            name="file-length-check",
            description=f"Warn when a file exceeds line limits (default {max_lines} lines).",
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
        )
        self.max_lines = max_lines

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        max_lines = ctx.options.get("max_lines", self.max_lines)

        all_md = ctx.cache.find_files(ctx.workspace_root, extensions=(".md",))
        for p in all_md:
            rel = p.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue

            text = ctx.cache.read_text(p)
            lines = text.count("\n") + 1
            if lines > max_lines:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=max_lines + 1,
                        message=f"File exceeds line length limit ({lines} > {max_lines} lines)",
                        remediation="Consider modularizing or splitting the document into smaller sections",
                        fixable=False,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )

        return violations
