"""``RULE-cli-tool-layout``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Phase, RulesRunError, Severity
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)


def _files(*paths: str) -> dict[str, str]:
    return dict.fromkeys(paths, "")


def test_package_level_modules_outside_the_layout_are_reported(tmp_path: Path) -> None:  # AC-01
    files = _files(
        "src/pkg/__init__.py",
        "src/pkg/cli.py",
        "src/pkg/errors.py",
        "src/pkg/features/scan/cli.py",
        "src/pkg/usecases.py",
    )
    found = check(RULE, tmp_path, files)
    assert [(v.file, v.line) for v in found] == [("src/pkg/usecases.py", 1)]
    assert found[0].message.startswith("usecases is not a package-level module of the feature layout")
    assert {(v.severity, v.phase) for v in found} == {(Severity.ERROR, Phase.LINTER)}


def test_feature_modules_outside_the_layers_are_reported(tmp_path: Path) -> None:  # AC-02
    scan = "src/pkg/features/scan"
    files = _files(
        *(f"{scan}/{name}.py" for name in ("cli", "mcp", "services", "repositories", "models", "errors", "utils")),
        f"{scan}/usecases/run.py",
        f"{scan}/__init__.py",
        f"{scan}/helpers.py",
        "src/pkg/features/__init__.py",
        "src/pkg/features/run.py",
        "src/pkg/base/contracts.py",
        "src/pkg/utils/paths.py",
        "src/pkg/__main__.py",
    )
    assert sorted(v.file for v in check(RULE, tmp_path, files)) == ["src/pkg/features/run.py", f"{scan}/helpers.py"]


def test_files_outside_a_src_package_and_tests_are_not_checked(tmp_path: Path) -> None:
    files = _files("scripts/tool.py", "src/pkg/tests/test_scan.py", "src/conftest.py", "tool/src/x.py", "src/pkg.py")
    assert check(RULE, tmp_path, files) == []


def test_version_modules_are_allowed_and_a_nested_src_file_does_not_stop_the_run(tmp_path: Path) -> None:
    files = _files("src/pkg/__about__.py", "src/pkg/_version.py", "src/pkg/templates/src/x.py", "src/pkg/helpers.py")
    assert [v.file for v in check(RULE, tmp_path, files)] == ["src/pkg/helpers.py"]


def test_extra_modules_allow_a_justified_exception(tmp_path: Path) -> None:
    files = _files("src/pkg/plugins.py", "src/pkg/features/scan/schemas.py")
    settings = {"extra_root_modules": ["plugins"], "extra_feature_modules": ["schemas"]}
    assert check(RULE, tmp_path, files, settings=settings) == []


@pytest.mark.parametrize("settings", [{"extra_root_modules": ["not-a-name"]}, {"extra_feature_modules": [""]}])
def test_invalid_settings_are_refused(tmp_path: Path, settings: dict) -> None:
    with pytest.raises(RulesRunError):
        check(RULE, tmp_path, _files("src/pkg/cli.py"), settings=settings)
