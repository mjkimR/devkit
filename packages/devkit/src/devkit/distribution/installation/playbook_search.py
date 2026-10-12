"""``devkit playbook search``: BM25 over synchronized playbook metadata; never returns procedure bodies."""

from __future__ import annotations

import dataclasses
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from devkit.core.errors import ArgumentError, ReceiptError
from devkit.core.receipt import MANAGED_PATH, RECEIPT_PATH
from devkit.distribution.bundles.playbooks import is_latin_text, read_playbook_header
from devkit.distribution.installation.config import (
    DEFAULT_PLAYBOOK_LIMIT,
    DEFAULT_PLAYBOOK_MAX_BYTES,
    DEFAULT_PLAYBOOK_MIN_SCORE,
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

MAX_QUERY_BYTES = 512


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.findall(r"[a-z0-9]+", normalized)


def bm25_scores(documents: list[str], query: str) -> list[float]:
    """BM25 with positive IDF, k1=1.5, b=0.75 and unique query terms."""
    terms = sorted(set(tokenize(query)))
    frequencies = [Counter(tokenize(document)) for document in documents]
    lengths = [sum(frequency.values()) for frequency in frequencies]
    average = sum(lengths) / len(lengths) if lengths else 0
    if not average:
        return [0.0] * len(documents)
    idf = {
        term: math.log1p((len(documents) - count + 0.5) / (count + 0.5))
        for term in terms
        for count in [sum(term in frequency for frequency in frequencies)]
    }
    return [
        sum(
            idf[term] * frequency[term] * 2.5 / (frequency[term] + 1.5 * (0.25 + 0.75 * length / average))
            for term in terms
            if frequency[term]
        )
        for frequency, length in zip(frequencies, lengths, strict=True)
    ]


def _encoded_size(result: SearchResult) -> int:
    """Bytes of ``result`` as the CLI prints it (indented JSON plus the final newline)."""
    return len(json.dumps(result.to_dict(), indent=2, ensure_ascii=False).encode()) + 1


def _bounds(root: Path, limit: int | None, min_score: float | None, max_bytes: int | None) -> tuple[int, float, int]:
    """The effective bounds: each argument, else ``[playbooks]`` of the configuration, else the default."""
    config = read_playbook_config(root)
    limit = limit if limit is not None else int(config.get("limit", DEFAULT_PLAYBOOK_LIMIT))
    min_score = min_score if min_score is not None else float(config.get("min_score", DEFAULT_PLAYBOOK_MIN_SCORE))
    max_bytes = max_bytes if max_bytes is not None else int(config.get("max_bytes", DEFAULT_PLAYBOOK_MAX_BYTES))
    if not PLAYBOOK_LIMIT_MIN <= limit <= PLAYBOOK_LIMIT_MAX:
        raise ArgumentError(
            f"--limit {limit}: expected {PLAYBOOK_LIMIT_MIN}..{PLAYBOOK_LIMIT_MAX}", target_files=["--limit"]
        )
    if not math.isfinite(min_score) or min_score < 0:
        raise ArgumentError(
            f"--min-score {min_score}: expected a finite nonnegative number", target_files=["--min-score"]
        )
    if not PLAYBOOK_MAX_BYTES_MIN <= max_bytes <= PLAYBOOK_MAX_BYTES_MAX:
        raise ArgumentError(
            f"--max-bytes {max_bytes}: expected {PLAYBOOK_MAX_BYTES_MIN}..{PLAYBOOK_MAX_BYTES_MAX}",
            target_files=["--max-bytes"],
        )
    return limit, min_score, max_bytes


def search_playbooks(
    start: Path,
    query: str,
    *,
    limit: int | None = None,
    min_score: float | None = None,
    max_bytes: int | None = None,
) -> SearchResult:
    """Rank the synchronized playbooks of the project containing ``start`` against an English ``query``.

    Unset bounds come from ``[playbooks]`` in ``.devkit/config.toml``, else the defaults.
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
    limit, min_score, max_bytes = _bounds(root, limit, min_score, max_bytes)
    if _encoded_size(SearchResult(query, [], False)) > max_bytes:
        raise ArgumentError(
            "search query exceeds the result output budget",
            target_files=["QUERY", "--max-bytes"],
            fix="Shorten the query or raise --max-bytes",
        )
    candidates: list[PlaybookCandidate] = []
    documents: list[str] = []
    with project_lock(root, shared=True):
        receipt = read_synchronized(root)
        for asset in receipt.assets("playbook"):
            # An overridden playbook is read from its override, never from the managed copy.
            allowed = (f"{MANAGED_PATH}/{asset.bundle}/", override_rel(asset.bundle, ""))
            for name in asset.entrypoints:
                if not name.startswith(allowed) or name not in asset.paths:
                    raise ReceiptError(f"{RECEIPT_PATH}: invalid playbook entrypoint: {name}")
                metadata = read_playbook_header(read_owned(root, receipt, name), name)
                documents.append(" ".join((metadata.name, metadata.description, *metadata.aliases)))
                candidates.append(
                    PlaybookCandidate(
                        asset.bundle,
                        asset.id,
                        metadata.name,
                        metadata.description,
                        list(metadata.aliases),
                        str(root / name),
                    )
                )
    ranked = [
        (score, candidate)
        for score, candidate in zip(bm25_scores(documents, query), candidates, strict=True)
        if score > 0 and score >= min_score
    ]
    ranked.sort(key=lambda pair: (-pair[0], pair[1].bundle, pair[1].id, pair[1].path))
    results: list[PlaybookCandidate] = []
    for score, candidate in ranked[:limit]:
        results.append(dataclasses.replace(candidate, score=round(score, 6)))
        if _encoded_size(SearchResult(query, results, len(results) < len(ranked))) > max_bytes:
            results.pop()
            break
    return SearchResult(query, results, len(results) < len(ranked))
