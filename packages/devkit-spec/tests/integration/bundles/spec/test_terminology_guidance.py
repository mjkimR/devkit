"""The terminology guidance of the ``spec`` bundle: the ``living-spec-writing`` Glossary rules, the seeded glossary
columns and the ``spec-sync`` glossary question (SPEC-terminology-authoring-guidance)."""

from __future__ import annotations

import re

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text

HEADER = "| Term | Definition | Owner | Avoid | Code identifiers |"


def _glossary_section() -> str:
    return raw("instructions/living-spec-writing.md").split("\n## Glossary\n", 1)[1]


def test_the_glossary_section_carries_six_rules_and_the_code_boundary() -> None:
    description = re.search(r"^description: (.+)$", raw("instructions/living-spec-writing.md"), re.MULTILINE)
    assert description is not None and "terminology and the glossary" in description.group(1)
    section = _glossary_section()
    assert_rule(section, "package redefinition", "that package's documents only")
    assert re.findall(r"^(\d)\. ", section, re.MULTILINE) == [str(n) for n in range(1, 7)]
    assert_rule(section, "does not authorize renaming", "code", "APIs", "schemas")


def test_the_glossary_section_names_the_project_list_the_synonyms_and_the_fallback() -> None:
    section = _glossary_section()
    assert_rule(section, "project additions and exceptions", "`docs/steering/glossary.md`")
    assert_rule(section, "`docs/steering/glossary.yaml`", "Avoid entry", "synonym", "cluster")
    assert_rule(section, "glossary without the `Owner`, `Avoid` and `Code identifiers` columns")


def test_the_seeded_glossary_has_five_columns_and_no_rename_mandate() -> None:
    assert HEADER in raw("seed/docs/steering/glossary.md").splitlines()
    glossary = text("seed/docs/steering/glossary.md")
    assert "## Avoided Generic Nouns" in glossary and "`living-spec-writing` instruction" in glossary
    assert "Authoring Guidelines" not in glossary and "Code symbols (classes, DB tables, API fields)" not in glossary


def test_spec_sync_asks_the_glossary_question_in_step_one() -> None:
    step_one = raw("skills/spec-sync/SKILL.md").split("1. **Impact**", 1)[1].split("2. **Record**", 1)[0]
    assert_rule(step_one, "introduce or rename a domain term", "`docs/steering/glossary.md`")
