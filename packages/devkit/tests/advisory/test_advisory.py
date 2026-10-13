from __future__ import annotations

import pytest
from devkit.advisory import (
    ACTION_TEXT,
    UNEXPECTED_CODE,
    ActionMode,
    Actor,
    Advisory,
    AdvisoryError,
    ExitCode,
    Level,
    Retry,
    as_advisory_error,
    render_error,
)


@pytest.mark.parametrize(
    ("advisory", "mode"),
    [
        (Advisory(input_error=True, guardrail=True, actor=Actor.TOOL, retry=Retry.SAFE), ActionMode.INPUT_ERROR),
        (Advisory(guardrail=True, actor=Actor.TOOL, retry=Retry.SAFE), ActionMode.BLOCKED),
        (Advisory(actor=Actor.DEVELOPER, retry=Retry.SAFE), ActionMode.MAINTENANCE),
        (Advisory(actor=Actor.TOOL, retry=Retry.UNSAFE), ActionMode.HALT),
        (Advisory(actor=Actor.TOOL, retry=Retry.AFTER_FIX), ActionMode.AUTO),
        (Advisory(actor=Actor.USER, retry=Retry.SAFE), ActionMode.INTERACTION),
        (Advisory(actor=Actor.NONE, retry=Retry.SAFE), ActionMode.DEFER),
        (Advisory(actor=Actor.NONE, retry=Retry.AFTER_FIX), ActionMode.HALT),
        (Advisory(), ActionMode.HALT),
        (Advisory(level=Level.WARNING, input_error=True, actor=Actor.USER), ActionMode.CONTINUE),
        (Advisory(level=Level.NOTICE, guardrail=True, retry=Retry.UNSAFE), ActionMode.NOTE),
    ],
)
def test_mode_derivation_order(advisory: Advisory, mode: ActionMode) -> None:
    assert advisory.mode is mode


def test_every_mode_has_a_directive() -> None:
    assert set(ACTION_TEXT) == set(ActionMode)
    for mode, text in ACTION_TEXT.items():
        assert text.startswith(f"{mode.value} — ")
        assert "likely" not in text


def test_lines_follow_sentinel_format() -> None:
    advisory = Advisory(
        code="CONFIG_INVALID",
        actor=Actor.DEVELOPER,
        retry=Retry.AFTER_FIX,
        input_error=True,
        retry_after="60s",
        fix="Set timeout = 30",
        what_to_report="The config is invalid",
        target_files=("config.toml:12", "--timeout"),
        details=("line 12", "expected integer"),
    )
    assert advisory.lines("Invalid configuration") == [
        "[ERROR]  (CONFIG_INVALID) Invalid configuration",
        "[ACTION] INPUT_ERROR — Do not retry with identical input. Retrying unchanged will",
        "         fail identically. Correct the flag, argument, or input file before rerunning.",
        "[WHEN]   Not before: 60s",
        "[TARGET] config.toml:12, --timeout",
        "[FIX]    Set timeout = 30",
        "[REPORT] The config is invalid",
        "[DETAIL] line 12",
        "[DETAIL] expected integer",
    ]
    assert Advisory(code="").lines("m")[0] == "[ERROR]  (GENERAL_ERROR) m"
    assert Advisory().lines()[0].startswith("[ACTION] HALT")


def test_error_defaults_and_overrides() -> None:
    error = AdvisoryError("Something went wrong", "first detail")
    assert str(error) == "Something went wrong"
    assert (error.code, error.exit_code, error.mode) == ("GENERAL_ERROR", ExitCode.ERROR, ActionMode.HALT)
    assert error.details == ("first detail",)
    assert repr(error) == "AdvisoryError(code='GENERAL_ERROR', message='Something went wrong')"

    class LockHeldError(AdvisoryError):
        code = "LOCK_HELD"
        actor = Actor.NONE
        retry = Retry.SAFE

    deferred = LockHeldError("Another sync is running", retry_after="30s", exit_code=ExitCode.FINDINGS)
    assert deferred.mode is ActionMode.DEFER
    assert deferred.exit_code == ExitCode.FINDINGS
    assert "[WHEN]   Not before: 30s" in deferred.render()
    assert LockHeldError("x", retry=Retry.UNSAFE).mode is ActionMode.HALT
    assert LockHeldError.retry is Retry.SAFE


