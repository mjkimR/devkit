"""Steering documents in the ``spec`` bundle: the context declaration, the constitution line, the role contracts, the
seeded steering glossary and the moved glossary paths (SPEC-foundation-documents)."""

from __future__ import annotations

import re
import tomllib

import pytest
from devkit_core.core import frontmatter
from devkit_docs.utils.text import foreign_letters
from spec_support.bundle_text import BUNDLE, DOCS, flat, raw, text

ROLES = sorted(path.name.removesuffix(".jinja") for path in (BUNDLE / "subagents").glob("*.md*"))
OLD_PATHS = ("docs/glossary.md", "docs/glossary.yaml", "../glossary.md")


def test_the_manifest_declares_the_steering_directory() -> None:
    manifest = tomllib.loads((DOCS / "bundle.toml").read_text())
    assert manifest["context_documents"] == "docs/steering"
    core = manifest["presets"]["core"]["assets"]
    assert "steering-documents" in core
    assert any(asset["id"] == "steering-documents" and asset["kind"] == "rule" for asset in manifest["assets"])


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_the_constitution_names_the_list_and_its_trigger(environment: str) -> None:
    constitution = raw(DOCS / "AGENTS.md", environment)
    lines = [line for line in constitution.split("\n- ") if "`docs/steering/`" in line]
    assert len(lines) == 1, lines
    line = flat(lines[0])
    assert "`devkit get-context docs` lists each file's title and summary under `documents`" in line
    assert "Read a file's body before a wording, naming, interface or content decision its summary covers" in line


@pytest.mark.parametrize("role", ROLES)
def test_every_role_contract_loads_the_spec_context(role: str) -> None:
    contract = text(f"subagents/{role}")
    assert "`uv run devkit get-context spec`" in contract
    assert ".devkit/managed/spec/AGENTS.md" not in contract


def test_the_seed_holds_the_steering_glossary_and_no_root_copy() -> None:
    seed = DOCS / "seed/docs"
    assert not (seed / "glossary.md").exists() and not (seed / "glossary.yaml").exists()
    assert (seed / "steering/glossary.yaml").is_file()
    parsed = frontmatter.parse(raw("seed/docs/steering/glossary.md"))
    assert parsed.data is not None and set(parsed.data) == {"title", "summary"}
    summary = parsed.data["summary"]
    assert isinstance(summary, str) and not foreign_letters(summary) and len(summary) <= 300
    assert "| Term | Definition | Owner | Avoid | Code identifiers |" in parsed.body
    assert sorted(path.name for path in (seed / "steering").iterdir()) == ["glossary.md", "glossary.yaml"]
    assert "`../steering/glossary.md`" in raw("seed/docs/architecture/README.md")
    assert "**`steering/`**" in raw("seed/docs/README.md") and "`glossary.md`" in raw("seed/docs/README.md")


def _sources() -> list[str]:
    return sorted(
        path.relative_to(BUNDLE).as_posix()
        for path in BUNDLE.rglob("*")
        if path.is_file()
        and "tests" not in path.relative_to(BUNDLE).parts
        and "__pycache__" not in path.parts
        and path.suffix in {".md", ".jinja", ".toml", ".yaml"}
    )


@pytest.mark.parametrize("source", _sources())
def test_no_bundle_source_names_the_old_glossary_path(source: str) -> None:
    content = (BUNDLE / source).read_text()
    assert not [old for old in OLD_PATHS if old in content]


@pytest.mark.parametrize(
    "source",
    [
        "instructions/living-spec-writing.md",
        "instructions/architecture-writing.md",
        "skills/spec-sync/SKILL.md",
        "playbooks/adr-compaction/SKILL.md",
        "playbooks/brownfield-adoption/references/migration.md",
        "rules/document_reference/guide.md",
        "rules/id_convention/guide.md",
        "rules/proposal_boundaries/guide.md",
    ],
)
def test_the_glossary_guidance_names_the_steering_path(source: str) -> None:
    assert "`docs/steering/glossary.md`" in text(
        DOCS / source if source.startswith("rules/") and "proposal_boundaries" not in source else source
    )


def test_living_spec_writing_defines_steering_documents() -> None:
    body = raw("instructions/living-spec-writing.md")
    section = flat(body[body.index("## Steering documents") : body.index("## Glossary")])
    assert "`docs/steering/`" in section and "no `id`" in section and "`RULE-steering-documents`" in section
    description = re.search(r"^description: (.*)$", body, re.MULTILINE)
    assert description is not None and "steering documents" in description.group(1)
