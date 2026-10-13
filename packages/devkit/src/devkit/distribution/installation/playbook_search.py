"""``devkit playbook search``: lexical, dense or hybrid search over synchronized playbook metadata.

Never returns procedure bodies. The ranking is ``devkit.search``'s over each
playbook's name, description and aliases; ``auto`` (the default) is hybrid when
the ``agt-devkit[search]`` extra is installed and lexical otherwise.
"""

from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

from devkit.core.errors import ArgumentError, ReceiptError
from devkit.core.receipt import MANAGED_PATH, RECEIPT_PATH
from devkit.distribution.bundles.playbooks import is_latin_text, read_playbook_header
from devkit.distribution.installation.config import (
    DEFAULT_PLAYBOOK_LIMIT,
    DEFAULT_PLAYBOOK_MAX_BYTES,
    DEFAULT_PLAYBOOK_MIN_SCORE,
    DEFAULT_PLAYBOOK_MIN_SIMILARITY,
    DEFAULT_PLAYBOOK_MODE,
    PLAYBOOK_LIMIT_MAX,
    PLAYBOOK_LIMIT_MIN,
    PLAYBOOK_MAX_BYTES_MAX,
    PLAYBOOK_MAX_BYTES_MIN,
    read_playbook_config,
)
from devkit.distribution.installation.overrides import override_rel
from devkit.distribution.installation.reading import read_owned, read_synchronized, synchronized_project_root
from devkit.distribution.installation.results import PlaybookCandidate, SearchResult
from devkit.distribution.installation.transaction import project_lock
from devkit.search import SearchDocument, SearchIndex, SearchMode, tokenize

MAX_QUERY_BYTES = 512


@dataclasses.dataclass(frozen=True)
class _Bounds:
    limit: int
    min_score: float
    min_similarity: float
    max_bytes: int
    mode: SearchMode


def _encoded_size(result: SearchResult) -> int:
    """Bytes of ``result`` as the CLI prints it (indented JSON plus the final newline)."""
    return len(json.dumps(result.to_dict(), indent=2, ensure_ascii=False).encode()) + 1


def _bounds(
    root: Path,
    limit: int | None,
    min_score: float | None,
    min_similarity: float | None,
    max_bytes: int | None,
    mode: str | None,
) -> _Bounds:
    """The effective bounds: each argument, else ``[playbooks]`` of the configuration, else the default."""
    config = read_playbook_config(root)
    limit = limit if limit is not None else int(config.get("limit", DEFAULT_PLAYBOOK_LIMIT))
    min_score = min_score if min_score is not None else float(config.get("min_score", DEFAULT_PLAYBOOK_MIN_SCORE))
    if min_similarity is None:
        min_similarity = float(config.get("min_similarity", DEFAULT_PLAYBOOK_MIN_SIMILARITY))
    max_bytes = max_bytes if max_bytes is not None else int(config.get("max_bytes", DEFAULT_PLAYBOOK_MAX_BYTES))
    mode = (mode if mode is not None else str(config.get("mode", DEFAULT_PLAYBOOK_MODE))).lower()
    if not PLAYBOOK_LIMIT_MIN <= limit <= PLAYBOOK_LIMIT_MAX:
        raise ArgumentError(
            f"--limit {limit}: expected {PLAYBOOK_LIMIT_MIN}..{PLAYBOOK_LIMIT_MAX}", target_files=["--limit"]
        )
    if not math.isfinite(min_score) or min_score < 0:
        raise ArgumentError(
            f"--min-score {min_score}: expected a finite nonnegative number", target_files=["--min-score"]
        )
    if not 0 <= min_similarity <= 1:
        raise ArgumentError(
            f"--min-similarity {min_similarity}: expected a number between 0 and 1", target_files=["--min-similarity"]
        )
    if not PLAYBOOK_MAX_BYTES_MIN <= max_bytes <= PLAYBOOK_MAX_BYTES_MAX:
        raise ArgumentError(
            f"--max-bytes {max_bytes}: expected {PLAYBOOK_MAX_BYTES_MIN}..{PLAYBOOK_MAX_BYTES_MAX}",
            target_files=["--max-bytes"],
        )
    modes = [item.value for item in SearchMode]
    if mode not in modes:
        raise ArgumentError(f"--mode {mode}: expected one of {', '.join(modes)}", target_files=["--mode"])
    return _Bounds(limit, min_score, min_similarity, max_bytes, SearchMode(mode))


