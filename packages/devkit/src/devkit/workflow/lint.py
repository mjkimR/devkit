"""The ``lint-clean`` binding to ``devkit.rules``."""

from __future__ import annotations

from pathlib import Path


def rules_lint(root: Path, files: list[str]) -> list[str]:
    """Run the project's rules (linter phase) over ``files`` and describe each error-severity violation.

    ``run_project_rules`` applies the project's whole ``[rules]`` policy
    (including ``exclude``), exactly as ``devkit rules check`` does. Rule
    loading or execution errors raise ``RuntimeError``.
    """
    from devkit.rules import run_project_rules

    if not files:
        return []
    run = run_project_rules(root, targets=files)
    if run.errors:
        raise RuntimeError("; ".join(run.errors))
    return [
        f"{v.file}:{v.line} {v.rule_id} {v.message}"
        for v in run.result.violations
        if v.severity.value == "error" and not v.fixed
    ]
