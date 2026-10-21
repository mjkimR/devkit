"""The commented config template a tool describes its ``[tool.<name>]`` tables with."""

from __future__ import annotations

import tomllib

import pytest
from devkit_dist.features.project.services.config_template import (
    TemplateKey,
    TemplateTable,
    check_tables,
    render_key,
    render_tool_template,
    uncomment,
)

TABLES = [
    TemplateTable((TemplateKey("enabled", True, "turn the tool on"),)),
    TemplateTable(
        (TemplateKey("name", help="the package name", kind="string", example="api"),),
        path=("packages",),
        help="A package.",
        array=True,
    ),
    TemplateTable(
        (
            TemplateKey("timeout", 10, "seconds per call", kind="integer from 1 to 300"),
            TemplateKey("root", help="unset: the Git directory", example="/srv/x"),
            TemplateKey("tags", ["a", "b"]),
        ),
        path=("limits",),
        help="Limits.",
    ),
]


def test_render_key_shows_the_default_its_kind_and_help() -> None:
    assert render_key(TemplateKey("timeout", 10, "seconds  per\ncall")) == "# timeout = 10  # integer; seconds per call"
    assert render_key(TemplateKey("on", False), indent="  ") == "#   on = false  # boolean"
    assert render_key(TemplateKey("mode", "warn", kind='"warn" or "block"')) == '# mode = "warn"  # "warn" or "block"'


def test_a_key_unset_by_default_shows_its_example_as_one() -> None:
    key = TemplateKey("root", help="unset: the Git directory", example="/srv/x")
    assert render_key(key) == '# root = "/srv/x"  # example; string; unset: the Git directory'
    assert render_key(key, example=True) == '# root = "/srv/x"  # string; unset: the Git directory'


def test_render_tool_template() -> None:
    assert render_tool_template("demo", TABLES) == (
        "# [tool.demo]\n"
        "#   enabled = true  # boolean; turn the tool on\n"
        "\n"
        "## A package. None by default; the values below are examples.\n"
        "# [[tool.demo.packages]]\n"
        '#   name = "api"  # string; the package name\n'
        "\n"
        "## Limits.\n"
        "# [tool.demo.limits]\n"
        "#   timeout = 10  # integer from 1 to 300; seconds per call\n"
        '#   root = "/srv/x"  # example; string; unset: the Git directory\n'
        '#   tags = ["a", "b"]  # array\n'
    )


def test_uncommenting_the_template_reads_back_its_values() -> None:
    text = render_tool_template("demo", TABLES)
    assert tomllib.loads(text) == {}
    assert tomllib.loads(uncomment(text)) == {
        "tool": {
            "demo": {
                "enabled": True,
                "packages": [{"name": "api"}],
                "limits": {"timeout": 10, "root": "/srv/x", "tags": ["a", "b"]},
            }
        }
    }


@pytest.mark.parametrize(
    ("value", "problem"),
    [
        ("tables", "returned str, expected a list of TemplateTable"),
        ([TemplateKey("x", 1)], "expected a list of TemplateTable"),
        ([TemplateTable((TemplateKey("x", 1),), path=("a.b",))], "is not made of bare TOML keys"),
        ([TemplateTable((TemplateKey("x", 1),)), TemplateTable((TemplateKey("y", 1),))], "listed twice"),
        ([TemplateTable(())], "expected one TemplateKey or more"),
        ([TemplateTable((TemplateKey("x", 1), TemplateKey("x", 2)))], "a key is listed twice"),
        ([TemplateTable((TemplateKey("a b", 1),))], "is not a bare TOML key"),
        ([TemplateTable((TemplateKey("x"),))], "neither a default nor an example"),
        ([TemplateTable((TemplateKey("x", object()),))], "key x"),
    ],
)
def test_check_tables_refuses_what_cannot_render(value: object, problem: str) -> None:
    with pytest.raises(ValueError, match=problem):
        check_tables(value)


def test_uncomment_removes_one_hash_per_line() -> None:
    assert uncomment("## prose\n# key = 1\nkept = 2\n  # indented\n") == "# prose\n key = 1\nkept = 2\n  # indented\n"
