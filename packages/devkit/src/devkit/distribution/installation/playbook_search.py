from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from ..bundles.common import BundleError
from ..bundles.playbooks import read_playbook_header, require_english_text
from .config import read_playbook_config
from .overrides import override_rel
from .reading import read_owned, read_synchronized, synchronized_root
from .results import PlaybookCandidate, SearchResult
from .transaction import project_lock
from .workspace import MANAGED


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


def search_playbooks(
    start: Path,
    query: str,
    *,
    limit: int | None = None,
    min_score: float | None = None,
    max_bytes: int | None = None,
) -> SearchResult:
    require_english_text(query, "search query")
    if not tokenize(query) or len(query.encode()) > 512:
        raise BundleError("search query must contain English search terms and fit within 512 bytes")
    root = synchronized_root(start)
    cfg = read_playbook_config(root)
    eff_limit = limit if limit is not None else int(cfg.get("limit", 5))
    eff_min_score = min_score if min_score is not None else float(cfg.get("min_score", 0.1))
    eff_max_bytes = max_bytes if max_bytes is not None else int(cfg.get("max_bytes", 8192))
    if (
        not 1 <= eff_limit <= 20
        or not math.isfinite(eff_min_score)
        or eff_min_score < 0
        or not 1024 <= eff_max_bytes <= 65536
    ):
        raise BundleError("invalid search bounds: limit 1..20, finite nonnegative min-score, max-bytes 1024..65536")
    empty: SearchResult = {"query": query, "results": [], "truncated": False}
    if len(json.dumps(empty, indent=2, ensure_ascii=False).encode()) + 1 > eff_max_bytes:
        raise BundleError("search query exceeds the result output budget")
    candidates: list[PlaybookCandidate] = []
    documents: list[str] = []
    with project_lock(root, shared=True):
        receipt = read_synchronized(root)
        for asset in receipt.assets("playbook"):
            # An overridden playbook is read from its override, never from the managed copy.
            allowed = (f"{MANAGED}/{asset.bundle}/", override_rel(asset.bundle, ""))
            for name in asset.entrypoints:
                if not name.startswith(allowed) or name not in asset.paths:
                    raise BundleError(f"invalid playbook entrypoint in receipt: {name}")
                metadata = read_playbook_header(read_owned(root, receipt, name), name)
                documents.append(" ".join((metadata.name, metadata.description, *metadata.aliases)))
                candidates.append(
                    {
                        "bundle": asset.bundle,
                        "id": asset.id,
                        "name": metadata.name,
                        "description": metadata.description,
                        "aliases": list(metadata.aliases),
                        "path": str(root / name),
                    }
                )
    ranked = [
        (score, candidate)
        for score, candidate in zip(bm25_scores(documents, query), candidates, strict=True)
        if score > 0 and score >= eff_min_score
    ]
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["bundle"], pair[1]["id"], pair[1]["path"]))
    results: list[PlaybookCandidate] = []
    response: SearchResult = {"query": query, "results": results, "truncated": bool(ranked)}
    for score, candidate in ranked[:eff_limit]:
        result: PlaybookCandidate = {**candidate, "score": round(score, 6)}
        results.append(result)
        response["truncated"] = len(results) < len(ranked)
        if len(json.dumps(response, indent=2, ensure_ascii=False).encode()) + 1 > eff_max_bytes:
            results.pop()
            break
    response["truncated"] = len(results) < len(ranked)
    return response
