"""Process identity and retired-group discovery guards."""

from devkit_agt.features.isolated_execution.repositories.runtime import _discover, same


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
