"""``RULE-ux-coverage``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

from devkit_agt.features.rules import Severity, Violation
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)
UC = "docs/usecases/account/UC-sign-in.md"
LOGIN = "docs/ux/account/UX-login.md"
NAV = "docs/ux/account/UX-nav.md"
OTHER = "docs/ux/account/UX-other.md"
HEADER = (
    "| Trigger | Step | From | To | Target | Capability | Feedback |\n| --- | --- | --- | --- | --- | --- | --- |\n"
)


def _usecase(*steps: str, extensions: tuple[str, ...] = ()) -> str:
    main = "".join(f"{n}. {text}\n" for n, text in enumerate(steps, start=1))
    ext = "".join(f"- {text}\n" for text in extensions)
    return (
        "---\nid: UC-sign-in\ntitle: Sign in\nsummary: A person signs in.\narea: account\nstatus: active\n---\n"
        f"# [UC-sign-in] Sign in\n\n## 2. Main Success Scenario\n\n{main}\n## 3. Extensions\n\n{ext}"
    )


def _ux(slug: str, *steps: str, usecases: str = "  - UC-sign-in\n", element: str = "screen") -> str:
    rows = "".join(f"| Press | {step} | a | b | end | | Done |\n" for step in steps)
    return (
        f"---\nid: UX-{slug}\ntitle: {slug}\nsummary: The {slug} screen.\narea: account\nelement: {element}\n"
        f"status: draft\nusecases:\n{usecases}---\n# [UX-{slug}] {slug}\n\n## 4. Interactions\n\n{HEADER}{rows}"
    )


def _found(violations: list[Violation]) -> list[tuple[str, int, str]]:
    return [(v.file, v.line, v.message) for v in violations]


def test_a_covered_use_case_passes(tmp_path: Path) -> None:
    files = {UC: _usecase("Opens `UX-login`.", extensions=("**1a.** Fails in `UX-login`; resumes at step 1.",))}
    files[LOGIN] = _ux("login", "`UC-sign-in` 1", "`UC-sign-in` 1a")
    assert check(RULE, tmp_path, files) == []


def test_uncovered_steps_and_stepless_interactions_are_warnings(tmp_path: Path) -> None:
    files = {
        UC: _usecase(
            "Opens `UX-login`.", "The system sends a mail.", extensions=("**2a.** No mail; the use case ends.",)
        ),
        LOGIN: _ux("login", "`UC-sign-in` 1", "-"),
        OTHER: _ux("other", "`UC-sign-in` 1"),
    }
    violations = check(RULE, tmp_path, files)
    assert {v.severity for v in violations} == {Severity.WARNING}
    assert sorted(_found(violations)) == [
        (UC, 13, "UC-sign-in step 2 cites no UX document"),
        (UC, 17, "UC-sign-in step 2a cites no UX document"),
        (LOGIN, 18, "interaction has no Step"),
    ]
    # Only a UX document in the run: the step reports land on the first listing document the run targets (AC-10).
    on_other = _found(check(RULE, tmp_path, targets=[OTHER]))
    assert on_other == [
        (OTHER, 9, f"UC-sign-in step 2 cites no UX document ({UC})"),
        (OTHER, 9, f"UC-sign-in step 2a cites no UX document ({UC})"),
    ]
    assert _found(check(RULE, tmp_path, targets=[UC])) == [
        (UC, 13, "UC-sign-in step 2 cites no UX document"),
        (UC, 17, "UC-sign-in step 2a cites no UX document"),
    ]


def test_a_use_case_no_ux_document_lists_is_not_reported(tmp_path: Path) -> None:
    files = {UC: _usecase("Opens the page."), LOGIN: _ux("login", "`UC-sign-in` 1", usecases="  - UC-other\n")}
    files["docs/usecases/account/UC-other.md"] = _usecase("x").replace("UC-sign-in", "UC-other")
    assert [v.file for v in check(RULE, tmp_path, files, targets=[UC])] == []


def test_global_interactions_with_a_reason_are_not_reported(tmp_path: Path) -> None:
    """AC-01, AC-02: the navigation case; an unclassified empty cell still warns."""
    files = {
        UC: _usecase("Opens `UX-login`.", "Reads `UX-nav`."),
        LOGIN: _ux("login", "`UC-sign-in` 1"),
        NAV: _ux(
            "nav",
            "global: a preference control that belongs to no task",
            "GLOBAL: accessibility link on every screen",
            "global: the small-screen menu, independent of `UC-sign-in` 2",
            "`UC-sign-in` 2",
            "-",
            element="panel",
        ),
    }
    assert _found(check(RULE, tmp_path, files)) == [(NAV, 21, "interaction has no Step")]


def test_off_screen_steps_with_a_reason_are_not_reported(tmp_path: Path) -> None:
    """AC-03, AC-04: the mail case; an unclassified uncited step still warns."""
    files = {
        UC: _usecase(
            "Opens `UX-login`.",
            "The system sends the confirmation mail. Off screen: the mail leaves by SMTP and nothing appears.",
            "The system archives the attempt.",
            extensions=("**2a.** No mail (off-screen: the retry runs in the background); the use case ends.",),
        ),
        LOGIN: _ux("login", "`UC-sign-in` 1"),
    }
    assert _found(check(RULE, tmp_path, files)) == [(UC, 14, "UC-sign-in step 3 cites no UX document")]


def test_a_classification_without_a_reason_keeps_the_gap_reported(tmp_path: Path) -> None:
    """AC-05: both defective forms, each with its own warning and nothing else for the item."""
    files = {
        UC: _usecase("Opens `UX-login`.", "The system cleans up. off screen:"),
        LOGIN: _ux("login", "`UC-sign-in` 1", "global:"),
    }
    violations = check(RULE, tmp_path, files)
    assert {v.severity for v in violations} == {Severity.WARNING}
    assert _found(violations) == [
        (UC, 13, "UC-sign-in step 2 is classified off screen without a reason"),
        (LOGIN, 18, "interaction is classified global without a reason"),
    ]


def test_an_off_screen_phrase_on_a_citing_step_is_contradictory(tmp_path: Path) -> None:
    """AC-06: the phrase on a step that cites a screen is reported, not the gap."""
    files = {
        UC: _usecase("Opens `UX-login`; off screen: the result is cached."),
        LOGIN: _ux("login", "`UC-sign-in` 1"),
    }
    assert _found(check(RULE, tmp_path, files)) == [
        (UC, 12, "UC-sign-in step 1 is classified off screen but cites UX-login")
    ]


def test_an_invalid_step_cell_is_not_a_coverage_report(tmp_path: Path) -> None:
    """AC-07: a mixed or misspelled cell is RULE-ux-links's error, never a coverage warning."""
    files = {
        UC: _usecase("Opens `UX-login`."),
        LOGIN: _ux("login", "`UC-sign-in` 1", "`UC-sign-in` 1, global: also a shortcut", "globl: typo"),
    }
    assert check(RULE, tmp_path, files) == []