@pytest.mark.parametrize(
    ("error", "mode"),
    [
        (AdvisoryError.invalid_input("bad flag", code="X", target_files=["--x"]), ActionMode.INPUT_ERROR),
        (AdvisoryError.blocked("refused", code="X", fix="# ignore[X]: reason"), ActionMode.BLOCKED),
        (AdvisoryError.auto_fix("stale", fix="make gen", code="X"), ActionMode.AUTO),
        (AdvisoryError.interaction("confirm", code="X", what_to_report="Proceed?", fix="run"), ActionMode.INTERACTION),
    ],
)
def test_factories_render_their_mode(error: AdvisoryError, mode: ActionMode) -> None:
    assert error.mode is mode
    assert f"[ACTION] {mode.value} — " in error.render()


def test_factories_keep_subclass() -> None:
    class DomainError(AdvisoryError):
        code = "DOMAIN"

    error = DomainError.blocked("Domain layer must not import frameworks", "ADR-0004", target_files=["a.py:1:1"])
    assert isinstance(error, DomainError)
    assert error.code == "DOMAIN"
    assert error.lines()[0] == "[ERROR]  (DOMAIN) Domain layer must not import frameworks"
    assert "[DETAIL] ADR-0004" in error.lines()


def test_serialization_and_problem_details() -> None:
    error = AdvisoryError.interaction("Invalid token", code="AUTH_FAILED", what_to_report="Log in again")
    assert error.to_dict(include_advisory=False) == {
        "code": "AUTH_FAILED",
        "level": "ERROR",
        "message": "Invalid token",
        "exit_code": 2,
    }
    advisory = error.to_dict()["advisory"]
    # JSON carries what the block shows, the directive text included, and no empty fields.
    assert advisory == {
        "code": "AUTH_FAILED",
        "level": "ERROR",
        "mode": "INTERACTION",
        "action": " ".join(ACTION_TEXT[ActionMode.INTERACTION].split("\n")),
        "actor": "USER",
        "retry": "AFTER_FIX",
        "guardrail": False,
        "input_error": False,
        "what_to_report": "Log in again",
    }
    full = AdvisoryError(
        "busy", "d", code="LOCKED", retry=Retry.SAFE, retry_after="30s", fix="x", target_files=["a", " "]
    ).to_dict()["advisory"]
    assert (full["retry_after"], full["fix"], full["target_files"], full["details"]) == ("30s", "x", ["a"], ["d"])
    # The failure fields describe an error only; a brief notice without fix shows no directive.
    warning = error.with_level(Level.WARNING).to_dict()["advisory"]
    assert set(warning) == {"code", "level", "mode", "action", "what_to_report"}
    assert warning["action"].startswith("CONTINUE — ")
    brief = AdvisoryError("fyi", code="FYI", level=Level.NOTICE, brief=True).to_dict()["advisory"]
    assert brief == {"code": "FYI", "level": "NOTICE", "mode": "NOTE"}

    problem = error.to_problem_details(status=401, type_base="https://docs.example.com/errors/")
    assert problem["type"] == "https://docs.example.com/errors/AUTH_FAILED"
    assert (problem["title"], problem["status"], problem["detail"]) == ("AUTH_FAILED", 401, "Invalid token")
    assert problem["advisory"]["mode"] == "INTERACTION"
    bare = error.to_problem_details(include_advisory=False)
    assert bare["type"] == "about:blank"
    assert "status" not in bare and "advisory" not in bare


def test_unexpected_errors_are_maintenance() -> None:
    known = AdvisoryError.auto_fix("stale", fix="make gen")
    assert as_advisory_error(known) is known
    wrapped = as_advisory_error(KeyError("missing"))
    assert (wrapped.code, wrapped.mode) == (UNEXPECTED_CODE, ActionMode.MAINTENANCE)
    assert as_advisory_error(RuntimeError()).message == "RuntimeError"
    assert wrapped.message == "KeyError: 'missing'"
    rendered = render_error(ValueError("boom"))
    assert rendered.startswith("[ERROR]  (UNEXPECTED_ERROR) ValueError: boom\n[ACTION] MAINTENANCE")
    assert "[TARGET], when present, names the affected files." in rendered and "\n[TARGET] " not in rendered


