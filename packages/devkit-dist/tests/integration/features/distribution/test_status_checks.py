"""Optional status providers preserve core reporting and agent advisory semantics."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import Level
from devkit_dist.features.distribution.models.errors import NotSynchronizedError, StatusCheckExtensionFailedNotice
from devkit_dist.features.distribution.services.installation import status_checks
from devkit_dist.features.distribution.usecases.status import get_project_status
from distsupport.distribution import cli


@dataclass
class Entry:
    name: str
    value: str
    provider: Callable[[Path], object]
    load_error: Exception | None = None

    def load(self) -> Callable[[Path], object]:
        if self.load_error is not None:
            raise self.load_error
        return self.provider


def _entries(monkeypatch: pytest.MonkeyPatch, entries: list[Entry]) -> None:
    original = status_checks.metadata.entry_points
    monkeypatch.setattr(
        status_checks.metadata,
        "entry_points",
        lambda group: entries if group == status_checks.GROUP else original(group=group),
    )


def test_check_order_and_advisory_identity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, Path]] = []
    warning = StatusCheckExtensionFailedNotice("provider warning")
    notice = warning.with_level(Level.NOTICE)

    def provider(name: str, result: object) -> Callable[[Path], object]:
        def check(root: Path) -> object:
            calls.append((name, root))
            return result

        return check

    _entries(
        monkeypatch,
        [
            Entry("z", "a", provider("z", [])),
            Entry("a", "b", provider("ab", (notice,))),
            Entry("a", "a", provider("aa", [warning])),
        ],
    )
    report = get_project_status(tmp_path, [])
    assert calls == [(name, tmp_path.resolve()) for name in ("aa", "ab", "z")]
    assert report.notices == [warning, notice]
    assert report.ok and report.host_hooks == []


@pytest.mark.parametrize(
    "result",
    [None, "text", [object()], [StatusCheckExtensionFailedNotice("valid"), object()], [NotSynchronizedError("error")]],
)
def test_invalid_result_is_rejected_atomically(result: object, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _entries(monkeypatch, [Entry("bad", "bad:check", lambda _: result)])
    [warning] = status_checks.status_check_notices(tmp_path)
    assert warning.code == "STATUS_CHECK_EXTENSION_FAILED" and warning.level is Level.WARNING
    assert "bad:check" in warning.message and warning.to_dict()["advisory"]


@pytest.mark.parametrize("failure", [RuntimeError("broken"), SystemExit(9)])
def test_provider_failure_preserves_later_checks(
    failure: BaseException, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(_: Path) -> object:
        raise failure

    good = StatusCheckExtensionFailedNotice("later provider")
    _entries(monkeypatch, [Entry("a", "bad", fail), Entry("z", "good", lambda _: [good])])
    warning, later = status_checks.status_check_notices(tmp_path)
    assert warning.code == "STATUS_CHECK_EXTENSION_FAILED" and later is good


def test_load_and_discovery_failures_are_warnings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _entries(monkeypatch, [Entry("bad", "bad:load", lambda _: [], ImportError("missing package"))])
    assert status_checks.status_check_notices(tmp_path)[0].code == "STATUS_CHECK_EXTENSION_FAILED"

    def broken(*, group: str) -> object:
        raise RuntimeError(group)

    monkeypatch.setattr(status_checks.metadata, "entry_points", broken)
    [warning] = status_checks.status_check_notices(tmp_path)
    assert "discovery" in warning.message and "devkit.status_checks" in warning.message


def test_keyboard_interrupt_propagates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def stop(_: Path) -> object:
        raise KeyboardInterrupt

    _entries(monkeypatch, [Entry("stop", "stop", stop)])
    with pytest.raises(KeyboardInterrupt):
        status_checks.status_check_notices(tmp_path)


def test_empty_group_and_json_strict_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _entries(monkeypatch, [])
    assert get_project_status(tmp_path, []).notices == []
    _entries(monkeypatch, [Entry("bad", "bad:load", lambda _: None)])
    for options, code in (([], 0), (["--strict"], 1)):
        result = CliRunner().invoke(cli, ["status", "-w", str(tmp_path), *options])
        assert result.exit_code == code, result.output
        assert result.stderr == ""
        report = json.loads(result.stdout)
        assert report["errors"] == []
        assert [item["code"] for item in report["notices"]] == ["STATUS_CHECK_EXTENSION_FAILED"]


def test_extension_failure_keeps_core_status_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_dist.features.distribution.usecases import status

    problem = NotSynchronizedError("core problem")
    monkeypatch.setattr(status, "_problems", lambda *_: [problem])
    _entries(monkeypatch, [Entry("bad", "bad:load", lambda _: None)])
    report = get_project_status(tmp_path, [])
    assert report.errors == [problem] and not report.ok
    assert [item.code for item in report.notices] == ["STATUS_CHECK_EXTENSION_FAILED"]
