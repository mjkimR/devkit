"""Derive and optionally apply document ownership from specification bundles."""

from __future__ import annotations

import posixpath
from collections.abc import Sequence
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase
from devkit_docs.base.errors import UnresolvedIdError
from devkit_docs.features.documents import Document, DocumentIndex, Kind, is_id
from devkit_docs.utils.paths import _bundle_dir

from devkit_spec.base.errors import (
    DEVKIT,
    EntrypointsApplyError,
    EntrypointsCodeUnmatchedError,
    EntrypointsInputInvalidError,
    EntrypointsInputMissingError,
    EntrypointsTargetError,
)
from devkit_spec.features.entrypoints import (
    Applied,
    adopt_nested_selectors,
    aggregate,
    apply,
    derive,
    exclude,
    fold_by_directory_selectors,
    load_bundle,
    select,
    unmatched_selectors,
)
from devkit_spec.features.entrypoints.models.derive import Pair, Reason, SkipKind, Skipped, State

DEFAULT_STATUS = "completed,in-progress"


def _check_options(
    spec_dir: str | None,
    every: bool,
    status: str | None,
    min_count: int | None,
    write: bool,
    targets: Sequence[str],
) -> None:
    if (spec_dir is None) == (not every):
        raise ArgumentError(
            "derive needs exactly one of --spec and --all",
            target_files=["--spec", "--all"],
            fix=f"Pass --spec with one spec bundle directory ({DEVKIT} docs list spec --history lists them) or --all",
        )
    if spec_dir is not None and (status is not None or min_count is not None):
        raise ArgumentError(
            "--status and --min-count apply to --all only",
            target_files=["--status", "--min-count"],
            fix="Drop --status and --min-count, or use --all instead of --spec",
        )
    if min_count is not None and min_count < 1:
        raise ArgumentError(
            f"--min-count {min_count}: must be at least 1",
            target_files=["--min-count"],
            fix="Pass --min-count 1 or more",
        )
    if targets and not write:
        raise ArgumentError("--target requires --apply", target_files=["--target"], fix="Add --apply or drop --target")


def _specs(index: DocumentIndex, status: str) -> list[Document]:
    """The ``spec.md`` of every bundle (``specs/<YYYY-MM>/<bundle>/spec.md``) whose status is in ``status``, by ID."""
    wanted = {part.strip().lower() for part in status.split(",") if part.strip()}
    found = [
        document
        for document in index.documents
        if document.kind is Kind.SPEC
        and len(parts := document.path.split("/")) == 4
        and parts[0] == "specs"
        and parts[3] == "spec.md"
        and (not wanted or document.status.lower() in wanted)
    ]
    return sorted(found, key=lambda document: (document.id, document.path))


def _resolve_targets(index: DocumentIndex, targets: Sequence[str], derived: set[str]) -> set[str] | None:
    """The document paths ``--target`` names (IDs or workspace-relative paths); ``None`` without targets."""
    if not targets:
        return None
    only: set[str] = set()
    for target in targets:
        value = target.strip()
        if is_id(value):
            try:
                path = index.resolve(value).path
            except UnresolvedIdError as exc:
                raise EntrypointsTargetError(
                    f"--target {value}: no document has this ID", target_files=[value]
                ) from exc
        else:
            path = posixpath.normpath(value)
        if path not in derived:
            raise EntrypointsTargetError(f"--target {value}: not among the derived documents", target_files=[path])
        only.add(path)
    return only


class DeriveEntrypointsUseCase(BaseUseCase):
    """DeriveEntrypoints execution boundary."""

    def execute(
        self,
        root: Path,
        spec_dir: str | None,
        status: str | None,
        min_count: int | None,
        write: bool,
        targets: tuple[str, ...],
        codes: tuple[str, ...],
        excludes: tuple[str, ...],
    ) -> tuple[list[Pair], list[Skipped], list[Applied], dict[str, int], list[AdvisoryError], Sequence[AdvisoryError]]:
        index = DocumentIndex.load(root)
        documents = {document.path: document for document in index.documents}
        skipped: list[Skipped] = []
        if spec_dir is not None:
            pairs, skipped = derive(root, load_bundle(root, _bundle_dir(root, spec_dir)), documents)
        else:
            per_bundle: list[list[Pair]] = []
            for spec in _specs(index, status or DEFAULT_STATUS):
                bundle_dir = spec.path.rsplit("/", 1)[0]
                try:
                    bundle = load_bundle(root, bundle_dir)
                except (EntrypointsInputMissingError, EntrypointsInputInvalidError) as exc:
                    reason = (
                        Reason.INPUT_MISSING if isinstance(exc, EntrypointsInputMissingError) else Reason.INVALID_INPUT
                    )
                    skipped.append(Skipped(SkipKind.BUNDLE, bundle_dir, reason, spec=spec.id))
                    continue
                bundle_pairs, bundle_skipped = derive(root, bundle, documents)
                per_bundle.append(bundle_pairs)
                skipped += bundle_skipped
            pairs = aggregate(per_bundle, 1 if min_count is None else min_count)

        pairs = fold_by_directory_selectors(root, pairs, codes, documents)
        pairs = adopt_nested_selectors(root, pairs, codes, documents)
        derived = {pair.doc_path for pair in pairs}
        only = _resolve_targets(index, targets, derived) if write else None
        pairs = select(pairs, codes)
        unmatched = unmatched_selectors(pairs, codes, only)
        if unmatched:
            raise EntrypointsCodeUnmatchedError(
                f"{len(unmatched)} --code path(s) match no candidate"
                + (" of the --target documents" if only is not None else ""),
                *(f"--code {code}" for code in unmatched),
                target_files=unmatched,
            )
        pairs, excluded = exclude(pairs, excludes)
        skipped += excluded
        applied: list[Applied] = []
        errors: list[AdvisoryError] = []
        if write:
            result = apply(root, pairs, only)
            applied, skipped = result.applied, skipped + result.skipped
            if result.failures:
                paths = [path for path, _ in result.failures]
                errors.append(
                    EntrypointsApplyError(
                        f"{len(paths)} document(s) could not be written",
                        *(f"{path}: {problem}" for path, problem in result.failures),
                        target_files=paths,
                    )
                )
        summary = {
            "pairs": len(pairs),
            "new": sum(pair.state is State.NEW and pair.exists and pair.folded_into is None for pair in pairs),
            "missing": sum(pair.state is State.NEW and not pair.exists and pair.folded_into is None for pair in pairs),
            "folded": sum(pair.state is State.NEW and pair.folded_into is not None for pair in pairs),
            "declared": sum(pair.state is State.DECLARED for pair in pairs),
            "skipped": len(skipped),
            "applied": len(applied),
        }
        return pairs, skipped, applied, summary, errors, index.problems
