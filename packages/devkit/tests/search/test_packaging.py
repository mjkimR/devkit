"""The import cost of ``devkit.search``, the bundled model package and the model fetch script."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from devkit.search import DEFAULT_MODEL, SearchDocument, SearchIndex, SearchMode, load_embedder
from testsupport.search import write_safetensors

REPO = Path(__file__).resolve().parents[4]
PACKAGE = REPO / "packages/devkit-embed/src/devkit_embed"


def test_lexical_search_never_imports_the_dense_dependencies() -> None:
    probe = (
        "import sys\n"
        "from devkit.search import SearchDocument, SearchIndex, SearchMode\n"
        "assert SearchIndex([SearchDocument('a', 'replica')]).search('replica', mode=SearchMode.LEXICAL)\n"
        "print(sorted({'numpy', 'tokenizers'} & set(sys.modules)))\n"
    )
    result = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "[]"


def _fetch_script():
    spec = importlib.util.spec_from_file_location("fetch_model", REPO / "scripts/fetch_model.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_fetch_script_converts_to_aligned_float16_deterministically(tmp_path: Path) -> None:
    fetch = _fetch_script()
    matrix = np.array([[0.1, -2.5, 3.0], [65504.0, 1e-8, 0.333]], dtype=np.float32)
    write_safetensors(tmp_path / "source.safetensors", matrix, "F32")
    fetch.to_float16(tmp_path / "source.safetensors", tmp_path / "a.safetensors")
    fetch.to_float16(tmp_path / "source.safetensors", tmp_path / "b.safetensors")
    data = (tmp_path / "a.safetensors").read_bytes()
    assert data == (tmp_path / "b.safetensors").read_bytes()
    length = int.from_bytes(data[:8], "little")
    assert length % 8 == 0
    assert json.loads(data[8 : 8 + length]) == {
        "embeddings": {"dtype": "F16", "shape": [2, 3], "data_offsets": [0, 12]}
    }
    converted = np.frombuffer(data[8 + length :], dtype="<f2").reshape(2, 3)
    assert converted.tolist() == matrix.astype(np.float16).tolist()
    assert fetch.sha256(tmp_path / "a.safetensors") == hashlib.sha256(data).hexdigest()


def test_the_model_package_pins_its_source_and_outputs() -> None:
    spec = json.loads((PACKAGE / "model.json").read_text())
    assert spec["name"] == DEFAULT_MODEL and spec["max_tokens"] == 512
    assert len(spec["source"]["revision"]) == 40
    assert set(spec["files"]) == set(spec["source"]["files"]) == {"model.safetensors", "tokenizer.json"}
    assert spec["files"]["tokenizer.json"] == spec["source"]["files"]["tokenizer.json"]  # copied unchanged


@pytest.mark.skipif(not (PACKAGE / "model.safetensors").is_file(), reason="model files not fetched (just model-fetch)")
def test_the_default_model_is_installed_and_ranks_by_meaning() -> None:
    embedder = load_embedder()
    assert (embedder.name, embedder.dimensions, embedder.max_tokens) == (DEFAULT_MODEL, 256, 512)
    documents = [
        SearchDocument("secrets", "Secrets must not enter the repository: API keys, tokens and passwords"),
        SearchDocument("length", "File length warning for long source files"),
        SearchDocument("commits", "Conventions for git commit messages"),
    ]
    hits = SearchIndex(documents, embedder=embedder).search("leaked credentials", mode=SearchMode.DENSE)
    assert hits[0].id == "secrets"
