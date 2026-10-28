"""Every advisory code devkit-spec defines is documented under ``docs/``: agents branch on codes, people look them up."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = Path(__file__).resolve().parents[3] / "src"
CODE = re.compile(r"""\bcode\s*(?::\s*str\s*)?=\s*["']([A-Z][A-Z0-9_]+)["']""")


def test_every_code_is_documented() -> None:
    codes = {match.group(1) for path in SRC.rglob("*.py") for match in CODE.finditer(path.read_text())}
    assert "SPEC_CONFIG_INVALID" in codes  # the scan works
    documented = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "docs").rglob("*.md"))
    assert sorted(code for code in codes if f"`{code}`" not in documented) == []


def test_the_agent_invocation_matches_devkit_dist() -> None:
    """The package base repeats devkit_dist's agent-facing invocation (a base may not import a feature module)."""
    from devkit_dist.features.project.models.invocation import AGENT_INVOCATION

    from devkit_spec.base.errors import DEVKIT

    assert DEVKIT == AGENT_INVOCATION
