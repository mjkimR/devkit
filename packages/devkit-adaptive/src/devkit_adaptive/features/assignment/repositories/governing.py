"""Resolve assignment constraints in the assignee's document index."""

from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_docs.features.documents.models.ids import is_id
from devkit_docs.features.documents.repositories.index import DocumentIndex

from devkit_adaptive.base.errors import GoverningUnresolved


def resolve(root: Path, values: list[str]) -> list[str]:
    if "none" in values:
        if values != ["none"]:
            raise ArgumentError("--governing none cannot accompany another value")
        return []
    index: DocumentIndex | None = None
    result: list[str] = []
    failures: list[str] = []
    for value in values:
        if is_id(value):
            if index is None:
                index = DocumentIndex.load(root)
            try:
                result.append(index.resolve(value).id)
            except AdvisoryError as exc:
                if exc.code not in {"DOCS_ID_UNRESOLVED", "DOCS_ID_DUPLICATE"}:
                    raise
                failures.append(f"{value}: {'duplicate-id' if exc.code == 'DOCS_ID_DUPLICATE' else 'unknown-id'}")
        else:
            path = (root / value).resolve()
            if not path.exists() or (not Path(value).is_absolute() and not path.is_relative_to(root)):
                failures.append(f"{value}: missing-path")
            else:
                result.append(path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path))
    if failures:
        raise GoverningUnresolved("governing documents could not be resolved", *failures)
    return result
