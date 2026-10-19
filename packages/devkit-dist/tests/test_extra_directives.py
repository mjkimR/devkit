"""The ``[FIX]`` of a missing ``search`` or ``mcp`` extra names the devkit requirement the project already declares.

devkit-dist never detects whether the project depends on devkit-dist or devkit-agt, so every directive names both
forms, each a full Git requirement, and never asks for a second requirement next to the first
(``ADR-dist-module-split``).
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from devkit.core.errors import AGT_REQUIREMENT, DIST_REQUIREMENT, extra_install_fix
from devkit.host.errors import HostMcpDependencyError
from devkit.search.errors import ModelNotFoundError, SearchExtraMissingError
from distsupport.distribution import cli

AGT = "devkit-agt[{extra}] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
DIST = "devkit-dist[{extra}] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"


@pytest.mark.parametrize("extra", ["search", "mcp"])
def test_the_directive_names_the_extra_on_either_requirement(extra: str) -> None:
    fix = extra_install_fix(extra)
    assert f"uv add '{AGT.format(extra=extra)}' when it depends on devkit-agt" in fix
    assert fix.endswith(f"else uv add '{DIST.format(extra=extra)}'")
    assert fix.count("uv add") == 2  # one requirement either way, never both


def test_the_requirements_are_source_explicit() -> None:
    assert AGT_REQUIREMENT == "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
    assert (
        DIST_REQUIREMENT == "devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"
    )


def test_every_missing_extra_error_uses_the_directive() -> None:
    assert SearchExtraMissingError("x").fix == extra_install_fix("search")
    assert (ModelNotFoundError("x").fix or "").endswith(extra_install_fix("search"))
    assert (HostMcpDependencyError("x").fix or "").startswith(extra_install_fix("mcp"))


def test_the_playbook_search_mode_help_names_both_extras() -> None:
    result = CliRunner().invoke(cli, ["playbook", "search", "--help"])
    assert result.exit_code == 0
    text = " ".join(result.stdout.split())
    assert "devkit-dist[search] or devkit-agt[search]" in text
