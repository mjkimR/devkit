"""The ``lint-clean`` binding to ``devkit_agt.features.rules``."""

from __future__ import annotations

from pathlib import Path


def lint_with_rules(root: Path, files: list[str]) -> list[str]:
    """Run the project's rules (linter phase) over ``files`` and describe each error-severity violation.

    ``run_project_rules`` applies the project's whole ``[rules]`` policy
    (including ``exclude``), exactly as ``devkit rules check`` does. Rule
    loading, policy or execution problems raise ``devkit_agt.features.rules.RulesRunError``
    (``RULES_RUN_FAILED``) carrying them; an invalid ``[rules]`` table or target
    raises the rule engine's own error. ``evaluate_definition`` passes any of them through unchanged
    as ``UnitEvaluation.lint_error``.
    """
    from devkit_agt.features.rules import run_project_rules

    if not files:
        return []
    run = run_project_rules(root, targets=files)
    run.raise_for_problems()
    return [f"{v.file}:{v.line} {v.rule_id} {v.message}" for v in run.blocking_violations]
