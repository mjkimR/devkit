"""Search query mode, indexed documents and ranked results."""

import dataclasses
from enum import StrEnum
from typing import Any


class SearchMode(StrEnum):
    AUTO = "auto"  # hybrid when the search extra is installed, else lexical
    LEXICAL = "lexical"  # BM25 over metadata and body; standard library only
    DENSE = "dense"  # cosine similarity of metadata embeddings; needs the search extra
    HYBRID = "hybrid"  # Reciprocal Rank Fusion of the lexical and dense rankings; needs the search extra


@dataclasses.dataclass(frozen=True)
class SearchDocument:
    id: str
    metadata: str
    body: str = ""


@dataclasses.dataclass(frozen=True)
class SearchHit:
    id: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)
