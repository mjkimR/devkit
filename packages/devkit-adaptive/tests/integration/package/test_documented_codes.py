"""Every adaptive advisory code is documented in the Living Spec."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = Path(__file__).resolve().parents[3] / "src"


def test_every_code_is_documented():
    codes = {
        match.group(1)
        for path in SRC.rglob("*.py")
        for match in re.finditer(r'code\s*=\s*"(ADAPTIVE_[A-Z_]+)"', path.read_text())
    }
    assert "ADAPTIVE_SCOPE_OVERLAP" in codes
    documented = "\n".join(path.read_text() for path in (ROOT / "docs").rglob("*.md"))
    assert sorted(code for code in codes if f"`{code}`" not in documented) == []
