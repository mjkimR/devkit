"""``RULE-cli-tool-heavy-imports``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Phase, RulesRunError, Severity
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)


def _found(found: list) -> list[tuple[str, int, str]]:
    return [(v.file, v.line, v.message) for v in found]


def test_only_module_level_heavy_imports_are_reported(tmp_path: Path) -> None:  # AC-15
    source = "import click\nimport httpx\n\n\ndef scan():\n    import numpy\n"
    found = check(RULE, tmp_path, {"src/pkg/cli.py": source})
    assert _found(found) == [
        ("src/pkg/cli.py", 2, "httpx is imported at module level of a CLI module; every command pays for it")
    ]
    assert {(v.severity, v.phase) for v in found} == {(Severity.ERROR, Phase.LINTER)}


def test_extra_heavy_modules_cover_the_tool_own_modules(tmp_path: Path) -> None:  # AC-15
    files = {
        "src/pkg/cli/scan.py": "from pkg.models import Model\nfrom ..models import Other\nfrom . import helpers\n",
        "src/pkg/models.py": "",
    }
    assert check(RULE, tmp_path, files) == []
    found = check(RULE, tmp_path, files, settings={"extra_heavy_modules": ["pkg.models"]})
    assert [(v.line, v.message.split(" ")[0]) for v in found] == [(1, "pkg.models"), (2, "pkg.models")]


@pytest.mark.parametrize(
    "source",
    [
        "from google.cloud import storage\n",
        "import pandas as pd\n",
        "from sqlalchemy.orm import Session\n",
        "try:\n    import requests\nexcept ImportError:\n    requests = None\n",
        "if True:\n    import rich\n",
        "class Command:\n    import pydantic\n",
    ],
)
def test_every_import_executed_at_import_time_counts(tmp_path: Path, source: str) -> None:
    assert len(check(RULE, tmp_path, {"src/pkg/__main__.py": source})) == 1


def test_annotations_only_and_non_cli_modules_are_not_reported(tmp_path: Path) -> None:
    typed = "from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    import pandas\nelse:\n    pass\n"
    qualified = "import typing\n\nif typing.TYPE_CHECKING:\n    from httpx import Client\n"
    files = {
        "src/pkg/cli.py": typed,
        "src/pkg/cli/commands.py": qualified,
        "src/pkg/services/fetch.py": "import httpx\n",
        "src/pkg/cli/tests/test_cli.py": "import httpx\n",
        "scripts/cli.py": "import httpx\n",
    }
    assert check(RULE, tmp_path, files) == []


def test_heavy_modules_replace_the_defaults(tmp_path: Path) -> None:
    source = "import httpx\nimport yaml\n"
    found = check(RULE, tmp_path, {"src/pkg/cli.py": source}, settings={"heavy_modules": ["yaml"]})
    assert [v.line for v in found] == [2]


@pytest.mark.parametrize("settings", [{"heavy_modules": ["not a module"]}, {"extra_heavy_modules": [""]}])
def test_invalid_settings_are_refused(tmp_path: Path, settings: dict) -> None:
    with pytest.raises(RulesRunError):
        check(RULE, tmp_path, {"src/pkg/cli.py": ""}, settings=settings)
