"""``devkit rules test``: each selected rule's ``tests/`` runs in a pytest subprocess; output, exit codes and errors."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.rules import RuleRegistry
from devkit.rules.cli import cli
from devkit.rules.engine import rule_tests
from devkit.rules.engine.rule_tests import rule_folder
from testsupport.rules import write

RULE = """
from devkit.rules import RuleContext, Violation
from devkit.rules.rules import BaseRule


class {name}(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="{rule_id}", name="{rule_id}", description="test rule")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return [Violation(self.id, rel, 1, "found") for rel in ctx.changed_files]
"""

PASSING = """
from devkit.rules.testing import check, load_rule

RULE = load_rule(__file__)


def test_reports_each_target(tmp_path):
    assert [v.file for v in check(RULE, tmp_path, {"a.md": "x"}, targets=["a.md"])] == ["a.md"]
"""

FAILING = """
def test_fails():
    assert 1 == 2, "deliberate"
"""


def _rule(rules: Path, name: str, rule_id: str, tests: dict[str, str] | None = None) -> Path:
    folder = rules / name
    write(folder, "rule.py", RULE.format(name=name.title().replace("_", ""), rule_id=rule_id))
    for test, text in (tests or {}).items():
        write(folder, f"tests/{test}", text)
    return folder


def _invoke(root: Path, *args: str) -> tuple[int, str, str]:
    result = CliRunner().invoke(cli, ["test", "-w", str(root), *args])
    return result.exit_code, result.stdout, result.stderr


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "ws"
    rules = root / "rules"
    _rule(rules, "good", "RULE-good", {"test_rule.py": PASSING})
    _rule(rules, "bad", "RULE-bad", {"test_rule.py": FAILING})
    _rule(rules, "bare", "RULE-bare")
    return root


def test_passing_failing_and_missing_tests(workspace: Path) -> None:
    code, out, _ = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "RULE-good", "RULE-bad", "RULE-bare")
    assert code == 1
    lines = out.splitlines()
    assert lines[0].startswith("[RULE_TEST: RULE-good tests=rules/good/tests result=passed exit=0 log=")
    assert lines[1].startswith("[RULE_TEST: RULE-bad tests=rules/bad/tests result=failed exit=1 log=")
    assert '[RULE_TEST_SUMMARY: RULE-bad "1 failed in' in out
    assert any(line.startswith("[RULE_TEST_OUTPUT: RULE-bad shown=") for line in lines)
    assert "test_fails" in out and "deliberate" in out
    assert "[RULE_TEST: RULE-bare tests=rules/bare/tests result=no-tests exit=- log=-]" in lines
    assert lines[-1] == "[SUMMARY: rules=3 passed=1 failed=1 no_tests=1]"
    log = Path(lines[0].rsplit("log=", 1)[1].rstrip("]"))
    assert log.is_file() and "1 passed" in log.read_text()
    found = [p for p in workspace.rglob("*") if p.name in {"__pycache__", ".pytest_cache"}]
    assert found == []


def test_json_output(workspace: Path) -> None:
    code, out, _ = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "--format", "json", "RULE-bad")
    assert code == 1
    data = json.loads(out)
    assert set(data) == {"results", "summary", "notices"}
    assert data["summary"] == {"rules": 1, "passed": 0, "failed": 1, "no_tests": 0}
    (entry,) = data["results"]
    assert (entry["rule_id"], entry["tests"], entry["result"], entry["exit_code"]) == (
        "RULE-bad",
        "rules/bad/tests",
        "failed",
        1,
    )
    assert entry["summaries"][0].startswith("1 failed") and "deliberate" in entry["output"]


def test_all_rules_run_when_none_is_named_and_pytest_args_pass_through(workspace: Path) -> None:
    code, out, _ = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "--", "-k", "not test_fails")
    # Built-in rules run too; RULE-bad's only test is deselected, which pytest reports as nothing collected.
    assert code == 0, out
    assert "[RULE_TEST: RULE-bad tests=rules/bad/tests result=no-tests exit=5 " in out
    assert "[RULE_TEST: RULE-good tests=rules/good/tests result=passed exit=0 " in out
    assert "[RULE_TEST: RULE-markdown-link " in out


def test_unknown_rule_is_an_argument_error(workspace: Path) -> None:
    code, out, err = _invoke(workspace, "RULE-nope")
    assert code == 2 and out == ""
    assert "ARGUMENT_INVALID" in err and "unknown rule: RULE-nope" in err


def test_missing_pytest_is_reported(workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rule_tests, "pytest_available", lambda: False)
    code, out, err = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "RULE-good")
    assert code == 2 and out == ""
    assert "RULES_TEST_UNAVAILABLE" in err and "uv add --dev pytest" in err
    code, out, _ = _invoke(workspace, "--format", "json", "RULE-markdown-link")
    assert code == 2 and json.loads(out)["error"]["code"] == "RULES_TEST_UNAVAILABLE"


def test_loading_problems_are_warnings(workspace: Path) -> None:
    write(workspace, "rules/broken/rule.py", "raise RuntimeError('boom')\n")
    code, out, err = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "RULE-good")
    assert code == 0, out
    assert "[WARN]" in err and "RULES_LOAD_FAILED" in err


def test_rule_folder_is_the_package_root_or_the_module_directory(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    _rule(rules, "flat", "RULE-flat")
    write(rules / "nested", "__init__.py", "from .sub.impl import NestedRule\n")
    write(rules / "nested", "sub/__init__.py", "")
    write(rules / "nested", "sub/impl.py", RULE.format(name="NestedRule", rule_id="RULE-nested"))
    registry = RuleRegistry()
    registry.discover_from_dir(rules)
    assert registry.errors == []
    folders = {rule.id: rule_folder(rule) for rule in registry.get_all()}
    assert folders == {"RULE-flat": (rules / "flat").resolve(), "RULE-nested": (rules / "nested").resolve()}

    from devkit.rules.rules import MarkdownLinkRule

    folder = rule_folder(MarkdownLinkRule())
    assert folder is not None and folder.name == "markdown_link" and (folder / "tests").is_dir()


def test_runs_are_isolated_from_the_project_pytest_setup(workspace: Path) -> None:
    write(
        workspace,
        "pyproject.toml",
        '[tool.pytest.ini_options]\naddopts = ["-p", "no_such_plugin"]\nfilterwarnings = ["error"]\n',
    )
    write(
        workspace,
        "conftest.py",
        "import pytest\n\n@pytest.fixture(autouse=True)\ndef leak():\n    raise RuntimeError('project conftest applied')\n",
    )
    write(
        workspace, "rules/good/tests/test_warns.py", "import warnings\n\ndef test_warns():\n    warnings.warn('fine')\n"
    )
    code, out, _ = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "RULE-good")
    assert code == 0, out
    assert out.splitlines()[0].startswith("[RULE_TEST: RULE-good tests=rules/good/tests result=passed exit=0")
