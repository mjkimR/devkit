"""Process identity and retired-group discovery guards."""

from types import SimpleNamespace

from devkit_agt.features.isolated_execution.repositories import runtime
from devkit_agt.features.isolated_execution.repositories.runtime import _discover, same, validate_group_leaders


def test_linux_process_identity_uses_stable_proc_start_ticks(monkeypatch) -> None:
    monkeypatch.setattr(runtime.sys, "platform", "linux")
    timestamps = iter(("12:15:56", "12:15:45"))
    monkeypatch.setattr(
        runtime.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout=f"7 1 7 Sat Nov 7 {next(timestamps)} 2026 S test-process\n"),
    )
    monkeypatch.setattr(
        runtime.Path,
        "read_text",
        lambda path: "boot-a" if path.name == "boot_id" else "7 (test) " + " ".join(["S"] * 19 + ["13078"]),
    )
    saved = runtime.processes()[7]
    current = runtime.processes()[7]
    assert same(saved, current)
    validate_group_leaders({7: saved}, 7, {7: current}, {7}, unreaped=True)
    assert not same(saved, {"pid": 7, "birth": "linux:boot-a:13079"})
    assert not same(saved, {"pid": 7, "birth": "linux:boot-b:13078"})
    assert not same(saved, {"pid": 7, "birth": "Sat Nov 7 12:15:56 2026:13078"})
    assert not same(saved, {"pid": 8, "birth": current["birth"]})


def test_macos_process_identity_uses_full_start_time(monkeypatch) -> None:
    monkeypatch.setattr(runtime.sys, "platform", "darwin")
    assert not same(
        {"pid": 7, "birth": "Sat Nov 7 12:15:56 2026"},
        {"pid": 7, "birth": "Sat Nov 7 12:15:45 2026"},
    )


def test_reused_pid_is_not_the_original_process() -> None:
    assert not same({"pid": 7, "birth": "first"}, {"pid": 7, "birth": "second"})
    # exec can change argv on a positively identified existing process.
    assert same({"pid": 7, "birth": "first", "argv": "shell"}, {"pid": 7, "birth": "first", "argv": "native"})


def test_retired_group_does_not_adopt_unrelated_reused_pid() -> None:
    known = {7: {"pid": 7, "birth": "first", "ppid": 1, "pgid": 7}}
    table = {
        7: {"pid": 7, "birth": "second", "ppid": 1, "pgid": 7},
        8: {"pid": 8, "birth": "other", "ppid": 7, "pgid": 7},
    }
    _discover(known, 7, table, unreaped=False)
    assert set(known) == {7}


def test_reaped_leader_keeps_unobserved_same_group_orphan_owned() -> None:
    known = {101: {"pid": 101, "birth": "leader", "ppid": 1, "pgid": 101}}
    table = {102: {"pid": 102, "birth": "child", "ppid": 1, "pgid": 101}}
    _discover(known, 101, table, unreaped=False)
    assert 102 in known


def test_owned_group_retires_after_empty_observation_and_never_readopts() -> None:
    known = {101: {"pid": 101, "birth": "leader", "ppid": 1, "pgid": 101}}
    groups = {101}
    child = {102: {"pid": 102, "birth": "child", "ppid": 1, "pgid": 101}}
    _discover(known, 101, child, unreaped=False, groups=groups)
    assert groups == {101} and 102 in known
    _discover(known, 101, {}, unreaped=False, groups=groups)
    assert not groups
    reused = {103: {"pid": 103, "birth": "other", "ppid": 1, "pgid": 101}}
    _discover(known, 101, reused, unreaped=False, groups=groups)
    assert 103 not in known


def test_process_table_is_locale_independent(monkeypatch) -> None:
    # Under ko_KR/ja_JP, ps renders lstart in four tokens ("화 11/10 16:41:11 2026"),
    # which misaligned positional parsing and dropped every process.
    monkeypatch.setattr(runtime.sys, "platform", "darwin")
    monkeypatch.setenv("LC_ALL", "ko_KR.UTF-8")

    def ps(*args, **kwargs):
        env = kwargs.get("env") or runtime.os.environ
        if env.get("LC_ALL") == "C":
            return SimpleNamespace(stdout="7 1 7 Tue Nov 10 16:41:11 2026 Ss test-process --flag\n")
        return SimpleNamespace(stdout="7 1 7 화 11/10 16:41:11 2026 Ss test-process --flag\n")

    monkeypatch.setattr(runtime.subprocess, "run", ps)
    table = runtime.processes()
    assert table[7]["argv"] == "test-process --flag"
    assert table[7]["birth"] == "Tue Nov 10 16:41:11 2026"