def search_playbooks(
    start: Path,
    query: str,
    *,
    limit: int | None = None,
    min_score: float | None = None,
    min_similarity: float | None = None,
    max_bytes: int | None = None,
    mode: str | None = None,
) -> SearchResult:
    """Rank the synchronized playbooks of the project containing ``start`` against an English ``query``.

    Unset bounds and the mode come from ``[playbooks]`` in ``.devkit/config.toml``, else the defaults.
    ``min_score`` bounds the lexical (BM25) ranking and ``min_similarity`` the dense one; a hybrid
    candidate's ``score`` is its fused value. ``auto`` resolves to ``hybrid`` or ``lexical``, and the
    result reports the mode that ran. An explicit ``dense`` or ``hybrid`` without the ``agt-devkit[search]``
    extra raises ``SEARCH_EXTRA_MISSING``.
    """
    if not is_latin_text(query):
        raise ArgumentError(
            "search query: use English text (non-Latin letters are not supported)", target_files=["QUERY"]
        )
    if not tokenize(query) or len(query.encode()) > MAX_QUERY_BYTES:
        raise ArgumentError(
            f"search query must contain English search terms and fit within {MAX_QUERY_BYTES} bytes",
            target_files=["QUERY"],
        )
    root = synchronized_project_root(start)
    bounds = _bounds(root, limit, min_score, min_similarity, max_bytes, mode)
    # "lexical" is the longest mode name a result can report, so this holds whichever mode runs.
    if _encoded_size(SearchResult(query, SearchMode.LEXICAL, [], False)) > bounds.max_bytes:
        raise ArgumentError(
            "search query exceeds the result output budget",
            target_files=["QUERY", "--max-bytes"],
            fix="Shorten the query or raise --max-bytes",
        )
    candidates: list[tuple[PlaybookCandidate, str]] = []
    with project_lock(root, shared=True):
        receipt = read_synchronized(root)
        for asset in receipt.assets("playbook"):
            # An overridden playbook is read from its override, never from the managed copy.
            allowed = (f"{MANAGED_PATH}/{asset.bundle}/", override_rel(asset.bundle, ""))
            for name in asset.entrypoints:
                if not name.startswith(allowed) or name not in asset.paths:
                    raise ReceiptError(f"{RECEIPT_PATH}: invalid playbook entrypoint: {name}")
                metadata = read_playbook_header(read_owned(root, receipt, name), name)
                candidate = PlaybookCandidate(
                    asset.bundle,
                    asset.id,
                    metadata.name,
                    metadata.description,
                    list(metadata.aliases),
                    str(root / name),
                )
                candidates.append((candidate, " ".join((metadata.name, metadata.description, *metadata.aliases))))
    # Indexed in (bundle, id, path) order with fixed-width ids, so ties inside each ranking, and so the
    # fused scores of a hybrid search, follow the same order as ties in the final ranking.
    candidates.sort(key=lambda pair: (pair[0].bundle, pair[0].id, pair[0].path))
    documents = [SearchDocument(f"{number:06d}", text) for number, (_, text) in enumerate(candidates)]
    index = SearchIndex(documents)
    resolved = index.resolve_mode(bounds.mode) if documents else _without_documents(bounds.mode)
    hits = index.search(query, mode=resolved, min_score=bounds.min_score, min_similarity=bounds.min_similarity)
    ranked = [(hit.score, candidates[int(hit.id)][0]) for hit in hits]
    ranked.sort(key=lambda pair: (-pair[0], pair[1].bundle, pair[1].id, pair[1].path))
    results: list[PlaybookCandidate] = []
    for score, candidate in ranked[: bounds.limit]:
        results.append(dataclasses.replace(candidate, score=round(score, 6)))
        if _encoded_size(SearchResult(query, resolved, results, len(results) < len(ranked))) > bounds.max_bytes:
            results.pop()
            break
    return SearchResult(query, resolved, results, len(results) < len(ranked))


def _without_documents(mode: SearchMode) -> SearchMode:
    """With no playbook to rank, ``auto`` reports ``lexical`` without loading the model."""
    return SearchMode.LEXICAL if mode is SearchMode.AUTO else mode
