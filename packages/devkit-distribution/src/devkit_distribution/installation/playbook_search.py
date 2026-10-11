from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.playbooks import read_playbook_header, require_english_text

from .reading import read_owned, synchronized_root
from .sync import read_receipt
from .transaction import JOURNAL, project_lock, snapshot


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
    start: Path, query: str, *, limit: int = 5, min_score: float = 0.1, max_bytes: int = 8192
) -> dict[str, object]:
    require_english_text(query, "search query")
    if not tokenize(query) or len(query.encode()) > 512:
        raise BundleError("search query must contain English search terms and fit within 512 bytes")
    if not 1 <= limit <= 20 or not math.isfinite(min_score) or min_score < 0 or not 1024 <= max_bytes <= 65536:
        raise BundleError("invalid search bounds: limit 1..20, finite nonnegative min-score, max-bytes 1024..65536")
    empty = {"query": query, "results": [], "truncated": False}
    if len(json.dumps(empty, indent=2, ensure_ascii=False).encode()) + 1 > max_bytes:
        raise BundleError("search query exceeds the result output budget")
    root = synchronized_root(start)
    candidates: list[dict[str, object]] = []
    documents: list[str] = []
    with project_lock(root):
        if snapshot(root, JOURNAL) is not None:
            raise BundleError("pending transaction; run devkit recover first")
        receipt = read_receipt(root)
        for asset in receipt["assets"]:
            if asset["kind"] != "playbook":
                continue
            if "entrypoints" not in asset:
                raise BundleError("playbook search metadata is outdated; run devkit sync first")
            prefix = f".devkit/managed/{asset['bundle']}/"
            for name in asset["entrypoints"]:
                if not name.startswith(prefix) or name not in asset["paths"]:
                    raise BundleError("invalid playbook entrypoint in receipt")
                metadata = read_playbook_header(read_owned(root, receipt, name), name)
                documents.append(" ".join((metadata.name, metadata.description, *metadata.aliases)))
                candidates.append(
                    {
                        "bundle": asset["bundle"],
                        "id": asset["id"],
                        "name": metadata.name,
                        "description": metadata.description,
                        "aliases": list(metadata.aliases),
                        "path": str(root / name),
                    }
                )
    ranked = [
        (score, candidate)
        for score, candidate in zip(bm25_scores(documents, query), candidates, strict=True)
        if score > 0 and score >= min_score
    ]
    ranked.sort(key=lambda pair: (-pair[0], str(pair[1]["bundle"]), str(pair[1]["id"]), str(pair[1]["path"])))
    results: list[dict[str, object]] = []
    response: dict[str, object] = {"query": query, "results": results, "truncated": bool(ranked)}
    for score, candidate in ranked[:limit]:
        result = {**candidate, "score": round(score, 6)}
        results.append(result)
        response["truncated"] = len(results) < len(ranked)
        if len(json.dumps(response, indent=2, ensure_ascii=False).encode()) + 1 > max_bytes:
            results.pop()
            break
    response["truncated"] = len(results) < len(ranked)
    return response
