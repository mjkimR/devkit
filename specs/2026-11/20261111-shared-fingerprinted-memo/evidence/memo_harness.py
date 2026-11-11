"""Differential fixture harness for the two fingerprinted memos (SPEC-shared-fingerprinted-memo).

Drives only public entry points: ``DocumentIndex.load`` (a writing load and a load with a supplied file list) and
``WorkspaceCache`` with ``get_file_facts`` and ``flush_file_facts`` (``facts_writer=True`` and a reader). Each fixture
first warms a real memo with the code under test, then plants a sentinel entry, so "used" is visible in the public
result: the docs index reports the sentinel reason as a problem and the facts cache returns the sentinel payload.
Each row records whether the memo was used, whether the memo file was written, and the memo log records as logger,
level and message (no ``exc_info``), with the fixture root replaced by ``<root>``.

The document index keeps parse results in process, so each fixture is prepared in one child process and measured
in another.

Usage: ``uv run python memo_harness.py <scratch-dir>``; prints the table on stdout.
"""

from __future__ import annotations

import ast
import json
import logging
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from devkit_agt.features.rules import (
    FactsDependency,
    FileFactsDescriptor,
    FileFactsSource,
    JsonValue,
    WorkspaceCache,
)
from devkit_docs.features.documents.repositories.index import DocumentIndex

SENTINEL_REASON = "MEMO-SENTINEL"
SENTINEL_VALUE = 999
DOCS_MEMO = (".devkit", "transient", "docs", "document-index.json")
FACTS_MEMO = (".devkit", "transient", "rules", "facts", "RULE-harness-facts.json")


class Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        if record.name.endswith((".repositories.memo", ".workspace.facts")):
            self.records.append(record)


def _extract(source: FileFactsSource) -> tuple[str, int]:
    node = source.get_python_nodes(ast.Constant)[0]
    assert isinstance(node, ast.Constant) and type(node.value) is int
    return source.path, node.value


def _decode(value: JsonValue) -> tuple[str, int]:
    if not isinstance(value, list) or len(value) != 2 or not isinstance(value[0], str) or type(value[1]) is not int:
        raise ValueError("invalid harness facts")
    return value[0], value[1]


DESCRIPTOR = FileFactsDescriptor(
    "RULE-harness-facts", 1, (FactsDependency("harness.extract", b"v1"),), _extract, list, _decode
)


def _workspace(root: Path) -> None:
    (root / ".devkit" / "transient").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "docs" / "note.md").write_text("# Note\n")
    (root / "one.py").write_text("value = 1\n")


def _sentinel_docs(root: Path) -> dict:
    DocumentIndex.load(root)
    path = root.joinpath(*DOCS_MEMO)
    memo = json.loads(path.read_text())
    entry = memo["entries"]["docs/note.md"]
    memo["entries"]["docs/note.md"] = [entry[0], "e", SENTINEL_REASON]
    return memo


def _sentinel_facts(root: Path) -> dict:
    cache = WorkspaceCache(root, facts_writer=True, git_filter=False)
    cache.get_file_facts("one.py", DESCRIPTOR)
    cache.flush_file_facts()
    path = root.joinpath(*FACTS_MEMO)
    memo = json.loads(path.read_text())
    memo["entries"]["one.py"]["payload"] = ["one.py", SENTINEL_VALUE]
    return memo


def _dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) if not isinstance(value, str) else value)


def _relocate(root: Path, memo_parts: tuple[str, ...], index: int, memo: dict) -> None:
    """Move the component at ``index`` of the memo path elsewhere inside ``root`` and symlink it back."""
    _dump(root.joinpath(*memo_parts), memo)
    original = root.joinpath(*memo_parts[: index + 1])
    moved = root / "elsewhere" / original.name
    moved.parent.mkdir(exist_ok=True)
    shutil.move(str(original), str(moved))
    original.symlink_to(moved, target_is_directory=moved.is_dir())


