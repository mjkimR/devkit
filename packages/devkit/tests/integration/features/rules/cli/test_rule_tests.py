"""``devkit rules test``: each selected rule's ``tests/`` runs in a pytest subprocess; output, exit codes and errors."""

from __future__ import annotations

import json
from pathlib import Path

import devkit_agt.features.rules.usecases.rule_tests as rule_tests
import pytest
from click.testing import CliRunner
from devkit_agt.features.rules import RuleRegistry
from devkit_agt.features.rules.cli import cli
from devkit_agt.features.rules.usecases.rule_tests import rule_folder
from testsupport.rules import write

RULE = """
from devkit_agt.features.rules import RuleContext, Violation
from devkit_agt.features.rules.services.builtins import BaseRule


class {name}(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="{rule_id}", name="{rule_id}", description="test rule")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return [Violation(self.id, rel, 1, "found") for rel in ctx.changed_files]
"""

PASSING = """
from devkit_agt.features.rules.services.testing import check, load_rule

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
    assert lines[-1] == "[SUMMARY: rules=3 passed=1 failed=1 no_tests=1 interrupted=0]"
    log = Path(lines[0].rsplit("log=", 1)[1].rstrip("]"))
    assert log.is_file() and "1 passed" in log.read_text()
    found = [p for p in workspace.rglob("*") if p.name in {"__pycache__", ".pytest_cache"}]
    assert found == []


def test_json_output(workspace: Path) -> None:
    code, out, _ = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "--format", "json", "RULE-bad")
    assert code == 1
    data = json.loads(out)
    assert set(data) == {"results", "summary", "notices"}
    assert data["summary"] == {"rules": 1, "passed": 0, "failed": 1, "no_tests": 0, "interrupted": 0}
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

    from devkit_agt.features.rules.services.builtins import MarkdownLinkRule

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


def test_an_override_of_the_module_alone_keeps_the_managed_guide_and_tests(tmp_path: Path) -> None:
    from devkit_agt.features.rules.services.builtins.base import guide_path
    from devkit_agt.features.rules.usecases.rule_tests import tests_directory

    managed = tmp_path / ".devkit/managed/team/rules/good"
    override = tmp_path / ".devkit/overrides/team/rules/good"
    _rule(managed.parent, "good", "RULE-good", {"test_rule.py": PASSING})
    write(managed, "guide.md", "# [RULE-good] Good\n")
    # The override holds the module alone; the guide and the tests stay in the managed copy.
    module = RULE.format(name="Good", rule_id="RULE-good")
    write(override, "rule.py", module.replace('description="test rule")', 'description="test rule", guide="guide.md")'))
    registry = RuleRegistry()
    registry.discover_from_dir(override.parent)
    (rule,) = registry.get_all()
    assert guide_path(rule) == (managed / "guide.md").resolve()
    assert tests_directory(rule) == (managed / "tests").resolve()


def test_managed_tests_kept_by_an_override_run_against_the_overridden_module(tmp_path: Path) -> None:
    import inspect

    from devkit_agt.features.rules.services.testing import load_rule
    from devkit_core.core.plugins import PluginPackage, plugin_modules

    managed = tmp_path / ".devkit/managed/team/rules/good"
    override = tmp_path / ".devkit/overrides/team/rules/good"
    _rule(managed.parent, "good", "RULE-good", {"test_rule.py": PASSING})
    write(managed, "helpers.py", "LABEL = 'managed'\n")
    # The override replaces the module alone, breaking it; its helper and its tests stay managed.
    broken = RULE.format(name="Good", rule_id="RULE-good").replace(
        'return [Violation(self.id, rel, 1, "found") for rel in ctx.changed_files]', "return []"
    )
    write(override, "rule.py", "from .helpers import LABEL\n" + broken)
    for anchor in (managed / "tests/test_rule.py", override):
        assert Path(inspect.getfile(type(load_rule(anchor)))).resolve() == (override / "rule.py").resolve()
    # As devkit loads the deployed asset: the override's module beside the managed helper.
    modules = plugin_modules([("helpers", managed / "helpers.py"), ("rule", override / "rule.py")])
    registry = RuleRegistry()
    (rule,) = registry.discover_from_packages([PluginPackage("team:good", managed, modules)])
    (result,) = rule_tests.RunRuleTestsUseCase().execute(tmp_path, [rule])
    assert result.tests == (managed / "tests").resolve()
    assert result.result is rule_tests.RuleTestResult.FAILED  # the managed tests caught the broken override


def test_with_a_receipt_load_rule_loads_only_the_files_it_lists(tmp_path: Path) -> None:
    import inspect

    from devkit_agt.features.rules.models.errors import RuleLoadError
    from devkit_agt.features.rules.services.testing import load_rule
    from testsupport.rules import digests, write_receipt

    managed = tmp_path / ".devkit/managed/team/rules/good"
    override = tmp_path / ".devkit/overrides/team/rules/good"
    _rule(managed.parent, "good", "RULE-good", {"test_rule.py": PASSING})
    write(override, "rule.py", RULE.format(name="Good", rule_id="RULE-good"))
    # Files the receipt does not list: devkit never loads them, so neither does load_rule.
    write(managed, "stray.py", RULE.format(name="Stray", rule_id="RULE-stray"))
    write(override, "extra.py", RULE.format(name="Extra", rule_id="RULE-extra"))
    managed_rule = ".devkit/managed/team/rules/good/rule.py"
    asset = {"bundle": "team", "id": "good", "kind": "rule", "paths": [".devkit/overrides/team/rules/good/rule.py"]}
    write_receipt(tmp_path, [asset], digests(tmp_path, managed_rule))
    for anchor in (managed / "tests/test_rule.py", override):
        rule = load_rule(anchor)
        assert rule.id == "RULE-good"
        assert Path(inspect.getfile(type(rule))).resolve() == (override / "rule.py").resolve()

    write(override, "rule.py", "raise RuntimeError('not loaded')\n")
    asset["paths"] = [managed_rule]
    write_receipt(tmp_path, [asset], digests(tmp_path, managed_rule))
    assert Path(inspect.getfile(type(load_rule(override)))).resolve() == (managed / "rule.py").resolve()

    (managed / "rule.py").write_text(RULE.format(name="Good", rule_id="RULE-drifted"))
    with pytest.raises(RuleLoadError, match="differs from the hash in the receipt"):
        load_rule(managed)
    write_receipt(tmp_path, [])
    with pytest.raises(RuleLoadError, match="is not a rule asset the installation receipt"):
        load_rule(managed)


def test_an_interrupted_run_prints_the_results_so_far(workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import dataclasses

    import devkit_agt.features.compact as compact

    real = compact.run_command
    calls: list[int] = []

    def interrupt_second(*args: object, **kwargs: object) -> object:
        run = real(*args, **kwargs)  # type: ignore[arg-type]
        calls.append(1)
        if len(calls) == 2:
            raise compact.CommandInterrupted(dataclasses.replace(run, interrupted=2, exit_code=130))
        return run

    monkeypatch.setattr(compact, "run_command", interrupt_second)
    code, out, _ = _invoke(workspace, "--rules-dir", str(workspace / "rules"), "RULE-good", "RULE-bad", "RULE-bare")
    lines = out.splitlines()
    assert code == 130
    assert lines[0].startswith("[RULE_TEST: RULE-good tests=rules/good/tests result=passed exit=0 ")
    assert lines[1].startswith("[RULE_TEST: RULE-bad tests=rules/bad/tests result=interrupted exit=130 ")
    assert lines[-1] == "[SUMMARY: rules=2 passed=1 failed=0 no_tests=0 interrupted=1]"


def test_opened_files_records_workspace_reads_only_while_active(tmp_path: Path) -> None:
    import os

    from devkit_agt.features.rules.services.testing import opened_files, write_files

    write_files(tmp_path, {"a.py": "x\n", "docs/b.md": "# B\n", "c.toml": "", "late.txt": ""})
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_text("x")
    with opened_files(tmp_path) as opened, opened_files(tmp_path / "docs") as docs:
        (tmp_path / "a.py").read_text()
        with open(tmp_path / "docs/b.md", "rb"):
            pass
        os.close(os.open(tmp_path / "c.toml", os.O_RDONLY))
        outside.read_text()
    (tmp_path / "late.txt").read_text()
    assert opened == {"a.py", "docs/b.md", "c.toml"} and docs == {"b.md"}
