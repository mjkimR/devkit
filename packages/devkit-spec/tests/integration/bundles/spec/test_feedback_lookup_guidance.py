"""Recording looks up existing feedback of every status before writing (SPEC-feedback-dedup-and-compaction).

The lookup command, the sameness judgment and the status table are pinned in the `spec-feedback` recording procedure,
and the sweep reuses that step instead of its former equal-`target` deduplication
(``ADR-recording-looks-up-existing-feedback-of-every-status-first``).
"""

from __future__ import annotations

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text

SKILL = "skills/spec-feedback/SKILL.md"
SWEEP = "skills/spec-feedback/references/sweep.md"
LOOKUP = '`devkit docs search "<symptom and asset words>" --kind feedback --history -n 5`'


def _procedure() -> str:
    skill = raw(SKILL)
    start = skill.index("## Recording procedure")
    return skill[start : skill.index("## Completion", start)]


# AC-01
def test_recording_searches_every_status_before_writing() -> None:
    procedure = _procedure()
    assert procedure.index("2. Look up existing feedback of every status") < procedure.index("3. Write the file")
    assert LOOKUP in " ".join(procedure.split())
    assert_rule(procedure, "same observation", "same symptom of the same asset or behavior", "whatever its `target`")
    assert_rule(procedure, "no search score decides sameness")
    assert_rule(procedure, "compact record hit", "only the entries that match", "matching entry decides")


# AC-02
def test_the_matched_status_decides_the_action() -> None:
    procedure = _procedure()
    for row in (
        ("| `open` |", "record nothing", "name the existing id", "inside your write scope", "report that names the id"),
        ("| `dismissed` |", "record nothing unless", "evidence against the recorded reason", "cite the id"),
        ("| `resolved` |", "regression", "cites the resolved id", "`recurring: true`"),
        (
            "| `promoted`, `forwarded` |",
            "destination is live",
            "record nothing and name it",
            "completed, rejected, closed or no longer resolves",
            "new item that cites the id",
        ),
    ):
        assert_rule(procedure, *row)
    assert_rule(raw(SKILL), "step 2 says not to record", "`> Feedback exists: <ID> (<status>)`")


# AC-03
def test_the_sweep_runs_the_same_lookup_across_namespaces() -> None:
    sweep = raw(SWEEP)
    assert_rule(sweep, "**look up**", "step 2 of the skill's recording procedure", "`--all-namespaces`")
    assert '`devkit docs search "<symptom and asset words>" --kind feedback --history --all-namespaces -n 5`' in text(
        SWEEP
    )
    assert_rule(sweep, "duplicate", "keep the existing id")
    assert_rule(sweep, "**record**", "from its step 3")
    assert "--status open --all-namespaces" not in sweep
    assert "same nature" not in text(SWEEP)
