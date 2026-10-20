"""Validate repository milestone membership and decomposition sources before authoring writes."""

from pathlib import Path

from devkit.core import ArgumentError

from devkit_spec.documents import DocumentIndex
from devkit_spec.documents.ids import Kind


def milestone_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    index = DocumentIndex.load(root)
    matches = index.by_id.get(value, [])
    if (
        not value.startswith("MS-")
        or len(matches) != 1
        or matches[0].kind is not Kind.MILESTONE
        or matches[0].path != f"docs/roadmap/{value}.md"
    ):
        raise ArgumentError(
            f"--milestone {value!r} must name one existing global milestone",
            target_files=["--milestone"],
            fix="Pass an MS- ID shown by devkit spec list milestone, or omit --milestone",
        )
    return value


def decomposition_source(root: Path, value: str | None, slug: str) -> str | None:
    if value is None:
        return None
    from devkit_spec.proposals.backlog import check_backlog_editable

    value = value.strip()
    if not value.startswith("PROP-") or value == f"PROP-{slug}":
        raise ArgumentError(
            "--decomposed-from must name another draft proposal",
            target_files=["--decomposed-from"],
            fix="Pass PROP-<source-slug> of the draft being decomposed",
        )
    check_backlog_editable(root, value, decomposition=True)
    return value
