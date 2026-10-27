"""Validate repository milestone membership and decomposition sources before authoring writes."""

from pathlib import Path

from devkit_core.core import ArgumentError

from devkit_spec.features.documents import DocumentIndex
from devkit_spec.features.documents.models.ids import Kind


def milestone_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    index = DocumentIndex.load(root)
    found = index.canonical(value)
    if (
        not value.startswith("MS-")
        or found is None
        or found[0].kind is not Kind.MILESTONE
        or found[0].path != f"docs/roadmap/{found[0].id}.md"
    ):
        raise ArgumentError(
            f"--milestone {value!r} must name one existing global milestone",
            target_files=["--milestone"],
            fix="Pass an MS- ID shown by devkit spec list milestone, or omit --milestone",
        )
    return found[0].id


def decomposition_source(root: Path, value: str | None, slug: str) -> str | None:
    if value is None:
        return None
    from devkit_spec.features.proposals.usecases.backlog import check_backlog_editable
    from devkit_spec.features.proposals.usecases.scaffold import clean_slug

    value = value.strip()
    if not value.startswith("PROP-") or clean_slug(value) == slug:
        raise ArgumentError(
            "--decomposed-from must name another draft proposal",
            target_files=["--decomposed-from"],
            fix="Pass PROP-<source-slug> of the draft being decomposed",
        )
    return check_backlog_editable(root, value, decomposition=True).id
