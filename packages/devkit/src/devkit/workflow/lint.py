"""The ``lint-clean`` binding to ``devkit.rules``."""

from __future__ import annotations

from pathlib import Path


def rules_lint(root: Path, files: list[str]) -> list[str]:
    """Run the project's rules (linter phase) over ``files`` and describe each error-severity violation.

    ``run_project_rules`` applies the project's whole ``[rules]`` policy
    (including ``exclude``), exactly as ``devkit rules check`` does. Rule
    loading, policy or execution problems raise ``devkit.rules.RulesRunError``
    (``RULES_RUN_FAILED``) carrying them; an invalid ``[rules]`` table or target
    raises the rule engine's own error.
    """
    from devkit.rules import RulesRunError, run_project_rules

    if not files:
        return []
    run = run_project_rules(root, targets=files)
    if run.errors:
        raise RulesRunError(run.errors)
    return [
        f"{v.file}:{v.line} {v.rule_id} {v.message}"
        for v in run.result.violations
        if v.severity.value == "error" and not v.fixed
    ]