def test_multi_line_values_continue_under_their_sentinel() -> None:
    error = AdvisoryError(
        "git commit failed\nfatal: bad object",
        "first\nsecond",
        fix="run this\nthen that",
        what_to_report="line one\n\nline three",
        actor=Actor.DEVELOPER,
    )
    lines = error.lines()
    assert lines[0] == "[ERROR]  (GENERAL_ERROR) git commit failed"
    assert lines[1] == "         fatal: bad object"
    assert "[FIX]    run this" in lines and "         then that" in lines
    assert lines[-2:] == ["[DETAIL] first", "         second"]
    assert "" not in lines and "[REPORT] line one\n         line three" in error.render()  # blank lines are dropped
    sentinels = ("[ERROR]", "[ACTION]", "[WHEN]", "[TARGET]", "[FIX]", "[REPORT]", "[DETAIL]")
    assert all(line.startswith((*sentinels, " " * 9)) or line == "" for line in lines)


def test_subclass_defaults_cover_every_field() -> None:
    class SyncNeeded(AdvisoryError):
        code = "SYNC_NEEDED"
        actor = Actor.TOOL
        retry = Retry.AFTER_FIX
        fix = "devkit sync"
        what_to_report = "The workspace was out of date"
        retry_after = "1m"
        target_files = (".devkit/installation.json",)

    error = SyncNeeded("stale")
    assert (error.fix, error.what_to_report, error.retry_after) == (
        "devkit sync",
        "The workspace was out of date",
        "1m",
    )
    assert error.target_files == (".devkit/installation.json",) and error.mode is ActionMode.AUTO
    override = SyncNeeded("stale", fix="devkit sync --check", target_files=["a"])
    assert override.fix == "devkit sync --check" and override.target_files == ("a",)
    assert SyncNeeded.auto_fix("stale", fix="x").target_files == (".devkit/installation.json",)


def test_details_are_strings_and_serialize_to_json() -> None:
    import json
    from pathlib import Path

    error = AdvisoryError.invalid_input("bad", Path("a/b"), 3, ValueError("v"), target_files=["x"])
    assert error.details == ("a/b", "3", "v")
    payload = json.loads(json.dumps(error.to_dict()))
    assert payload["advisory"]["details"] == ["a/b", "3", "v"] and payload["exit_code"] == int(ExitCode.ERROR)
    assert json.loads(json.dumps(error.to_problem_details(status=422)))["status"] == 422


def test_exit_codes_follow_the_checker_convention() -> None:
    assert [(code.name, int(code)) for code in ExitCode] == [("OK", 0), ("FINDINGS", 1), ("ERROR", 2)]


def test_advisory_fields_forward_through_a_subclass_constructor() -> None:
    from typing import Unpack

    from devkit.advisory import AdvisoryFields

    class StatefulError(AdvisoryError):
        code = "STATEFUL"

        def __init__(self, message: str, *, extra: int, **fields: Unpack[AdvisoryFields]) -> None:
            super().__init__(message, **fields)
            self.extra = extra

    error = StatefulError("x", extra=3, input_error=True, exit_code=ExitCode.FINDINGS, target_files=["a"])
    assert (error.extra, error.mode, error.exit_code, error.target_files) == (
        3,
        ActionMode.INPUT_ERROR,
        ExitCode.FINDINGS,
        ("a",),
    )


class OrphanWarning(AdvisoryError):
    code = "ORPHAN_LEFT"
    level = Level.WARNING
    actor = Actor.USER


class VersionNotice(AdvisoryError):
    code = "TOOL_VERSION_CHANGED"
    level = Level.NOTICE
    brief = True


def test_warning_renders_continue_and_never_fails() -> None:
    warning = OrphanWarning("left modified file in place: a.md", target_files=["a.md"], what_to_report="Delete it")
    assert (warning.mode, warning.exit_code) == (ActionMode.CONTINUE, ExitCode.OK)
    lines = warning.lines()
    assert lines[0] == "[WARN]   (ORPHAN_LEFT) left modified file in place: a.md"
    assert lines[1].startswith("[ACTION] CONTINUE — ")
    assert "[TARGET] a.md" in lines and "[REPORT] Delete it" in lines
    assert warning.to_dict()["level"] == "WARNING" and warning.to_dict()["exit_code"] == 0


