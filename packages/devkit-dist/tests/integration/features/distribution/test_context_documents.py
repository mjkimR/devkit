"""Context documents: the ``context_documents`` manifest field and the ``documents`` list of ``devkit get-context``
(``ADR-bundle-context-lists-project-documents``), and the ``devkit.context_documents`` providers that add the
directories of the working directory (``ADR-namespace-steering-directories``, ``SPEC-namespace-steering`` AC-05 to
AC-07)."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from click.testing import CliRunner
from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles import context_documents, load_bundle
from devkit_dist.features.distribution.services.bundles.context_documents import HEADER_LIMIT
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.context import GetContext
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.distribution import cli

MANIFEST = """schema = 1
name = "team"
version = "0.1.0"
{declaration}
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
"""


def _source(tmp_path: Path, declaration: str) -> Path:
    source = tmp_path / "source"
    source.mkdir(parents=True, exist_ok=True)
    (source / "guide.md").write_text("---\nname: guide\ndescription: Use when writing.\n---\nBody.\n")
    (source / "bundle.toml").write_text(MANIFEST.format(declaration=declaration))
    return source


def _project(tmp_path: Path, declaration: str = 'context_documents = "docs/steering"') -> Path:
    target = tmp_path / "consumer"
    target.mkdir(parents=True)
    update_config(target, presets={"team": ["all"]})
    sync_project(target, [InstalledBundle("team-content", "0.1.0", load_bundle(_source(tmp_path, declaration)))])
    return target


def _doc(title: str = "Title", summary: str = "Scope of the file.") -> str:
    return f"---\ntitle: {title}\nsummary: {summary}\n---\n# Body\n"


def _documents(target: Path) -> list[dict[str, Any]]:
    return GetContext().execute(target, "team").to_dict()["documents"]


@pytest.fixture
def providers(monkeypatch: pytest.MonkeyPatch) -> list[SimpleNamespace]:
    """The ``devkit.context_documents`` entry points the test registers; none unless it appends one."""
    entries: list[SimpleNamespace] = []
    groups = {context_documents.PROVIDER_GROUP: entries}
    monkeypatch.setattr(context_documents.metadata, "entry_points", lambda group: list(groups.get(group, [])))
    return entries


def _entry(name: str, provider: Callable[..., object]) -> SimpleNamespace:
    """A ``devkit.context_documents`` entry point whose ``load()`` returns ``provider``."""
    return SimpleNamespace(name=name, value=f"pkg:{name}", load=lambda: provider)


def _namespaces(tmp_path: Path) -> Path:
    """The AC-05 fixture: the declared directory, an ``api`` mirror, a ``web`` mirror with a README, no ``gone``."""
    target = _project(tmp_path)
    for rel, title in [("docs/steering/a", "A"), ("docs/steering/b", "B"), ("docs/packages/api/steering/z", "Z")]:
        (target / f"{rel}.md").parent.mkdir(parents=True, exist_ok=True)
        (target / f"{rel}.md").write_text(_doc(title, f"Scope of {title}."))
    web = target / "docs/packages/web/steering"
    web.mkdir(parents=True)
    for name in ["c", "d", "README"]:
        (web / f"{name}.md").write_text(_doc(name.upper()))
    (target / "packages/api").mkdir(parents=True)
    return target


def _mirrors(root: Path, working: Path, directory: str) -> tuple[list[str], list[str]]:
    return ["docs/packages/api/steering"], ["docs/packages/web/steering", "docs/packages/gone/steering"]


def _invoke(*args: str) -> Any:
    return CliRunner().invoke(cli, ["get-context", "team", *args])


def _paths(documents: list[dict[str, Any]], root: Path) -> list[str]:
    return [str(Path(item["path"]).relative_to(root)) for item in documents]


def test_the_manifest_field_follows_the_seeded_target_grammar(tmp_path: Path) -> None:
    assert load_bundle(_source(tmp_path, 'context_documents = "docs/steering"')).context_documents == "docs/steering"
    assert load_bundle(_source(tmp_path, "")).context_documents is None


@pytest.mark.parametrize(
    "value",
    ["42", '""', '"/abs"', '"../up"', '"docs\\\\steering"', '".devkit/x"', '"docs/.git/x"', '"AGENTS.md"', '"a//b"'],
)
def test_an_invalid_declaration_is_bundle_invalid(tmp_path: Path, value: str) -> None:
    with pytest.raises(BundleError, match="context_documents"):
        load_bundle(_source(tmp_path, f"context_documents = {value}"))


def test_documents_lists_the_markdown_files_directly_in_the_directory(tmp_path: Path) -> None:
    target = _project(tmp_path)
    steering = target / "docs/steering"
    (steering / "sub").mkdir(parents=True)
    (steering / "b.md").write_text(_doc("B", "Second scope."))
    (steering / "a.md").write_text(_doc("A", "First scope."))
    (steering / "README.md").write_text(_doc())
    (steering / "glossary.yaml").write_text("terms: []\n")
    (steering / "sub/c.md").write_text(_doc())
    result = CliRunner().invoke(cli, ["get-context", "team", "--workspace-root", str(target)])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["documents"] == [
        {"path": str(steering / "a.md"), "title": "A", "summary": "First scope."},
        {"path": str(steering / "b.md"), "title": "B", "summary": "Second scope."},
    ]
    assert all(Path(item["path"]).is_absolute() for item in _documents(target))


def test_documents_is_empty_when_undeclared_or_absent(tmp_path: Path) -> None:
    undeclared = _project(tmp_path / "one", "")
    (undeclared / "docs/steering").mkdir(parents=True)
    (undeclared / "docs/steering/a.md").write_text(_doc())
    assert _documents(undeclared) == []
    assert _documents(_project(tmp_path / "two")) == []


def test_a_symlinked_directory_is_not_listed(tmp_path: Path) -> None:
    target = _project(tmp_path)
    real = tmp_path / "elsewhere"
    real.mkdir()
    (real / "a.md").write_text(_doc())
    (target / "docs").mkdir()
    (target / "docs/steering").symlink_to(real, target_is_directory=True)
    assert _documents(target) == []
    (target / "docs/steering").unlink()
    (target / "docs").rmdir()
    (target / "docs").symlink_to(tmp_path / "linked-docs", target_is_directory=True)
    (tmp_path / "linked-docs/steering").mkdir(parents=True)
    (tmp_path / "linked-docs/steering/a.md").write_text(_doc())
    assert _documents(target) == []


def test_symlinked_and_non_regular_entries_are_skipped(tmp_path: Path) -> None:
    target = _project(tmp_path)
    steering = target / "docs/steering"
    steering.mkdir(parents=True)
    (tmp_path / "outside.md").write_text(_doc())
    (steering / "link.md").symlink_to(tmp_path / "outside.md")
    (steering / "dir.md").mkdir()
    os.mkfifo(steering / "pipe.md")
    (steering / "real.md").write_text(_doc())
    assert [Path(item["path"]).name for item in _documents(target)] == ["real.md"]


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (b"\xff\xfe---\ntitle: T\n---\n", (None, None)),
        (b"# No frontmatter\n", (None, None)),
        (b"---\ntitle: [unclosed\n---\n", (None, None)),
        (b"---\ntitle: T\nsummary: S\n", (None, None)),
        (b"---\ntitle: 42\nsummary: [a]\n---\n", (None, None)),
        (b"---\ntitle: T\n---\n", ("T", None)),
        (b"---\ntitle: T\nsummary: S\n---\n" + "é".encode() * HEADER_LIMIT, ("T", "S")),
        (b"---\ntitle: T\n" + b"x: y\n" * HEADER_LIMIT + b"---\n", (None, None)),
        (b"---\ntitle: T\nsummary: S\n---\n# Caf\xe9\n", ("T", "S")),
        (b"---\ntitle: \xe9\nsummary: S\n---\n", (None, None)),
        (b"---\n" + b"x" * (HEADER_LIMIT - 8) + b"\n---", (None, None)),
    ],
    ids=[
        "non-utf8",
        "no-frontmatter",
        "malformed",
        "unclosed",
        "non-string",
        "missing",
        "oversized",
        "late-close",
        "non-utf8-body",
        "non-utf8-header",
        "cut-closer",
    ],
)
def test_an_unreadable_value_is_null(tmp_path: Path, content: bytes, expected: tuple[str | None, str | None]) -> None:
    target = _project(tmp_path)
    (target / "docs/steering").mkdir(parents=True)
    (target / "docs/steering/a.md").write_bytes(content)
    [document] = _documents(target)
    assert (document["title"], document["summary"]) == expected


def test_an_unreadable_file_is_listed_with_nulls(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root reads files regardless of permissions")
    target = _project(tmp_path)
    (target / "docs/steering").mkdir(parents=True)
    locked = target / "docs/steering/a.md"
    locked.write_text(_doc())
    locked.chmod(0)
    try:
        assert _documents(target) == [{"path": str(locked), "title": None, "summary": None}]
    finally:
        locked.chmod(0o644)


def test_the_list_stays_bounded_at_the_default_caps(tmp_path: Path) -> None:
    target = _project(tmp_path)
    steering = target / "docs/steering"
    steering.mkdir(parents=True)
    for number in range(10):  # RULE-steering-documents defaults: max_files 10, max_summary_length 300
        (steering / f"topic-{number}.md").write_text(_doc("t" * 60, "s" * 300))
    documents = _documents(target)
    assert len(documents) == 10
    size = len(json.dumps(documents).encode()) - sum(len(json.dumps(item["path"])) for item in documents)
    assert size <= 4096, size


def test_two_listed_directories_stay_bounded_at_the_default_caps(
    tmp_path: Path, providers: list[SimpleNamespace]
) -> None:
    target = _project(tmp_path)
    for rel in ["docs/steering", "docs/packages/api/steering"]:
        (target / rel).mkdir(parents=True)
        for number in range(10):
            (target / rel / f"topic-{number}.md").write_text(_doc("t" * 60, "s" * 300))
    providers.append(_entry("docs", lambda root, working, directory: (["docs/packages/api/steering"], [])))
    documents = _documents(target)
    assert len(documents) == 20
    size = len(json.dumps(documents).encode()) - sum(len(json.dumps(item["path"])) for item in documents)
    assert size <= 2 * 4096, size


def test_provider_directories_are_merged_and_the_mentioned_ones_counted(
    tmp_path: Path, providers: list[SimpleNamespace]
) -> None:
    target = _namespaces(tmp_path)
    providers.append(_entry("docs", _mirrors))
    result = _invoke("--workspace-root", str(target))
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["documents"] == [
        {"path": str(target / "docs/packages/api/steering/z.md"), "title": "Z", "summary": "Scope of Z."},
        {"path": str(target / "docs/steering/a.md"), "title": "A", "summary": "Scope of A."},
        {"path": str(target / "docs/steering/b.md"), "title": "B", "summary": "Scope of B."},
    ]
    assert data["documents_elsewhere"] == [{"path": str(target / "docs/packages/web/steering"), "files": 2}]
    assert data["notices"] == [] and result.stderr == ""


def test_a_listed_directory_is_not_mentioned_and_duplicates_collapse(
    tmp_path: Path, providers: list[SimpleNamespace]
) -> None:
    target = _namespaces(tmp_path)
    providers.append(
        _entry(
            "docs",
            lambda root, working, directory: (
                ["docs/packages/api/steering", "docs/steering", "docs/packages/api/steering"],
                ["docs/packages/api/steering", "docs/steering", "docs/packages/web/steering"],
            ),
        )
    )
    data = GetContext().execute(target, "team").to_dict()
    assert _paths(data["documents"], target) == [
        "docs/packages/api/steering/z.md",
        "docs/steering/a.md",
        "docs/steering/b.md",
    ]
    assert data["documents_elsewhere"] == [{"path": str(target / "docs/packages/web/steering"), "files": 2}]


def test_without_a_provider_the_declared_directory_alone_is_listed(
    tmp_path: Path, providers: list[SimpleNamespace]
) -> None:
    target = _namespaces(tmp_path)
    data = GetContext().execute(target, "team").to_dict()
    assert _paths(data["documents"], target) == ["docs/steering/a.md", "docs/steering/b.md"]
    assert data["documents_elsewhere"] == [] and data["notices"] == []


def test_no_provider_runs_without_a_declared_directory(tmp_path: Path, providers: list[SimpleNamespace]) -> None:
    target = _project(tmp_path, "")
    calls: list[tuple[Path, Path, str]] = []
    providers.append(_entry("docs", lambda *args: calls.append(args) or ([], [])))
    data = GetContext().execute(target, "team").to_dict()
    assert data["documents"] == [] and data["documents_elsewhere"] == [] and calls == []


def test_the_working_directory_reaches_the_provider(
    tmp_path: Path, providers: list[SimpleNamespace], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _namespaces(tmp_path)
    calls: list[tuple[Path, Path, str]] = []
    providers.append(_entry("docs", lambda *args: calls.append(args) or _mirrors(*args)))
    monkeypatch.chdir(target)
    assert _invoke("--for", "packages/api").exit_code == 0
    monkeypatch.chdir(target / "packages/api")
    assert _invoke().exit_code == 0
    monkeypatch.chdir(tmp_path)
    assert _invoke("-w", str(target)).exit_code == 0
    GetContext().execute(target / "packages", "team")
    assert calls == [
        (target, target / "packages/api", "docs/steering"),
        (target, target / "packages/api", "docs/steering"),
        (target, target, "docs/steering"),
        (target, target, "docs/steering"),
    ]


@pytest.mark.parametrize("value", ["..", "docs/steering/a.md", "packages/missing"], ids=["outside", "file", "missing"])
def test_an_invalid_for_is_an_argument_error_before_any_provider_runs(
    tmp_path: Path, providers: list[SimpleNamespace], monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    target = _namespaces(tmp_path)
    calls: list[tuple[Path, Path, str]] = []
    providers.append(_entry("docs", lambda *args: calls.append(args) or _mirrors(*args)))
    monkeypatch.chdir(target)
    result = _invoke("--for", value)
    assert result.exit_code == 2, result.output
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "ARGUMENT_INVALID" and "--for" in error["message"]
    assert error["advisory"]["target_files"] == ["--for"]
    assert calls == []


@pytest.mark.parametrize(
    "provider",
    [
        lambda root, working, directory: (_ for _ in ()).throw(RuntimeError("registry broken")),
        lambda root, working, directory: (["../up"], []),
        lambda root, working, directory: ["docs/packages/api/steering"],
        lambda root, working, directory: ("docs/packages/api/steering", []),
        lambda root, working, directory: ([], [42]),
    ],
    ids=["raises", "unsafe", "not-a-pair", "string", "non-string-item"],
)
def test_a_failing_provider_degrades_to_the_declared_directory_with_a_warning(
    tmp_path: Path, providers: list[SimpleNamespace], provider: Callable[..., object]
) -> None:
    target = _namespaces(tmp_path)
    providers.append(_entry("docs", provider))
    result = _invoke("--workspace-root", str(target))
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert _paths(data["documents"], target) == ["docs/steering/a.md", "docs/steering/b.md"]
    assert data["documents_elsewhere"] == []
    [notice] = data["notices"]
    assert notice["code"] == "CONTEXT_DOCUMENTS_EXTENSION_FAILED" and notice["level"] == "WARNING"
    assert "context documents extension docs failed" in notice["message"]
    assert "devkit.context_documents entry point docs" in notice["advisory"]["what_to_report"]
    assert result.stderr == ""  # JSON mode: the one object carries the advisory (ARCH-08-1)
    strict = _invoke("--workspace-root", str(target), "--strict")
    assert strict.exit_code == 1 and json.loads(strict.stdout)["notices"] == data["notices"]


def test_an_entry_point_that_does_not_load_is_a_warning(tmp_path: Path, providers: list[SimpleNamespace]) -> None:
    target = _namespaces(tmp_path)

    def broken() -> object:
        raise ImportError("no module named pkg")

    providers.append(SimpleNamespace(name="broken", value="pkg:broken", load=broken))
    providers.append(_entry("docs", _mirrors))
    data = GetContext().execute(target, "team").to_dict()
    assert _paths(data["documents"], target) == [
        "docs/packages/api/steering/z.md",
        "docs/steering/a.md",
        "docs/steering/b.md",
    ]
    assert data["documents_elsewhere"] == [{"path": str(target / "docs/packages/web/steering"), "files": 2}]
    [notice] = data["notices"]
    assert notice["code"] == "CONTEXT_DOCUMENTS_EXTENSION_FAILED"
    assert notice["message"] == "context documents extension broken failed: no module named pkg"
