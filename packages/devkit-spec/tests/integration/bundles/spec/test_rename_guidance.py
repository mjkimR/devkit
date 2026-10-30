"""The ``spec-specify`` rename guidance: a rename spec keeps its old IDs as plain text, so ``devkit rules fix`` leaves
its mapping table intact (SPEC-alias-references-in-quick-references AC-07)."""

from __future__ import annotations

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw


def test_a_rename_spec_writes_the_old_ids_as_plain_text() -> None:
    specify = raw("skills/spec-specify/SKILL.md")
    assert_rule(specify, "rename spec", "old IDs as plain text", "mapping tables", "`devkit rules fix`", "alias")
