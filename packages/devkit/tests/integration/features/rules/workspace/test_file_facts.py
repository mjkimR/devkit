"""Per-file identity, disposable storage and mutation lifecycle contracts."""

from __future__ import annotations

import ast
import json
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
from devkit_agt.features.rules import (
    FactsDependency,
    FileFactsDescriptor,
    FileFactsSource,
    JsonValue,
    WorkspaceCache,
)
from devkit_agt.features.rules.repositories.workspace import facts as storage


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / ".devkit/transient").mkdir(parents=True)
    (tmp_path / "one.py").write_text("value = 1\n")
    (tmp_path / "two.py").write_text("value = 2\n")
    return tmp_path


@pytest.fixture
def descriptor() -> FileFactsDescriptor[tuple[str, int]]:
    def extract(source: FileFactsSource) -> tuple[str, int]:
        nodes = source.get_python_nodes(ast.Constant)
        assert isinstance(nodes[0], ast.Constant)
        assert type(nodes[0].value) is int
        return source.path, nodes[0].value

    def encode(value: tuple[str, int]) -> JsonValue:
        return [*value]

    def decode(value: JsonValue) -> tuple[str, int]:
        if not isinstance(value, list) or len(value) != 2 or not isinstance(value[0], str) or type(value[1]) is not int:
            raise ValueError("invalid test facts")
        return value[0], value[1]

    return FileFactsDescriptor("RULE-test-facts", 1, (FactsDependency("test.extract", b"v1"),), extract, encode, decode)


def warm(root: Path, descriptor: FileFactsDescriptor, *, paths: tuple[str, ...] = ("one.py", "two.py")) -> Path:
    cache = WorkspaceCache(root, facts_writer=True)
    for path in paths:
        cache.get_file_facts(path, descriptor)
    cache.flush_file_facts()
    return root / ".devkit/transient/rules/facts/RULE-test-facts.json"


def test_fresh_cache_hits_without_ast_and_does_not_rewrite(root: Path, descriptor: FileFactsDescriptor) -> None:
    memo = warm(root, descriptor)
    stamp = memo.stat().st_mtime_ns
    cache = WorkspaceCache(root, facts_writer=True)
    with patch.object(cache, "get_python_ast", side_effect=AssertionError("warm extraction parsed")):
        assert cache.get_file_facts("one.py", descriptor) == ("one.py", 1)
        cache.flush_file_facts()
    assert memo.stat().st_mtime_ns == stamp


def test_same_size_restored_mtime_and_context_changes_miss(root: Path, descriptor: FileFactsDescriptor) -> None:
    warm(root, descriptor)
    path = root / "one.py"
    before = path.stat()
    path.write_text("value = 9\n")
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert WorkspaceCache(root).get_file_facts("one.py", descriptor) == ("one.py", 9)
    cache = WorkspaceCache(root)
    with patch.object(cache, "get_python_ast", wraps=cache.get_python_ast) as parse:
        cache.get_file_facts("two.py", descriptor, context_key={"setting": 1})
        assert parse.call_count == 1
    path.rename(root / "renamed.py")
    assert WorkspaceCache(root).get_file_facts("renamed.py", descriptor) == ("renamed.py", 9)


@pytest.mark.parametrize("change", ["schema", "helper", "framework", "python", "missing"])
def test_provenance_changes_invalidate(root: Path, descriptor: FileFactsDescriptor, monkeypatch, change: str) -> None:
    warm(root, descriptor)
    if change == "schema":
        descriptor = replace(descriptor, schema_version=2)
    elif change == "helper":
        descriptor = replace(
            descriptor, source_dependencies=(*descriptor.source_dependencies, FactsDependency("helper", b"new"))
        )
    elif change == "framework":
        monkeypatch.setattr(storage, "_FRAMEWORK", (FactsDependency("framework", b"new"),))
    elif change == "python":
        monkeypatch.setattr(storage.sys, "version", storage.sys.version.replace("3.12", "3.13"))
    else:
        descriptor = replace(descriptor, source_dependencies=(FactsDependency("missing", None),))
    cache = WorkspaceCache(root)
    with patch.object(cache, "get_python_ast", wraps=cache.get_python_ast) as parse:
        assert cache.get_file_facts("one.py", descriptor) == ("one.py", 1)
        assert parse.call_count == 1


@pytest.mark.parametrize("bad", ["{", "[]", '{"version": false}', '{"version": 1, "entries": []}', "null"])
def test_corrupt_stores_are_silent_misses(root: Path, descriptor: FileFactsDescriptor, bad: str) -> None:
    memo = warm(root, descriptor)
    memo.write_text(bad)
    assert WorkspaceCache(root).get_file_facts("one.py", descriptor) == ("one.py", 1)


def test_bad_entry_codec_is_a_miss(root: Path, descriptor: FileFactsDescriptor) -> None:
    memo = warm(root, descriptor)
    value = json.loads(memo.read_text())
    value["entries"]["one.py"]["payload"] = {"bad": "shape"}
    memo.write_text(json.dumps(value))
    assert WorkspaceCache(root).get_file_facts("one.py", descriptor) == ("one.py", 1)


