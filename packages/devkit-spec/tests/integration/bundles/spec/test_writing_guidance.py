"""The layered writing guidance of the ``spec`` bundle: the common baseline, one instruction per document kind and
the templates that point to them (SPEC-writing-guidance-layers, ADR-layered-writing-guidance)."""

from __future__ import annotations

import re
from pathlib import Path

from devkit_dist.features.distribution.services.bundles import load_bundle

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"
INSTRUCTIONS = {
    "contract-authoring",
    "living-spec-writing",
    "document-writing",
    "decision-writing",
    "capability-writing",
    "story-writing",
    "architecture-writing",
}


def _read(relative: str) -> str:
    return (BUNDLE / relative).read_text(encoding="utf-8")


def _description(name: str) -> str:
    found = re.search(r"^description: (.+)$", _read(f"instructions/{name}.md"), re.MULTILINE)
    assert found is not None, name
    return found.group(1)


def test_the_core_preset_ships_the_common_and_per_kind_instructions() -> None:
    bundle = load_bundle(BUNDLE)
    kinds = {asset.id: asset.kind for asset in bundle.assets}
    assert {asset for asset in bundle.select(["core"]) if kinds[asset] == "instruction"} == INSTRUCTIONS
    assert {path.stem for path in (BUNDLE / "instructions").glob("*.md")} == INSTRUCTIONS


def test_every_instruction_header_names_its_trigger_within_the_budget() -> None:
    for name in sorted(INSTRUCTIONS):
        description = _description(name)
        assert description.startswith("Read before"), name
        assert len(description) <= 300, (name, len(description))


def test_the_decision_template_and_guide_carry_the_y_statement_and_confirmation() -> None:
    template = _read("templates/decision.md")
    assert "## 6. Confirmation" in template and "accepting <downside>" in template
    guide = " ".join(_read("instructions/decision-writing.md").split())
    assert "Y-statement" in guide and "**Confirmation**" in guide


def test_the_capability_guide_gives_every_ears_template_and_the_template_points_to_it() -> None:
    guide = _read("instructions/capability-writing.md")
    for clause in (
        "`<system> MUST <response>`",
        "`WHEN <event>",
        "`WHILE <state>",
        "`IF <unwanted condition>, THEN",
        "`WHERE <feature",
    ):
        assert clause in guide, clause
    assert "capability-writing" in _read("templates/capability.md")


def test_the_story_and_architecture_guides_and_the_story_template() -> None:
    story = " ".join(_read("instructions/story-writing.md").split())
    assert "Example Mapping" in story and "Given/When/Then" in story
    assert _read("templates/story.md").count("story-writing") == 2
    architecture = " ".join(_read("instructions/architecture-writing.md").split())
    assert "fitness function" in architecture
    for part in ("Source", "Stimulus", "Environment", "Response", "Measure"):
        assert f"| {part} |" in architecture, part
