"""Validate repository milestone membership and decomposition sources before authoring writes."""

from pathlib import Path

from devkit_core.core import ArgumentError
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION as DEVKIT
from devkit_docs.features.documents import DocumentIndex, milestone_path_valid
from devkit_docs.features.documents.models.ids import Kind
from devkit_docs.features.documents.repositories.config import read_docs_config
from devkit_docs.features.documents.services.namespaces import living_path


def milestone_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    index = DocumentIndex.load(root)
    found = index.canonical(value)
    registered = read_docs_config(root).namespaces
    if (
        not value.startswith("MS-")
        or found is None
        or index.canonical(found[0].id) is None
        or found[0].kind is not Kind.MILESTONE
        or Path(found[0].path).stem != found[0].id
        or not milestone_path_valid(living_path(found[0].path, namespaces=registered), found[0].status)
    ):
        raise ArgumentError(
            f"--milestone {value!r} must name one existing milestone at the global or a namespace roadmap root",
            target_files=["--milestone"],
            fix=f"Pass an MS- ID shown by {DEVKIT} docs list milestone --all-namespaces, or omit --milestone",
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
            fix=f"Pass the PROP- ID of the draft being decomposed ({DEVKIT} docs list proposal lists them)",
        )
    return check_backlog_editable(root, value, decomposition=True).id
