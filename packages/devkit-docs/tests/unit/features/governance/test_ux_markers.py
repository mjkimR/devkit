"""The coverage-exception markers of the shared UX model (`SPEC-ux-coverage-explicit-exceptions` AC-01, AC-03, AC-07)."""

from __future__ import annotations

from pathlib import Path

import pytest

from devkit_docs.features.documents import DocumentIndex
from devkit_docs.features.governance.services.ux import use_case, ux_document

HEADER = (
    "| Trigger | Step | From | To | Target | Capability | Feedback |\n| --- | --- | --- | --- | --- | --- | --- |\n"
)


def _index(tmp_path: Path, files: dict[str, str]) -> DocumentIndex:
    for path, text in files.items():
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return DocumentIndex.load(tmp_path)


def _ux(*cells: str) -> str:
    rows = "".join(f"| Press | {cell} | a | b | end | | Done |\n" for cell in cells)
    return (
        "---\nid: UX-nav\ntitle: Nav\nsummary: The nav.\narea: account\nelement: panel\nstatus: draft\n"
        f"usecases:\n  - UC-sign-in\n---\n# [UX-nav] Nav\n\n## 4. Interactions\n\n{HEADER}{rows}"
    )


def _uc(*steps: str) -> str:
    main = "".join(f"{n}. {text}\n" for n, text in enumerate(steps, start=1))
    return (
        "---\nid: UC-sign-in\ntitle: Sign in\nsummary: A person signs in.\narea: account\nstatus: active\n---\n"
        f"# [UC-sign-in] Sign in\n\n## 2. Main Success Scenario\n\n{main}"
    )


@pytest.mark.parametrize(
    ("cell", "reason", "valid"),
    [
        ("global: a preference control", "a preference control", True),
        ("GLOBAL: accessibility link", "accessibility link", True),
        ("global: independent of `UC-sign-in` 2", "independent of `UC-sign-in` 2", True),
        ("global:", "", True),
        ("-", None, True),
        ("`UC-sign-in` 1", None, True),
        ("`UC-sign-in` 1, global: also", None, False),
        ("globl: typo", None, False),
    ],
)
def test_global_cells(tmp_path: Path, cell: str, reason: str | None, valid: bool) -> None:
    path = "docs/ux/account/UX-nav.md"
    index = _index(tmp_path, {path: _ux(cell), "docs/usecases/account/UC-sign-in.md": _uc("Opens the page.")})
    document = next(d for d in index.documents if d.path == path)
    (row,) = ux_document(index, document, (tmp_path / path).read_text(encoding="utf-8")).rows
    assert (row.global_reason, row.step_valid) == (reason, valid)
    assert row.steps == () or not valid or reason is None


@pytest.mark.parametrize(
    ("step", "reason"),
    [
        ("Sends the mail. Off screen: the mail leaves by SMTP.", "the mail leaves by SMTP"),
        ("Retries (off-screen: the retry runs in the background).", "the retry runs in the background"),
        ("Ends. off screen:", ""),
        ("Sends the mail offscreen: typo.", None),
        ("Sends the mail.", None),
    ],
)
def test_off_screen_steps(tmp_path: Path, step: str, reason: str | None) -> None:
    path = "docs/usecases/account/UC-sign-in.md"
    index = _index(tmp_path, {path: _uc(step)})
    document = next(d for d in index.documents if d.path == path)
    (parsed,) = use_case(index, document, (tmp_path / path).read_text(encoding="utf-8")).steps
    assert parsed.off_screen == reason
