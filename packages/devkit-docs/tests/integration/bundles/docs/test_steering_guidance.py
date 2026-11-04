"""Namespace steering directories in the ``docs`` bundle guidance: the constitution item, the writing instruction and
the steering rule guide name ``docs/packages/<name>/steering/`` beside ``docs/steering/``."""

from __future__ import annotations

from pathlib import Path

from distsupport.guidance import assert_rule

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_docs/bundles/docs/bundle"


def _items(markdown: str) -> list[str]:
    return markdown.split("\n- ")


def test_the_constitution_item_names_both_directories_and_the_for_request() -> None:
    items = [item for item in _items((BUNDLE / "AGENTS.md").read_text()) if "`docs/steering/`" in item]
    assert len(items) == 1, items
    assert_rule(items[0], "`docs/packages/<name>/steering/`", "registered namespace", "working directory")
    assert_rule(items[0], "`documents_elsewhere`", "other packages", "steering directories")
    assert_rule(items[0], "`documents_elsewhere`", "`uv run devkit get-context docs --for <dir>`")


def test_living_spec_writing_sends_package_background_to_the_namespace_directory() -> None:
    body = (BUNDLE / "instructions/living-spec-writing.md").read_text()
    section = body[body.index("## Steering documents") : body.index("## Glossary")]
    assert_rule(section, "package background", "`docs/packages/<name>/steering/`", "registered namespace")
    assert_rule(section, "`docs/packages/<name>/steering/glossary.md`", "`docs/packages/<name>/steering/glossary.yaml`")
    glossary = body[body.index("## Glossary") :]
    assert_rule(glossary, "read together with the root glossary", "package redefinition", "package's documents only")
    assert_rule(glossary, "`docs/packages/<name>/glossary.md`", "move", "merge", "English `summary`")
    assert_rule(glossary, "never copy the global glossary")


def test_the_steering_rule_guide_names_both_directories_and_the_glossary_findings() -> None:
    guide = (BUNDLE / "rules/steering_documents/guide.md").read_text()
    assert_rule(guide, "`docs/steering/`", "`docs/packages/<name>/steering/`", "one directory at a time")
    assert_rule(guide, "optional `glossary.md`", "`glossary.yaml`", "`ux-objects.md`")
    assert_rule(guide, "legacy `docs/packages/<name>/glossary.md`", "manual move/merge")
    assert "unregistered" in guide
    reference = (BUNDLE / "rules/document_reference/guide.md").read_text()
    assert_rule(reference, "Steering files", "`docs/steering/`", "`docs/packages/<name>/steering/`")


def test_ux_objects_are_optional_local_rows_read_with_global_rows() -> None:
    guide = (BUNDLE / "instructions/ux-writing.md").read_text()
    assert_rule(guide, "namespace UX", "root register together with", "`docs/packages/<name>/steering/ux-objects.md`")
    assert_rule(guide, "namespace-specific object rows", "namespace register", "shared object rows", "root register")
    assert_rule(guide, "only when local rows are needed", "never copy")
    assert_rule(guide, "link and coverage rules do not parse", "object registers")


def test_seed_ux_creates_only_registers_with_needed_rows() -> None:
    guide = (BUNDLE / "seed/docs/ux/README.md").read_text()
    assert_rule(guide, "`docs/steering/ux-objects.md`", "created only when shared rows are needed")
    assert_rule(guide, "existing root", "`docs/packages/<name>/steering/ux-objects.md`", "only for needed local rows")
