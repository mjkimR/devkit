from __future__ import annotations

from agent_rule_engine.engine.models import Phase, RuleContext, Severity, Violation
from agent_rule_engine.rules.base import BaseRule


class DocumentReferenceRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-document-reference",
            name="document-id-reference-check",
            description="Validates document ID uniqueness and verifies that all referenced document IDs exist in the catalog.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        catalog = ctx.cache.get_catalog(ctx.workspace_root)

        # 1. Check duplicate IDs
        for doc_id, paths in catalog.duplicate_ids.items():
            for p in paths:
                if ctx.is_file_targeted(p):
                    violations.append(
                        Violation(
                            rule_id=self.id,
                            file=p,
                            line=1,
                            message=f"Duplicate document ID '{doc_id}' detected across multiple files: {', '.join(paths)}",
                            remediation="Ensure every document ID is globally unique across the repository",
                            fixable=False,
                            severity=self.severity,
                            phase=self.phase,
                        )
                    )

        # 2. Check referenced IDs exist
        for rel_path, doc in catalog.documents_by_path.items():
            if not ctx.is_file_targeted(rel_path):
                continue

            for ref_id in doc.references:
                # Ignore self-references
                if ref_id == doc.id:
                    continue
                if not catalog.has_id(ref_id):
                    violations.append(
                        Violation(
                            rule_id=self.id,
                            file=rel_path,
                            line=1,
                            message=f"Referenced document ID '{ref_id}' does not exist in the repository catalog",
                            remediation=f"Ensure target document '{ref_id}' exists or update reference",
                            fixable=False,
                            severity=self.severity,
                            phase=self.phase,
                        )
                    )

        return violations
