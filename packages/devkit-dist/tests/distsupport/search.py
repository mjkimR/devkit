"""Search test helpers: tiny embedding models written the way a model package lays them out."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer, models, normalizers, pre_tokenizers


def write_safetensors(path: Path, matrix: np.ndarray, dtype: str = "F16") -> None:
    data = matrix.astype("<f2" if dtype == "F16" else "<f4").tobytes()
    header = json.dumps(
        {"embeddings": {"dtype": dtype, "shape": list(matrix.shape), "data_offsets": [0, len(data)]}}
    ).encode()
    path.write_bytes(len(header).to_bytes(8, "little") + header + data)


def write_model(
    directory: Path,
    vectors: Mapping[str, Sequence[float]],
    *,
    name: str = "tiny",
    max_tokens: int = 512,
    dtype: str = "F16",
) -> Path:
    """A model whose vocabulary is ``[UNK]`` (a zero row) followed by the words of ``vectors``, in order."""
    directory.mkdir(parents=True, exist_ok=True)
    words = ["[UNK]", *vectors]
    tokenizer = Tokenizer(models.WordPiece({word: index for index, word in enumerate(words)}, unk_token="[UNK]"))
    tokenizer.normalizer = normalizers.BertNormalizer(lowercase=True)
    tokenizer.pre_tokenizer = pre_tokenizers.BertPreTokenizer()
    tokenizer.save(str(directory / "tokenizer.json"))
    dimensions = len(next(iter(vectors.values())))
    matrix = np.array([[0.0] * dimensions, *vectors.values()], dtype=np.float32)
    write_safetensors(directory / "model.safetensors", matrix, dtype)
    (directory / "model.json").write_text(json.dumps({"name": name, "max_tokens": max_tokens}))
    return directory
