"""Every advisory code the devkit wheels (devkit-dist, devkit-agt, devkit-advisory) can report is documented under
``docs/``.

An agent branches on codes and a person looks them up, so a code that exists only in the source is a contract
nobody can read. Codes are found where they are defined: as a class attribute (``code = "X"``), a keyword
argument (``code="X"``) or a ``*_CODE`` constant. A rule's own ``tests/`` under the sources hold fixture codes only.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SOURCES = (
    REPO / "packages/devkit-core/src/devkit_core",
    REPO / "packages/devkit-dist/src/devkit",
    REPO / "packages/devkit/src/devkit",
    REPO / "packages/devkit-advisory/src/devkit",
)
DOCS = REPO / "docs"
CODE = re.compile(r"""(?:\bcode\s*(?::\s*str\s*)?=|\b[A-Z_]+_CODE\s*=)\s*["']([A-Z][A-Z0-9_]+)["']""")


def _defined_codes() -> dict[str, set[str]]:
    codes: dict[str, set[str]] = {}
    for source in SOURCES:
        for path in source.rglob("*.py"):
            if "tests" in path.relative_to(source).parts:
                continue
            for match in CODE.finditer(path.read_text(encoding="utf-8")):
                codes.setdefault(match.group(1), set()).add(str(path.relative_to(source)))
    return codes


def test_every_code_is_documented() -> None:
    codes = _defined_codes()
    assert {"ARGUMENT_INVALID", "GENERAL_ERROR", "UNEXPECTED_ERROR", "RUN_SLOW_COMMAND"} <= set(codes)  # the scan works
    documented = "\n".join(path.read_text(encoding="utf-8") for path in DOCS.rglob("*.md"))
    missing = {code: sorted(files) for code, files in codes.items() if f"`{code}`" not in documented}
    assert missing == {}, "document these codes in the module's reference under docs/"
