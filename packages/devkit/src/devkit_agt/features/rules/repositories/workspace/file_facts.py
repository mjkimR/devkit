"""Run-local extraction retention, isolated from invalidated cross-file judgments."""

from __future__ import annotations

import ast
import hashlib
import json
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, cast

from devkit_agt.features.rules.models.file_facts import FactsT, FileFactsDescriptor, FrozenJsonValue, JsonValue
from devkit_agt.features.rules.repositories.workspace.facts import FactsStore, canonical_json, logical_path

if TYPE_CHECKING:
    from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache


def _freeze(value: JsonValue) -> FrozenJsonValue:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value


@dataclass(frozen=True)
class _Source:
    path: str
    context: FrozenJsonValue
    _cache: WorkspaceCache
    _input_path: str | Path

    def get_python_ast(self) -> ast.Module:
        return self._cache.get_python_ast(self._input_path)

    def get_python_nodes(self, *types: type[ast.AST]) -> tuple[ast.AST, ...]:
        return self._cache.get_python_nodes(self._input_path, *types)


def source_digest(data: bytes) -> str:
    """Digest exactly the bytes retained by the workspace reader."""
    return hashlib.blake2b(data).hexdigest()


class FileFactsCache:
    def __init__(self, cache: WorkspaceCache, *, root: Path, enabled: bool, writer: bool, prune: bool) -> None:
        self.cache = cache
        self.root = root.resolve()
        self.enabled = enabled
        self.writer = writer
        self.prune = prune
        self.stores: dict[FileFactsDescriptor[Any], FactsStore] = {}
        self.values: dict[tuple[FileFactsDescriptor[Any], str, str], Any] = {}
        self.paths: dict[str, set[str]] = {}
        self.digests: dict[str, str] = {}

    def get(self, path: str | Path, descriptor: FileFactsDescriptor[FactsT], context: JsonValue) -> FactsT:
        resolved = self.cache._resolve_path(path)
        logical = Path(path)
        if logical.is_absolute():
            with suppress(ValueError):
                logical = logical.relative_to(self.cache.workspace_root)
        name = logical.as_posix()
        # Reading errors keep the same semantics as extraction and never produce successful empty entries.
        data = self.cache.read_bytes(path)
        persistent = self.enabled and logical_path(name) and resolved.is_relative_to(self.cache.workspace_root)
        try:
            key = canonical_json(context)
            frozen = _freeze(json.loads(key))
        except (ValueError, RecursionError):
            # Unsupported contexts can still be used by direct extractors, without retention/reuse.
            return descriptor.extract(_Source(name, cast(FrozenJsonValue, context), self.cache, path))
        identity = (descriptor, name, key)
        if identity in self.values:
            return cast(FactsT, self.values[identity])
        resolved_key = resolved.as_posix()
        digest = self.digests.get(resolved_key)
        if digest is None:
            digest = self.digests[resolved_key] = source_digest(data)
        store = None
        if persistent:
            store = self.stores.get(descriptor)
            if store is None:
                store = self.stores[descriptor] = FactsStore(descriptor, self.root)
            hit, facts = store.get(name, digest, key)
            if hit:
                self.values[identity] = facts
                self.paths.setdefault(resolved_key, set()).add(name)
                return cast(FactsT, facts)
        facts = descriptor.extract(_Source(name, frozen, self.cache, path))
        self.values[identity] = facts
        self.paths.setdefault(resolved_key, set()).add(name)
        if store is not None:
            store.put(name, digest, key, facts)
        return facts

    def complete(self, descriptor: FileFactsDescriptor[Any], paths: list[str]) -> None:
        store = self.stores.get(descriptor)
        if store is None and self.enabled:
            store = self.stores[descriptor] = FactsStore(descriptor, self.root)
        if store is not None and all(logical_path(path) for path in paths):
            store.complete = set(paths)

    def invalidate(self, resolved: str | None = None) -> None:
        names = self.paths.pop(resolved, set()) if resolved is not None else None
        if resolved is None:
            self.paths.clear()
            self.digests.clear()
            self.values.clear()
        else:
            self.digests.pop(resolved, None)
            self.values = {key: value for key, value in self.values.items() if key[1] not in cast(set[str], names)}
        for store in self.stores.values():
            if names is None:
                store.pending.clear()
            else:
                for name in names:
                    store.pending.pop(name, None)
            # A pre-fix enumeration cannot authorize pruning the post-fix path set.
            store.complete = None

    def flush(self) -> None:
        if self.writer and self.enabled:
            for store in self.stores.values():
                store.flush(prune=self.prune)
