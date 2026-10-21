"""The opt-in ``authoring`` bundle: its manifest, and its two rules run from a synchronized consumer."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.rules import resolve_managed_rules
from devkit_dist.cli import cli
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.project.repositories.receipt import load_receipt
from testsupport.rules import write

PACKAGE = Path(__file__).parents[2]
BUNDLE = PACKAGE / "src/devkit_agt/authoring_guide/bundle"


def test_presets_pair_each_playbook_with_its_rule() -> None:
    bundle = load_bundle(BUNDLE)
    assert (bundle.name, bundle.default_preset, bundle.auto_select) == ("authoring", "all", False)
    assert bundle.select(["skill-authoring"]) == {"skill-authoring", "skill-document-size"}
    assert bundle.select(["agent-guide-authoring"]) == {"agent-guide-authoring", "agent-guide-size"}
    pyproject = tomllib.loads((PACKAGE / "pyproject.toml").read_text())
    assert bundle.version == pyproject["project"]["version"]


def test_content_is_english_and_skill_documents_fit_their_own_budget() -> None:
    hangul = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")
    for path in sorted(BUNDLE.rglob("*.md")):
        assert not hangul.search(path.read_text()), path.name
        assert path.stat().st_size <= 12288, path.name


def _run(*args: str) -> str:
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output
    return result.stdout


def _violations(root: Path, *extra: str) -> dict[str, list[dict[str, object]]]:
    result = CliRunner().invoke(
        cli, ["rules", "check", "-w", str(root), "--phase", "hygiene", "--format", "json", *extra]
    )
    assert result.exit_code == 0, result.output
    found: dict[str, list[dict[str, object]]] = {}
    for item in json.loads(result.stdout)["violations"]:
        found.setdefault(str(item["rule_id"]), []).append(item)
    return found


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    _run("add", "authoring", "--workspace-root", str(root))
    return root


def test_add_deploys_both_presets_and_the_playbooks_are_searchable(consumer: Path) -> None:
    config = tomllib.loads((consumer / ".devkit/config.toml").read_text())
    assert config["presets"]["authoring"] == "all"
    for query, name in [
        ("restructure a large skill", "skill-authoring"),
        ("curate agent guide", "agent-guide-authoring"),
    ]:
        found = json.loads(_run("playbook", "search", query, "--workspace-root", str(consumer)))
        assert found["results"][0]["name"] == name


def test_deployed_rules_run_from_the_receipt(consumer: Path) -> None:
    # Each rule's behaviour is tested in its folder (rules/<name>/tests/); this checks the deployed copies load.
    write(consumer, ".agents/skills/demo/SKILL.md", "x" * 13000)
    write(consumer, "packages/app/AGENTS.md", "x" * 9000)
    found = _violations(consumer)
    assert [item["file"] for item in found["RULE-skill-document-size"]] == [".agents/skills/demo/SKILL.md"]
    assert [item["file"] for item in found["RULE-agent-guide-size"]] == ["packages/app/AGENTS.md"]


def test_rule_tests_ship_with_the_rules_and_are_never_loaded(consumer: Path) -> None:
    assert _run("bundle", "validate", str(BUNDLE))
    receipt = load_receipt(consumer)
    assert receipt is not None
    for name in ("skill_document_size", "agent_guide_size"):
        test = f".devkit/managed/authoring/rules/{name}/tests/test_rule.py"
        assert (consumer / test).is_file()
        assert test in receipt.file_records
    packages = [p for p in resolve_managed_rules(consumer).packages if "/authoring/" in p.location.as_posix()]
    assert sorted(dotted for package in packages for dotted in package.modules) == ["rule", "rule"]


def test_rules_test_runs_the_deployed_copy_without_writing_into_it(consumer: Path) -> None:
    result = CliRunner().invoke(
        cli, ["rules", "test", "-w", str(consumer), "RULE-skill-document-size", "RULE-agent-guide-size"]
    )
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert lines[0].startswith(
        "[RULE_TEST: RULE-skill-document-size tests=.devkit/managed/authoring/rules/skill_document_size/tests "
        "result=passed exit=0 log="
    )
    assert lines[-1] == "[SUMMARY: rules=2 passed=2 failed=0 no_tests=0 interrupted=0]"
    written = [p for p in (consumer / ".devkit").rglob("*") if p.name in {"__pycache__", ".pytest_cache"}]
    assert written == []
    assert _run("sync", "--check", "--workspace-root", str(consumer)) is not None
