"""The spec rules and the index read the kind table when they run: an injected row changes their result, and a
Living Spec kind the rules have no grammar for fails instead of borrowing another kind's."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest
from devkit_agt.features.rules import RulesRunError
from devkit_agt.features.rules.services.testing import check

from devkit_docs.features.documents import DocumentIndex, Kind, KindTableError
from devkit_docs.features.documents.models import kinds
from devkit_docs.features.documents.models.kinds import ROWS, Summary, validate
from devkit_docs.features.governance.usecases import id_convention
from devkit_docs.features.governance.usecases.code_entrypoints import CodeEntrypointsRule
from devkit_docs.features.governance.usecases.document_reference import DocumentReferenceRule
from devkit_docs.features.governance.usecases.document_summary import DocumentSummaryRule
from devkit_docs.features.governance.usecases.id_convention import IdConventionRule
from devkit_docs.features.governance.usecases.spec_format import SpecFormatRule


def _inject(monkeypatch: pytest.MonkeyPatch, **changes: dict[str, object]) -> None:
    """Replace the kind table with one whose row of each named kind (``Kind`` member name) has ``changes``."""
    rows = [replace(row, **changes.get(row.kind.name, {})) for row in ROWS]  # type: ignore[arg-type]
    monkeypatch.setattr(kinds, "_TABLE", validate(rows))


def _messages(rule, root: Path, files: dict[str, str]) -> list[tuple[str, str]]:
    return [(v.file, v.message) for v in check(rule, root, files)]


PLAN = {"specs/2026-10/20261001-unit/plan.md": "---\nid: PLAN-unit\nspec: SPEC-unit\n---\n# Plan\n"}


def test_the_summary_requirement_follows_the_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert _messages(DocumentSummaryRule(), tmp_path, PLAN) == []
    _inject(monkeypatch, PLAN={"summary": Summary.ALWAYS})
    assert _messages(DocumentSummaryRule(), tmp_path, {}) == [(next(iter(PLAN)), "PLAN-unit has no summary")]


def test_the_entrypoint_bearing_kinds_follow_the_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {
        "docs/architecture/ARCH-sample.md": (
            "---\nid: ARCH-sample\ntitle: A\nstatus: active\nentrypoints: [src/missing.py]\n---\n# [ARCH-sample] A\n"
        )
    }
    assert _messages(CodeEntrypointsRule(), tmp_path, files) == []
    _inject(monkeypatch, ARCHITECTURE={"entrypoints": True})
    assert _messages(CodeEntrypointsRule(), tmp_path, {}) == [
        ("docs/architecture/ARCH-sample.md", "Dead code entrypoint: 'src/missing.py' (missing or outside workspace)")
    ]


def test_the_relation_field_prefixes_follow_the_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {
        **PLAN,
        "specs/2026-10/20261001-unit/spec.md": "---\nid: SPEC-unit\nstatus: planned\n---\n# [SPEC-unit] U\n",
    }
    assert _messages(DocumentReferenceRule(), tmp_path, files) == []
    _inject(monkeypatch, SPEC={"relation_fields": ()}, PLAN={"relation_fields": ("plan", "spec")})
    assert _messages(DocumentReferenceRule(), tmp_path, {}) == [
        ("specs/2026-10/20261001-unit/plan.md", "spec takes PLAN- IDs, got SPEC-unit")
    ]


def test_the_default_status_follows_the_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _inject(monkeypatch, MILESTONE={"default_status": "active"})
    check(SpecFormatRule(), tmp_path, {"docs/roadmap/MS-next.md": "# [MS-next] Next\n"}, fix=True)
    assert (tmp_path / "docs/roadmap/MS-next.md").read_text(encoding="utf-8") == (
        f"---\nid: MS-next\ntitle: Next\nstatus: active\ncreated_at: {date.today().isoformat()}\n---\n\n"
        "# [MS-next] Next\n"
    )


def test_the_terminal_statuses_follow_the_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "docs/decisions/2026-10/20261001-choice.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nid: ADR-choice\nstatus: accepted\n---\n# [ADR-choice] Choice\n", encoding="utf-8")
    index = DocumentIndex.load(tmp_path)
    document = index.by_id["ADR-choice"][0]
    assert not index.is_terminal(document)
    _inject(monkeypatch, DECISION={"terminal_statuses": frozenset({"superseded", "accepted"})})
    assert index.is_terminal(document)


def test_the_area_check_follows_the_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {
        "docs/capabilities/core/CAP-CORE-x.md": (
            "---\nid: CAP-CORE-x\ntitle: X\nstatus: active\narea: other\n---\n# [CAP-CORE-x] X\n"
        )
    }
    assert _messages(IdConventionRule(), tmp_path, files) == [
        ("docs/capabilities/core/CAP-CORE-x.md", 'Frontmatter area is "other" but the directory requires "core"')
    ]
    _inject(monkeypatch, CAPABILITY={"area_scoped": False})
    assert _messages(IdConventionRule(), tmp_path, {}) == []


def test_every_living_spec_row_has_a_path_grammar() -> None:
    living = {row.kind for row in kinds.definitions() if row.living_spec}
    assert set(id_convention._LIVING_GRAMMARS) == living


def test_a_living_spec_kind_without_a_grammar_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {"docs/padrs/PADR-x.md": "---\nid: PADR-x\ntitle: X\nstatus: draft\n---\n# X\n"}
    assert _messages(IdConventionRule(), tmp_path, files) == []
    _inject(monkeypatch, PROPOSAL_DECISION={"living_spec": True, "directory": "padrs"})
    with pytest.raises(RulesRunError, match="Living Spec kind proposal-decision has no path grammar"):
        check(IdConventionRule(), tmp_path)
    with pytest.raises(KindTableError, match="Living Spec kind proposal-decision has no path grammar"):
        id_convention._living_spec("docs/padrs/PADR-x.md", Kind.PROPOSAL_DECISION, "docs", ())


def test_an_area_scoped_kind_whose_grammar_sets_no_area_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {
        "docs/architecture/ARCH-sample.md": "---\nid: ARCH-sample\ntitle: A\nstatus: active\n---\n# [ARCH-sample] A\n"
    }
    assert _messages(IdConventionRule(), tmp_path, files) == []
    _inject(monkeypatch, ARCHITECTURE={"area_scoped": True})
    with pytest.raises(RulesRunError, match="area-scoped kind architecture has a path grammar"):
        check(IdConventionRule(), tmp_path)


def test_every_identifier_target_kind_outside_the_living_spec_has_a_path_remediation() -> None:
    assert set(id_convention._PATH_REMEDIATIONS) == {Kind.DECISION, Kind.SPEC, Kind.FEEDBACK, Kind.MILESTONE}


def test_a_target_kind_without_a_path_remediation_fails() -> None:
    assert id_convention._path_remediation(Kind.MILESTONE).startswith("Rename or move the file to docs/roadmap/")
    with pytest.raises(KindTableError, match="kind material has no path remediation"):
        id_convention._path_remediation(Kind.MATERIAL)
