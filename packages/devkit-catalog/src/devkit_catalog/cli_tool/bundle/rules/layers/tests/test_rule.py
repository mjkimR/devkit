"""``RULE-cli-tool-layers``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Phase, Severity
from devkit_agt.features.rules.services.testing import check, load_rule, write_files

RULE = load_rule(__file__)
SCAN = "src/pkg/features/scan"


def _found(found: list) -> list[tuple[str, int]]:
    return sorted((v.file, v.line) for v in found)


def test_click_and_devkit_cli_stay_in_cli_modules(tmp_path: Path) -> None:  # AC-03
    both = "import click\nfrom devkit_cli import echo_json\n"
    files = {
        f"{SCAN}/services.py": "import click\n",
        f"{SCAN}/usecases.py": "from devkit_cli import Boundary\n",
        f"{SCAN}/cli.py": both,
        "src/pkg/cli.py": both,
        "src/pkg/__main__.py": "from pkg.cli import cli\n",
    }
    found = check(RULE, tmp_path, files)
    assert _found(found) == [(f"{SCAN}/services.py", 1), (f"{SCAN}/usecases.py", 1)]
    assert {v.message for v in found} == {
        "click is imported outside a CLI module",
        "devkit_cli is imported outside a CLI module",
    }
    assert {(v.severity, v.phase) for v in found} == {(Severity.ERROR, Phase.LINTER)}


def test_layers_import_downward_only(tmp_path: Path) -> None:  # AC-04
    files = {
        f"{SCAN}/models.py": "from pkg.features.scan.services import scan\n",
        f"{SCAN}/repositories.py": "from .models import Item\nfrom ..other.models import Other\n",
        f"{SCAN}/services.py": "import pkg.features.scan.repositories\n",
        f"{SCAN}/usecases.py": "\n\nfrom pkg.features.other import cli\n",
    }
    found = check(RULE, tmp_path, files)
    assert _found(found) == [(f"{SCAN}/models.py", 1), (f"{SCAN}/usecases.py", 3)]
    assert "models imports the higher layer services of its own feature" in {v.message.split(" (")[0] for v in found}


def test_relative_imports_resolve_against_the_file_package(tmp_path: Path) -> None:
    files = {
        f"{SCAN}/services.py": "from ..other.cli import command\n",
        f"{SCAN}/models.py": "from . import services\n",
        f"{SCAN}/usecases/run.py": "from ..services import scan\nfrom ..cli import group\n",
    }
    assert _found(check(RULE, tmp_path, files)) == [
        (f"{SCAN}/models.py", 1),
        (f"{SCAN}/services.py", 1),
        (f"{SCAN}/usecases/run.py", 2),
    ]


def test_command_line_libraries_are_confined_in_every_file_of_the_package(tmp_path: Path) -> None:
    files = {
        "src/pkg/features/__init__.py": "import click\n",
        f"{SCAN}/__init__.py": "from devkit_cli import Boundary\n",
        f"{SCAN}/schemas.py": "import click\nfrom pkg.features.scan.cli import scan\n",
    }
    assert _found(check(RULE, tmp_path, files)) == [
        ("src/pkg/features/__init__.py", 1),
        (f"{SCAN}/__init__.py", 1),
        (f"{SCAN}/schemas.py", 1),
    ]


def test_a_file_in_a_nested_src_directory_does_not_stop_the_run(tmp_path: Path) -> None:
    files = {"src/pkg/templates/src/x.py": "import click\n", f"{SCAN}/services.py": "import click\n"}
    assert _found(check(RULE, tmp_path, files)) == [(f"{SCAN}/services.py", 1)]


def test_transports_reach_any_lower_layer_but_lower_layers_never_reach_the_command_line(tmp_path: Path) -> None:
    files = {  # AC-05
        f"{SCAN}/cli.py": "from pkg.features.scan.usecases import Scan\nfrom pkg.features.scan import repositories\n",
        f"{SCAN}/services.py": "from pkg.cli import boundary\n",
        f"{SCAN}/mcp.py": "from .usecases.run import Scan\nfrom pkg.features.scan.utils import paths\n",
    }
    found = check(RULE, tmp_path, files)
    assert _found(found) == [(f"{SCAN}/services.py", 1)]
    assert found[0].message == "pkg.cli is the command line; only CLI modules import it"


def test_the_root_group_loads_features_lazily(tmp_path: Path) -> None:  # AC-06
    source = (
        "import click\nfrom pkg.features.scan.cli import scan\nfrom pkg import errors\n\n\n"
        "def load():\n    from pkg.features.report.cli import report\n    return report\n"
    )
    found = check(RULE, tmp_path, {"src/pkg/cli.py": source})
    assert _found(found) == [("src/pkg/cli.py", 2)]
    assert found[0].message.startswith("the root cli imports pkg.features.scan.cli at module level")


def test_package_level_modules_stay_below_features(tmp_path: Path) -> None:  # AC-07
    files = {
        "src/pkg/base/contracts.py": "from pkg.features.scan.models import Item\n",
        "src/pkg/utils/paths.py": "from pkg.base.contracts import Contract\n",
        "src/pkg/errors.py": "from devkit.advisory import AdvisoryError\n",
    }
    assert _found(check(RULE, tmp_path, files)) == [("src/pkg/base/contracts.py", 1)]


def test_annotations_only_and_feature_packages_are_not_checked(tmp_path: Path) -> None:
    files = {
        f"{SCAN}/models.py": (
            "from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    from pkg.features.scan.services import Scan\n"
        ),
        f"{SCAN}/__init__.py": "from pkg.features.scan.cli import scan\n",
        f"{SCAN}/usecases.py": "import json\nfrom other_package.features.x.cli import y\n",
        "src/pkg/tests/test_cli.py": "import click\n",
    }
    assert check(RULE, tmp_path, files) == []


def test_one_violation_per_import_statement(tmp_path: Path) -> None:
    source = "from pkg.features.scan import services, usecases\n"
    assert len(check(RULE, tmp_path, {f"{SCAN}/models.py": source})) == 1


def _parses_through_the_shared_cache(root: Path, monkeypatch: pytest.MonkeyPatch, files: dict[str, str]) -> None:
    """Run the rule on a shared cache; each Python file it scanned was parsed through ``ctx.cache`` and left intact."""
    import ast

    from devkit_agt.features.rules import RuleContext, WorkspaceCache

    write_files(root, files)
    ctx = RuleContext(workspace_root=root, cache=WorkspaceCache(root))
    RULE.check(ctx)
    original = ast.parse
    parsed: list[str] = []
    monkeypatch.setattr(ast, "parse", lambda *args, **kwargs: parsed.append(str(args[0])) or original(*args, **kwargs))
    for name in files:
        tree = ctx.cache.get_python_ast(name)
        assert ast.dump(tree, include_attributes=True) == ast.dump(
            original((root / name).read_bytes()), include_attributes=True
        )
    assert parsed == []  # the rule had already parsed every scanned file through ctx.cache


def test_sources_are_parsed_once_through_the_shared_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = {f"{SCAN}/services.py": "import click\n", f"{SCAN}/cli.py": "from .usecases import run\n"}
    _parses_through_the_shared_cache(tmp_path, monkeypatch, files)


def test_a_file_that_does_not_parse_is_left_to_the_language_linter(tmp_path: Path) -> None:
    assert check(RULE, tmp_path, {f"{SCAN}/services.py": "import click\ndef broken(:\n"}) == []
