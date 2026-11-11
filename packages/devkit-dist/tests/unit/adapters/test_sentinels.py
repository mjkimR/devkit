"""The sentinel lines and the ``--version`` option every devkit command group shares (``ARCH-08-1-agent-output``)."""

from __future__ import annotations

from importlib.metadata import version

import click
import pytest
from click.testing import CliRunner
from devkit_dist.adapters.cli import echo_page, fields_line, sentinel, version_option


def test_sentinel_and_fields_line() -> None:
    assert sentinel("DOC", "CAP-x", path="docs/a b.md", historical=False, area=None) == (
        '[DOC: CAP-x path="docs/a b.md" historical=no area=-]'
    )
    assert sentinel("EMPTY", "") == "[EMPTY: -]"
    assert fields_line("COUNT", total=3, kind="a=b") == '[COUNT: total=3 kind="a=b"]'


@pytest.mark.parametrize(
    ("total", "offset", "limit", "count", "expected"),
    [
        (
            5,
            0,
            2,
            2,
            [
                "[PAGE: total=5 offset=0 limit=2 count=2 next=2]",
                "[NEXT_CMD: uv run devkit docs list --kind 'a b' --offset 2]",
            ],
        ),
        (5, 4, 2, 1, ["[PAGE: total=5 offset=4 limit=2 count=1 next=-]"]),
        (5, 0, 0, 5, ["[PAGE: total=5 offset=0 limit=0 count=5 next=-]"]),
    ],
)
def test_echo_page(
    capsys: pytest.CaptureFixture[str], total: int, offset: int, limit: int, count: int, expected: list[str]
) -> None:
    echo_page("uv run devkit docs", total, offset, limit, count, ["list", "--kind", "a b"])
    assert capsys.readouterr().out.splitlines() == expected


@pytest.mark.parametrize(("label", "shown"), [(None, "devkit-dist"), ("devkit", "devkit")])
def test_version_option(label: str | None, shown: str) -> None:
    @click.group()
    @version_option("devkit-dist", label=label)
    def group() -> None:
        """A command group."""

    result = CliRunner().invoke(group, ["--version"])
    assert (result.exit_code, result.output) == (0, f"[VERSION: {shown} {version('devkit-dist')}]\n")
    assert f"Print a [VERSION: {shown} <version>] line and exit" in CliRunner().invoke(group, ["--help"]).output
