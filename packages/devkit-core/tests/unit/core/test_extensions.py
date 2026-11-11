"""``devkit_core.core.extensions``: the isolated entry-point loop and the post-command extension runner."""

from __future__ import annotations

import sys
import types
from collections.abc import Callable
from importlib import metadata

import pytest
from devkit.advisory import AdvisoryError, Level
from devkit_core.core import extensions
from devkit_core.core.extensions import (
    DISCOVERY,
    ExtensionCalled,
    ExtensionFailed,
    call_extensions,
    run_extensions,
)

GROUP = "devkit.test_extensions"
MODULE = "devkit_core_test_extension_targets"


class _Notice(AdvisoryError):
    code = "TEST_NOTICE"
    level = Level.NOTICE


class _Failed(AdvisoryError):
    code = "TEST_EXTENSION_FAILED"
    level = Level.WARNING


class _Raised(AdvisoryError):
    code = "TEST_RAISED"


def _install(monkeypatch: pytest.MonkeyPatch, **targets: object) -> None:
    """Register ``targets`` as the entry points of ``GROUP``, listed in reverse name order."""
    module = types.ModuleType(MODULE)
    for name, target in targets.items():
        setattr(module, name, target)
    monkeypatch.setitem(sys.modules, MODULE, module)
    entries = [metadata.EntryPoint(name, f"{MODULE}:{name}", GROUP) for name in sorted(targets, reverse=True)]

    def entry_points(*, group: str) -> list[metadata.EntryPoint]:
        return entries if group == GROUP else []

    monkeypatch.setattr(extensions.metadata, "entry_points", entry_points)


def _exits() -> object:
    raise SystemExit(3)


def _raises() -> object:
    raise ValueError("")


def test_call_extensions_isolates_each_entry_point_in_name_order(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, b_exits=_exits, a_ok=lambda: 1, c_raises=_raises, d_ok=lambda: 2)
    outcomes = call_extensions(GROUP, lambda entry: entry.load()())
    assert [outcome.name for outcome in outcomes] == ["a_ok", "b_exits", "c_raises", "d_ok"]
    first, exited, raised, last = outcomes
    assert isinstance(first, ExtensionCalled) and first.result == 1
    assert isinstance(exited, ExtensionFailed) and isinstance(exited.error, SystemExit)
    assert exited.problem == "3"
    assert isinstance(raised, ExtensionFailed) and raised.problem == "ValueError"  # empty message: the type name
    assert raised.entry is not None and raised.entry.value == f"{MODULE}:c_raises"
    assert isinstance(last, ExtensionCalled) and last.result == 2


def test_call_extensions_fail_fast_stops_at_the_first_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    loaded: list[str] = []

    def call(entry: metadata.EntryPoint) -> object:
        loaded.append(entry.name)
        return entry.load()()

    _install(monkeypatch, a_ok=lambda: 1, b_raises=_raises, c_ok=lambda: 2)
    outcomes = call_extensions(GROUP, call, fail_fast=True)
    assert [type(outcome) for outcome in outcomes] == [ExtensionCalled, ExtensionFailed]
    assert loaded == ["a_ok", "b_raises"]


def test_call_extensions_reports_a_failed_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    def entry_points(*, group: str) -> list[metadata.EntryPoint]:
        raise SystemExit("broken metadata")

    monkeypatch.setattr(extensions.metadata, "entry_points", entry_points)
    (outcome,) = call_extensions(GROUP, lambda entry: entry.load())
    assert isinstance(outcome, ExtensionFailed)
    assert (outcome.name, outcome.entry, outcome.problem) == (DISCOVERY, None, "broken metadata")


def test_call_extensions_lets_keyboard_interrupt_propagate(monkeypatch: pytest.MonkeyPatch) -> None:
    def interrupted() -> object:
        raise KeyboardInterrupt

    _install(monkeypatch, a=interrupted)
    with pytest.raises(KeyboardInterrupt):
        call_extensions(GROUP, lambda entry: entry.load()())


def _run(monkeypatch: pytest.MonkeyPatch, **targets: Callable[[], object]) -> list[AdvisoryError]:
    _install(monkeypatch, **targets)
    return run_extensions(
        GROUP,
        lambda extension: extension(),
        failed=lambda name, problem: _Failed(f"{name} failed: {problem}"),
        notice=lambda line, name: _Notice(line, f"extension: {name}"),
    )


def test_run_extensions_turns_returns_into_notices(monkeypatch: pytest.MonkeyPatch) -> None:
    def returns() -> object:
        return ["line", _Raised("lowered", level=Level.ERROR)]

    def raises() -> object:
        raise _Raised("kept", level=Level.ERROR)

    notices = _run(monkeypatch, a=returns, b=lambda: None, c=raises, d=lambda: "text")
    assert [(item.code, item.level, item.message) for item in notices] == [
        ("TEST_NOTICE", Level.NOTICE, "line"),
        ("TEST_RAISED", Level.WARNING, "lowered"),
        ("TEST_RAISED", Level.WARNING, "kept"),
        ("TEST_EXTENSION_FAILED", Level.WARNING, "d failed: returned str, expected list[str | AdvisoryError]"),
    ]
    assert notices[0].details == ("extension: a",)
    assert notices[2].details[-1] == "extension: c"


def test_run_extensions_isolates_system_exit_and_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    notices = _run(monkeypatch, a=_exits, b=lambda: ["after"])
    assert [item.message for item in notices] == ["a failed: 3", "after"]

    def entry_points(*, group: str) -> list[metadata.EntryPoint]:
        raise RuntimeError("no metadata")

    monkeypatch.setattr(extensions.metadata, "entry_points", entry_points)
    notices = run_extensions(
        GROUP,
        lambda extension: extension(),
        failed=lambda name, problem: _Failed(f"{name} failed: {problem}"),
        notice=lambda line, name: _Notice(line),
    )
    assert [item.message for item in notices] == ["discovery failed: no metadata"]