@pytest.mark.parametrize(
    "component",
    [
        ".devkit",
        ".devkit/transient",
        ".devkit/transient/rules",
        ".devkit/transient/rules/facts",
        ".devkit/transient/rules/facts/RULE-test-facts.json",
    ],
)
def test_symlink_components_are_not_read_or_written(
    root: Path, descriptor: FileFactsDescriptor, component: str
) -> None:
    warm(root, descriptor)
    path = root / component
    target = path.with_name(path.name + ".saved")
    path.rename(target)
    path.symlink_to(target, target_is_directory=target.is_dir())
    cache = WorkspaceCache(root, facts_writer=True)
    with patch.object(cache, "get_python_ast", wraps=cache.get_python_ast) as parse:
        assert cache.get_file_facts("one.py", descriptor) == ("one.py", 1)
        assert parse.call_count == 1
        cache.flush_file_facts()
    assert path.is_symlink()


def test_no_transient_and_default_library_calls_never_create_store(
    tmp_path: Path, descriptor: FileFactsDescriptor
) -> None:
    (tmp_path / "one.py").write_text("value=1")
    cache = WorkspaceCache(tmp_path, facts_writer=True)
    cache.get_file_facts("one.py", descriptor)
    cache.flush_file_facts()
    assert not (tmp_path / ".devkit").exists()
    (tmp_path / ".devkit/transient").mkdir(parents=True)
    cache = WorkspaceCache(tmp_path)
    cache.get_file_facts("one.py", descriptor)
    cache.flush_file_facts()
    assert not (tmp_path / ".devkit/transient/rules").exists()


def test_read_only_borrow_uses_snapshot_bytes_and_does_not_write(
    root: Path, tmp_path: Path, descriptor: FileFactsDescriptor
) -> None:
    memo = warm(root, descriptor)
    original = memo.read_bytes()
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "one.py").write_bytes((root / "one.py").read_bytes())
    cache = WorkspaceCache(snapshot, facts_root=root)
    with patch.object(cache, "get_python_ast", side_effect=AssertionError("snapshot hit parsed")):
        assert cache.get_file_facts("one.py", descriptor) == ("one.py", 1)
    (snapshot / "one.py").write_text("value=7")
    cache.invalidate("one.py")
    assert cache.get_file_facts("one.py", descriptor) == ("one.py", 7)
    cache.flush_file_facts()
    assert memo.read_bytes() == original
    assert not (snapshot / ".devkit").exists()


def test_invalidation_drops_old_dirty_entries_and_rechecks(root: Path, descriptor: FileFactsDescriptor) -> None:
    cache = WorkspaceCache(root, facts_writer=True)
    cache.get_file_facts("one.py", descriptor)
    cache.write_text("one.py", "value=3\n")
    cache.flush_file_facts()
    assert not (root / ".devkit/transient/rules/facts/RULE-test-facts.json").exists()
    assert cache.get_file_facts("one.py", descriptor) == ("one.py", 3)
    cache.flush_file_facts()
    assert WorkspaceCache(root).get_file_facts("one.py", descriptor) == ("one.py", 3)
    cache.write_text("one.py", "value=4\n")
    cache.invalidate_many(["one.py", "two.py"])
    assert cache.get_file_facts("one.py", descriptor) == ("one.py", 4)
    cache.invalidate_all()
    assert cache.get_file_facts("one.py", descriptor) == ("one.py", 4)


def test_partial_preserves_and_explicit_full_enumeration_prunes(root: Path, descriptor: FileFactsDescriptor) -> None:
    memo = warm(root, descriptor)
    (root / "two.py").unlink()
    cache = WorkspaceCache(root, facts_writer=True)
    cache.get_file_facts("one.py", descriptor)
    cache.complete_file_facts(descriptor, ["one.py"])
    cache.flush_file_facts()
    assert set(json.loads(memo.read_text())["entries"]) == {"one.py", "two.py"}
    cache = WorkspaceCache(root, facts_writer=True, facts_prune=True)
    cache.get_file_facts("one.py", descriptor)
    cache.flush_file_facts()  # a normal return supplies no completeness evidence
    assert "two.py" in json.loads(memo.read_text())["entries"]
    cache.complete_file_facts(descriptor, ["one.py"])
    cache.flush_file_facts()
    assert set(json.loads(memo.read_text())["entries"]) == {"one.py"}
    cache = WorkspaceCache(root, facts_writer=True, facts_prune=True)
    cache.complete_file_facts(descriptor, [])
    cache.flush_file_facts()
    assert json.loads(memo.read_text())["entries"] == {}


def test_nonregular_and_unwritable_memos_are_silent(root: Path, descriptor: FileFactsDescriptor) -> None:
    memo = warm(root, descriptor)
    memo.unlink()
    memo.mkdir()
    cache = WorkspaceCache(root, facts_writer=True)
    assert cache.get_file_facts("one.py", descriptor) == ("one.py", 1)
    cache.flush_file_facts()
    memo.rmdir()
    with patch.object(storage, "atomic_write_bytes", side_effect=PermissionError):
        cache.flush_file_facts()
    assert not memo.exists()


