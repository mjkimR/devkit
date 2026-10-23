"""Disposable per-rule JSON stores; cache failures never become rule advisories."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, cast

from devkit_core.core import atomic_write_bytes
from devkit_core.core.logs import get_logger

from devkit_agt.features.rules.models.file_facts import FactsDependency, FileFactsDescriptor

logger = get_logger(__name__)
FORMAT_VERSION = 1


def capture_facts_dependency(name: str, filename: str, *, module_name: str | None = None) -> FactsDependency:
    """Capture actual executing source provenance, before later workspace edits."""
    try:
        if module_name is None:
            source = Path(filename).read_bytes()
        else:
            module = sys.modules.get(module_name)
            loader = getattr(module, "__loader__", None)
            get_source = getattr(loader, "get_source", None)
            text = get_source(module_name) if get_source is not None else None
            source = text.encode("utf-8") if isinstance(text, str) else None
    except (OSError, ImportError, UnicodeError):
        source = None
    return FactsDependency(name, source)


_FRAMEWORK = (
    capture_facts_dependency(__name__, __file__),
    capture_facts_dependency("workspace.file_facts", str(Path(__file__).with_name("file_facts.py"))),
    capture_facts_dependency("workspace.cache", str(Path(__file__).with_name("cache.py"))),
    capture_facts_dependency("models.file_facts", str(Path(__file__).parents[2] / "models" / "file_facts.py")),
)


def canonical_json(value: Any) -> str:
    """Strict JSON: no tuples, non-string keys, non-finite numbers or arbitrary objects."""

    def validate(item: Any) -> None:
        if item is None or type(item) in (bool, int, str):
            return
        if type(item) is float and math.isfinite(item):
            return
        if type(item) is list:
            for child in item:
                validate(child)
            return
        if type(item) is dict and all(type(key) is str for key in item):
            for child in item.values():
                validate(child)
            return
        raise ValueError("unsupported JSON value")

    validate(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def facts_fingerprint(descriptor: FileFactsDescriptor[Any]) -> str | None:
    if not descriptor.source_dependencies or type(descriptor.schema_version) is not int:
        return None
    sources = (*_FRAMEWORK, *descriptor.source_dependencies)
    if any(source.source is None for source in sources):
        return None
    digest = hashlib.blake2b()
    for value in (str(FORMAT_VERSION), str(descriptor.schema_version), platform.python_implementation(), sys.version):
        digest.update(value.encode() + b"\0")
    for source in sources:
        digest.update(source.name.encode() + b"\0")
        digest.update(hashlib.blake2b(cast(bytes, source.source)).digest())
    return digest.hexdigest()


def logical_path(path: str) -> bool:
    p = PurePosixPath(path)
    return bool(path) and not p.is_absolute() and ".." not in p.parts and p.as_posix() == path and path != "."


def memo_path(root: Path, rule_id: str, *, create: bool = False) -> Path | None:
    """Require an existing transient directory; reject every symlink and obstructing component."""
    if re.fullmatch(r"RULE-[A-Za-z0-9][A-Za-z0-9_-]*", rule_id) is None:
        return None
    here = root
    for part in (".devkit", "transient", "rules", "facts"):
        here = here / part
        if here.is_symlink():
            return None
        if not here.exists():
            if not create or part in (".devkit", "transient"):
                return None
            here.mkdir(exist_ok=True)
        if not here.is_dir() or here.resolve() != here:
            return None
    path = here / f"{rule_id}.json"
    if path.is_symlink() or (path.exists() and not path.is_file()):
        return None
    return path


@dataclass
class FactsStore:
    descriptor: FileFactsDescriptor[Any]
    root: Path
    fingerprint: str | None = field(init=False)
    entries: dict[str, dict[str, Any]] = field(default_factory=dict)
    original: bytes | None = None
    pending: dict[str, dict[str, Any]] = field(default_factory=dict)
    complete: set[str] | None = None

    def __post_init__(self) -> None:
        self.fingerprint = facts_fingerprint(self.descriptor)
        if self.fingerprint is None:
            return
        try:
            path = memo_path(self.root, self.descriptor.rule_id)
            if path is None or not path.exists():
                return
            raw = path.read_bytes()
            value = json.loads(raw)
            if (
                type(value) is not dict
                or type(value.get("version")) is not int
                or value.get("version") != FORMAT_VERSION
                or value.get("fingerprint") != self.fingerprint
                or type(value.get("entries")) is not dict
            ):
                return
            entries: dict[str, dict[str, Any]] = {}
            for name, entry in value["entries"].items():
                if not logical_path(name) or type(entry) is not dict or set(entry) != {"digest", "context", "payload"}:
                    continue
                if not isinstance(entry["digest"], str) or re.fullmatch(r"[0-9a-f]{128}", entry["digest"]) is None:
                    continue
                if not isinstance(entry["context"], str):
                    continue
                if canonical_json(json.loads(entry["context"])) != entry["context"]:
                    continue
                canonical_json(entry["payload"])
                entries[name] = entry
            self.entries = entries
            self.original = raw
        except (OSError, ValueError, TypeError, RecursionError):
            logger.debug("Unable to load facts memo for %s", self.descriptor.rule_id, exc_info=True)

    def get(self, name: str, digest: str, context: str) -> tuple[bool, Any]:
        entry = self.pending.get(name, self.entries.get(name))
        if entry is None or entry["digest"] != digest or entry["context"] != context:
            return False, None
        try:
            return True, self.descriptor.decode(entry["payload"])
        except (ValueError, TypeError, KeyError, IndexError, OverflowError, RecursionError):
            logger.debug("Invalid facts payload for %s: %s", self.descriptor.rule_id, name, exc_info=True)
            self.entries.pop(name, None)
            self.pending.pop(name, None)
            return False, None

    def put(self, name: str, digest: str, context: str, facts: Any) -> None:
        if self.fingerprint is None:
            return
        # Encoder programming exceptions propagate; only unsupported JSON values bypass persistence.
        payload = self.descriptor.encode(facts)
        try:
            canonical_json(payload)
        except (ValueError, RecursionError):
            self.entries.pop(name, None)
            self.pending.pop(name, None)
            return
        self.pending[name] = {"digest": digest, "context": context, "payload": payload}

    def flush(self, *, prune: bool) -> None:
        if self.fingerprint is None:
            return
        entries = {**self.entries, **self.pending}
        if prune and self.complete is not None:
            entries = {name: entry for name, entry in entries.items() if name in self.complete}
        if entries == self.entries and not self.pending:
            return
        try:
            raw = canonical_json(
                {"version": FORMAT_VERSION, "fingerprint": self.fingerprint, "entries": entries}
            ).encode()
            if raw == self.original:
                return
            path = memo_path(self.root, self.descriptor.rule_id, create=True)
            if path is None:
                return
            atomic_write_bytes(path, raw)
            self.original = raw
            self.entries = entries
            self.pending.clear()
        except (OSError, ValueError, RecursionError):
            logger.debug("Unable to flush facts memo for %s", self.descriptor.rule_id, exc_info=True)
