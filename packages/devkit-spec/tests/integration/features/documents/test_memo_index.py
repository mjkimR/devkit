"""``DocumentIndex.load`` with the parse memo: results identical to a fresh build (``SPEC-document-index-cache``)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner, Result
from devkit_agt.features.rules.services.testing import check, load_rule
from devkit_dist.cli import cli as devkit_cli
from spec_support.types import Write

import devkit_spec
from devkit_spec.features.documents import DocumentIndex
from devkit_spec.features.documents.repositories import index as index_module
from devkit_spec.features.documents.repositories import memo as memo_module
from devkit_spec.features.documents.repositories.memo import ParseMemo, decode_entry

MEMO = ".devkit/transient/spec/document-index.json"
RULE = load_rule(Path(devkit_spec.__file__).parent / "bundles/spec/bundle/rules/document_reference/rule.py")


@pytest.fixture(autouse=True)
def _new_process() -> Iterator[None]:
    """Every load in these tests starts like a new process: no in-process parse results."""
    index_module._parsed.clear()
    yield
    index_module._parsed.clear()


@pytest.fixture
def transient(workspace: Path) -> Path:
    (workspace / ".devkit/transient").mkdir()
    return workspace


def _doc(document_id: str, body: str = "", **fields: str) -> str:
    header = "".join(f"{key}: {value}\n" for key, value in fields.items())
    return f"---\nid: {document_id}\nstatus: active\n{header}---\n{body}"


def _base(write: Write) -> None:
    write("docs/capabilities/core/CAP-CORE-a.md", _doc("CAP-CORE-a", "`UC-b` [UC-c] `UC-gone`\n", area="core"))
    write("docs/usecases/core/UC-b.md", _doc("UC-b", "`CAP-CORE-a`\n", title="B", area="core", aliases="[UC-old]"))
    write("docs/usecases/ops/UC-c.md", _doc("UC-c", "`UC-old`\n", title="C", created="2026-10-22"))
    write("specs/2026-10/20261001-done/spec.md", _doc("SPEC-done").replace("active", "completed"))
    write("specs/2026-10/20261001-done/plan.md", _doc("PLAN-done", "`SPEC-done`\n"))
    write("docs/guide.md", "# A guide without frontmatter\n")


def _view(index: DocumentIndex) -> tuple[Any, ...]:
    problems = [(p.code, p.message, p.target_files) for p in index.problems]
    return (index.documents, index.by_id, index.by_alias, problems, index.historical)


def _fresh(root: Path) -> DocumentIndex:
    index_module._parsed.clear()
    original = ParseMemo.open
    ParseMemo.open = classmethod(lambda cls, root, *, writes: None)  # type: ignore[method-assign,assignment]
    try:
        return DocumentIndex.load(root)
    finally:
        ParseMemo.open = original  # type: ignore[method-assign]
        index_module._parsed.clear()


def _load(root: Path, **kwargs: Any) -> DocumentIndex:
    index_module._parsed.clear()
    return DocumentIndex.load(root, **kwargs)


def _assert_fresh(root: Path) -> None:
    """A load with the memo, then a second one with the memo it wrote, both equal a fresh build."""
    first = _view(_load(root))
    second = _view(_load(root))
    expected = _view(_fresh(root))
    assert first == expected and second == expected


def _memo(root: Path) -> dict[str, Any]:
    return json.loads((root / MEMO).read_text(encoding="utf-8"))


def _assert_valid_memo(root: Path) -> None:
    stored = _memo(root)
    assert stored["version"] == memo_module.FORMAT_VERSION and stored["fingerprint"] == memo_module.fingerprint()
    for relative, entry in stored["entries"].items():
        decode_entry(relative, entry)


@pytest.fixture
def parses(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """The paths parsed afresh."""
    seen: list[str] = []
    original = index_module.parse_document

    def counting(path: str, text: str) -> Any:
        seen.append(path)
        return original(path, text)

    monkeypatch.setattr(index_module, "parse_document", counting)
    return seen


def test_a_warm_memo_parses_nothing_and_equals_a_fresh_build(transient: Path, write: Write, parses: list[str]) -> None:
    _base(write)
    _load(transient)
    assert (transient / MEMO).is_file() and len(parses) == 6
    parses.clear()
    warm = _view(_load(transient))
    assert parses == []
    assert warm == _view(_fresh(transient))


def _rename(root: Path) -> None:
    (root / "docs/usecases/ops/UC-c.md").rename(root / "docs/usecases/ops/UC-c2.md")


def _same_size_edit(root: Path) -> None:
    path = root / "docs/usecases/core/UC-b.md"
    before = path.stat()
    path.write_text(path.read_text(encoding="utf-8").replace("title: B", "title: X"), encoding="utf-8")
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert path.stat().st_size == before.st_size


def _edit(path: str, old: str, new: str) -> Callable[[Path], None]:
    def change(root: Path) -> None:
        target = root / path
        target.write_text(target.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    return change


CHANGES: dict[str, Callable[[Path], object]] = {
    "content edit": _edit("docs/capabilities/core/CAP-CORE-a.md", "`UC-gone`", "`UC-c` `UC-new`"),
    "same-size edit with mtime restored": _same_size_edit,
    "new file": lambda root: (root / "docs/usecases/core/UC-new.md").write_text(_doc("UC-new"), encoding="utf-8"),
    "deletion": lambda root: (root / "docs/usecases/ops/UC-c.md").unlink(),
    "rename": _rename,
    "alias added": _edit("docs/usecases/ops/UC-c.md", "title: C", "aliases: [UC-older]\ntitle: C"),
    "alias changed": _edit("docs/usecases/core/UC-b.md", "[UC-old]", "[UC-older]"),
    "alias removed": _edit("docs/usecases/core/UC-b.md", "aliases: [UC-old]\n", ""),
    "ID change": _edit("docs/usecases/ops/UC-c.md", "id: UC-c", "id: UC-d"),
    "frontmatter malformed": _edit("docs/usecases/ops/UC-c.md", "title: C", "title: C\ntitle: again"),
    "file turned non-UTF-8": lambda root: (root / "docs/usecases/ops/UC-c.md").write_bytes(b"---\nid: UC-c\xff\n---\n"),
    "completion": _edit("specs/2026-10/20261001-done/spec.md", "completed", "draft"),
}


@pytest.mark.parametrize("change", list(CHANGES))
def test_loads_after_a_change_equal_a_fresh_build(transient: Path, write: Write, change: str) -> None:
    _base(write)
    _load(transient)
    CHANGES[change](transient)
    _assert_fresh(transient)
    _assert_valid_memo(transient)


def test_a_malformed_frontmatter_turned_back_reuses_nothing_stale(transient: Path, write: Write) -> None:
    _base(write)
    path = transient / "docs/usecases/ops/UC-c.md"
    original = path.read_text(encoding="utf-8")
    _load(transient)
    path.write_text(original.replace("title: C", "title: C\ntitle: again"), encoding="utf-8")
    _assert_fresh(transient)
    assert [p.target_files for p in _load(transient).problems] == [("docs/usecases/ops/UC-c.md",)]
    path.write_text(original, encoding="utf-8")
    _assert_fresh(transient)
    assert _load(transient).problems == []


def test_a_changed_fingerprint_discards_the_memo(
    transient: Path, write: Write, parses: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _base(write)
    _load(transient)
    monkeypatch.setattr(memo_module, "fingerprint", lambda: "another parser")
    parses.clear()
    assert _view(_load(transient)) == _view(_fresh(transient))
    assert len(parses) == 12  # the load parsed every file again, then the fresh build
    assert _memo(transient)["fingerprint"] == "another parser"


def test_no_fingerprint_means_no_memo(transient: Path, write: Write, monkeypatch: pytest.MonkeyPatch) -> None:
    _base(write)
    monkeypatch.setattr(memo_module, "fingerprint", lambda: None)
    assert _view(_load(transient)) == _view(_fresh(transient))
    assert not (transient / ".devkit/transient/spec").exists()


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *args],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_a_branch_switch_and_back_equals_a_fresh_build(transient: Path, write: Write) -> None:
    _base(write)
    (transient / ".gitignore").write_text(".devkit/transient/\n", encoding="utf-8")
    _git(transient, "init", "-q", "-b", "main")
    _git(transient, "add", "-A")
    _git(transient, "commit", "-q", "-m", "main")
    _git(transient, "checkout", "-q", "-b", "other")
    CHANGES["content edit"](transient)
    CHANGES["ID change"](transient)
    CHANGES["deletion"](transient)
    write("docs/usecases/core/UC-other.md", _doc("UC-other", "`UC-b`\n"))
    _git(transient, "add", "-A")
    _git(transient, "commit", "-q", "-m", "other")
    _load(transient)
    for branch in ("main", "other", "main"):
        _git(transient, "checkout", "-q", branch)
        _assert_fresh(transient)


def _spec(root: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["spec", *args, "-w", str(root)])


COMMANDS = (
    ("list",),
    ("list", "usecase", "--format", "json"),
    ("list", "--history"),
    ("resolve", "UC-old", "CAP-CORE-a", "UC-missing"),
    ("refs", "UC-b", "--direction", "in"),
    ("refs", "CAP-CORE-a"),
    ("search", "core", "--mode", "lexical"),
)


def _outputs(root: Path) -> list[tuple[int, str, str]]:
    results = []
    for command in COMMANDS:
        index_module._parsed.clear()
        result = _spec(root, *command)
        results.append((result.exit_code, result.stdout, result.stderr))
    return results


def _outputs_without_memo(root: Path, monkeypatch: pytest.MonkeyPatch) -> list[tuple[int, str, str]]:
    with monkeypatch.context() as patched:
        patched.setattr(ParseMemo, "open", classmethod(lambda cls, root, *, writes: None))
        return _outputs(root)


def test_commands_print_what_they_print_without_a_memo(
    transient: Path, write: Write, monkeypatch: pytest.MonkeyPatch
) -> None:
    _base(write)
    _outputs(transient)  # warm
    for change in ("content edit", "alias changed", "ID change", "frontmatter malformed"):
        CHANGES[change](transient)
        with_memo = _outputs(transient)
        assert with_memo == _outputs_without_memo(transient, monkeypatch)
        assert with_memo[3][0] == 2 and with_memo[0][0] == 0


# --- readers and line endings ------------------------------------------------------------------------------------

LINE_ENDINGS = {
    "docs/a.md": b"---\r\nid: CAP-A-a\r\nstatus: active\r\nusecases:\r\n  - UC-old\r\n---\r\nSee [UC-b] and `UC-old`.\r\n",
    "docs/b.md": b"---\rid: UC-b\rstatus: active\raliases:\r  - UC-old\r---\rBody [CAP-A-a] `UC-c`\r",
    "docs/c.md": "﻿---\nid: UC-c\nstatus: active\naliases: [UC-cc]\n---\n`CAP-A-a` [UC-b] `UC-cc`\n".encode(),
    "docs/d.md": b"\xef\xbb\xbf---\r\nid: UC-d\r\nstatus: active\r\n---\r\n[UC-c] `UC-old`\r\n",
}


def _rules_load(root: Path) -> DocumentIndex:
    files = sorted(root.glob("docs/*.md"))
    return _load(root, files=files, read=lambda path: path.read_bytes().decode("utf-8"))


def _rules_fresh(root: Path, monkeypatch: pytest.MonkeyPatch) -> DocumentIndex:
    with monkeypatch.context() as patched:
        patched.setattr(ParseMemo, "open", classmethod(lambda cls, root, *, writes: None))
        return _rules_load(root)


def _rule_run(root: Path) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]], dict[str, bytes]]:
    def found(violations: list[Any]) -> list[tuple[Any, ...]]:
        return sorted((v.file, v.line, v.message, v.fixable, v.fixed) for v in violations)

    index_module._parsed.clear()
    reports = found(check(RULE, root))
    index_module._parsed.clear()
    fixes = found(check(RULE, root, fix=True))
    return reports, fixes, {name: (root / name).read_bytes() for name in LINE_ENDINGS}


def _line_endings(root: Path) -> None:
    for name, data in LINE_ENDINGS.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_bytes(data)


@pytest.mark.parametrize("walk_first", [True, False])
def test_readers_with_other_line_endings_never_share_an_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, walk_first: bool
) -> None:
    with_memo, without = tmp_path / "with", tmp_path / "without"
    for root in (with_memo, without):
        (root / ".devkit/transient").mkdir(parents=True)
        _line_endings(root)
    walk_fresh, rules_fresh = _view(_fresh(without)), _view(_rules_fresh(without, monkeypatch))
    assert walk_fresh != rules_fresh  # the two readers give other texts, so other results
    for _ in range(2):
        if walk_first:
            assert _view(_load(with_memo)) == walk_fresh
            assert _view(_rules_load(with_memo)) == rules_fresh
        else:
            assert _view(_rules_load(with_memo)) == rules_fresh
            assert _view(_load(with_memo)) == walk_fresh
    if walk_first:
        _load(with_memo)
    with monkeypatch.context() as patched:
        patched.setattr(ParseMemo, "open", classmethod(lambda cls, root, *, writes: None))
        expected = _rule_run(without)
    assert _rule_run(with_memo) == expected
    assert expected[1] and any(fixed for *_, fixed in expected[1])  # the fixes rewrote something


# --- a memo that cannot be trusted ---------------------------------------------------------------------------------


def _truncate(path: Path) -> None:
    path.write_bytes(path.read_bytes()[: path.stat().st_size // 2])


def _rewrite(change: Callable[[dict[str, Any]], None]) -> Callable[[Path], None]:
    def corrupt(path: Path) -> None:
        stored = json.loads(path.read_text(encoding="utf-8"))
        change(stored)
        path.write_text(json.dumps(stored), encoding="utf-8")

    return corrupt


def _malformed_entry(stored: dict[str, Any]) -> None:
    stored["entries"]["docs/usecases/core/UC-b.md"][2] = ["UC-b"]


CORRUPTIONS: dict[str, Callable[[Path], object]] = {
    "truncated": _truncate,
    "invalid JSON": lambda path: path.write_text("{not json", encoding="utf-8"),
    "not UTF-8": lambda path: path.write_bytes(b"\xff\xfe{}"),
    "another version": _rewrite(lambda stored: stored.update(version=99)),
    "a boolean version": _rewrite(lambda stored: stored.update(version=True)),
    "another fingerprint": _rewrite(lambda stored: stored.update(fingerprint="other")),
    "not the shape": lambda path: path.write_text("[]", encoding="utf-8"),
    "a NaN": lambda path: path.write_text('{"version": NaN}', encoding="utf-8"),
    "a malformed entry": _rewrite(_malformed_entry),
}


@pytest.mark.parametrize("corruption", list(CORRUPTIONS))
def test_a_corrupt_memo_gives_a_fresh_build_and_is_rewritten(
    transient: Path, write: Write, monkeypatch: pytest.MonkeyPatch, corruption: str
) -> None:
    _base(write)
    _load(transient)
    expected = _outputs_without_memo(transient, monkeypatch)
    CORRUPTIONS[corruption](transient / MEMO)
    assert _outputs(transient) == expected
    assert all("[WARN" not in stderr and "[NOTICE" not in stderr for _, _, stderr in expected)
    _assert_valid_memo(transient)
    CORRUPTIONS[corruption](transient / MEMO)
    _assert_fresh(transient)
    _assert_valid_memo(transient)


def test_a_discarded_memo_is_logged_only_under_verbose(transient: Path, write: Write) -> None:
    _base(write)
    _load(transient)
    CORRUPTIONS["invalid JSON"](transient / MEMO)
    quiet = _spec(transient, "list")
    assert "document memo" not in quiet.stderr
    CORRUPTIONS["invalid JSON"](transient / MEMO)
    index_module._parsed.clear()
    verbose = _spec(transient, "list", "-v")
    assert "document memo" in verbose.stderr and "discarded" in verbose.stderr
    assert verbose.stdout == quiet.stdout and verbose.exit_code == quiet.exit_code == 0


def test_a_directory_at_the_memo_path_is_left_alone(transient: Path, write: Write) -> None:
    _base(write)
    (transient / MEMO).mkdir(parents=True)
    (transient / MEMO / "kept").write_text("x", encoding="utf-8")
    _assert_fresh(transient)
    assert (transient / MEMO).is_dir() and [p.name for p in (transient / MEMO).iterdir()] == ["kept"]


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="needs POSIX permissions without root")
def test_an_unwritable_memo_directory_is_left_as_it_was(transient: Path, write: Write) -> None:
    _base(write)
    spec = transient / ".devkit/transient/spec"
    spec.mkdir()
    spec.chmod(0o555)
    try:
        _assert_fresh(transient)
        assert list(spec.iterdir()) == []
    finally:
        spec.chmod(0o755)


# --- concurrency ----------------------------------------------------------------------------------------------------


def _concurrent_loads(root: Path, count: int) -> tuple[list[tuple[Any, ...]], list[BaseException]]:
    """``count`` threads load ``root`` at once; their views and errors."""
    barrier = threading.Barrier(count)
    views: list[tuple[Any, ...]] = []
    errors: list[BaseException] = []

    def load() -> None:
        try:
            barrier.wait()
            views.append(_view(DocumentIndex.load(root)))
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=load) for _ in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return views, errors


def test_concurrent_loads_all_equal_a_fresh_build_and_leave_a_valid_memo(transient: Path, write: Write) -> None:
    _base(write)
    for round_ in range(3):
        write(f"docs/usecases/core/UC-round{round_}.md", _doc(f"UC-round{round_}", "`UC-b`\n"))
        expected = _view(_fresh(transient))
        views, errors = _concurrent_loads(transient, 8)
        assert errors == [] and views == [expected] * 8
        _assert_valid_memo(transient)
        index_module._parsed.clear()


# --- where no memo belongs -----------------------------------------------------------------------------------------


def test_a_workspace_without_transient_gets_no_memo(workspace: Path, write: Write) -> None:
    _base(write)
    before = sorted(p.relative_to(workspace) for p in workspace.rglob("*"))
    assert _view(_load(workspace)) == _view(_fresh(workspace))
    assert sorted(p.relative_to(workspace) for p in workspace.rglob("*")) == before


@pytest.mark.parametrize("link", [".devkit/transient", ".devkit/transient/spec", MEMO, ".devkit"])
def test_a_symbolic_link_on_the_way_is_not_followed(tmp_path: Path, link: str) -> None:
    root, outside = tmp_path / "root", tmp_path / "outside"
    outside.mkdir()
    (root / "docs").mkdir(parents=True)
    (root / "docs/a.md").write_text(_doc("CAP-A-a"), encoding="utf-8")
    (root / link).parent.mkdir(parents=True, exist_ok=True)
    if link == MEMO:
        (outside / "memo.json").write_text("outside", encoding="utf-8")
        (root / link).symlink_to(outside / "memo.json")
    else:
        if link == ".devkit/transient/spec":
            (outside / "spec").mkdir()
        (outside / "transient").mkdir(exist_ok=True)
        (root / link).symlink_to(outside / Path(link).name if link != ".devkit" else outside)
    before = sorted((p.relative_to(outside), p.read_bytes() if p.is_file() else b"") for p in outside.rglob("*"))
    assert _view(_load(root)) == _view(_fresh(root))
    after = sorted((p.relative_to(outside), p.read_bytes() if p.is_file() else b"") for p in outside.rglob("*"))
    assert after == before


# --- writers --------------------------------------------------------------------------------------------------------


def test_an_unchanged_workspace_leaves_the_memo_untouched(transient: Path, write: Write) -> None:
    _base(write)
    write("docs/usecases/core/UC-nan.md", _doc("UC-nan", weight=".nan"))
    (transient / "docs/usecases/core/UC-binary.md").write_bytes(b"---\nid: UC-binary\xff\n---\n")
    _load(transient)
    assert _memo(transient)["entries"]["docs/usecases/core/UC-nan.md"][1] == memo_module.UNSTORABLE
    assert "docs/usecases/core/UC-binary.md" not in _memo(transient)["entries"]
    before = ((transient / MEMO).read_bytes(), (transient / MEMO).stat().st_mtime_ns)
    for _ in range(2):
        index = _load(transient)
        assert "UC-nan" in index.by_id and len(index.problems) == 1
        assert ((transient / MEMO).read_bytes(), (transient / MEMO).stat().st_mtime_ns) == before


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="needs POSIX permissions without root")
def test_an_unreadable_file_is_no_change(transient: Path, write: Write) -> None:
    _base(write)
    locked = write("docs/usecases/core/UC-locked.md", _doc("UC-locked"))
    locked.chmod(0o000)
    try:
        _load(transient)
        before = ((transient / MEMO).read_bytes(), (transient / MEMO).stat().st_mtime_ns)
        assert len(_load(transient).problems) == 1
        assert ((transient / MEMO).read_bytes(), (transient / MEMO).stat().st_mtime_ns) == before
    finally:
        locked.chmod(0o644)


def test_loads_with_a_supplied_list_or_reader_never_write(transient: Path, write: Write, parses: list[str]) -> None:
    _base(write)
    files = sorted((transient / "docs").rglob("*.md"))
    _load(transient, files=files)
    _load(transient, read=lambda path: path.read_text(encoding="utf-8"))
    assert not (transient / ".devkit/transient/spec").exists()
    _load(transient)
    before = ((transient / MEMO).read_bytes(), (transient / MEMO).stat().st_mtime_ns)
    CHANGES["content edit"](transient)
    parses.clear()
    _load(transient, files=files)
    _load(transient, read=lambda path: path.read_text(encoding="utf-8"))
    assert parses == ["docs/capabilities/core/CAP-CORE-a.md"] * 2
    assert ((transient / MEMO).read_bytes(), (transient / MEMO).stat().st_mtime_ns) == before


def test_a_supplied_list_reuses_the_memo(transient: Path, write: Write, parses: list[str]) -> None:
    _base(write)
    _load(transient)
    parses.clear()
    files = sorted((transient / "docs").rglob("*.md"))
    _load(transient, files=files)
    assert parses == []
    shutil.rmtree(transient / ".devkit/transient/spec")
    _load(transient, files=files)
    assert len(parses) == len(files)
