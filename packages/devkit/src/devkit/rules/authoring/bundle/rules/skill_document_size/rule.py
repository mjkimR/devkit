"""``RULE-skill-document-size``: warn when a skill or playbook Markdown file outgrows its byte budget.

Shipped by the ``authoring`` bundle (preset ``skill-authoring``) and loaded by
``devkit rules`` from the synchronized copy. Files the installation receipt
owns (agent projections of bundle skills) are skipped: they are fixed in the
bundle source, not in the project.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from devkit.core import load_receipt
from devkit.rules.engine.models import Phase, RuleContext, Severity, Violation
from devkit.rules.engine.settings import match_path, validate_pattern
from devkit.rules.rules.base import BaseRule

# Project-native skills, and skill and playbook sources of bundles (in-repository bundles included).
DEFAULT_PATHS = (".agents/skills/**", ".claude/skills/**", "**/bundle/skills/**", "**/bundle/playbooks/**")

REMEDIATION = (
    "Restructure the document without hiding required constraints: compress repeated explanation;"
    " move conditional content to references/ and state when each file is read; keep SKILL.md a thin router."
    ' Follow the skill-authoring playbook (`uv run devkit playbook search "restructure a large skill"`).'
    " For a justified exception, raise max_bytes for this exact path in"
    " [[rules.settings.RULE-skill-document-size.overrides]] with a comment giving the reason"
)


@dataclass(frozen=True)
class SkillDocumentSizeSettings:
    max_bytes: int = 8192
    extensions: list[str] = field(default_factory=lambda: [".md"])
    paths: list[str] = field(default_factory=lambda: list(DEFAULT_PATHS))


class SkillDocumentSizeRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-skill-document-size",
            name="skill-document-size-check",
            description="Warn when a skill or playbook Markdown file exceeds its byte budget.",
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
            settings=SkillDocumentSizeSettings(),
            guide="guide.md",
            related=("authoring:skill-authoring",),
        )

    def validate_settings(self, settings: SkillDocumentSizeSettings) -> None:
        if settings.max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        for ext in settings.extensions:
            if len(ext) < 2 or not ext.startswith(".") or any(c in ext for c in "/\\*?[]"):
                raise ValueError(f"extensions must be literal dot-prefixed extensions, got {ext!r}")
        for pattern in settings.paths:
            validate_pattern(pattern)

    def check(self, ctx: RuleContext) -> list[Violation]:
        receipt = load_receipt(ctx.workspace_root)
        owned = set(receipt.file_records) if receipt is not None else set()
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=None):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if path.is_symlink() or rel in owned or not ctx.is_file_targeted(rel):
                continue
            settings: SkillDocumentSizeSettings = ctx.settings(self, rel)
            if path.suffix not in settings.extensions or not any(match_path(p, rel) for p in settings.paths):
                continue
            size = len(ctx.cache.read_bytes(path))
            if size > settings.max_bytes:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=1,
                        message=f"File has {size} bytes; effective max_bytes is {settings.max_bytes}",
                        remediation=REMEDIATION,
                        fixable=False,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )
        return violations
