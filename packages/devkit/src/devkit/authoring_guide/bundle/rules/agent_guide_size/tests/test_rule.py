"""``RULE-agent-guide-size``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest

from devkit.core import GUIDANCE_END, GUIDANCE_START
from devkit.rules import RulesRunError
from devkit.rules.testing import check, load_rule

RULE = load_rule(__file__)

BLOCK = f"{GUIDANCE_START}\nManaged guidance.\n{GUIDANCE_END}\n"


def test_reports_guides_with_the_devkit_block_share(tmp_path: Path) -> None:
    guide = "# Project\n\n" + "x" * 8192 + "\n\n" + BLOCK
    files = {
        "AGENTS.md": guide,
        "packages/app/AGENTS.md": "x" * 9000,
        "tools/kit/src/kit/bundle/AGENTS.md": "x" * 9000,  # a bundle constitution
        "docs/AGENTS-notes.md": "x" * 9000,
    }
    (tmp_path / "CLAUDE.md").symlink_to("AGENTS.md")  # measured once, through its target
    found = check(RULE, tmp_path, files)
    assert [v.file for v in found] == ["AGENTS.md", "packages/app/AGENTS.md"]
    size, share = len(guide.encode()), len(BLOCK.encode()) - 1  # the block ends at its end marker
    assert found[0].message == (
        f"Guide has {size} bytes, including {share} bytes of the devkit guidance block; effective max_bytes is 8192"
    )
    assert found[1].message == "Guide has 9000 bytes; effective max_bytes is 8192"


def test_max_bytes_applies_per_path(tmp_path: Path) -> None:
    files = {"AGENTS.md": "x" * 600, "packages/app/AGENTS.md": "x" * 600}
    settings = {"max_bytes": 500, "overrides": [{"path": "packages/**", "max_bytes": 1000}]}
    assert [v.file for v in check(RULE, tmp_path, files, settings=settings)] == ["AGENTS.md"]


def test_max_bytes_must_be_positive(tmp_path: Path) -> None:
    with pytest.raises(RulesRunError, match="max_bytes must be a positive integer"):
        check(RULE, tmp_path, settings={"max_bytes": 0})


def test_follows_changed_file_targets(tmp_path: Path) -> None:
    files = {"AGENTS.md": "x" * 9000, "packages/app/AGENTS.md": "x" * 9000}
    found = check(RULE, tmp_path, files, targets=["packages/app/AGENTS.md"])
    assert [v.file for v in found] == ["packages/app/AGENTS.md"]
