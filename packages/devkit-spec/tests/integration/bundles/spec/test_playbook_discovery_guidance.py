"""`spec` intake runs one bounded playbook search and offers at most one confirmed playbook (SPEC-spec-playbook-discovery).

These tests pin the wording the agent applies; whether the agent's selection keeps the offer rare is shown by the
Unit's recorded manual run, not here (``ADR-spec-intake-playbook-discovery``).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from distsupport.guidance import assert_rule
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
    skill = raw(SKILL, environment)
    start = skill.index("1. **Playbook discovery at intake**")
    return skill[start : skill.index("2. Classify per the constitution", start)]


# AC-01
@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_intake_runs_one_bounded_search_before_classification(environment: str) -> None:
    skill = text(SKILL, environment)
    step = _intake_step(environment)
    assert skill.index("1. **Playbook discovery at intake**") < skill.index("2. Classify per the constitution")
    assert_rule(step, "playbook discovery at intake", "before classification", "before any unit")
    assert_rule(step, "intake is", "`/spec <intent>`", "user's own message", "outside the agreed scope")
    assert_rule(step, "no message from another agent", "host payload", "worker turn", "no hook", "is intake")
    assert_rule(step, "run one", '`devkit playbook search "<english query>" --limit 3 --max-bytes 4096`', "per intake")
    assert_rule(step, "canonical artifact nouns", "adr", "living spec", "release", "paraphrase")
    assert_rule(step, "no automatic refinement")
    assert_rule(step, "query in english", "requested operation", "on its artifact")
    assert_rule(step, "without qualifiers", "only name the subject")
    assert "Do not search or route to playbooks" not in skill


# AC-02
def test_skip_table_conversation_stops_and_not_skipped_cases() -> None:
    step = _intake_step("local")
    for row in (
        ("| continuation", "existing proposal or unit"),
        ("| a follow-up", "same task"),
        ("| the entry is already explicit", "names a playbook id"),
        ("| execution inside a selected playbook", "no nested search"),
        ("| an information-only question", "no change and no operation"),
    ):
        assert_rule(step, *row)
    assert_rule(step, "task kind", "planning depth", "never exempt")
    assert_rule(step, "skip every later intake", "not to use playbooks")
    assert_rule(step, "never offer a candidate", "declined", "same conversation", "reworded")
    assert_rule(step, "not skipped", "new request", "earlier work finished")
    assert_rule(step, "not skipped", "how to perform an operation")


# AC-03
def test_selection_rule_offers_operations_never_topics() -> None:
    step = _intake_step("local")
    assert_rule(step, "scores never decide")
    for condition in ("**operation, not topic**", "**primary operation**", "**scope fits**", "**one line**"):
        assert condition in step, condition
    assert_rule(step, "topic match", "never offered", '"feedback quick fixes" never offers `feedback-hygiene`')
    assert_rule(step, "at most one offer line", "per intake")


# AC-04
def test_confirm_first_offer_silent_no_match_and_recorded_selection() -> None:
    step = _intake_step("local")
    reference = raw(REFERENCE)
    assert_rule(step, "nothing of it runs", "before the user confirms", "explicit invocation")
    assert_rule(step, "wait for the answer", "before creating a unit, a branch or an edit")
    assert_rule(step, "no match", "silently", "no question", "no draft offer")
    for code in ("NOT_SYNCHRONIZED", "CONFIG_LOCAL_RENDER_STALE", "ARGUMENT_INVALID", "SEARCH_EXTRA_MISSING"):
        assert code in step, code
    assert_rule(step, "lock timeout", "counts as no match", "never run its remediation")
    assert_rule(reference, "record the playbook id", "`plan-intent` note")
    assert_rule(reference, "confirmation grants what an explicit invocation grants", "no more")


# AC-05
def test_post_selection_procedure_is_a_reference_read_only_on_a_match() -> None:
    step = _intake_step("local")
    assert_rule(step, "on a match read [playbooks](references/playbooks.md)", "only on a match")
    reference = raw(REFERENCE)
    assert reference.startswith("# Playbooks found at intake\n")
    assert_rule(reference, "read this only on a match")
    for action in (
        ("run `devkit get-context <bundle>`",),
        ("read the selected playbook body",),
        ("check its prerequisites", "stops the playbook"),
        ("follow the procedure", "completion conditions"),
        ("no nested", "playbook search"),
    ):
        assert_rule(reference, *action)
    assert not (BUNDLE / "skills/spec-playbook").exists()
    assert "spec-playbook" not in raw("bundle.toml")


# AC-07
@pytest.mark.parametrize("path", PLAYBOOKS, ids=lambda path: path.stem if path.stem != "SKILL" else path.parent.name)
def test_playbook_entry_reads_invoked_or_confirmed(path: Path) -> None:
    body = " ".join(path.read_text("utf-8").split())
    assert "invoked or confirmed" in body
    assert "only on explicit invocation through `devkit-playbook`" not in body


def test_adr_compaction_confirmation_authorizes_deletions_at_session_depth() -> None:
    body = raw("playbooks/adr-compaction/SKILL.md")
    assert_rule(body, "only when", "invoked or confirmed", "authorizes", "adr deletions", "`session` depth")


# AC-08
def test_guidance_pointer_keeps_the_intake_rule_in_one_line() -> None:
    pointer = raw("guidance/spec-pointer.md")
    assert len(pointer.strip().splitlines()) == 1
    assert_rule(pointer, "`/spec <intent>`", "each new task intake", "intake step first")
