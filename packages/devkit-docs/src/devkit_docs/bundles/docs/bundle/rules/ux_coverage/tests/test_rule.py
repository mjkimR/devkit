"""``RULE-ux-coverage``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

from devkit_agt.features.rules import Severity, Violation
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)
UC = "docs/usecases/account/UC-sign-in.md"
LOGIN = "docs/ux/account/UX-login.md"
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


def _ux(slug: str, *steps: str, usecases: str = "  - UC-sign-in\n") -> str:
    rows = "".join(f"| Press | {step} | a | b | end | | Done |\n" for step in steps)
    return (
        f"---\nid: UX-{slug}\ntitle: {slug}\nsummary: The {slug} screen.\narea: account\nelement: screen\n"
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
        (LOGIN, 9, f"UC-sign-in step 2 cites no UX document ({UC})"),
        (LOGIN, 9, f"UC-sign-in step 2a cites no UX document ({UC})"),
        (LOGIN, 18, "interaction has no Step"),
    ]
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
