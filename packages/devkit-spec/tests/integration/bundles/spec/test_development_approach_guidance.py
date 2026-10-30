"""SDD guidance names the non-SDD approach adaptive-dev and its entry /adaptive-dev (SPEC-rename-incubation-to-adaptive-dev AC-07)."""

from __future__ import annotations

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text

GUIDANCE = ("AGENTS.md", "guidance/spec-pointer.md", "skills/spec/SKILL.md", "playbooks/sdd-baseline/SKILL.md")


def test_constitution_routes_adaptive_dev_to_its_own_guidance() -> None:
    assert_rule(raw("AGENTS.md"), "Under `adaptive-dev`", "adaptive-dev guidance", "no implicit Unit")


def test_pointer_names_the_adaptive_dev_approach() -> None:
    assert_rule(raw("guidance/spec-pointer.md"), "For adaptive-dev", "without SDD records")


def test_spec_skill_routes_to_the_adaptive_dev_entry() -> None:
    assert_rule(raw("skills/spec/SKILL.md"), "under `adaptive-dev`", "the `/adaptive-dev` entry when selected")


@pytest.mark.parametrize("path", GUIDANCE)
def test_guidance_names_no_former_approach(path: str) -> None:
    assert "incubat" not in text(path).lower(), path
