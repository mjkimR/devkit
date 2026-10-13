"""Refuse to build a wheel without the fetched model files, or with files that do not match model.json.

An editable install (``uv sync`` in the workspace) is not checked: a checkout works without the
files until dense search runs, which then reports ``SEARCH_MODEL_INVALID``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

DATA = Path("src/devkit_embed")


class ModelFilesHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if version == "editable":
            return
        directory = Path(self.root) / DATA
        expected = json.loads((directory / "model.json").read_text(encoding="utf-8"))["files"]
        for name, digest in expected.items():
            path = directory / name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise RuntimeError(f"{path}: missing or not the pinned file; run `just model-fetch` first")