def test_notice_action_is_recommended_and_omitted_only_when_brief_without_fix() -> None:
    assert VersionNotice("devkit 1 -> 2").lines() == ["[NOTICE] (TOOL_VERSION_CHANGED) devkit 1 -> 2"]
    with_fix = VersionNotice("devkit 1 -> 2", fix="devkit status").lines()
    assert with_fix[1].startswith("[ACTION] NOTE — ") and with_fix[-1] == "[FIX]    devkit status"
    full = AdvisoryError("installed bundles not selected: x", code="BUNDLE_UNSELECTED", level=Level.NOTICE)
    assert full.lines()[1].startswith("[ACTION] NOTE — ")
    assert AdvisoryError("x", brief=True).lines()[1].startswith("[ACTION] HALT")  # brief applies to notices only


def test_retry_after_is_an_error_field() -> None:
    notice = AdvisoryError("x", level=Level.NOTICE, retry_after="1m")
    assert not any(line.startswith("[WHEN]") for line in notice.lines())


def test_sentinels_are_nine_characters_wide() -> None:
    from devkit.advisory.advisory import HEADLINE

    assert {len(sentinel) for sentinel in HEADLINE.values()} == {9}


def test_with_level_copies_without_calling_the_constructor() -> None:
    class DriftError(AdvisoryError):
        code = "OVERRIDE_DRIFT"
        actor = Actor.USER
        retry = Retry.AFTER_FIX

        def __init__(self, message: str, *, selectors: list[str]) -> None:
            super().__init__(message, "detail", fix="devkit override diff a:b", target_files=selectors)
            self.selectors = selectors

    error = DriftError("drift", selectors=["a:b"])
    warning = error.with_level(Level.WARNING)
    assert isinstance(warning, DriftError) and warning is not error
    assert (warning.code, warning.selectors, warning.details, warning.fix) == (
        "OVERRIDE_DRIFT",
        ["a:b"],
        ("detail",),
        "devkit override diff a:b",
    )
    assert (warning.level, warning.mode, warning.exit_code) == (Level.WARNING, ActionMode.CONTINUE, ExitCode.OK)
    assert (error.level, error.mode, error.exit_code) == (Level.ERROR, ActionMode.INTERACTION, ExitCode.ERROR)
    assert str(warning) == "drift"
    assert error.with_level(Level.NOTICE, brief=True).brief is True
    assert warning.with_level(Level.ERROR).exit_code == ExitCode.ERROR


def test_a_raised_notice_is_a_defect() -> None:
    wrapped = as_advisory_error(VersionNotice("devkit 1 -> 2"))
    assert (wrapped.code, wrapped.level, wrapped.mode) == (UNEXPECTED_CODE, Level.ERROR, ActionMode.MAINTENANCE)
    assert "NOTICE advisory was raised" in wrapped.message


def test_every_rendered_line_starts_with_a_published_sentinel() -> None:
    # devkit.compact recognizes blocks by these constants; a new field must be added to them.
    from devkit.advisory.advisory import CONTINUATION, FIELDS, HEADLINE

    errors = [
        AdvisoryError(
            "message\n\nsecond",
            "detail\n\nmore",
            retry_after="later",
            target_files=["a"],
            fix="fix\nmore",
            what_to_report="report",
        ),
        AdvisoryError("m", "", "  \n", fix="\nrun x", what_to_report="\n\nask", target_files=[""]),
        AdvisoryError("\nm", "\n  indented"),
    ]
    for error in errors:
        for line in error.lines():
            assert line.startswith((*HEADLINE.values(), *FIELDS, CONTINUATION)), line
            assert line == line.rstrip() and line.strip() not in {s.strip() for s in (*FIELDS, *HEADLINE.values())}, (
                line
            )


def test_blank_values_render_no_line_and_leading_blank_lines_are_skipped() -> None:
    error = AdvisoryError("m", "", "real", fix="\nrun x", target_files=["", "a", " "], actor=Actor.DEVELOPER)
    assert error.lines()[-3:] == ["[TARGET] a", "[FIX]    run x", "[DETAIL] real"]
    assert AdvisoryError("m", target_files=[""]).lines() == AdvisoryError("m").lines()
    assert AdvisoryError("\n\nfirst\n\nsecond").lines()[:2] == ["[ERROR]  (GENERAL_ERROR) first", "         second"]


def test_the_headline_is_always_rendered_with_the_code() -> None:
    assert AdvisoryError("", code="X").lines()[0] == "[ERROR]  (X)"
    assert AdvisoryError("", code="X", level=Level.NOTICE, brief=True).lines() == ["[NOTICE] (X)"]


