"""Search registers use the same namespace selection as document candidates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit_dist.cli import cli
from docs_support.types import Write

CONFIG = (
    '[[tool.docs.namespaces]]\nname = "web"\npath = "apps/web"\n'
    '[[tool.docs.namespaces]]\nname = "api"\npath = "services/api"\n'
)


def _synonyms(primary: str, alias: str = "shared") -> str:
    return f"terms:\n  - primary: {primary}\n    synonyms: [{alias}]\n"


@pytest.fixture
def registers(workspace: Path, write: Write) -> Path:
    write(".devkit/config.toml", CONFIG)
    write("docs/steering/glossary.yaml", _synonyms("rootterm"))
    write("docs/packages/api/steering/glossary.yaml", _synonyms("apiterm"))
    write("docs/packages/web/steering/glossary.yaml", _synonyms("webterm"))
    write("docs/packages/unknown/steering/glossary.yaml", "terms: invalid\n")
    write("docs/capabilities/core/CAP-CORE-example.md", "---\nid: CAP-CORE-example\nstatus: active\n---\nshared\n")
    (workspace / "services/api").mkdir(parents=True)
    return workspace


def _search(root: Path, *args: str) -> Result:
    return CliRunner().invoke(
        cli, ["docs", "search", "shared", "--mode", "lexical", "--format", "json", "-w", str(root), *args]
    )


def test_selected_namespace_keeps_global_and_excludes_others(registers: Path) -> None:
    result = _search(registers, "--namespace", "api")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["expanded"] == "shared rootterm apiterm"
    assert json.loads(_search(registers, "--namespace", "global").stdout)["expanded"] == "shared rootterm"


def test_cwd_and_all_namespace_selection(registers: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(registers / "services/api")
    assert json.loads(_search(registers).stdout)["expanded"] == "shared rootterm apiterm"
    assert json.loads(_search(registers, "--all-namespaces").stdout)["expanded"] == "shared rootterm apiterm webterm"
    monkeypatch.chdir(registers)
    assert json.loads(_search(registers).stdout)["expanded"] == "shared rootterm apiterm webterm"


@pytest.mark.parametrize(
    "invalid",
    ["terms: invalid\n", "terms: [{synonyms: [alias]}]\n", "terms: [{primary: term, synonyms: invalid}]\n", ": :\n"],
)
def test_invalid_selected_file_names_actual_target(registers: Path, write: Write, invalid: str) -> None:
    path = "docs/packages/web/steering/glossary.yaml"
    write(path, invalid)
    assert _search(registers, "--namespace", "api").exit_code == 0
    result = _search(registers, "--namespace", "web")
    assert result.exit_code == 2, result.output
    payload = json.loads(result.stdout)
    assert "DOCS_GLOSSARY_INVALID" in result.stdout
    assert path in result.stdout
    assert "Correct " + path in result.stdout
    assert payload


def test_absent_namespace_register_is_optional(workspace: Path, write: Write) -> None:
    write(".devkit/config.toml", CONFIG)
    result = _search(workspace, "--namespace", "api")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["expanded"] == "shared"
