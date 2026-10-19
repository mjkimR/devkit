"""``RULE-advisory-unique-code``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest

from devkit.rules import Phase, RulesRunError, Severity
from devkit.rules.testing import check, load_rule

RULE = load_rule(__file__)

ADVISORY = "from devkit.advisory import AdvisoryError\n\n\n"


def _found(found: list) -> list[tuple[str, int, str]]:
    return [(v.file, v.line, v.message) for v in found]


def test_unrelated_classes_declaring_one_code_are_reported(tmp_path: Path) -> None:
    files = {
        "a.py": ADVISORY + 'class A(AdvisoryError):\n    code = "DUP"\n',
        "b.py": ADVISORY + 'class B(AdvisoryError):\n    code: str = "DUP"\n',
    }
    found = check(RULE, tmp_path, files)
    assert _found(found) == [
        ("a.py", 5, 'Code "DUP" is also declared by b.B (b.py:5); a code names one condition'),
        ("b.py", 5, 'Code "DUP" is also declared by a.A (a.py:5); a code names one condition'),
    ]
    assert {(v.severity, v.phase) for v in found} == {(Severity.ERROR, Phase.LINTER)}


def test_a_subclass_may_redeclare_its_base_code(tmp_path: Path) -> None:
    files = {
        "src/kit/core.py": ADVISORY + 'class LockHeld(AdvisoryError):\n    code = "LOCK_HELD"\n',
        "src/kit/dist.py": (
            "from kit.core import LockHeld as CoreLockHeld\n"
            "from devkit.advisory import AdvisoryError\n\n"
            "class Base(AdvisoryError):\n    pass\n\n"
            'class LockHeld(Base, CoreLockHeld):\n    code = "LOCK_HELD"\n'
        ),
    }
    assert check(RULE, tmp_path, files) == []


def test_a_constructor_code_owned_by_an_unrelated_class_is_reported(tmp_path: Path) -> None:
    files = {
        "a.py": ADVISORY + 'class A(AdvisoryError):\n    code = "OWNED"\n',
        "b.py": ADVISORY + "class B(AdvisoryError):\n    pass\n\n\ndef run():\n    raise B('msg', code='OWNED')\n",
    }
    assert _found(check(RULE, tmp_path, files)) == [
        ("a.py", 5, 'Code "OWNED" is also declared by b.B (b.py:9); a code names one condition'),
        ("b.py", 9, 'Code "OWNED" is also declared by a.A (a.py:5); a code names one condition'),
    ]


def test_constructor_codes_on_one_line_are_accepted(tmp_path: Path) -> None:
    files = {
        "src/kit/errors.py": (
            ADVISORY
            + 'CODE = "REFUSED_X"\n\n'
            + 'class Refused(AdvisoryError):\n    code = "REFUSED"\n\n'
            + 'class Narrow(Refused):\n    code = "REFUSED"\n\n'
            + "def one():\n    return Refused('m', code=CODE)\n"
        ),
        "src/kit/gates.py": "from kit import errors\n\n\ndef two():\n    return errors.Refused.blocked('m', code='REFUSED_X')\n",
    }
    assert check(RULE, tmp_path, files) == []


def test_imports_resolve_to_the_defining_module(tmp_path: Path) -> None:
    files = {
        "src/kit/__init__.py": "from .core.errors import ConfigError\n",
        "src/kit/core/__init__.py": "",
        "src/kit/core/errors.py": ADVISORY + 'class ConfigError(AdvisoryError):\n    code = "CONFIG_INVALID"\n',
        "src/kit/gate/errors.py": ADVISORY + 'class ConfigError(AdvisoryError):\n    code = "GATE_CONFIG_INVALID"\n',
        "src/kit/gate/hooks.py": (
            "import kit.gate.errors as gate_errors\n"
            "from .errors import ConfigError as GateConfig\n\n"
            'class HookConfig(gate_errors.ConfigError):\n    code = "GATE_CONFIG_INVALID"\n\n'
            'class LocalConfig(GateConfig):\n    code = "GATE_CONFIG_INVALID"\n'
        ),
        "src/kit/sync.py": 'from kit import ConfigError\n\nclass SyncConfig(ConfigError):\n    code = "CONFIG_INVALID"\n',
    }
    assert check(RULE, tmp_path, files) == []


def test_bases_outside_the_workspace_count_and_other_classes_do_not(tmp_path: Path) -> None:
    files = {
        "app.py": ADVISORY + 'class A(AdvisoryError):\n    code = "DUP"\n\nclass B(AdvisoryError):\n    code = "DUP"\n',
        "other.py": 'class C(Exception):\n    code = "DUP"\n\nclass D:\n    code = "DUP"\n',
    }
    assert [(v.file, v.line) for v in check(RULE, tmp_path, files)] == [("app.py", 5), ("app.py", 8)]


def test_test_files_are_excluded_and_bases_are_configurable(tmp_path: Path) -> None:
    files = {
        "a.py": ADVISORY + 'class A(AdvisoryError):\n    code = "DUP"\n',
        "tests/test_x.py": ADVISORY + 'class T(AdvisoryError):\n    code = "DUP"\n',
        "conftest.py": ADVISORY + 'class F(AdvisoryError):\n    code = "DUP"\n',
        "ext.py": 'import lib\n\nclass X(lib.Base):\n    code = "EXT"\n\nclass Y(lib.Base):\n    code = "EXT"\n',
    }
    assert check(RULE, tmp_path, files) == []
    found = check(RULE, tmp_path, files, settings={"bases": ["lib.Base"]})
    assert [(v.file, v.line) for v in found] == [("ext.py", 4), ("ext.py", 7)]


@pytest.mark.parametrize("settings", [{"exclude": ["/abs/**"]}, {"bases": ["AdvisoryError"]}])
def test_invalid_settings_are_refused(tmp_path: Path, settings: dict) -> None:
    with pytest.raises(RulesRunError) as raised:
        check(RULE, tmp_path, settings=settings)
    assert [problem.code for problem in raised.value.problems] == ["RULES_SETTINGS_INVALID"]


def test_targets_limit_reporting_not_analysis(tmp_path: Path) -> None:
    files = {
        "a.py": ADVISORY + 'class A(AdvisoryError):\n    code = "DUP"\n',
        "b.py": ADVISORY + 'class B(AdvisoryError):\n    code = "DUP"\n',
    }
    assert _found(check(RULE, tmp_path, files, targets=["b.py"])) == [
        ("b.py", 5, 'Code "DUP" is also declared by a.A (a.py:5); a code names one condition'),
    ]


def test_unparseable_files_are_skipped(tmp_path: Path) -> None:
    files = {
        "broken.py": "class (:\n",
        "a.py": ADVISORY + 'class A(AdvisoryError):\n    code = "DUP"\n',
        "b.py": ADVISORY + 'class B(AdvisoryError):\n    code = "DUP"\n',
    }
    assert [v.file for v in check(RULE, tmp_path, files)] == ["a.py", "b.py"]
