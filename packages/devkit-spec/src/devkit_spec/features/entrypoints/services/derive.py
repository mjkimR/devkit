"""Derivation: join a bundle's ``_Boundary`` code paths with its reconciled capability and use case documents.

Document side: each ``reconcile.md`` target that is not ``waived`` and is entrypoint-bearing (``paths``), once.
Code side: each ``_Boundary`` entry that is a literal path outside ``docs/`` and ``specs/``, once per bundle; one
under another candidate of the same bundle is folded into the shortest such ancestor. Every (document, code) pair
is reported with ``state`` (``declared`` when an equal or ancestor entrypoint exists, else ``new``) and ``exists``
(the path is in the working tree). What is not turned into a pair is ``Skipped`` with a reason. A pair is a
mechanical join of declarations, not proof that the code implements the document.
"""

from __future__ import annotations

import posixpath
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from devkit_spec.base.errors import EntrypointsPathError
from devkit_spec.features.documents import Document
from devkit_spec.features.entrypoints.models.derive import Pair, Reason, SkipKind, Skipped, State
from devkit_spec.features.entrypoints.repositories.bundle import Bundle
from devkit_spec.features.entrypoints.services.paths import ROOT, covers, entrypoint_bearing, exists, normalize

NOT_APPLICABLE = ("n/a", "none")
EXCLUDED_TREES = ("docs", "specs")
FEEDBACK = "feedback"


@dataclass(frozen=True)
class _Doc:
    id: str
    path: str
    entrypoints: tuple[str, ...]


@dataclass
class _Candidate:
    path: str
    task: int
    folded: str | None = None


def declared_entrypoints(document: Document) -> tuple[str, ...]:
    """The string values of a document's ``entrypoints`` (none when the field is absent or not a list)."""
    value = document.frontmatter.get("entrypoints")
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def classify_boundary(raw: str) -> tuple[str | None, Reason | None]:
    """The normalized code path of one ``_Boundary`` entry, or why it is skipped."""
    value = raw.strip()
    if not value or value.lower() in NOT_APPLICABLE:
        return None, Reason.NOT_A_PATH
    try:
        code = normalize(value)
    except EntrypointsPathError:
        return None, Reason.INVALID_PATH
    if code == ROOT or code in EXCLUDED_TREES or code.startswith(tuple(f"{tree}/" for tree in EXCLUDED_TREES)):
        return None, Reason.EXCLUDED_TREE
    return code, None


def feedback_file(code: str) -> bool:
    """Whether the normalized ``code`` names a spec bundle's feedback file, ``specs/**/feedback/<name>.md``.

    Such a path stays ``excluded-tree`` here, because a feedback file is never a code entrypoint; scope collection
    alone takes an exactly declared one of another bundle as a file scope (``CAP-COLL-work-scope-registry``).
    """
    parts = code.split("/")
    return len(parts) >= 4 and parts[0] == "specs" and parts[-2] == FEEDBACK and parts[-1].endswith(".md")


def derive(root: Path, bundle: Bundle, documents: Mapping[str, Document]) -> tuple[list[Pair], list[Skipped]]:
    """The pairs of one bundle and what was skipped; ``documents`` maps workspace-relative paths to the index's
    documents."""
    skipped: list[Skipped] = []
    docs: list[_Doc] = []
    seen_docs: set[str] = set()
    for target in bundle.targets:
        written = target.file.strip()
        if not written:
            continue
        file = posixpath.normpath(written)

        def skip(reason: Reason, value: str = written) -> None:
            skipped.append(Skipped(SkipKind.TARGET, value, reason, spec=bundle.spec_id))

        if target.resolution.strip().lower() == "waived":
            skip(Reason.WAIVED)
        elif not entrypoint_bearing(file):
            skip(Reason.NOT_ENTRYPOINT_BEARING)
        elif file in seen_docs:
            continue
        elif file in documents:
            seen_docs.add(file)
            document = documents[file]
            docs.append(_Doc(document.id, file, declared_entrypoints(document)))
        else:
            skip(Reason.NOT_A_DOCUMENT if (root / file).is_file() else Reason.MISSING_DOC)

    candidates: list[_Candidate] = []
    seen_code: set[str] = set()
    for task in bundle.tasks:
        for raw in task.values:
            code, reason = classify_boundary(raw)
            if code is None:
                skipped.append(Skipped(SkipKind.BOUNDARY, raw, reason or Reason.NOT_A_PATH, bundle.spec_id, task.index))
            elif code not in seen_code:
                seen_code.add(code)
                candidates.append(_Candidate(code, task.index))
    _fold(candidates)

    present = {candidate.path: exists(root, candidate.path) for candidate in candidates}
    pairs = [
        Pair(
            doc=doc.id,
            doc_path=doc.path,
            code=candidate.path,
            state=state_for(doc.entrypoints, candidate.path),
            exists=present[candidate.path],
            spec=bundle.spec_id,
            task=candidate.task,
            folded_into=candidate.folded,
        )
        for doc in docs
        for candidate in candidates
    ]
    return sort_pairs(pairs), skipped


def _fold(candidates: list[_Candidate]) -> None:
    for candidate in candidates:
        for other in candidates:
            if (
                other.path != candidate.path
                and candidate.path.startswith(f"{other.path}/")
                and (candidate.folded is None or len(other.path) < len(candidate.folded))
            ):
                candidate.folded = other.path


