"""Adaptive-dev guidance links large builds to the consuming project's documents."""

from __future__ import annotations

from pathlib import Path

from distsupport.guidance import assert_rule

PACKAGE = Path(__file__).parents[3]
BUNDLE = PACKAGE / "src/devkit_adaptive/bundles/adaptive_dev/bundle"
SKILL = BUNDLE / "skills/adaptive-dev"
DOCUMENTS = SKILL / "references/documents.md"


def test_skill_routes_to_the_documents_reference_with_a_read_condition() -> None:
    text = (SKILL / "SKILL.md").read_text()
    assert DOCUMENTS.is_file()
    assert_rule(
        text,
        "`references/documents.md`",
        "before",
        "partitioning",
        "shared interface",
        "integrating a retained result",
        "writing a project document",
    )
    assert_rule(text, "write only documents", "next decision", "retained behavior")


def test_documents_reference_uses_the_project_document_system_when_one_exists() -> None:
    text = DOCUMENTS.read_text()
    assert_rule(text, "existing document destinations", "`uv run devkit get-context docs`", "`uv run devkit docs")
    assert_rule(text, "no document yet", "current context", "seed no document tree", "first document")


def test_documents_reference_binds_assignments_and_shared_interfaces_to_documents() -> None:
    text = DOCUMENTS.read_text()
    assert_rule(text, "before partitioning", "multi-writer", "govern the goal", "architecture", "decisions")
    assert_rule(text, "governing documents", "by ID", "absolute path", "`none`")
    assert_rule(text, "assignee", "constraints", "conflict", "Host", "instead of resolving it silently")
    assert_rule(text, "shared interface outlives its assignment", "current-state document", "interface identity")
    assert_rule(text, "short-lived", "keep it in the assignment")


def test_documents_reference_keeps_current_state_documents_with_retained_results() -> None:
    text = DOCUMENTS.read_text()
    assert_rule(text, "integrates a retained result", "capability or use case", "architecture", "decision")
    assert_rule(text, "current state", "not iteration history", "discarded experiment")
    assert_rule(text, "delegate document writing", "after the code", "integrated", "one owner per document")
    assert_rule(text, "unimplemented behavior", "defect")
    assert_rule(text, "document checks", "combined checks", "unverified")


def test_documents_reference_maps_retained_items_without_per_change_records() -> None:
    text = DOCUMENTS.read_text()
    assert_rule(text, "`.devkit/adaptive-dev.md`", "retained behavior, structure or choice", "`undocumented`")
    assert_rule(text, "link the document", "never copy")
    assert_rule(text, "no per-change record", "SDD Unit", "approval", "envelope")


def test_delegation_orchestration_and_context_name_project_documents() -> None:
    assert_rule(
        (SKILL / "references/delegation.md").read_text(),
        "supply one goal",
        "governing documents",
        "ID or absolute path",
        "`none`",
    )
    assert_rule(
        (SKILL / "references/orchestration.md").read_text(),
        "consuming project's",
        "document checks",
        "representative usage checks",
    )
    assert_rule(
        (SKILL / "references/current-context.md").read_text(),
        "map",
        "retained behavior, structure or choice",
        "document ID",
        "`undocumented`",
    )
    template = (BUNDLE / "templates/current-context.md").read_text()
    assert "\n## Documents\n" in template
    assert_rule(template, "retained behavior, structure or choice", "document ID", "`undocumented`", "never copy")


def test_architect_and_builder_overlays_hold_to_governing_documents() -> None:
    architect = (SKILL / "roles/architect.md").read_text()
    assert_rule(architect, "governing documents", "report a partition that conflicts")
    assert_rule(architect, "deliverables", "blocking dependencies", "shared interface ownership")
    builder = (SKILL / "roles/builder.md").read_text()
    assert_rule(builder, "governing documents", "report a mismatch", "instead of diverging")
    assert_rule(builder, "agreed interface and failure handling")


def test_assignment_guidance_records_verifies_and_resumes_without_install_condition():
    delegation = (SKILL / "references/delegation.md").read_text()
    assert_rule(
        delegation,
        "assignment new",
        "--governing",
        "assignment return",
        "assignment verify",
        "result=fail",
        "assignment close",
        "cannot record",
        "unrecorded",
    )
    assert_rule(
        (SKILL / "references/current-context.md").read_text(),
        "assignment list",
        "open",
        "interrupted",
        "assignment show",
        "ledger",
    )
    orchestration = (SKILL / "references/orchestration.md").read_text()
    assert "without assuming a harness is installed" not in orchestration
    assert_rule(orchestration, "uv run devkit worktree", "documented Git procedure")
    assert_rule(orchestration, "--parent", "closes all children", "records nothing")
    assert_rule(DOCUMENTS.read_text(), "first document", "seed no document tree")
    assert_rule(DOCUMENTS.read_text(), "uv run devkit rules check", "unverified")
    assert_rule(DOCUMENTS.read_text(), "--governing", "recording")
    for name in ("product-clarifier", "product-researcher", "usage-reviewer"):
        assert "devkit adaptive assignment" not in (BUNDLE / f"subagents/{name}.md").read_text()
