"""Literal write-scope authority between assignments."""

import pytest
from devkit_adaptive.base.errors import AuthorityNotNarrowed, ScopeOverlap
from devkit_adaptive.features.assignment.services.validation import authority


def _held(write, *, parent=None, commit=False):
    return {"a1": {"id": "a1", "status": "open", "parent": parent, "write": write, "commit": commit}}


@pytest.mark.parametrize(
    "mine,theirs,overlap",
    [
        ("src/a", "src", True),
        ("src", "src/a", True),
        ("src", "src", True),
        (".", "anything", True),
        ("src-other", "src", False),
        ("a:b", "a:b", True),
    ],
)
def test_overlapping_scope_is_refused_either_way(mine, theirs, overlap):
    if overlap:
        with pytest.raises(ScopeOverlap):
            authority(_held([theirs]), [mine], False, None, [])
    else:
        authority(_held([theirs]), [mine], False, None, [])


def test_child_scope_must_fit_the_parent():
    authority(_held(["src"]), ["src/a"], False, "a1", [])
    with pytest.raises(AuthorityNotNarrowed):
        authority(_held(["src"]), ["src-other"], False, "a1", [])
