"""Formal documentation checkpoints in the docs and spec bundles (SPEC-formal-doc-authoring-checkpoints AC-01, AC-07,
AC-08): fact-type routing, capability exclusions, datasheet condition, reference pages, the reconcile record index and
the reviewer's reimplementability classes."""

from __future__ import annotations

import re
from pathlib import Path

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text

CAPABILITY = Path(__file__).resolve().parents[6] / "docs/capabilities/documents/CAP-DOCS-documentation-ownership.md"


def _fact_rows(markdown: str) -> list[str]:
    """The fact-type table rows, whitespace-normalized, from the table whose header starts with ``Fact type``."""
    lines = [line.strip() for line in markdown.splitlines()]
    start = next(i for i, line in enumerate(lines) if line.startswith("| Fact type |"))
    rows: list[str] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        rows.append(" ".join(line.split()))
    return rows


def test_one_routing_table_of_fifteen_fact_types_matches_the_capability() -> None:
    """SPEC-formal-doc-padding-trim AC-03: the fact-type and responsibility tables are one table of 15 rows."""
    guide = raw("instructions/living-spec-writing.md")
    capability = CAPABILITY.read_text()
    rows = _fact_rows(guide)
    assert len(rows) == 15
    assert rows[0].startswith(
        "| Behavior, validity, safety, limit, output order or tie-break a consumer can observe | Capability |"
    )
    assert any(row.startswith("| How an ID, key, hash, token or name is derived | Design;") for row in rows)
    assert any(row.startswith("| Actor goal, scenario and success contract | Use case |") for row in rows)
    assert _fact_rows(capability) == rows  # the canonical copy in this repository's Living Spec
    for document in (guide, capability):
        assert document.count("| Fact type | Owner |") == 1
        assert "| Responsibility / reader question |" not in document


def test_capability_design_and_reference_guidance() -> None:
    capability = raw("instructions/capability-writing.md")
    assert "\n## What Stays Out\n" in capability
    assert_rule(capability, "pseudocode", "design")
    assert "Observable contract only" in raw("templates/capability.md")
    for path in ("instructions/design-writing.md", "templates/design.md"):
        assert_rule(raw(path), "later run, another process or another tool reads back", "datasheet")
    writing = raw("instructions/document-writing.md")
    assert "\n## Reference Pages\n" in writing
    assert_rule(writing, "`Code | Level | Condition | Fix`", "observable trigger")
    template = raw("templates/reference.md")
    assert not template.startswith("---") and "| Code | Level | Condition | Fix |" in template


def test_the_reconcile_record_indexes_the_formal_assessment() -> None:
    sync = raw("skills/spec-sync/SKILL.md")
    assert "related_designs: [DESIGN-<slug>]" in sync and 'domain: "none: <bounded source-based reason>"' in sync
    assert_rule(text("skills/spec-sync/SKILL.md"), "`formal_docs.<role>", "never both", "body keeps")


def test_the_reconcile_reviewer_names_four_reimplementability_classes() -> None:
    reviewer = raw("subagents/reconcile-reviewer.md")
    assert_rule(reviewer, "`diff_scope` adds or changes", "never for gaps older")
    classes = re.findall(r"^\s+- (P[123]): (.+)$", reviewer, flags=re.MULTILINE)
    assert [severity for severity, _ in classes] == ["P1", "P2", "P2", "P3"]
    assert "contradicts" in classes[0][1] and "persisted format" in classes[1][1]
    assert "trigger condition" in classes[2][1] and "restates mechanism" in classes[3][1]


def test_plan_and_review_route_new_formats_derivations_orderings_and_codes() -> None:
    for path in ("skills/spec-plan/SKILL.md", "skills/spec-review/SKILL.md"):
        assert_rule(raw(path), "persisted format", "identity derivation", "ordering", "code", "fact-type table")
