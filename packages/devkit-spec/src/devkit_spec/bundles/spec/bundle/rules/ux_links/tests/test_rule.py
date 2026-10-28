"""``RULE-ux-links``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Violation
from devkit_agt.features.rules.services.testing import check, load_rule
from devkit_docs.features.documents import DocumentIndex
from devkit_docs.features.governance.services.ux import use_case

RULE = load_rule(__file__)
UC = "docs/usecases/account/UC-sign-in.md"
HEADER = (
    "| Trigger | Step | From | To | Target | Capability | Feedback |\n| --- | --- | --- | --- | --- | --- | --- |\n"
)


def usecase(steps: list[str], extensions: tuple[str, ...] = (), *, intro: str = "", slug: str = "sign-in") -> str:
    main = "".join(f"{n}. {text}\n" for n, text in enumerate(steps, start=1))
    ext = "".join(f"- {text}\n" for text in extensions)
    return (
        f"---\nid: UC-{slug}\ntitle: Sign in\nsummary: A person signs in.\narea: account\nstatus: active\n---\n"
        f"# [UC-{slug}] Sign in\n\n## 1. Goal\n\n- **Goal**: sign in\n\n## 2. Main Success Scenario\n\n{intro}{main}\n"
        f"## 3. Extensions\n\n{ext}\n## 5. Acceptance Criteria\n\n### Scenario 1\n- **Covers**: main success scenario\n"
        "1. Not a step.\n"
    )


def ux(
    slug: str,
    rows: list[tuple[str, str]],
    *,
    element: str | None = "screen",
    usecases: tuple[str, ...] = ("UC-sign-in",),
    content: str = "",
    table: str = HEADER,
) -> str:
    """A UX document; each row is ``(Step cell, Target cell)``."""
    element_line = f"element: {element}\n" if element is not None else ""
    listed = "".join(f"  - {item}\n" for item in usecases)
    body = "".join(f"| Press | {step} | populated | loading | {target} | | Spinner |\n" for step, target in rows)
    return (
        f"---\nid: UX-{slug}\ntitle: {slug}\nsummary: The {slug} element.\narea: account\n{element_line}status: draft\n"
        f"usecases:\n{listed}---\n# [UX-{slug}] {slug}\n\n## 1. Purpose\n\nSign in.\n\n## 2. Content\n\n{content}\n\n"
        f"## 3. States\n\n- populated\n\n## 4. Interactions\n\n{table}{body}\n## 5. Evidence\n\nNone.\n"
    )


def path(slug: str) -> str:
    return f"docs/ux/account/UX-{slug}.md"


def found(violations: list[Violation]) -> list[tuple[str, str]]:
    return sorted((v.file, v.message) for v in violations)


def two_screens(target: str = "`UX-done`") -> dict[str, str]:
    return {
        UC: usecase(["The person opens `UX-login`.", "The system shows `UX-done`."]),
        path("login"): ux("login", [("`UC-sign-in` 1", target)]),
        path("done"): ux("done", [("`UC-sign-in` 2", "")]),
    }


def test_a_consistent_pair_passes(tmp_path: Path) -> None:
    assert check(RULE, tmp_path, two_screens()) == []


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (
            ux("login", [("`UC-sign-in` 1", "`UX-done`")], element=None),
            "element is missing; set screen, modal or panel",
        ),
        (
            ux("login", [("`UC-sign-in` 1", "`UX-done`")], element="page"),
            'element "page" is not screen, modal or panel',
        ),
        (
            ux("login", [("`UC-sign-in` 1", "`UX-done`")], table="| Trigger | Step | Target |\n| --- | --- | --- |\n"),
            "Interactions has no table with the columns Trigger | Step | From | To | Target | Capability | Feedback",
        ),
        (ux("login", [("step one", "`UX-done`")]), 'Step cell "step one" is not `UC-<slug>` <key>'),
        (ux("login", [("`UC-sign-in` 1", "home")]), 'Target "home" is not a UX document, close, back or end'),
        (ux("login", [("`UC-sign-in` 1", "`UX-gone`")]), 'Target "`UX-gone`" is not a UX document, close, back or end'),
    ],
    ids=["no-element", "bad-element", "table", "step-cell", "target-word", "target-unknown"],
)
def test_the_documents_own_shape(tmp_path: Path, text: str, message: str) -> None:
    files = {**two_screens(), path("login"): text}
    assert (path("login"), message) in found(check(RULE, tmp_path, files))


def test_a_missing_interactions_section(tmp_path: Path) -> None:
    text = ux("login", [("`UC-sign-in` 1", "`UX-done`")]).replace("## 4. Interactions", "## 4. Actions")
    files = {**two_screens(), path("login"): text}
    assert (path("login"), "no Interactions section") in found(check(RULE, tmp_path, files))


def test_a_target_that_is_not_a_ux_document(tmp_path: Path) -> None:
    files = {**two_screens("`UC-sign-in`")}
    assert (path("login"), 'Target "`UC-sign-in`" is not a UX document, close, back or end') in found(
        check(RULE, tmp_path, files)
    )


@pytest.mark.parametrize(
    ("login", "message"),
    [
        (ux("login", [("`UC-sign-in` 7", "`UX-done`")]), "Step names UC-sign-in 7, which is not a step of UC-sign-in"),
        (
            ux("login", [("`UC-sign-in` 1", "`UX-done`"), ("`UC-sign-in` 2", "")]),
            "Step names UC-sign-in 2, which does not cite UX-login",
        ),
        (
            ux("login", [("`UC-sign-in` 1", "`UX-done`"), ("`UC-other` 1", "")]),
            "Step names UC-other, which usecases does not list",
        ),
        (
            ux("login", [("`UC-sign-in` 1", "`UX-done`")], usecases=("UC-sign-in", "UC-other")),
            "usecases lists UC-other, but no Step cell names it",
        ),
    ],
    ids=["unknown-key", "not-citing", "unlisted", "unused-entry"],
)
def test_step_cells_and_usecases_agree_with_the_steps(tmp_path: Path, login: str, message: str) -> None:
    other = usecase(["The person opens the page."], slug="other")
    files = {**two_screens(), path("login"): login, "docs/usecases/account/UC-other.md": other}
    assert (path("login"), message) in found(check(RULE, tmp_path, files))


def test_a_citing_step_needs_the_reverse_usecases_entry(tmp_path: Path) -> None:
    files = {
        **two_screens(),
        "docs/usecases/account/UC-other.md": usecase(["The person opens `UX-login`."], slug="other"),
    }
    assert (path("login"), "UC-other step 1 cites UX-login, whose usecases does not list UC-other") in found(
        check(RULE, tmp_path, files)
    )


def test_exits_and_modal_close(tmp_path: Path) -> None:
    files = {
        UC: usecase(["The person opens `UX-login`.", "The person confirms in `UX-confirm`.", "It shows `UX-done`."]),
        path("login"): ux("login", [("`UC-sign-in` 1", "`UX-confirm`")]),
        path("confirm"): ux("confirm", [("`UC-sign-in` 2", "`UX-done`")], element="modal"),
        path("done"): ux("done", [("`UC-sign-in` 3", "")]),
    }
    assert found(check(RULE, tmp_path, files)) == [(path("confirm"), "modal has no close or back interaction")]
    files[path("done")] = ux("done", [("`UC-sign-in` 3", "")])
    files[UC] = usecase(
        ["The person opens `UX-login`.", "The person confirms in `UX-confirm`.", "It shows `UX-done`.", "`UX-login`."]
    )
    files[path("login")] = ux("login", [("`UC-sign-in` 1", "`UX-confirm`"), ("`UC-sign-in` 4", "")])
    files[path("confirm")] = ux(
        "confirm", [("`UC-sign-in` 2", "`UX-done`"), ("`UC-sign-in` 2", "close")], element="modal"
    )
    assert found(check(RULE, tmp_path, files)) == [(path("done"), "screen has no exit in UC-sign-in")]


def test_a_panel_never_needs_an_exit_and_a_self_target_is_none(tmp_path: Path) -> None:
    files = {
        UC: usecase(["The person opens `UX-login`.", "The person reads `UX-help`.", "It shows `UX-done`."]),
        path("login"): ux("login", [("`UC-sign-in` 1", "`UX-login`")], content="- `UX-help`"),
        path("help"): ux("help", [("`UC-sign-in` 2", "`UX-done`")], element="panel"),
        path("done"): ux("done", [("`UC-sign-in` 3", "")]),
    }
    assert found(check(RULE, tmp_path, files)) == [(path("login"), "screen has no exit in UC-sign-in")]


def test_reachability_per_use_case(tmp_path: Path) -> None:
    files = {
        UC: usecase(
            ["Opens `UX-a`.", "Goes on in `UX-b`.", "Reads the mail.", "Returns in `UX-c`."],
            ("**2a.** The link expired: the system shows `UX-d`; resumes at step 2.",),
        ),
        path("a"): ux("a", [("`UC-sign-in` 1", "end")]),
        path("b"): ux("b", [("`UC-sign-in` 2", "")]),
        path("c"): ux("c", [("`UC-sign-in` 4", "")]),
        path("d"): ux("d", [("`UC-sign-in` 2a", "`UX-b`")]),
    }
    assert found(check(RULE, tmp_path, files)) == []  # UX-b is reached from the extension's screen UX-d
    files[path("d")] = ux("d", [("`UC-sign-in` 2a", "back")])
    assert found(check(RULE, tmp_path, files)) == [(path("b"), "UX-b is not reachable from an entry of UC-sign-in")]
    files[path("a")] = ux("a", [("`UC-sign-in` 1", "`UX-b`")])
    assert found(check(RULE, tmp_path, files)) == []


def test_a_system_step_between_two_screens_needs_an_interaction(tmp_path: Path) -> None:
    files = {
        UC: usecase(["Submits `UX-form`.", "The system validates and shows `UX-result`.", "Done in `UX-result`."]),
        path("form"): ux("form", [("`UC-sign-in` 1", "end")]),
        path("result"): ux("result", [("`UC-sign-in` 2", ""), ("`UC-sign-in` 3", "")]),
    }
    assert found(check(RULE, tmp_path, files)) == [
        (path("result"), "UX-result is not reachable from an entry of UC-sign-in")
    ]
    files[path("form")] = ux("form", [("`UC-sign-in` 1", "`UX-result`")])
    assert found(check(RULE, tmp_path, files)) == []


def test_a_panel_named_in_content_contributes_edges(tmp_path: Path) -> None:
    files = {
        UC: usecase(["Opens `UX-home`.", "Opens `UX-settings`."]),
        path("home"): ux("home", [("`UC-sign-in` 1", "back")], content="- Navigation (`UX-nav`)"),
        path("nav"): ux("nav", [("", "`UX-settings`")], element="panel", usecases=()),
        path("settings"): ux("settings", [("`UC-sign-in` 2", "")]),
    }
    assert found(check(RULE, tmp_path, files)) == []


def test_a_report_lands_where_the_run_looks(tmp_path: Path) -> None:
    files = {**two_screens(), path("login"): ux("login", [("`UC-sign-in` 1", "`UX-done`"), ("`UC-sign-in` 2", "")])}
    message = "Step names UC-sign-in 2, which does not cite UX-login"
    assert [(v.file, v.message) for v in check(RULE, tmp_path, files, targets=[path("login")])] == [
        (path("login"), message)
    ]
    on_usecase = check(RULE, tmp_path, targets=[UC])
    assert [(v.file, v.line, v.message) for v in on_usecase] == [
        (UC, usecase_line(tmp_path, "2. The system"), f"{message} ({path('login')})")
    ]
    assert check(RULE, tmp_path, targets=["docs/ux/account/UX-done.md"]) == []
    files[path("login")] = ux("login", [("`UC-sign-in` 1", "`UX-done`"), ("`UC-sign-in` 1", "home")], element="page")
    assert len(check(RULE, tmp_path, files)) == 2
    assert check(RULE, tmp_path, targets=[UC]) == []  # a finding about the UX document alone


def usecase_line(root: Path, prefix: str) -> int:
    lines = (root / UC).read_text(encoding="utf-8").splitlines()
    return next(number for number, line in enumerate(lines, start=1) if line.startswith(prefix))


def test_the_step_parser_tolerates_the_formats_in_use(tmp_path: Path) -> None:
    text = (
        "---\nid: UC-sign-in\ntitle: T\narea: account\nstatus: active\n---\n# [UC-sign-in] T\n\n"
        "## 2. Main Success Scenario\n\nAn intro paragraph citing `UX-intro`.\n\n"
        "1. The person opens the form.\n2. The system checks it\n   and shows `UX-done`.\n\n"
        "```text\n3. not a step `UX-code`\n```\n\n"
        "## 3. Extensions\n\n- **1a.** It fails: resumes at\n  step 1.\n\nFree prose citing `UX-prose`.\n\n"
        "- **\\*a.** Any step: the use case ends.\n- **2b.** Retry; resumes at 1a.\n\n"
        "## 5. Acceptance Criteria\n\n### Scenario 1\n- **Covers**: 2a\n1. Not a step `UX-x`.\n"
    )
    (tmp_path / UC).parent.mkdir(parents=True)
    (tmp_path / UC).write_text(text, encoding="utf-8")
    index = DocumentIndex.load(tmp_path)
    parsed = use_case(index, index.resolve("UC-sign-in"), text)
    assert [(s.key, s.extension, s.resumes, s.screens) for s in parsed.steps] == [
        ("1", False, None, ()),
        ("2", False, None, ("UX-done",)),
        ("1a", True, "1", ()),
        ("*a", True, None, ()),
        ("2b", True, "1a", ()),
    ]


def test_a_nested_numbered_list_continues_its_step_and_same_step_resumes(tmp_path: Path) -> None:
    text = (
        "---\nid: UC-sign-in\ntitle: T\narea: account\nstatus: active\n---\n# [UC-sign-in] T\n\n"
        "## 2. Main Success Scenario\n\n1. Fills the form:\n   1. types the name\n   2. types `UX-form`\n2. Done.\n\n"
        "## 3. Extensions\n\n- **2a.** Fails; resumes at the same step.\n- **\\*a.** Cancels; resumes at the same step.\n"
    )
    (tmp_path / UC).parent.mkdir(parents=True)
    (tmp_path / UC).write_text(text, encoding="utf-8")
    index = DocumentIndex.load(tmp_path)
    parsed = use_case(index, index.resolve("UC-sign-in"), text)
    assert [(s.key, s.resumes, s.screens) for s in parsed.steps] == [
        ("1", None, ("UX-form",)),
        ("2", None, ()),
        ("2a", "2", ()),
        ("*a", None, ()),
    ]


def test_a_starred_key_in_a_step_cell(tmp_path: Path) -> None:
    for cell in ("`UC-sign-in` *a", "`UC-sign-in` \\*a"):
        files = {
            UC: usecase(["Opens `UX-login`.", "Done."], ("**\\*a.** Cancels in `UX-login`; the use case ends.",)),
            path("login"): ux("login", [("`UC-sign-in` 1", "end"), (cell, "close")]),
        }
        assert check(RULE, tmp_path, files) == [], cell


def test_an_extension_that_ends_needs_no_exit_but_one_resuming_on_a_screen_does(tmp_path: Path) -> None:
    files = {
        UC: usecase(
            ["Opens `UX-login`.", "Signs in at `UX-done`."],
            ("**1a.** Locked: the system shows `UX-locked`; the use case ends.",),
        ),
        path("login"): ux("login", [("`UC-sign-in` 1", "`UX-done`")]),
        path("done"): ux("done", [("`UC-sign-in` 2", "")]),
        path("locked"): ux("locked", [("`UC-sign-in` 1a", "")]),
    }
    assert check(RULE, tmp_path, files) == []
    files[UC] = usecase(
        ["Opens `UX-login`.", "Signs in at `UX-done`."],
        ("**1a.** Locked: the system shows `UX-locked`; resumes at step 2.",),
    )
    assert found(check(RULE, tmp_path, files)) == [(path("locked"), "screen has no exit in UC-sign-in")]


def test_a_step_cell_naming_an_unresolved_use_case_is_left_to_document_reference(tmp_path: Path) -> None:
    files = {**two_screens(), path("login"): ux("login", [("`UC-sign-in` 1", "`UX-done`"), ("`UC-gone` 1", "")])}
    assert check(RULE, tmp_path, files) == []
