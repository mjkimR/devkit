"""Context documents: the ``context_documents`` manifest field and the ``documents`` list of ``devkit get-context``
(``ADR-bundle-context-lists-project-documents``)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles import load_bundle
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
