"""A payload delegating a cross-feature choice settles the architecture declaration (SPEC-generated-conflicts-follow-ups, AC-05)."""

from __future__ import annotations

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw

PAYLOAD = "skills/spec-delegate/references/payload.md"


# AC-05
@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_a_delegated_cross_feature_choice_names_the_declaration_or_rules_out_a_new_edge(environment: str) -> None:
    assert_rule(
        raw(PAYLOAD, environment),
        "delegates a cross-feature design choice",
        "names in the write scope the architecture declaration",
        "limited to its feature edge entries",
        "states that a new feature edge is out of scope",
    )
