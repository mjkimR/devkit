from __future__ import annotations

import re
from pathlib import Path

from agent_advisory import ACTION_TEXT
from devkit_distribution.bundles import load_bundle

BUNDLE = Path(__file__).parents[1] / "src/agent_advisory/bundle"


def test_bundle_presets_split_core_and_python() -> None:
    bundle = load_bundle(BUNDLE)
    assert bundle.name == "agent-advisory"
    assert bundle.default_preset == "core"
    assert bundle.select(["core"]) == {"error-advisory"}
    assert bundle.select(["python"]) == {"error-advisory", "error-advisory-python"}


def test_guide_directives_match_runtime_texts() -> None:
    guide = (BUNDLE / "instructions/error-advisory.md").read_text()
    blocks = re.findall(r"```text\n(\w+ — .*?)```", guide, flags=re.DOTALL)
    rendered = {block.split(" — ", 1)[0]: " ".join(block.split()) for block in blocks}
    assert {mode.value: " ".join(text.split()) for mode, text in ACTION_TEXT.items()} == rendered