def test_step_reports_target_the_use_case_first(tmp_path: Path) -> None:
    """AC-10: the use case when targeted, else the first listing UX document in the run; rows stay on the screen."""
    files = {
        UC: _usecase("Opens `UX-login`.", "The system archives the attempt.", "Opens `UX-nav`; off screen: cached."),
        LOGIN: _ux("login", "`UC-sign-in` 1", "-"),
        NAV: _ux("nav", "`UC-sign-in` 3"),
    }
    everything = _found(check(RULE, tmp_path, files))
    assert everything == [
        (UC, 13, "UC-sign-in step 2 cites no UX document"),
        (UC, 14, "UC-sign-in step 3 is classified off screen but cites UX-nav"),
        (LOGIN, 18, "interaction has no Step"),
    ]
    assert _found(check(RULE, tmp_path, targets=[NAV])) == [
        (NAV, 9, f"UC-sign-in step 2 cites no UX document ({UC})"),
        (NAV, 9, f"UC-sign-in step 3 is classified off screen but cites UX-nav ({UC})"),
    ]
    assert _found(check(RULE, tmp_path, targets=[LOGIN])) == [
        (LOGIN, 9, f"UC-sign-in step 2 cites no UX document ({UC})"),
        (LOGIN, 9, f"UC-sign-in step 3 is classified off screen but cites UX-nav ({UC})"),
        (LOGIN, 18, "interaction has no Step"),
    ]
    assert _found(check(RULE, tmp_path, targets=[UC])) == everything[:2]


def test_a_surface_without_a_task_flow_passes(tmp_path: Path) -> None:
    """A screen and a panel with ``usecases: []`` and a header-only table, and a modal whose close row is a global
    control, are not reported (the ``ux-writing`` criteria for surfaces beyond pages and forms)."""
    arena = (
        "---\nid: UX-arena\ntitle: Arena\nsummary: The arena viewport.\narea: play\nelement: screen\nstatus: draft\n"
        "usecases: []\ncapabilities: []\n---\n# [UX-arena] Arena\n\n## 2. Content\n\n- **Primary region**: the viewport\n\n"
        "## 4. Interactions\n\n" + HEADER
    )
    hud = arena.replace("UX-arena", "UX-hud").replace("Arena", "HUD").replace("element: screen", "element: panel")
    pause = (
        arena.replace("UX-arena", "UX-pause").replace("Arena", "Pause").replace("element: screen", "element: modal")
        + "| Press Resume | global: a pause control that belongs to no task | paused | playing | close | | Resumes |\n"
    )
    files = {
        UC: _usecase("Opens the page."),
        "docs/ux/play/UX-arena.md": arena,
        "docs/ux/play/UX-hud.md": hud,
        "docs/ux/play/UX-pause.md": pause,
    }
    assert check(RULE, tmp_path, files) == []