def _fixtures(memo_parts: tuple[str, ...]) -> dict[str, Callable[[Path, dict], None]]:
    """Each fixture turns a warmed workspace and its sentinel memo into the state under test."""
    file = memo_parts
    leaf_dir = memo_parts[:-1]
    first_below = memo_parts[:3]

    def write(change: Callable[[dict], object]) -> Callable[[Path, dict], None]:
        return lambda root, memo: _dump(root.joinpath(*file), change(memo))

    def remove_tree(parts: tuple[str, ...]) -> Callable[[Path, dict], None]:
        return lambda root, memo: shutil.rmtree(root.joinpath(*parts))

    def plain_file(parts: tuple[str, ...]) -> Callable[[Path, dict], None]:
        def apply(root: Path, memo: dict) -> None:
            target = root.joinpath(*parts)
            shutil.rmtree(target)
            target.write_text("x")

        return apply

    def directory_at_file(root: Path, memo: dict) -> None:
        target = root.joinpath(*file)
        target.unlink(missing_ok=True)
        target.mkdir()

    return {
        "valid": write(lambda memo: memo),
        "missing-file": lambda root, memo: root.joinpath(*file).unlink(missing_ok=True),
        "missing-below-transient": remove_tree(first_below),
        "no-transient": remove_tree((".devkit", "transient")),
        "devkit-is-file": plain_file((".devkit",)),
        "malformed": write(lambda memo: "{not json"),
        "nan-constant": write(lambda memo: json.dumps(memo)[:-1] + ', "x": NaN}'),
        "not-object": write(lambda memo: [memo]),
        "foreign-version": write(lambda memo: {**memo, "version": 2}),
        "bool-version": write(lambda memo: {**memo, "version": True}),
        "foreign-fingerprint": write(lambda memo: {**memo, "fingerprint": "0" * 32}),
        "entries-not-mapping": write(lambda memo: {**memo, "entries": []}),
        "missing-key": write(lambda memo: {k: v for k, v in memo.items() if k != "entries"}),
        "extra-key": write(lambda memo: {**memo, "extra": 1}),
        "non-regular": directory_at_file,
        "symlink-file": lambda root, memo: _relocate(root, file, len(file) - 1, memo),
        "symlink-leaf-dir": lambda root, memo: _relocate(root, file, len(leaf_dir) - 1, memo),
        "symlink-first-below": lambda root, memo: _relocate(root, file, 2, memo),
        "symlink-transient": lambda root, memo: _relocate(root, file, 1, memo),
        "symlink-devkit": lambda root, memo: _relocate(root, file, 0, memo),
        "non-directory-below": plain_file(first_below),
    }


def _state(path: Path) -> str:
    if path.is_symlink():
        target = path.resolve()
        return "symlink:" + (target.read_text() if target.is_file() else "-")
    if path.is_dir():
        return "dir"
    if path.is_file():
        return path.read_text()
    return "absent"


def _docs_run(root: Path, writes: bool) -> bool:
    index = DocumentIndex.load(root) if writes else DocumentIndex.load(root, files=[root / "docs" / "note.md"])
    return any(SENTINEL_REASON in str(getattr(problem, "message", problem)) for problem in index.problems)


def _facts_run(root: Path, writes: bool) -> bool:
    cache = WorkspaceCache(root, facts_writer=writes, git_filter=False)
    value = cache.get_file_facts("one.py", DESCRIPTOR)
    cache.flush_file_facts()
    return value == ("one.py", SENTINEL_VALUE)


def _prepare(root: Path, memo: str, name: str) -> None:
    root.mkdir(parents=True)
    _workspace(root)
    parts = DOCS_MEMO if memo == "docs" else FACTS_MEMO
    sentinel = _sentinel_docs(root) if memo == "docs" else _sentinel_facts(root)
    _fixtures(parts)[name](root, sentinel)


def _measure(root: Path, memo: str, mode: str) -> str:
    path = root.joinpath(*(DOCS_MEMO if memo == "docs" else FACTS_MEMO))
    before = _state(path)
    capture = Capture()
    devkit = logging.getLogger("devkit")
    devkit.addHandler(capture)
    devkit.setLevel(logging.DEBUG)
    run = _docs_run if memo == "docs" else _facts_run
    used = run(root, mode == "write")
    devkit.removeHandler(capture)
    after = _state(path)
    written = "same" if after == before else ("created" if before == "absent" else "rewritten")
    logs = "; ".join(
        f"{r.name.rsplit('.', 1)[-1]}/{r.levelname}/{r.getMessage().replace(str(root), '<root>')}"
        for r in capture.records
    )
    return f"{'used' if used else 'not used'} | {written} | {logs or '-'}"


def _child(*args: str) -> str:
    done = subprocess.run([sys.executable, __file__, *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


def main(argv: list[str]) -> int:
    if argv[1] == "--prepare":
        _prepare(Path(argv[2]), argv[3], argv[4])
        return 0
    if argv[1] == "--measure":
        print(_measure(Path(argv[2]), argv[3], argv[4]))
        return 0
    scratch = Path(argv[1]).resolve()
    if scratch.exists():
        shutil.rmtree(scratch)
    rows = [
        "| memo | mode | fixture | memo used | file | logs (logger/level/message) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for memo, parts in (("docs", DOCS_MEMO), ("facts", FACTS_MEMO)):
        for mode in ("write", "read"):
            for name in _fixtures(parts):
                root = scratch / memo / mode / name
                _child("--prepare", str(root), memo, name)
                rows.append(f"| {memo} | {mode} | {name} | {_child('--measure', str(root), memo, mode)} |")
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
