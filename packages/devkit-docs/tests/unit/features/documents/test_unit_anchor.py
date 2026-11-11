from __future__ import annotations

import pytest

from devkit_docs.base.layout import unnamespaced
from devkit_docs.features.documents import Document, Kind
from devkit_docs.features.documents.models.model import is_unit_anchor


def _anchor(path: str, kind: Kind = Kind.PROPOSAL, document_id: str = "PROP-x") -> bool:
    return is_unit_anchor(Document(id=document_id, path=path, kind=kind, frontmatter={}))


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("docs/proposals/PROP-x/proposal.md", True),
        ("docs/proposals/PROP-x.md", True),
        ("docs/packages/pkg/proposals/PROP-x/proposal.md", True),
        # A namespaced single-file proposal is not a unit anchor, as before the grammar was consolidated.
        ("docs/packages/pkg/proposals/PROP-x.md", False),
        ("docs/packages/pkg/proposals/PROP-x/target-docs.md", False),
        ("docs/packages/pkg/proposals/PROP-x/feedback/proposal.md", False),
        ("docs/packages/pkg/proposals/x/proposal.md", False),
        ("docs/packages/pkg/proposals/PROP-x/a/proposal.md", False),
    ],
)
def test_proposal_anchors_under_global_and_namespaced_roots(path: str, expected: bool) -> None:
    assert _anchor(path) is expected


def test_spec_anchor_stays_under_global_specs() -> None:
    assert _anchor("specs/2026-10/a/spec.md", Kind.SPEC, "SPEC-a")
    assert not _anchor("docs/packages/pkg/specs/2026-10/a/spec.md", Kind.SPEC, "SPEC-a")


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("docs/packages/pkg/proposals/PROP-x/proposal.md", "docs/proposals/PROP-x/proposal.md"),
        ("docs/packages/pkg/capabilities/CAP-A-x.md", "docs/capabilities/CAP-A-x.md"),
        ("docs/packages/pkg/x.md", "docs/x.md"),
        ("docs/packages/pkg", "docs/packages/pkg"),
        ("docs/proposals/PROP-x/proposal.md", "docs/proposals/PROP-x/proposal.md"),
        ("packages/pkg/proposals/PROP-x/proposal.md", "packages/pkg/proposals/PROP-x/proposal.md"),
    ],
)
def test_unnamespaced_maps_a_namespace_docs_root_to_docs(path: str, expected: str) -> None:
    assert unnamespaced(path) == expected
