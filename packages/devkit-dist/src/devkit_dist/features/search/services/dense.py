"""Dense embeddings from a static (Model2Vec) embedding model shipped as a Python package.

A model package registers its directory under the ``devkit.embedding_models``
entry-point group. The directory holds ``model.json`` (name, dimensions, token
limit), ``tokenizer.json`` (a Hugging Face tokenizer) and ``model.safetensors``
(one ``embeddings`` tensor of shape ``[vocabulary, dimensions]``, ``F16`` or
``F32``). A text's vector is the mean of the embedding rows of its first
``max_tokens`` tokens (unknown tokens left out), scaled to unit length; a text
without tokens gets the zero vector.

numpy and tokenizers come from the ``search`` extra and are imported
inside the functions here, so importing this module costs nothing until a
model is loaded.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from devkit_core.core.logs import get_logger

from devkit_dist.features.search.models.errors import ModelInvalidError, ModelNotFoundError, SearchExtraMissingError

if TYPE_CHECKING:
    import numpy as np
    from tokenizers import Tokenizer

logger = get_logger(__name__)

MODEL_GROUP = "devkit.embedding_models"
DEFAULT_MODEL = "potion-base-8m"
METADATA_FILE = "model.json"
TOKENIZER_FILE = "tokenizer.json"
WEIGHTS_FILE = "model.safetensors"
TENSOR = "embeddings"
_DTYPES = {"F16": ("float16", 2), "F32": ("float32", 4)}


def _require_extra() -> None:
    try:
        import numpy  # noqa: F401
        import tokenizers  # noqa: F401
    except ImportError as error:
        raise SearchExtraMissingError(f"dense search needs numpy and tokenizers: {error}") from error


class Embedder:
    """A loaded embedding model: ``encode`` turns texts into unit-length ``float32`` vectors."""

    def __init__(self, name: str, embeddings: np.ndarray, tokenizer: Tokenizer, max_tokens: int) -> None:
        self.name = name
        self.dimensions = int(embeddings.shape[1])
        self.max_tokens = max_tokens
        self._embeddings = embeddings
        self._tokenizer = tokenizer
        unknown = getattr(tokenizer.model, "unk_token", None)
        self._unknown = tokenizer.token_to_id(unknown) if isinstance(unknown, str) else None

    @classmethod
    def from_directory(cls, directory: Path) -> Embedder:
        """Load the model files in ``directory``; ``ModelInvalidError`` when one is missing or malformed."""
        _require_extra()
        from tokenizers import Tokenizer

        try:
            metadata = json.loads((directory / METADATA_FILE).read_text(encoding="utf-8"))
            name, max_tokens = metadata["name"], metadata["max_tokens"]
            if not isinstance(name, str) or not isinstance(max_tokens, int) or max_tokens < 1:
                raise ValueError(f"{METADATA_FILE}: name must be a string and max_tokens a positive integer")
            tokenizer = Tokenizer.from_file(str(directory / TOKENIZER_FILE))
            embeddings = _read_embeddings(directory / WEIGHTS_FILE)
        except Exception as error:  # tokenizers reports a malformed file as a plain Exception
            raise ModelInvalidError(
                f"embedding model in {directory}: {error}", target_files=[str(directory)]
            ) from error
        if tokenizer.get_vocab_size() > embeddings.shape[0]:
            raise ModelInvalidError(
                f"embedding model in {directory}: the tokenizer has {tokenizer.get_vocab_size()} tokens"
                f" but {WEIGHTS_FILE} only {embeddings.shape[0]} rows",
                target_files=[str(directory)],
            )
        tokenizer.no_truncation()
        tokenizer.no_padding()
        logger.info("loaded embedding model %s from %s", name, directory)
        return cls(name, embeddings, tokenizer, max_tokens)

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        """One row per text: the unit-length mean of its token embeddings, or zeros for a text without tokens."""
        import numpy as np

        vectors = np.zeros((len(texts), self.dimensions), dtype=np.float32)
        if not texts:
            return vectors
        for row, encoding in enumerate(self._tokenizer.encode_batch(list(texts), add_special_tokens=False)):
            ids = [token for token in encoding.ids if token != self._unknown][: self.max_tokens]
            if not ids:
                continue
            vector = self._embeddings[ids].astype(np.float32).mean(axis=0)
            norm = float(np.linalg.norm(vector))
            if norm > 0:
                vectors[row] = vector / norm
        return vectors


def _read_embeddings(path: Path) -> np.ndarray:
    """The ``embeddings`` tensor of a safetensors file, memory-mapped read-only."""
    import numpy as np

    size = path.stat().st_size
    with path.open("rb") as handle:
        length = int.from_bytes(handle.read(8), "little")
        if not 0 < length <= size - 8:
            raise ValueError(f"{path.name}: invalid safetensors header length {length}")
        header: dict[str, Any] = json.loads(handle.read(length))
    entry = header[TENSOR]
    dtype, width = _DTYPES[entry["dtype"]]
    rows, columns = entry["shape"]
    start, end = entry["data_offsets"]
    if end - start != rows * columns * width or 8 + length + end > size:
        raise ValueError(f"{path.name}: the {TENSOR} tensor does not match its shape {rows}x{columns}")
    return np.memmap(path, dtype=dtype, mode="r", offset=8 + length + start, shape=(rows, columns))


def load_embedder(name: str = DEFAULT_MODEL) -> Embedder:
    """The embedding model registered under ``name`` in the ``devkit.embedding_models`` entry-point group.

    The entry point names the model package (a module); its files sit next to the module's ``__init__``.
    """
    _require_extra()
    from importlib import metadata

    entries = {entry.value: entry for entry in metadata.entry_points(group=MODEL_GROUP, name=name)}
    if not entries:
        raise ModelNotFoundError(f"no installed package provides the embedding model {name!r}")
    if len(entries) > 1:
        raise ModelInvalidError(
            f"embedding model {name!r} is registered by several packages: {', '.join(sorted(entries))}"
        )
    [(target, entry)] = entries.items()
    try:
        module = entry.load()
    except ImportError as error:
        raise ModelInvalidError(f"embedding model {name!r}: cannot import {target}: {error}") from error
    location = getattr(module, "__file__", None)
    if not location:
        raise ModelInvalidError(f"embedding model {name!r}: {target} is not a regular package")
    return Embedder.from_directory(Path(location).parent)
