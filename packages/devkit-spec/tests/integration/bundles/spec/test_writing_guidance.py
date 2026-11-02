"""The layered writing guidance of the ``spec`` bundle: the common baseline, one instruction per document kind and
the templates that point to them (SPEC-writing-guidance-layers, ADR-layered-writing-guidance)."""

from __future__ import annotations

import re

from devkit_dist.features.distribution.services.bundles import load_bundle
from distsupport.guidance import assert_rule
from spec_support.bundle_text import DOCS as BUNDLE
from spec_support.bundle_text import raw, text

INSTRUCTIONS = {
    "contract-authoring",
    "living-spec-writing",
    "document-writing",
    "decision-writing",
    "capability-writing",
    "usecase-writing",
    "ux-writing",
    "architecture-writing",
}


def _description(name: str) -> str:
    found = re.search(r"^description: (.+)$", raw(f"instructions/{name}.md"), re.MULTILINE)
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
    template = text("templates/decision.md")
    assert "## 6. Confirmation" in template and "accepting <downside>" in template
    guide = text("instructions/decision-writing.md")
    assert "Y-statement" in guide and "**Confirmation**" in guide


def test_the_decision_guide_and_template_keep_a_partly_replaced_adr_accepted() -> None:
    guide = raw("instructions/decision-writing.md")
    assert_rule(guide, "`status: superseded`", "`superseded_by`", "only when", "replaces all")
    assert_rule(guide, "stays `accepted`", "without `superseded_by`", "superseded in part by `adr-<new>`")
    assert_rule(guide, "names it in `supersedes`", "which clauses it")
    template = raw("templates/decision.md")
    assert_rule(template, "superseded (only when a later adr replaces all")
    assert_rule(template, "# supersedes: [adr-<slug>]", "wholly or in part", "replaced clauses in decision outcome")
    assert_rule(template, "stay accepted", "superseded in part by `adr-<new>`")


def test_the_decision_guide_and_template_mark_normative_outcome_clauses() -> None:
    guide = raw("instructions/decision-writing.md")
    assert_rule(guide, "one list item per clause", "declarative sentence without an rfc 2119 keyword")
    assert_rule(guide, "backticked id", "section or rule that holds it", "keyword that document uses")
    assert_rule(guide, "`cap-<area>-<slug>` rule 3 (must)")
    assert_rule(guide, "no document restates", "rationale or context only")
    assert_rule(guide, "follow the restating document", "where and how strongly")
    assert_rule(guide, "**confirmation**", "restating ids")
    assert "Split a multi-part decision" not in guide
    assert "Give a normative clause one RFC 2119 keyword" not in guide
    assert_rule(guide, "an adr and to a padr alike", "at least one holds")
    for criterion in ("costly to reverse", "more than one package", "more than one viable option", "existing contract"):
        assert_rule(guide, criterion)
    assert_rule(guide, "meets none of them", "planning decisions", "`plan.md`")
    planning = raw("skills/spec/references/planning.md")
    assert_rule(planning, "new padr", "admission criteria", "planning decisions")
    template = raw("templates/decision.md")
    assert_rule(template, "<declarative clause> → `cap-<area>-<slug>` <section or rule> (<must|should|may>)")
    assert_rule(template, "`arch-<id>`", "rationale clause carries no trace")
    completion = raw("skills/spec/references/completion.md")
    assert_rule(
        completion, "lasting rules → capabilities or architecture with rfc 2119 keywords", "cites each restating id"
    )
    assert "lasting policy → ADRs" not in completion


def test_the_capability_guide_gives_every_ears_template_and_the_template_points_to_it() -> None:
    guide = text("instructions/capability-writing.md")
    for clause in (
        "`<system> MUST <response>`",
        "`WHEN <event>",
        "`WHILE <state>",
        "`IF <unwanted condition>, THEN",
        "`WHERE <feature",
    ):
        assert clause in guide, clause
    assert "capability-writing" in text("templates/capability.md")


def test_the_usecase_and_architecture_guides_and_the_usecase_template() -> None:
    usecase = text("instructions/usecase-writing.md")
    assert "Example Mapping" in usecase and "Given/When/Then" in usecase
    assert text("templates/usecase.md").count("usecase-writing") == 2
    architecture = text("instructions/architecture-writing.md")
    assert "fitness function" in architecture
    assert_rule(
        raw("instructions/architecture-writing.md"),
        "quality requirement",
        "scenario",
        "source",
        "stimulus",
        "environment",
        "response",
        "measure",
    )
