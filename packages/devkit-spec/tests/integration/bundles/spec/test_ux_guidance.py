"""The ``spec`` bundle's UX guidance: template, seed, ``ux-writing``, step citations and the placement of drafts and
the UX review before code (SPEC-ux-documentation AC-11, AC-12, AC-14)."""

from __future__ import annotations

from devkit_dist.features.distribution.services.bundles import load_bundle
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
    assert "templates/{capability,usecase,ux,decision,milestone}.md" in text("AGENTS.md.jinja")


def test_ux_writing_is_a_core_instruction_with_the_agreed_rules() -> None:
    bundle = load_bundle(DOCS)
    assert "ux-writing" in bundle.select(["core"])
    guide = text("instructions/ux-writing.md")
    for phrase in (
        "draft two or three contrasting candidates",
        "Never draw a character-cell layout",
        "Name every object by its glossary term",
        "`docs/steering/ux-objects.md`",
        "Create it with the project's first UX document; nothing seeds it",
        "cite the project's steering style files; never restate",
        "the wireframe, mock-up or screenshot tool is the project's",
        "A system step cites the screen its response appears on",
        "an ID the change creates (a new UX, UC or CAP ID) is plain text",
    ):
        assert phrase in guide, phrase
    assert "a step may cite the UX ID of the screen it happens on" in text("instructions/usecase-writing.md")
    assert "a system step cites the screen its response appears on" in text("instructions/usecase-writing.md")


def test_drafts_and_the_review_precede_the_plan() -> None:
    specify = text("skills/spec-specify/SKILL.md")
    assert "add a `Screens` section to `spec.md`" in specify
    assert "carry the Screens drafts of `target-docs.md` into this section" in specify
    assert "Write an ID the change creates (a new UX, UC or CAP ID) as plain text" in specify
    assert "offer the optional UX review before the plan" in specify
    assert "before `spec-plan` (feature) or `plan-tasks` (bugfix)" in specify
    assert "the optional UX review runs before `spec-plan`" in text("skills/spec-specify/references/feature.md")
    assert "runs inside `characterize`, before `plan-tasks`" in text("skills/spec-specify/references/bugfix.md")


def test_spec_sync_writes_the_drafts_and_lists_them() -> None:
    sync = text("skills/spec-sync/SKILL.md")
    assert "write each draft of the spec's `Screens` section to `docs/ux/<area>/UX-<slug>.md`" in sync
    assert "the drafted register rows to `docs/steering/ux-objects.md`" in sync
    assert "every drafted screen has a `docs/ux/` target" in sync


def test_the_effort_table_and_acceptance_request_name_the_ux_review() -> None:
    effort = raw("skills/spec/references/effort.md.jinja")
    row = next(line for line in effort.splitlines() if line.startswith("| UX review"))
    cells = [cell.strip() for cell in row.strip("|").split("|")]
    assert cells[2].startswith("recommended when screens change") and cells[3].startswith(
        "recommended when screens change"
    )
    assert "The UX review is an optional delegation, not a stage or a gate" in text("skills/spec/references/effort.md")
    assert "each `ux-review` round with its open findings" in text("workflows/sdd-proposal.md")
    assert "its open findings go to the user in the `plan-accept` request" in text("skills/spec/references/planning.md")
