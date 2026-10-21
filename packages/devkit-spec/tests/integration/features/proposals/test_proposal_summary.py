from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_core.base.errors import ArgumentError
from devkit_core.core.frontmatter import parse
from devkit_dist.cli import cli as devkit_cli
from spec_support.proposals import MONTH, STAMP, TODAY, accept, spec_dir

from devkit_spec.base.errors import ProposalInvalidError
from devkit_spec.features.proposals import create_padr, create_proposal, create_spec, handoff_proposal

SUMMARY = "Defines how login sessions expire: sessions end after 30 minutes."
PLACEHOLDER = "# summary: <one or two English sentences: what this proposal changes and why>"


def _meta(path: Path) -> dict[str, object]:
    data = parse(path.read_text(encoding="utf-8")).data
    assert data is not None
    return data


def test_creation_commands_write_the_summary(workspace: Path) -> None:
    proposal = workspace / create_proposal(workspace, "a", summary=f"  {SUMMARY} ", today=TODAY).path
    assert _meta(proposal)["summary"] == SUMMARY
    assert PLACEHOLDER not in proposal.read_text()
    padr = workspace / create_padr(workspace, "a", "Use JWT", summary=SUMMARY, today=TODAY).path
    assert _meta(padr)["summary"] == SUMMARY
    create_spec(workspace, "b", summary=SUMMARY, day=TODAY)
    spec = spec_dir(workspace, "b") / "spec.md"
    assert _meta(spec)["summary"] == SUMMARY
    assert f"title: b\nsummary: '{SUMMARY}'\nstatus: planned" in spec.read_text()


def test_without_summary_proposal_md_has_a_placeholder(workspace: Path) -> None:
    proposal = workspace / create_proposal(workspace, "a", today=TODAY).path
    assert f"title: a\n{PLACEHOLDER}\nstatus: draft" in proposal.read_text()
    assert "summary" not in _meta(proposal)
    padr = workspace / create_padr(workspace, "a", "Use JWT", today=TODAY).path
    assert "# summary: <one or two English sentences: what is decided and why>\n" in padr.read_text()
    assert "summary" not in _meta(padr)
    create_spec(workspace, "b", day=TODAY)
    assert "summary" not in (spec_dir(workspace, "b") / "spec.md").read_text()


def test_handoff_carries_the_summary(workspace: Path) -> None:
    proposal = workspace / create_proposal(workspace, "a", summary=SUMMARY, today=TODAY).path
    create_padr(workspace, "a", "Use JWT", summary="Sessions are signed JWTs.", today=TODAY)
    accept(proposal)
    result = handoff_proposal(workspace, "a", today=TODAY)
    assert _meta(spec_dir(workspace, "a") / "spec.md")["summary"] == SUMMARY
    assert result.decisions[0].path == f"docs/decisions/{MONTH}/{STAMP}-use-jwt.md"
    assert _meta(workspace / result.decisions[0].path)["summary"] == "Sessions are signed JWTs."

    plain = workspace / create_proposal(workspace, "b", today=TODAY).path
    accept(plain)
    handoff_proposal(workspace, "b", today=TODAY)
    assert "summary" not in _meta(spec_dir(workspace, "b") / "spec.md")


@pytest.mark.parametrize("value", ["3", "[a, b]", "{a: b}"])
def test_handoff_refuses_a_summary_that_is_not_a_string(workspace: Path, value: str) -> None:
    proposal = workspace / create_proposal(workspace, "a", today=TODAY).path
    accept(proposal, f"\nsummary: {value}")
    with pytest.raises(ProposalInvalidError) as raised:
        handoff_proposal(workspace, "a", today=TODAY)
    assert raised.value.target_files == ("docs/proposals/PROP-a/proposal.md",)
    assert proposal.is_file() and not (workspace / "specs").exists()


@pytest.mark.parametrize("summary", ["", "   ", "로그인 세션을 정의한다.", "Defines the ログイン flow."])
def test_empty_or_non_english_summary_is_an_argument_error(workspace: Path, summary: str) -> None:
    with pytest.raises(ArgumentError) as raised:
        create_proposal(workspace, "a", summary=summary, today=TODAY)
    assert raised.value.target_files == ("--summary",)
    assert "English sentences" in str(raised.value.advisory.fix)
    with pytest.raises(ArgumentError):
        create_spec(workspace, "b", summary=summary, day=TODAY)
    assert not (workspace / "docs/proposals").exists() and not (workspace / "specs").exists()
    create_proposal(workspace, "c", today=TODAY)
    with pytest.raises(ArgumentError):
        create_padr(workspace, "c", "Use JWT", summary=summary, today=TODAY)
    assert not any((workspace / "docs/proposals/PROP-c/decisions").iterdir())