def state_for(existing: Iterable[str], code: str) -> State:
    """``declared`` when an existing entrypoint equals ``code`` or is a directory containing it."""
    for entry in existing:
        try:
            declared = normalize(entry)
        except EntrypointsPathError:
            continue
        if covers(declared, code):
            return State.DECLARED
    return State.NEW


def sort_pairs(pairs: Iterable[Pair]) -> list[Pair]:
    return sorted(pairs, key=lambda pair: (pair.doc_path, pair.code))


def aggregate(per_bundle: Iterable[Sequence[Pair]], min_count: int) -> list[Pair]:
    """Merge per-bundle pairs by (document, code): folded pairs are left out, and pairs seen in fewer than
    ``min_count`` distinct specs are dropped."""
    merged: dict[tuple[str, str], Pair] = {}
    specs: dict[tuple[str, str], set[str]] = {}
    for pairs in per_bundle:
        for pair in pairs:
            if pair.folded_into is not None:
                continue
            key = (pair.doc_path, pair.code)
            if key not in merged:
                merged[key] = pair
                specs[key] = set()
            if pair.spec:
                specs[key].add(pair.spec)
    out = [
        replace(pair, spec=None, task=None, folded_into=None, count=len(specs[key]), specs=tuple(sorted(specs[key])))
        for key, pair in merged.items()
        if len(specs[key]) >= min_count
    ]
    return sort_pairs(out)


def _normalize_all(paths: Iterable[str]) -> list[str]:
    return [normalize(path) for path in paths]


def select(pairs: Sequence[Pair], includes: Sequence[str]) -> list[Pair]:
    """The pairs whose code path equals or lies under one of ``includes`` (all pairs when it is empty).

    Raises ``EntrypointsPathError`` for an invalid path.
    """
    wanted = _normalize_all(includes)
    if not wanted:
        return list(pairs)
    return [pair for pair in pairs if any(covers(path, pair.code) for path in wanted)]


def fold_by_directory_selectors(
    root: Path,
    pairs: Sequence[Pair],
    codes: Sequence[str],
    documents: Mapping[str, Document],
) -> list[Pair]:
    """When a code selector ends with '/', synthesize that directory as a candidate pair for documents
    having covered pairs, and fold those descendant pairs into it.

    Raises ``EntrypointsPathError`` if a trailing-slash code is not an existing directory in ``root``.
    """
    dir_codes: list[str] = []
    for code in codes:
        if code.endswith("/"):
            norm = normalize(code)
            if not (root / norm).is_dir():
                raise EntrypointsPathError(
                    f"invalid entrypoint {code!r}: not an existing directory",
                    target_files=[code],
                )
            if norm not in dir_codes:
                dir_codes.append(norm)

    if not dir_codes:
        return list(pairs)

    by_doc: dict[str, list[Pair]] = {}
    for pair in pairs:
        by_doc.setdefault(pair.doc_path, []).append(pair)

    out: list[Pair] = []
    for doc_path, doc_pairs in by_doc.items():
        doc_pairs_dict: dict[str, Pair] = {p.code: p for p in doc_pairs}
        doc_obj = documents.get(doc_path)
        declared = declared_entrypoints(doc_obj) if doc_obj else ()

        for dir_norm in dir_codes:
            covered = [p for p in doc_pairs_dict.values() if covers(dir_norm, p.code)]
            if not covered:
                continue

            if dir_norm in doc_pairs_dict:
                existing_dir_pair = doc_pairs_dict[dir_norm]
                if existing_dir_pair.folded_into is not None:
                    doc_pairs_dict[dir_norm] = replace(existing_dir_pair, folded_into=None)
            else:
                first = covered[0]
                if first.count is not None or first.specs is not None:
                    all_specs = tuple(sorted(set(s for p in covered if p.specs for s in p.specs)))
                    dir_pair = Pair(
                        doc=first.doc,
                        doc_path=doc_path,
                        code=dir_norm,
                        state=state_for(declared, dir_norm),
                        exists=True,
                        count=len(all_specs),
                        specs=all_specs,
                        folded_into=None,
                    )
                else:
                    dir_pair = Pair(
                        doc=first.doc,
                        doc_path=doc_path,
                        code=dir_norm,
                        state=state_for(declared, dir_norm),
                        exists=True,
                        spec=first.spec,
                        task=first.task,
                        folded_into=None,
                    )
                doc_pairs_dict[dir_norm] = dir_pair

            for p in covered:
                if p.code != dir_norm:
                    doc_pairs_dict[p.code] = replace(doc_pairs_dict[p.code], folded_into=dir_norm)

        out.extend(doc_pairs_dict.values())

    return sort_pairs(out)


def exclude(pairs: Sequence[Pair], excludes: Sequence[str]) -> tuple[list[Pair], list[Skipped]]:
    """Drop the pairs whose code path equals or lies under one of ``excludes``, each reported as skipped.

    Raises ``EntrypointsPathError`` for an invalid path.
    """
    dropped = _normalize_all(excludes)
    kept: list[Pair] = []
    skipped: list[Skipped] = []
    for pair in pairs:
        if any(covers(path, pair.code) for path in dropped):
            skipped.append(Skipped(SkipKind.BOUNDARY, pair.code, Reason.EXCLUDED, pair.spec, pair.task))
        else:
            kept.append(pair)
    return kept, skipped
