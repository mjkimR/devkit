"""The final Planning return names ``direction-handoff`` when ``next`` shows no current stage
(``SPEC-git-operator-planning-completion-route`` AC-04)."""

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw


def test_worker_records_name_direction_handoff_for_the_final_planning_return() -> None:
    records = raw("skills/spec/references/worker-records.md").split("## 2.", 1)[0]
    assert_rule(
        records,
        "**Final Planning return**",
        "`[STAGE: - complete=yes]`",
        "still `reviewing`",
        "at `direction-handoff`",
        "never `handoff` or `-`",
        "hold `plan-accept`",
        "no acceptance or handoff effect",
    )


def test_planning_step_six_names_direction_handoff() -> None:
    step = raw("skills/spec/references/planning.md").split("\n6. ", 1)[1]
    assert_rule(step, "`[STAGE: - complete=yes]`", "still `reviewing`", "`direction-handoff`", "never `handoff` or `-`")
