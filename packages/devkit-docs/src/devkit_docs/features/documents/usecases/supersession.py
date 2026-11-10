"""Read both directions of a decision's supersession without changing the reference graph."""

from collections.abc import Sequence
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_docs.features.documents import Document, DocumentIndex
from devkit_docs.features.documents.models.supersession import replacement_texts, supersedes_ids


class SupersessionDocumentsUseCase(BaseUseCase):
    def execute(
        self, root: Path, document_id: str
    ) -> tuple[str, list[dict[str, object]], list[dict[str, object]], Sequence[AdvisoryError]]:
        index = DocumentIndex.load(root)
        try:
            document = index.resolve(document_id)
            if not document.id.startswith(("ADR-", "PADR-")):
                raise ArgumentError(
                    "supersession requires an ADR or PADR ID",
                    target_files=[document_id],
                    fix="Pass an ADR or PADR ID or alias",
                )
        except AdvisoryError as exc:
            vars(exc)["notices"] = tuple(index.problems)
            raise

        def record(
            written: str, earlier: Document | None, later: Document | None, other: Document | None
        ) -> dict[str, object]:
            statement = (
                next(
                    (
                        item
                        for item in replacement_texts((root / later.path).read_text(encoding="utf-8"))
                        if not item.pointer and index.canonical_id(item.id) == (earlier.id if earlier else written)
                    ),
                    None,
                )
                if later
                else None
            )
            whole = (
                earlier is not None
                and later is not None
                and earlier.status == "superseded"
                and index.canonical_id(str(earlier.frontmatter.get("superseded_by", ""))) == later.id
            )
            return {
                "id": other.id if other else written,
                "path": other.path if other else None,
                "status": other.status if other else None,
                "scope": "whole" if whole else "partial",
                "line": statement.line if statement else None,
                "text": statement.text if statement else None,
            }

        outgoing = []
        for written in supersedes_ids(document.frontmatter.get("supersedes")):
            canonical = index.canonical(written)
            earlier = canonical[0] if canonical else None
            outgoing.append(record(written, earlier, document, earlier))
        incoming = [
            record(document.id, document, later, later)
            for later in index.documents
            if later.id.startswith("ADR-")
            and document.id
            in {index.canonical_id(item) for item in supersedes_ids(later.frontmatter.get("supersedes"))}
        ]
        return (
            document.id,
            sorted(outgoing, key=lambda x: str(x["id"])),
            sorted(incoming, key=lambda x: str(x["id"])),
            index.problems,
        )