def test_concurrent_atomic_writers_leave_valid_memo(root: Path, descriptor: FileFactsDescriptor) -> None:
    def run(path: str) -> None:
        warm(root, descriptor, paths=(path,))

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run, ("one.py", "two.py")))
    value = json.loads((root / ".devkit/transient/rules/facts/RULE-test-facts.json").read_text())
    assert set(value["entries"]).issubset({"one.py", "two.py"})
    assert value["entries"]
    assert WorkspaceCache(root).get_file_facts("one.py", descriptor) == ("one.py", 1)


def test_invalid_json_payload_bypasses_and_extractor_errors_propagate(
    root: Path, descriptor: FileFactsDescriptor
) -> None:
    bad = replace(descriptor, encode=lambda value: float("nan"))
    cache = WorkspaceCache(root, facts_writer=True)
    assert cache.get_file_facts("one.py", bad) == ("one.py", 1)
    cache.flush_file_facts()
    assert not (root / ".devkit/transient/rules/facts/RULE-test-facts.json").exists()

    def fail(source: FileFactsSource):
        raise RuntimeError("extractor bug")

    with pytest.raises(RuntimeError, match="extractor bug"):
        cache.get_file_facts("two.py", replace(descriptor, extract=fail))


def test_context_is_frozen_and_key_is_canonical(root: Path, descriptor: FileFactsDescriptor) -> None:
    contexts = []

    def extract(source: FileFactsSource):
        contexts.append(source.context)
        return descriptor.extract(source)

    desc = replace(descriptor, extract=extract)
    cache = WorkspaceCache(root)
    cache.get_file_facts("one.py", desc, context_key={"b": [2], "a": 1})
    cache.get_file_facts("one.py", desc, context_key={"a": 1, "b": [2]})
    assert len(contexts) == 1
    with pytest.raises(TypeError):
        contexts[0]["a"] = 3
    assert contexts[0]["b"] == (2,)


@pytest.mark.parametrize("data", [b"\xef\xbb\xbfvalue=1\n", b"# coding: latin-1\n# caf\xe9\nvalue=1\n"])
def test_raw_python_encodings_roundtrip(root: Path, descriptor: FileFactsDescriptor, data: bytes) -> None:
    (root / "one.py").write_bytes(data)
    warm(root, descriptor)
    cache = WorkspaceCache(root)
    with patch.object(cache, "get_python_ast", side_effect=AssertionError("warm encoding parsed")):
        assert cache.get_file_facts("one.py", descriptor) == ("one.py", 1)


@pytest.mark.parametrize("data", [b"value=\xff", b"def broken("])
def test_failed_extraction_never_persists_empty_facts(root: Path, descriptor: FileFactsDescriptor, data: bytes) -> None:
    (root / "one.py").write_bytes(data)
    cache = WorkspaceCache(root, facts_writer=True)
    with pytest.raises(SyntaxError):
        cache.get_file_facts("one.py", descriptor)
    cache.flush_file_facts()
    assert not (root / ".devkit/transient/rules/facts/RULE-test-facts.json").exists()


def test_virtual_dry_run_bytes_never_flush(root: Path, descriptor: FileFactsDescriptor) -> None:
    memo = warm(root, descriptor)
    original = memo.read_bytes()
    cache = WorkspaceCache(root, facts_writer=True)
    cache.write_text("one.py", "value=7\n", dry_run=True)
    assert cache.get_file_facts("one.py", descriptor) == ("one.py", 7)
    cache.flush_file_facts()
    assert memo.read_bytes() == original
    assert WorkspaceCache(root).get_file_facts("one.py", descriptor) == ("one.py", 1)


def test_dependency_uses_loader_verified_source_not_changed_disk(root: Path) -> None:
    import sys
    from importlib.abc import Loader as ImportLoader
    from types import ModuleType

    from devkit_agt.features.rules import capture_facts_dependency

    module = ModuleType("facts_provenance_probe")

    class Loader(ImportLoader):
        def get_source(self, name: str) -> str:
            return "verified = True\n"

    module.__loader__ = Loader()
    source = root / "probe.py"
    source.write_text("unstaged = True\n")
    with patch.dict(sys.modules, {module.__name__: module}):
        captured = capture_facts_dependency("probe", str(source), module_name=module.__name__)
    assert captured.source == b"verified = True\n"
    source.write_text("later_edit = True\n")
    assert captured.source == b"verified = True\n"


def test_symlink_retarget_invalidation_drops_logical_facts(root: Path, descriptor: FileFactsDescriptor) -> None:
    alias = root / "alias.py"
    alias.symlink_to(root / "one.py")
    cache = WorkspaceCache(root)
    assert cache.get_file_facts(alias, descriptor) == ("alias.py", 1)
    alias.unlink()
    alias.symlink_to(root / "two.py")
    cache.invalidate(alias)
    assert cache.get_file_facts(alias, descriptor) == ("alias.py", 2)
