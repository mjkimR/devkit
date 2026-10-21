"""The terminology guidance of the ``spec`` bundle: the ``living-spec-writing`` Glossary rules, the seeded glossary
columns and the ``spec-sync`` glossary question (SPEC-terminology-authoring-guidance)."""

from __future__ import annotations

import re
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"
HEADER = "| Term | Definition | Owner | Avoid | Code identifiers |"


def _read(relative: str) -> str:
    return (BUNDLE / relative).read_text(encoding="utf-8")


def test_the_glossary_section_carries_eight_rules_and_the_code_boundary() -> None:
    text = _read("instructions/living-spec-writing.md")
    description = re.search(r"^description: (.+)$", text, re.MULTILINE)
    assert description is not None and "terminology and the glossary" in description.group(1)
    section = text.split("\n## Glossary\n", 1)[1]
    assert "A package redefinition applies to that package's documents only." in section
    assert re.findall(r"^(\d)\. ", section, re.MULTILINE) == [str(n) for n in range(1, 9)]
    assert "does not authorize renaming code, APIs or schemas" in " ".join(section.split())


def test_the_glossary_section_names_the_project_list_the_synonyms_and_the_fallback() -> None:
    section = " ".join(_read("instructions/living-spec-writing.md").split("\n## Glossary\n", 1)[1].split())
    assert "Project additions and exceptions live in a section of `docs/glossary.md`" in section
    assert "`docs/glossary.yaml` exists, also add each Avoid entry as a synonym of the term's cluster" in section
    assert "A glossary without the `Owner`, `Avoid` and `Code identifiers` columns" in section


def test_the_seeded_glossary_has_five_columns_and_no_rename_mandate() -> None:
    text = _read("seed/docs/glossary.md")
    assert HEADER in text.splitlines()
    assert "## Avoided Generic Nouns" in text and "`living-spec-writing` instruction" in text
    assert "Authoring Guidelines" not in text and "Code symbols (classes, DB tables, API fields)" not in text


def test_spec_sync_asks_the_glossary_question_in_step_one() -> None:
    text = _read("skills/spec-sync/SKILL.md")
    step_one = text.split("### Step 1:", 1)[1].split("### Step 2:", 1)[0]
    assert "introduce or rename a domain term" in step_one and "`docs/glossary.md`" in step_one
