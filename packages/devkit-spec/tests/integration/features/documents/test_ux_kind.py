"""A UX document is a Living Spec document of its own kind: indexed, listed, searched and format-checked (AC-03)."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
from devkit_agt.features.rules.services.testing import check
from devkit_dist.cli import cli
from spec_support.types import Write

from devkit_spec.features.documents import DocumentIndex, Kind
from devkit_spec.features.governance.usecases.document_summary import DocumentSummaryRule
from devkit_spec.features.governance.usecases.spec_format import SpecFormatRule

LOGIN = "docs/ux/account/UX-login.md"
TEXT = (
    "---\nid: UX-login\ntitle: Login screen\n"
    'summary: "The login screen where a person signs in with an email address and a password."\n'
    "area: account\nelement: screen\nstatus: draft\n---\n# [UX-login] Login screen\n"
)


def _run(workspace: Path, *args: str) -> str:
    result = CliRunner().invoke(cli, ["spec", *args, "-w", str(workspace)])
    assert result.exit_code == 0, result.output
    return result.stdout


def test_a_ux_document_is_indexed_listed_and_searched(workspace: Path, write: Write) -> None:
    write(LOGIN, TEXT)
    document = DocumentIndex.load(workspace).resolve("UX-login")
    assert document.kind is Kind.UX and document.path == LOGIN
    assert _run(workspace, "resolve", "UX-login").startswith(f"[DOCUMENT: UX-login kind=ux status=draft path={LOGIN}")
    assert "[DOCUMENT: UX-login kind=ux" in _run(workspace, "list", "ux")
    assert "[HIT: UX-login " in _run(workspace, "search", "login screen", "--mode", "lexical")


def test_format_and_summary_rules_check_ux_documents(tmp_path: Path) -> None:
    files = {
        LOGIN: TEXT.replace("status: draft\n", ""),
        "docs/packages/api/ux/account/UX-pick.md": "---\nid: UX-pick\ntitle: Pick\nstatus: draft\n---\n# [UX-pick] P\n",
        ".devkit/config.toml": '[[tool.spec.namespaces]]\nname = "api"\npath = "packages/api"\n',
    }
    formats = [(v.file, v.message) for v in check(SpecFormatRule(), tmp_path, files)]
    assert formats == [(LOGIN, "frontmatter is missing the required field 'status'")]
    summaries = [(v.file, v.message) for v in check(DocumentSummaryRule(), tmp_path)]
    assert ("docs/packages/api/ux/account/UX-pick.md", "UX-pick has no summary") in summaries