def test_cli_summary_option(workspace: Path) -> None:
    runner = CliRunner()
    w = ["-w", str(workspace)]
    result = runner.invoke(devkit_cli, ["spec", "proposal", "new", "a", "--summary", SUMMARY, *w])
    assert result.exit_code == 0, result.output
    assert _meta(workspace / "docs/proposals/PROP-a/proposal.md")["summary"] == SUMMARY
    result = runner.invoke(devkit_cli, ["spec", "proposal", "padr", "a", "Use JWT", "--summary", SUMMARY, *w])
    assert result.exit_code == 0, result.output
    assert _meta(workspace / "docs/proposals/PROP-a/decisions/PADR-use-jwt.md")["summary"] == SUMMARY
    result = runner.invoke(devkit_cli, ["spec", "new", "b", "--summary", SUMMARY, "--format", "json", *w])
    assert result.exit_code == 0, result.output
    assert _meta(workspace / json.loads(result.stdout)["dir"] / "spec.md")["summary"] == SUMMARY

    for args in (
        ["spec", "new", "c", "--summary", "세션"],
        ["spec", "proposal", "new", "c", "--summary", " "],
        ["spec", "proposal", "padr", "a", "Other", "--summary", "세션"],
    ):
        result = runner.invoke(devkit_cli, [*args, "--format", "json", *w])
        assert result.exit_code == 2, result.output
        error = json.loads(result.stdout)["error"]
        assert error["code"] == "ARGUMENT_INVALID"
    assert not (workspace / "docs/proposals/PROP-c").exists()
    assert not (workspace / "docs/proposals/PROP-a/decisions/PADR-other.md").exists()


@pytest.mark.parametrize("command", ["spec", "proposal", "padr"])
@pytest.mark.parametrize("use_cli", [False, True], ids=["library", "cli"])
@pytest.mark.parametrize("length", [300, 301])
def test_summary_length_boundary(workspace: Path, command: str, use_cli: bool, length: int) -> None:
    summary = "Defines " + "a" * (length - len("Defines ") - 1) + "."
    if command == "padr":
        create_proposal(workspace, "existing", today=TODAY)
        # A refused PADR must not recreate even its output directory.
        (workspace / "docs/proposals/PROP-existing/decisions").rmdir()
    before = {
        path.relative_to(workspace): path.read_bytes() if path.is_file() else None for path in workspace.rglob("*")
    }
    padded = f"  {summary} \n"
    if use_cli:
        commands = {
            "spec": ["spec", "new", "boundary"],
            "proposal": ["spec", "proposal", "new", "boundary"],
            "padr": ["spec", "proposal", "padr", "existing", "Boundary"],
        }
        result = CliRunner().invoke(
            devkit_cli,
            [*commands[command], "--summary", padded, "--format", "json", "-w", str(workspace)],
        )
        payload = json.loads(result.stdout)
        if length > 300:
            assert result.exit_code == 2, result.output
            assert payload["error"]["code"] == "ARGUMENT_INVALID"
            assert payload["error"]["advisory"]["target_files"] == ["--summary"]
        else:
            assert result.exit_code == 0, result.output
            path = workspace / (payload["dir"] + "/spec.md" if command == "spec" else payload["path"])
            assert _meta(path)["summary"] == summary
    else:

        def create() -> Path:
            if command == "spec":
                created = create_spec(workspace, "boundary", summary=padded, day=TODAY)
                return workspace / created.dir / "spec.md"
            if command == "proposal":
                return workspace / create_proposal(workspace, "boundary", summary=padded, today=TODAY).path
            return workspace / create_padr(workspace, "existing", "Boundary", summary=padded, today=TODAY).path

        if length > 300:
            with pytest.raises(ArgumentError) as raised:
                create()
            assert raised.value.code == "ARGUMENT_INVALID"
            assert raised.value.target_files == ("--summary",)
        else:
            assert _meta(create())["summary"] == summary
    if length > 300:
        after = {
            path.relative_to(workspace): path.read_bytes() if path.is_file() else None for path in workspace.rglob("*")
        }
        assert after == before
