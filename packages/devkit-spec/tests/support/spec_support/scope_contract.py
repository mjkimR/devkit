"""The registry adapter contract, runnable against any ``Registry``.

Each scenario takes a fresh, empty registry whose ``hostname`` is ``host-a``.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from devkit_spec.base.errors import ScopeTaskExistsError, ScopeTimeoutError, ScopeTokenMismatchError
from devkit_spec.features.scope import Deadline, Registry, token_hash
from spec_support.scope import record


def _deadline() -> Deadline:
    return Deadline(10)


def register_query(registry: Registry) -> None:
    token, stored = registry.register(record("a", "/wt/a"), _deadline())
    assert token and stored.revision == 1
    assert stored.token_hash == token_hash(token), "records store the hash, never the token"
    assert stored.scopes[0].first_seen
    assert (stored.last_request_id, stored.last_added, stored.last_removed) == ("", 0, 0), "legacy keys stay empty"
    with pytest.raises(ScopeTaskExistsError):
        registry.register(record("a", "/wt/a2"), _deadline())
    registry.register(record("b", "/wt/b"), _deadline())
    records, problems = registry.query("ns", _deadline())
    assert problems == [] and [item.task_id for item in records] == ["a", "b"]
    assert registry.query("other", _deadline()) == ([], [])


def release(registry: Registry) -> None:
    token, _ = registry.register(record("a", "/wt/a"), _deadline())
    token_b, _ = registry.register(record("b", "/wt/b"), _deadline())
    with pytest.raises(ScopeTokenMismatchError):
        registry.release("ns", "a", token_b, _deadline())
    assert len(registry.query("ns", _deadline())[0]) == 2, "a foreign token releases nothing"
    registry.release("ns", "a", token, _deadline())
    registry.release("ns", "a", token, _deadline())  # repeating a release is a no-op
    assert [item.task_id for item in registry.query("ns", _deadline())[0]] == ["b"]


def shared_worktree(registry: Registry) -> None:
    _, first = registry.register(record("a", "/wt/same"), _deadline())
    assert not first.shared_worktree
    token_b, second = registry.register(record("b", "/wt/same"), _deadline())
    assert second.shared_worktree
    token_c, _ = registry.register(record("c", "/wt/same"), _deadline())
    assert all(item.shared_worktree for item in registry.query("ns", _deadline())[0])

    def shared() -> dict[str, bool]:
        return {item.task_id: item.shared_worktree for item in registry.query("ns", _deadline())[0]}

    registry.release("ns", "b", token_b, _deadline())
    assert shared() == {"a": True, "c": True}, "two records still share the worktree"
    registry.release("ns", "c", token_c, _deadline())
    assert shared() == {"a": False}, "the record left alone no longer shares its worktree"


def deadline(registry: Registry) -> None:
    expired = Deadline(0)
    with pytest.raises(ScopeTimeoutError):
        registry.query("ns", expired)
    with pytest.raises(ScopeTimeoutError):
        registry.register(record("a", "/wt/a"), expired)
    registry.register(record("a", "/wt/a"), _deadline())  # the registry is usable after a timed-out call


SCENARIOS: list[Callable[[Registry], None]] = [
    register_query,
    release,
    shared_worktree,
    deadline,
]
