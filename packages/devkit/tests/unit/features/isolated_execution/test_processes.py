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
