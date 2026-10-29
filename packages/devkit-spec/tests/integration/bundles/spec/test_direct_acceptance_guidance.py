"""The bundled guidance states the direct acceptance and the session reclassification of a queued draft
(``SPEC-draft-direct-acceptance`` AC-12): the contract phrases an agent acts on, not the wording around them."""

from __future__ import annotations

from pathlib import Path

from distsupport.guidance import assert_rule
from spec_support.bundle_text import flat, raw, text

from devkit_spec.features.proposals import create_proposal

ACCEPT = "devkit spec proposal accept"


def test_acceptances_are_recorded_with_the_accept_command() -> None:
    for rel in (
        "workflows/sdd-proposal.md",
        "skills/spec/references/backlog.md",
        "skills/spec-next/references/next-work.md",
        "skills/spec-next/references/workflow-signals.md",
        "skills/spec/references/proposals-catalog.md",
    ):
        assert ACCEPT in text(rel), rel
    workflow = text("workflows/sdd-proposal.md")
    assert "--action accept --by user`, written only after" not in workflow  # no hand-recorded plan-accept


def test_backlog_states_the_direct_acceptance_procedure() -> None:
    backlog = text("skills/spec/references/backlog.md")
    assert "Until direct acceptance exists" not in backlog
    for phrase in (
        f"{ACCEPT} <slug> --by user --direct --check",
        f"{ACCEPT} <slug> --by user|policy --direct --note",
        "collect-feedback",
    ):
        assert phrase in backlog, phrase
    backlog_raw = raw("skills/spec/references/backlog.md")
    assert_rule(backlog_raw, "present", "planning skipped", "`dev_effort`", "`pull_request = required`")
    assert_rule(backlog_raw, "commit a direct acceptance", "only on the base checkout")
    workflow = text("workflows/sdd-proposal.md")
    assert "Planning: skipped (direct acceptance)" in workflow
    assert_rule(
        raw("workflows/sdd-proposal.md"),
        "direct acceptance",
        "no planning run",
        "no `activity-effort`",
        "no `worker` envelope",
    )
    assert "SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED" in workflow
    assert_rule(raw("skills/spec/references/effort.md"), "direct acceptance", "no planning run", "no effort")


def test_the_lowering_rule_names_the_session_reclassification() -> None:
    assert_rule(raw("AGENTS.md"), "lower it only through", "session reclassification of a queued draft")
    backlog = raw("skills/spec/references/backlog.md")
    assert "## Session reclassification of a queued draft" in backlog
    for rule in (
        ("queued draft", "`session` task", "within the authorized goal, scope and constraints"),
        ("require", "no `padr-*.md` in `decisions/`"),
        ("session takes a new slug", "never integrates", "`git revert` the deletion"),
    ):
        assert_rule(backlog, *rule)
    assert "session reclassification" in text("skills/spec/references/feedback-retirement.md")
    assert "session reclassification" in text("skills/spec-next/references/next-work.md")


def test_the_scaffold_lifecycle_holds_for_a_direct_acceptance(tmp_path: Path) -> None:
    (tmp_path / ".devkit").mkdir()
    scaffold = flat((tmp_path / create_proposal(tmp_path, "idea").path).read_text(encoding="utf-8"))
    assert f"{ACCEPT} idea --by user" in scaffold and "--direct" in scaffold
    assert "set status: accepted and merge the Planning branch" not in scaffold
