"""The ``spec`` bundle's UX guidance: template, seed, ``ux-writing``, step citations and the placement of drafts and
the UX review before code (SPEC-ux-documentation AC-11, AC-12, AC-14)."""

from __future__ import annotations

from devkit_dist.features.distribution.services.bundles import load_bundle
from distsupport.guidance import assert_rule
from spec_support.bundle_text import DOCS, raw, text

COLUMNS = "| Trigger | Step | From | To | Target | Capability | Feedback |"


def test_the_template_carries_the_element_links_and_sections() -> None:
    template = raw("templates/ux.md")
    for line in ("id: UX-<slug>", "element: screen", "status: draft", "usecases:", "capabilities:"):
        assert line in template, line
    assert "# screen | modal | panel" in template and "# draft | active | deprecated" in template
    for heading in ("## 1. Purpose", "## 2. Content", "## 3. States", "## 4. Interactions", "## 5. Evidence"):
        assert f"\n{heading}\n" in template, heading
    assert COLUMNS in template and "ux-writing" in template


def test_the_seed_holds_the_ux_directory_but_no_register() -> None:
    seed = DOCS / "seed/docs"
    assert (seed / "ux/README.md").is_file()
    assert not (seed / "steering/ux-objects.md").exists()
    assert "| **`ux/`** | UX Documents |" in raw("seed/docs/README.md")
    assert "templates/{capability,usecase,ux,decision,milestone}.md" in text(DOCS / "AGENTS.md")


def test_ux_writing_is_a_core_instruction_with_the_agreed_rules() -> None:
    bundle = load_bundle(DOCS)
    assert "ux-writing" in bundle.select(["core"])
    guide = raw("instructions/ux-writing.md")
    assert_rule(guide, "two or three", "contrasting candidates", "recommendation")
    assert_rule(guide, "never", "character-cell layout")
    assert_rule(guide, "every object", "glossary term", "`docs/steering/glossary.md`")
    assert "`docs/steering/ux-objects.md`" in guide
    assert_rule(guide, "`docs/steering/ux-objects.md`", "first UX document", "nothing seeds")
    assert_rule(guide, "visual style", "steering style files", "never restate")
    assert_rule(guide, "medium", "wireframe", "mock-up", "screenshot", "project's")
    assert_rule(guide, "use case steps", "cite", "screens", "`usecase-writing`")
    assert_rule(guide, "draft", "change creates", "UX, UC or CAP ID", "plain text")
    usecase = raw("instructions/usecase-writing.md")
    assert_rule(usecase, "step", "may cite", "UX ID", "screen")
    assert_rule(usecase, "system step", "cites", "screen", "response")


def test_drafts_and_the_review_precede_the_plan() -> None:
    specify = raw("skills/spec-specify/SKILL.md")
    assert_rule(specify, "**Screens**", "add", "`Screens` section", "`spec.md`", "`ux`", "`ux-writing`")
    assert_rule(specify, "**Screens**", "carry", "Screens drafts", "`target-docs.md`")
    assert_rule(specify, "Screens section", "offer", "optional UX review", "before the plan", "`ux-reviewer`")
    assert_rule(specify, "`ux-reviewer`", "before `spec-plan` (feature)", "`plan-tasks` (bugfix)")
    for reference in ("feature", "bugfix"):
        assert_rule(raw(f"skills/spec-specify/references/{reference}.md"), "**Screens**", "draft", "`SKILL.md` §4")


def test_spec_sync_writes_the_drafts_and_lists_them() -> None:
    sync = raw("skills/spec-sync/SKILL.md")
    assert_rule(sync, "each draft", "`Screens` section", "`docs/ux/<area>/UX-<slug>.md`")
    assert_rule(sync, "`Screens` section", "register rows", "`docs/steering/ux-objects.md`")
    assert_rule(sync, "every drafted screen", "`docs/ux/` target")


def test_the_effort_table_and_acceptance_request_name_the_ux_review() -> None:
    effort = raw("skills/spec/references/effort.md.jinja")
    row = next(line for line in effort.splitlines() if line.startswith("| UX review"))
    cells = [cell.strip() for cell in row.strip("|").split("|")]
    assert cells[2].startswith("recommended when screens change") and cells[3].startswith(
        "recommended when screens change"
    )
    assert_rule(raw("skills/spec/references/effort.md"), "UX review", "optional delegation", "not a stage", "gate")
    assert_rule(raw("workflows/sdd-proposal.md"), "`plan-accept`", "each `ux-review` round", "open findings")
    assert_rule(raw("skills/spec/references/planning.md"), "`ux-reviewer`", "open findings", "`plan-accept` request")
