"""Every use case of this repository parses into numbered steps and keyed extensions (AC-08)."""

from __future__ import annotations

from pathlib import Path

from devkit_spec.features.documents import DocumentIndex, Kind
from devkit_spec.features.governance.services.ux import use_case

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "docs/usecases").is_dir())


def test_every_use_case_of_this_repository_parses() -> None:
    index = DocumentIndex.load(ROOT)
    usecases = [d for d in index.documents if d.kind is Kind.USECASE and d.path.startswith("docs/usecases/")]
    assert len(usecases) >= 10
    for document in usecases:
        parsed = use_case(index, document, (ROOT / document.path).read_text(encoding="utf-8"))
        keys = [step.key for step in parsed.main]
        assert keys == [str(n) for n in range(1, len(keys) + 1)] and keys, document.path
        assert any(step.extension for step in parsed.steps), document.path
        assert all(step.screens == () for step in parsed.steps), document.path
