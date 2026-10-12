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


def test_rule_authoring_example_rule_and_registration_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/titled.md").write_text("# Title\n")
    (tmp_path / "docs/untitled.md").write_text("No heading\n")
    monkeypatch.chdir(tmp_path)
    namespace: dict[str, Any] = {}
    (rule_source,) = _blocks("rule-authoring.md", "class DocHeadingRule(BaseRule)")
    (registration,) = _blocks("rule-authoring.md", "registry.register(DocHeadingRule())")
    exec(rule_source, namespace)
    exec(registration, namespace)
    result = namespace["result"]
    assert [(v.rule_id, v.file) for v in result.violations] == [("RULE-doc-heading", "docs/untitled.md")]

    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "doc_heading.py").write_text(rule_source)
    from devkit.rules import run_project_rules

    run = run_project_rules(tmp_path, rules_dir=rules)
    assert run.errors == []
    assert [v.file for v in run.result.violations if v.rule_id == "RULE-doc-heading"] == ["docs/untitled.md"]


def test_reference_settings_example_runs(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "a.md").write_text("TODO: write\n")
    (workspace / "b.md").write_text("done\n")
    (workspace / ".devkit").mkdir()
    (workspace / ".devkit/config.toml").write_text('[rules.settings.RULE-banned-words]\nbanned = ["TODO", "FIXME"]\n')
    rules = tmp_path / "rules"
    rules.mkdir()
    (source,) = _blocks("reference.md", "class BannedWordsRule(BaseRule)")
    (rules / "banned_words.py").write_text(source)
    from devkit.rules import run_project_rules

    run = run_project_rules(workspace, rules_dir=rules)
    assert run.errors == []
    assert [v.file for v in run.result.violations if v.rule_id == "RULE-banned-words"] == ["a.md"]
