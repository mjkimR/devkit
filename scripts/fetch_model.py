"""Fetch an embedding model package's weights and tokenizer, verified and converted to float16.

Usage: fetch_model.py <package data directory>

The directory's model.json pins the source (Hugging Face repository, revision,
SHA-256 of each source file) and the SHA-256 of each file this script writes.
Files that already match are left alone, so the script is cheap to rerun. The
float32 embeddings tensor is rounded to float16 (round to nearest even), which
is deterministic, so the output hash is fixed by the source hash. Needs numpy
(the devkit-agt[search] extra, installed by `just init`).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

import numpy as np

TENSOR = "embeddings"
URL = "https://huggingface.co/{repository}/resolve/{revision}/{name}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, target: Path, expected: str) -> None:
    with urllib.request.urlopen(url, timeout=60) as response, target.open("wb") as handle:
        while block := response.read(1 << 20):
            handle.write(block)
    actual = sha256(target)
    if actual != expected:
        raise SystemExit(f"error: {url}: SHA-256 {actual}, expected {expected}")


def to_float16(source: Path, target: Path) -> None:
    """Rewrite the safetensors file ``source`` with its embeddings tensor as F16 and a canonical header."""
    data = source.read_bytes()
    length = int.from_bytes(data[:8], "little")
    entry = json.loads(data[8 : 8 + length])[TENSOR]
    if entry["dtype"] != "F32":
        raise SystemExit(f"error: {source.name}: expected an F32 {TENSOR} tensor, found {entry['dtype']}")
    start, end = entry["data_offsets"]
    tensor = np.frombuffer(data, dtype="<f4", count=(end - start) // 4, offset=8 + length + start)
    converted = tensor.astype("<f2").tobytes()
    header = json.dumps(
        {TENSOR: {"dtype": "F16", "shape": entry["shape"], "data_offsets": [0, len(converted)]}},
        separators=(",", ":"),
    ).encode()
    header += b" " * (-len(header) % 8)  # the format allows trailing spaces; 8-byte alignment for the tensor
    target.write_bytes(len(header).to_bytes(8, "little") + header + converted)


def main(directory: Path) -> None:
    spec = json.loads((directory / "model.json").read_text(encoding="utf-8"))
    source, files = spec["source"], spec["files"]
    missing = [
        name for name, digest in files.items() if not (directory / name).is_file() or sha256(directory / name) != digest
    ]
    if not missing:
        print(f"[OK: {spec['name']} files are present and verified in {directory}]")
        return
    with tempfile.TemporaryDirectory(dir=directory) as scratch:
        for name in missing:
            fetched = Path(scratch) / f"source-{name}"
            download(URL.format(name=name, **source), fetched, source["files"][name])
            output = Path(scratch) / name
            if name == "model.safetensors":
                to_float16(fetched, output)
            else:
                os.replace(fetched, output)
            actual = sha256(output)
            if actual != files[name]:
                raise SystemExit(f"error: {name}: converted SHA-256 {actual}, expected {files[name]}")
            os.replace(output, directory / name)
            print(f"[FETCHED: {spec['name']} {name} sha256={actual}]")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: fetch_model.py <package data directory>")
    main(Path(sys.argv[1]))
