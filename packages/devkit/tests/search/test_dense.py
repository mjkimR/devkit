"""``devkit.search.dense``: loading a model package and encoding texts."""

from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path

import numpy as np
import pytest
from devkit.advisory import ActionMode
from devkit.search import (
    Embedder,
    ModelInvalidError,
    ModelNotFoundError,
    SearchExtraMissingError,
    load_embedder,
)
from testsupport.search import write_model, write_safetensors

VECTORS = {"replica": [1.0, 0.0], "restore": [0.0, 1.0], "release": [-1.0, 0.0]}


@pytest.mark.parametrize("dtype", ["F16", "F32"])
def test_a_text_is_the_unit_mean_of_its_known_token_rows(tmp_path: Path, dtype: str) -> None:
    embedder = Embedder.from_directory(write_model(tmp_path / "model", VECTORS, dtype=dtype))
    assert (embedder.name, embedder.dimensions, embedder.max_tokens) == ("tiny", 2, 512)
    vectors = embedder.encode(["Replica restore", "replica unknownword", "", "unknownword"])
    assert vectors.dtype == np.float32 and vectors.shape == (4, 2)
    assert vectors[0] == pytest.approx([2**-0.5, 2**-0.5], abs=1e-3)
    assert vectors[1] == pytest.approx([1.0, 0.0])  # the unknown token is left out, not averaged in
    assert vectors[2].tolist() == [0.0, 0.0] and vectors[3].tolist() == [0.0, 0.0]
    assert embedder.encode([]).shape == (0, 2)


def test_only_the_first_max_tokens_count(tmp_path: Path) -> None:
    embedder = Embedder.from_directory(write_model(tmp_path / "model", VECTORS, max_tokens=1))
    assert embedder.encode(["restore replica replica"])[0] == pytest.approx([0.0, 1.0])


def test_opposite_tokens_cancel_to_the_zero_vector(tmp_path: Path) -> None:
    embedder = Embedder.from_directory(write_model(tmp_path / "model", VECTORS))
    assert embedder.encode(["replica release"])[0].tolist() == [0.0, 0.0]


@pytest.mark.parametrize(
    ("damage", "message"),
    [
        (lambda d: (d / "model.json").unlink(), "model.json"),
        (lambda d: (d / "model.json").write_text('{"name": "x", "max_tokens": 0}'), "max_tokens"),
        (lambda d: (d / "tokenizer.json").write_text("{"), "model"),
        (lambda d: (d / "model.safetensors").write_bytes(b"\xff" * 8), "header length"),
        (lambda d: (d / "model.safetensors").write_bytes(b"\x02" + b"\x00" * 7 + b"{}"), "embeddings"),
        (lambda d: write_safetensors(d / "model.safetensors", np.zeros((2, 2))), "only 2 rows"),
    ],
)
def test_a_missing_or_malformed_file_is_model_invalid(tmp_path: Path, damage, message: str) -> None:
    directory = write_model(tmp_path / "model", VECTORS)
    damage(directory)
    with pytest.raises(ModelInvalidError, match=message) as raised:
        Embedder.from_directory(directory)
    assert raised.value.code == "SEARCH_MODEL_INVALID" and raised.value.mode is ActionMode.MAINTENANCE


def test_a_tensor_shorter_than_its_shape_is_model_invalid(tmp_path: Path) -> None:
    directory = write_model(tmp_path / "model", VECTORS)
    weights = directory / "model.safetensors"
    weights.write_bytes(weights.read_bytes()[:-2])
    with pytest.raises(ModelInvalidError, match="does not match its shape"):
        Embedder.from_directory(directory)


def test_without_the_extra_dense_search_asks_for_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    directory = write_model(tmp_path / "model", VECTORS)
    monkeypatch.setitem(sys.modules, "tokenizers", None)
    for call in (lambda: Embedder.from_directory(directory), load_embedder):
        with pytest.raises(SearchExtraMissingError) as raised:
            call()
        assert raised.value.code == "SEARCH_EXTRA_MISSING" and raised.value.mode is ActionMode.INTERACTION
        assert "devkit[search]" in (raised.value.fix or "")


def _register(monkeypatch: pytest.MonkeyPatch, *values: str) -> None:
    entries = [metadata.EntryPoint("tiny", value, "devkit.embedding_models") for value in values]

    def entry_points(*, group: str, name: str) -> list[metadata.EntryPoint]:
        return [entry for entry in entries if entry.group == group and entry.name == name]

    monkeypatch.setattr(metadata, "entry_points", entry_points)


def test_a_model_loads_from_the_package_its_entry_point_names(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    package = write_model(tmp_path / "tiny_model_pkg", VECTORS)
    (package / "__init__.py").write_text("")
    monkeypatch.syspath_prepend(str(tmp_path))
    _register(monkeypatch, "tiny_model_pkg")
    assert load_embedder("tiny").encode(["restore"])[0] == pytest.approx([0.0, 1.0])


def test_an_unregistered_or_ambiguous_model_name_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    _register(monkeypatch)
    with pytest.raises(ModelNotFoundError) as raised:
        load_embedder("tiny")
    assert raised.value.code == "SEARCH_MODEL_NOT_FOUND" and raised.value.mode is ActionMode.INTERACTION
    _register(monkeypatch, "one_pkg", "other_pkg")
    with pytest.raises(ModelInvalidError, match="several packages: one_pkg, other_pkg"):
        load_embedder("tiny")
    _register(monkeypatch, "no_such_model_pkg")
    with pytest.raises(ModelInvalidError, match="cannot import no_such_model_pkg"):
        load_embedder("tiny")
