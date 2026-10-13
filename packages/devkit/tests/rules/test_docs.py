"""The runnable examples in ``docs/rules`` execute against a real workspace."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

DOCS = Path(__file__).parents[4] / "docs/rules"
_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _blocks(name: str, marker: str) -> list[str]:
    return [block for block in _BLOCK.findall((DOCS / name).read_text("utf-8")) if marker in block]


def test_rule_authoring_example_package_and_registration_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/titled.md").write_text("# Title\n")
    (tmp_path / "docs/untitled.md").write_text("No heading\n")
    monkeypatch.chdir(tmp_path)
    package = tmp_path / "rules/doc_heading"
    (package / "tests").mkdir(parents=True)
    (helper,) = _blocks("rule-authoring.md", "def starts_with_h1(")
    (rule_source,) = _blocks("rule-authoring.md", "class DocHeadingRule(BaseRule)")
    (package / "headings.py").write_text(helper)
    (package / "rule.py").write_text(rule_source)
    (package / "guide.md").write_text("# RULE-doc-heading\n")
    (package / "tests/test_headings.py").write_text("raise RuntimeError('devkit never imports tests')\n")

    namespace: dict[str, Any] = {}
    (registration,) = _blocks("rule-authoring.md", "registry.discover_from_dir(")
    exec(registration, namespace)
    assert namespace["registry"].errors == []
    result = namespace["result"]
    assert [(v.rule_id, v.file) for v in result.violations] == [("RULE-doc-heading", "docs/untitled.md")]

    from devkit.rules import run_project_rules
    from devkit.rules.rules import guide_path

    run = run_project_rules(tmp_path, rules_dir=tmp_path / "rules")
    assert run.errors == []
    assert [v.file for v in run.result.violations if v.rule_id == "RULE-doc-heading"] == ["docs/untitled.md"]
    (rule,) = [rule for rule in run.rules if rule.id == "RULE-doc-heading"]
    assert guide_path(rule) == (package / "guide.md").resolve()


def test_reference_settings_example_runs(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "a.md").write_text("TODO: write\n")
    (workspace / "b.md").write_text("done\n")
    (workspace / ".devkit").mkdir()
    (workspace / ".devkit/config.toml").write_text('[rules.settings.RULE-banned-words]\nbanned = ["TODO", "FIXME"]\n')
    rules = tmp_path / "rules"
    (rules / "banned_words").mkdir(parents=True)
    (source,) = _blocks("reference.md", "class BannedWordsRule(BaseRule)")
    (rules / "banned_words/rule.py").write_text(source)
    from devkit.rules import run_project_rules

    run = run_project_rules(workspace, rules_dir=rules)
    assert run.errors == []
    assert [v.file for v in run.result.violations if v.rule_id == "RULE-banned-words"] == ["a.md"]
