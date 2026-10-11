from __future__ import annotations

from agent_rule_engine.engine.models import Phase, RuleContext, Severity, Violation
from agent_rule_engine.rules.base import BaseRule
from agent_rule_engine.workspace.catalog import is_valid_doc_id

_TARGET_DIRS = ("docs/capabilities", "docs/stories", "docs/proposals", "docs/specs", "specs")


class IdConventionRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-id-convention",
            name="slug-identifier-convention-check",
            description="Enforces standard slug-based identifiers and matching filename stems for specification documents.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        all_md = ctx.cache.find_files(ctx.workspace_root, extensions=(".md",))

        for p in all_md:
            if p.name == "README.md":
                continue
            rel = p.relative_to(ctx.workspace_root).as_posix()
            if not any(rel.startswith(f"{td}/") for td in _TARGET_DIRS):
                continue
            if not ctx.is_file_targeted(rel):
                continue

            fm, _, _ = ctx.cache.get_frontmatter(p)
            if not fm:
                continue

            doc_id = str(fm.get("id") or "").strip()
            if not doc_id:
                continue

            if not is_valid_doc_id(doc_id):
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=1,
                        message=f"Document ID '{doc_id}' does not match standard identifier format (e.g. US-foo-bar, CAP-baz, SPEC-xyz)",
                        remediation="Use an uppercase prefix (CAP, US, ARCH, ADR, PROP, SPEC, etc.) followed by a hyphen and slug",
                        fixable=False,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )

            # Check stem matches ID
            if p.stem != doc_id:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=1,
                        message=f"File stem '{p.stem}' does not match document frontmatter ID '{doc_id}'",
                        remediation=f"Rename file to '{doc_id}.md' or change frontmatter ID to '{p.stem}'",
                        fixable=False,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )

        return violations