def test_an_empty_code_is_the_default_code_everywhere() -> None:
    class Blank(AdvisoryError):
        code = ""

    for error in (AdvisoryError("m", code=""), Blank("m")):
        assert error.code == "GENERAL_ERROR" and error.lines()[0] == "[ERROR]  (GENERAL_ERROR) m"
        assert error.to_dict()["code"] == error.to_dict()["advisory"]["code"] == "GENERAL_ERROR"
        assert error.to_problem_details()["title"] == "GENERAL_ERROR"
    assert Advisory(code="").code == "GENERAL_ERROR"


def test_a_string_target_is_one_target() -> None:
    assert AdvisoryError("m", target_files="config.toml").target_files == ("config.toml",)
    assert AdvisoryError.invalid_input("m", target_files="config.toml").lines()[-1] == "[TARGET] config.toml"


class InputDefaultError(AdvisoryError):
    code = "INPUT_DEFAULT"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class GuardDefaultError(AdvisoryError):
    code = "GUARD_DEFAULT"
    guardrail = True
    exit_code = ExitCode.FINDINGS


class NoticeDefault(AdvisoryError):
    code = "NOTICE_DEFAULT"
    level = Level.NOTICE


@pytest.mark.parametrize("cls", [InputDefaultError, GuardDefaultError, NoticeDefault])
def test_factories_derive_their_mode_whatever_the_subclass_defaults(cls: type[AdvisoryError]) -> None:
    assert cls.blocked("x").mode is ActionMode.BLOCKED
    assert cls.interaction("x").mode is ActionMode.INTERACTION
    assert cls.auto_fix("x", fix="y").mode is ActionMode.AUTO
    assert cls.invalid_input("x").mode is ActionMode.INPUT_ERROR
    assert cls.blocked("x").exit_code != ExitCode.OK


def test_an_error_never_exits_ok() -> None:
    with pytest.raises(ValueError, match="ERROR advisory exits 1 or 2"):
        AdvisoryError("m", exit_code=ExitCode.OK)

    class OkWarning(AdvisoryError):
        level = Level.WARNING
        exit_code = ExitCode.OK

    warning = OkWarning("m")
    with pytest.raises(ValueError, match="ERROR advisory exits 1 or 2"):
        warning.with_level(Level.ERROR)
    assert AdvisoryError("m", level=Level.NOTICE, exit_code=ExitCode.FINDINGS).exit_code == ExitCode.OK


def test_an_auto_error_needs_its_fix() -> None:
    with pytest.raises(ValueError, match="AUTO error needs the fix"):
        AdvisoryError("m", actor=Actor.TOOL, retry=Retry.AFTER_FIX)
    with pytest.raises(ValueError, match="AUTO error needs the fix"):
        AdvisoryError.auto_fix("m", fix="")

    class ToolNotice(AdvisoryError):
        level = Level.NOTICE
        actor = Actor.TOOL
        retry = Retry.AFTER_FIX

    notice = ToolNotice("m")  # mode NOTE: no directive to run [FIX]
    with pytest.raises(ValueError, match="AUTO error needs the fix"):
        notice.with_level(Level.ERROR)


def test_with_level_error_keeps_the_instance_exit_code() -> None:
    findings = AdvisoryError("m", exit_code=ExitCode.FINDINGS)
    assert findings.with_level(Level.ERROR).exit_code == ExitCode.FINDINGS
    assert findings.with_level(Level.WARNING).exit_code == ExitCode.OK


class SelectorError(AdvisoryError):
    code = "SELECTOR"

    def __init__(self, message: str, *, selectors: list[str]) -> None:
        super().__init__(message, "detail", target_files=selectors)
        self.selectors = selectors


def test_subclasses_with_required_arguments_pickle_and_copy() -> None:
    import copy
    import pickle

    error = SelectorError("m", selectors=["a:b"]).with_level(Level.ERROR)
    error.exit_code = ExitCode.FINDINGS
    for clone in (pickle.loads(pickle.dumps(error)), copy.copy(error), copy.deepcopy(error)):
        assert type(clone) is SelectorError and clone is not error
        assert (clone.selectors, clone.details, clone.exit_code, clone.args) == (
            ["a:b"],
            ("detail",),
            ExitCode.FINDINGS,
            ("m",),
        )
        assert clone.render() == error.render()
