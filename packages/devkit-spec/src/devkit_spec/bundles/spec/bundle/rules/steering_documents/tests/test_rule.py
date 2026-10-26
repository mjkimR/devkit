"""``RULE-steering-documents``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from devkit_agt.features.rules import Violation
from devkit_agt.features.rules.models.errors import RulesRunError
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)
COUNT = "docs/steering/ has 11 Markdown files; at most 10 are allowed"


def _found(violations: list[Violation]) -> list[tuple[str, int, str]]:
    return [(v.file, v.line, v.message) for v in violations if not v.fixed]


def _doc(title: str | None = "Product", summary: str | None = "Read before naming a feature.", body: str = "") -> str:
    lines = ["---"]
    if title is not None:
        lines.append(f"title: {title}")
    if summary is not None:
        lines.append(f"summary: {summary}")
    return "\n".join([*lines, "---", ""]) + body


def test_well_formed_files_pass(tmp_path: Path) -> None:
    files = {
        "docs/steering/glossary.md": _doc("Glossary", "Read before naming a concept.", "# Glossary\n"),
        "docs/steering/glossary.yaml": "terms: []\n",
        "docs/steering/README.md": "# Steering\n",
        "docs/steering/product.md": _doc(body="# Product\n"),
    }
    assert check(RULE, tmp_path, files) == []


@pytest.mark.parametrize(
    ("path", "text", "expected"),
    [
        ("docs/steering/sub/a.md", _doc(), (1, "steering documents live directly in docs/steering/, not in sub/")),
        (
            "docs/steering/sub/README.md",
            "# x\n",
            (1, "steering documents live directly in docs/steering/, not in sub/"),
        ),
        ("docs/steering/notes.txt", "x\n", (1, "docs/steering/ holds only Markdown files and glossary.yaml")),
        ("docs/steering/other.yaml", "x: 1\n", (1, "docs/steering/ holds only Markdown files and glossary.yaml")),
        ("docs/steering/a.md", "---\nid: CAP-A-a\n" + _doc()[4:], (2, "steering documents carry no id")),
        ("docs/steering/a.md", _doc(title=None), (1, "steering document has no title")),
        ("docs/steering/a.md", _doc(title='""'), (2, "steering document has no title")),
        ("docs/steering/a.md", _doc(summary=None), (1, "steering document has no summary")),
        ("docs/steering/a.md", _doc(summary="[a]"), (3, "steering document has no summary")),
        ("docs/steering/a.md", _doc(summary="제품 소개"), (3, "summary must be English; it contains 제품소개")),
        ("docs/steering/a.md", _doc(summary="x" * 301), (3, "summary has 301 characters (300 at most)")),
        ("docs/steering/a.md", "---\ntitle: [\n---\n", (1, "steering document frontmatter is invalid")),
    ],
    ids=[
        "subdirectory",
        "subdirectory-readme",
        "other-file",
        "other-yaml",
        "id",
        "no-title",
        "empty-title",
        "no-summary",
        "non-string-summary",
        "foreign-summary",
        "long-summary",
        "invalid-frontmatter",
    ],
)
def test_shape_and_frontmatter_findings(tmp_path: Path, path: str, text: str, expected: tuple[int, str]) -> None:
    found = _found(check(RULE, tmp_path, {path: text}))
    assert len(found) == 1, found
    file, line, message = found[0]
    assert (file, line) == (path, expected[0]) and message.startswith(expected[1])


def test_a_missing_title_and_summary_on_a_file_without_frontmatter(tmp_path: Path) -> None:
    assert _found(check(RULE, tmp_path, {"docs/steering/a.md": "# A\n"})) == [
        ("docs/steering/a.md", 1, "steering document has no title"),
        ("docs/steering/a.md", 1, "steering document has no summary"),
    ]


def test_body_size_limit_and_setting(tmp_path: Path) -> None:
    exact = {"docs/steering/a.md": _doc(body="x" * 24576)}
    assert check(RULE, tmp_path / "exact", exact) == []
    over = {"docs/steering/a.md": _doc(body="x" * 24577)}
    assert _found(check(RULE, tmp_path / "over", over)) == [
        ("docs/steering/a.md", 5, "body has 24577 bytes; at most 24576 are allowed")
    ]
    assert check(RULE, tmp_path / "over", settings={"max_body_bytes": 30000}) == []


def _eleven() -> dict[str, str]:
    files = {f"docs/steering/topic-{number:02}.md": _doc() for number in range(11)}
    files["docs/steering/README.md"] = "# Steering\n"
    return files


def test_file_count_limit_reports_each_file_beyond_it(tmp_path: Path) -> None:
    assert _found(check(RULE, tmp_path, _eleven())) == [("docs/steering/topic-10.md", 1, COUNT)]
    assert check(RULE, tmp_path, settings={"max_files": 11}) == []
    assert _found(check(RULE, tmp_path, targets=["docs/steering/topic-00.md"])) == [
        ("docs/steering/topic-10.md", 1, COUNT)
    ]


def test_nothing_is_reported_when_no_steering_file_is_targeted(tmp_path: Path) -> None:
    files = {**_eleven(), "docs/other.md": "# Other\n", "docs/steering/sub/a.md": "x\n"}
    assert check(RULE, tmp_path, files, targets=["docs/other.md"]) == []


def test_a_staged_commit_adding_the_eleventh_file_is_reported(tmp_path: Path) -> None:
    from devkit_agt.features.rules.repositories.workspace.snapshot import git_snapshot, materialize_snapshot

    root = tmp_path / "repo"
    (root / "docs/steering").mkdir(parents=True)

    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    git("init", "-q")
    for number in range(1, 11):
        (root / f"docs/steering/topic-{number:02}.md").write_text(_doc())
    git("add", ".")
    git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "ten")
    (root / "docs/steering/topic-00.md").write_text(_doc())  # sorts first
    git("add", "docs/steering/topic-00.md")
    snapshot = git_snapshot(root, staged=True)
    materialized = tmp_path / "snapshot"
    materialize_snapshot(snapshot, materialized)
    found = _found(check(RULE, materialized, targets=list(snapshot.changed)))
    assert found == [("docs/steering/topic-10.md", 1, COUNT)]


@pytest.mark.parametrize("name", ["max_files", "max_body_bytes", "max_summary_length"])
def test_a_non_positive_setting_is_a_settings_error(tmp_path: Path, name: str) -> None:
    with pytest.raises(RulesRunError, match=name):
        check(RULE, tmp_path, {"docs/steering/a.md": _doc()}, settings={name: 0})


def test_a_file_get_context_cannot_read_is_reported(tmp_path: Path) -> None:
    """What get-context lists with null values (a non-UTF-8 file, frontmatter closing after its 4096-byte read)."""
    (tmp_path / "docs/steering").mkdir(parents=True)
    (tmp_path / "docs/steering/a.md").write_bytes(_doc().encode() + b"# Caf\xe9\n")
    late = "---\ntitle: T\nsummary: S\nnotes: |\n" + "  line\n" * 700 + "---\n"
    (tmp_path / "docs/steering/b.md").write_text(late)
    assert _found(check(RULE, tmp_path)) == [
        ("docs/steering/a.md", 1, "steering document must be UTF-8"),
        ("docs/steering/b.md", 1, f"frontmatter ends at byte {len(late)}; get-context reads only the first 4096 bytes"),
    ]
