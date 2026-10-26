"""`spec` intake runs one bounded playbook search and offers at most one confirmed playbook (SPEC-spec-playbook-discovery).

These tests pin the wording the agent applies; whether the agent's selection keeps the offer rare is shown by the
Unit's recorded manual run, not here (``ADR-spec-intake-playbook-discovery``).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spec_support.bundle_text import BUNDLE, raw, text

SKILL = "skills/spec/SKILL.md"
REFERENCE = "skills/spec/references/playbooks.md"
CATALOG = Path(__file__).resolve().parents[5] / "devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks"
PLAYBOOKS = [
    BUNDLE / "playbooks/brownfield-adoption/SKILL.md",
    BUNDLE / "playbooks/feedback-hygiene/SKILL.md",
    BUNDLE / "playbooks/adr-compaction/SKILL.md",
    CATALOG / "drift-reconciliation.md",
    CATALOG / "weekly-report.md",
]


def _intake_step(environment: str) -> str:
    skill = text(SKILL, environment)
    start = skill.index("1. **Playbook discovery at intake**")
    return skill[start : skill.index("2. Classify per the constitution", start)]


# AC-01
@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_intake_runs_one_bounded_search_before_classification(environment: str) -> None:
    skill = text(SKILL, environment)
    step = _intake_step(environment)
    assert skill.index("1. **Playbook discovery at intake**") < skill.index("2. Classify per the constitution")
    assert "before classification and before any Unit is created" in step
    assert "Intake is a `/spec <intent>` or a user's own message that requests a change or an operation outside" in step
    assert "no message from another agent (Host payload, worker turn, nested role), no hook and no stage" in step
    assert 'Run one `devkit playbook search "<English query>" --limit 3 --max-bytes 4096` per intake' in step
    assert "canonical artifact nouns (ADR, feedback, Living Spec, proposal, playbook, rule, release)" in step
    assert "no automatic refinement follows" in step
    assert "as the requested operation on its artifact" in step
    assert "without qualifiers that only name the subject" in step
    assert "Do not search or route to playbooks" not in skill


# AC-02
def test_skip_table_conversation_stops_and_not_skipped_cases() -> None:
    step = _intake_step("local")
    for row in (
        "| Continuation of an existing proposal or Unit:",
        "| A follow-up within the same task:",
        "| The entry is already explicit:",
        "| Execution inside a selected playbook |",
        "| An information-only question that requests no change and no operation |",
    ):
        assert row in step, row
    assert "Task kind and planning depth never exempt a task" in step
    assert "once the user said not to use playbooks in this conversation" in step
    assert "never offer a candidate the user declined again in the same conversation, even for a reworded" in step
    assert "Not skipped: a new request after earlier work finished" in step
    assert "a question that asks how to perform an operation" in step


# AC-03
def test_selection_rule_offers_operations_never_topics() -> None:
    step = _intake_step("local")
    assert "Scores never decide" in step
    for condition in ("**operation, not topic**", "**primary operation**", "**scope fits**", "**one line**"):
        assert condition in step, condition
    assert '"Feedback Quick Fixes" never offers `feedback-hygiene`' in step
    assert "at most one offer line per intake" in step


# AC-04
def test_confirm_first_offer_silent_no_match_and_recorded_selection() -> None:
    step = _intake_step("local")
    reference = text(REFERENCE)
    assert "nothing of it runs before the user confirms, and the confirmation is its explicit invocation" in step
    assert "wait for the answer before creating a Unit, a branch or an edit" in step
    assert "wait for the answer before creating a Unit, a branch or an edit" in reference
    assert "No match continues the ordinary path silently, with no question and no draft offer" in step
    for code in ("NOT_SYNCHRONIZED", "CONFIG_LOCAL_RENDER_STALE", "ARGUMENT_INVALID", "SEARCH_EXTRA_MISSING"):
        assert code in step, code
    assert "a lock timeout) counts as no match: never run its remediation for discovery's sake" in step
    assert "record the playbook ID in the `plan-intent` note" in reference
    assert "Nothing of the playbook runs before the user confirms" in reference
    assert "never offer that candidate again in the conversation" in reference


# AC-05
def test_post_selection_procedure_is_a_reference_read_only_on_a_match() -> None:
    step = _intake_step("local")
    assert "On a match read [playbooks](references/playbooks.md); only on a match." in step
    reference = text(REFERENCE)
    assert reference.startswith("# Playbooks found at intake Read this only on a match")
    for action in (
        "Run `devkit get-context <bundle>`",
        "Read the selected playbook body",
        "Check its prerequisites",
        "Follow the procedure through its completion conditions",
        "runs no nested playbook search",
    ):
        assert action in reference, action
    assert not (BUNDLE / "skills/spec-playbook").exists()
    assert "spec-playbook" not in raw("bundle.toml")


# AC-07
@pytest.mark.parametrize("path", PLAYBOOKS, ids=lambda path: path.stem if path.stem != "SKILL" else path.parent.name)
def test_playbook_entry_reads_invoked_or_confirmed(path: Path) -> None:
    body = " ".join(path.read_text("utf-8").split())
    assert "invoked or confirmed" in body
    assert "only on explicit invocation through `devkit-playbook`" not in body


def test_adr_compaction_confirmation_authorizes_deletions_at_session_depth() -> None:
    body = text("playbooks/adr-compaction/SKILL.md")
    assert "only when the user invoked or confirmed it" in body
    assert "that invocation authorizes the run's ADR deletions. It runs at `session` depth" in body


# AC-08
def test_guidance_pointer_keeps_the_intake_rule_in_one_line() -> None:
    pointer = raw("guidance/spec-pointer.md")
    assert len(pointer.strip().splitlines()) == 1
    assert "Start work with `/spec <intent>`; each new task intake runs its intake step first" in pointer
