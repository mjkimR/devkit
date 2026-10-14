"""``RULE-cli-contract``: citations are extracted from code only and walked through the click tree."""

from __future__ import annotations

from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from devkit.rules import RuleContext
from devkit.rules.engine.errors import RulesRunError
from devkit.rules.rules.cli_contract import CliContractRule
from devkit.rules.rules.cli_contract.citations import extract_citations, iter_option_names
from devkit.rules.testing import check


@click.group(name="devkit")
@click.option("--version", is_flag=True)
def root(version: bool) -> None:
    """The fixture command line."""


@root.group()
def scope() -> None:
    """A group of leaf commands."""


@scope.command()
@click.option("--spec")
@click.option("--request-id")
@click.option("--format", "output_format", type=click.Choice(["text", "json"]))
@click.option("--title", "-t")
@click.option("--strict/--no-strict")
def update(**_: object) -> None:
    """A leaf with options."""


@scope.command()
@click.option("-w", "--workspace-root")
def compare(**_: object) -> None:
    """A leaf with a shorthand."""


@root.group()
def workflow() -> None:
    """Nested groups."""


@workflow.group()
def envelope() -> None:
    """A group under a group."""


@envelope.command(name="new")
@click.argument("kind")
@click.option("--spec")
def envelope_new(**_: object) -> None:
    """A leaf with a positional argument."""


@root.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1, required=True, type=click.UNPROCESSED)
def run(command: tuple[str, ...]) -> None:
    """A wrapper passing options through."""


RULE = CliContractRule(root)


def _found(tmp_path: Path, text: str, **kwargs: object) -> list[tuple[int, str]]:
    return [(v.line, v.message) for v in check(RULE, tmp_path, {"docs/a.md": text}, **kwargs)]  # type: ignore[arg-type]


def test_citations_come_from_code_spans_and_fenced_lines_only() -> None:
    text = (
        "Run `devkit scope update --spec x` here; devkit scope nope in prose is no citation.\n"
        "```bash\n"
        "$ devkit workflow envelope new review --spec <dir>\n"
        "uv run --no-active devkit scope compare \\\n"
        "    -w .\n"
        "devkit scope update --format json | jq .  # piped\n"
        "devkit run -- pytest -x\n"
        "```\n"
        "`devkit.rules` and `devkit-agt` are names, not invocations.\n"
    )
    assert [(c.line, c.column, c.args) for c in extract_citations(text)] == [
        (1, 5, ("scope", "update", "--spec", "x")),
        (3, 1, ("workflow", "envelope", "new", "review", "--spec", "<dir>")),
        (4, 1, ("scope", "compare", "-w", ".")),
        (6, 1, ("scope", "update", "--format", "json")),
        (7, 1, ("run",)),
    ]


def test_option_names_of_usage_tokens() -> None:
    assert list(iter_option_names("[--staged|--ci]")) == ["--staged", "--ci"]
    assert list(iter_option_names("[--title/-t")) == ["--title", "-t"]
    assert list(iter_option_names("--format=json")) == ["--format"]
    assert list(iter_option_names("(--proposal")) == ["--proposal"]
    assert list(iter_option_names("<dir>")) == list(iter_option_names("-1")) == list(iter_option_names("-")) == []


def test_known_commands_options_and_arguments_pass(tmp_path: Path) -> None:
    text = (
        "`devkit --version`, `devkit scope`, `devkit scope update --spec x --request-id y --format json`,\n"
        "`devkit scope update --format=json --no-strict -t T`, `devkit scope compare -w <dir>`,\n"
        "`devkit scope compare (--proposal <slug> | --spec <dir>)...` is a usage line with alternatives,\n"
        "`devkit workflow envelope new review --spec <dir>`, `devkit scope <command>`, `devkit <command> --help`,\n"
        "`devkit run uv run pytest -x --tb=short`, `devkit scope update --help`.\n"
    )
    assert _found(tmp_path, text) == [
        (
            3,
            "Unknown option --proposal of 'devkit scope compare' in "
            "`devkit scope compare (--proposal <slug> | --spec <dir>)...`",
        ),
    ]


def test_unknown_commands_are_reported_once_per_citation(tmp_path: Path) -> None:
    text = "`devkit nope --bad`\n\n`devkit scope claim`\n\n`devkit workflow envelope old`\n"
    assert _found(tmp_path, text) == [
        (1, "Unknown command 'nope' of 'devkit' in `devkit nope --bad`"),
        (3, "Unknown command 'claim' of 'devkit scope' in `devkit scope claim`"),
        (5, "Unknown command 'old' of 'devkit workflow envelope' in `devkit workflow envelope old`"),
    ]


def test_options_belong_to_the_command_they_follow(tmp_path: Path) -> None:
    text = "`devkit scope update --expect a=1`\n\n`devkit scope update --version`\n\n`devkit --spec x scope`\n"
    assert _found(tmp_path, text) == [
        (1, "Unknown option --expect of 'devkit scope update' in `devkit scope update --expect a=1`"),
        (3, "Unknown option --version of 'devkit scope update' in `devkit scope update --version`"),
        (5, "Unknown option --spec of 'devkit' in `devkit --spec x scope`"),
    ]


def test_an_option_value_is_not_read_as_a_subcommand(tmp_path: Path) -> None:
    group = click.Group("devkit", params=[click.Option(["-C", "--dir"])], commands=[click.Command("sync")])
    found = check(CliContractRule(group), tmp_path, {"a.md": "`devkit -C nope sync`\n`devkit -C x nope`\n"})
    assert [(v.line, v.message) for v in found] == [(2, "Unknown command 'nope' of 'devkit' in `devkit -C x nope`")]


def test_exclude_and_unchecked_commands(tmp_path: Path) -> None:
    files = {
        "docs/decisions/adr.md": "`devkit scope finish`\n",
        "docs/plugins.md": "`devkit spec list` and `devkit scope update --planned`\n",
        "docs/guide.md": "`devkit scope finish`\n",
    }
    settings = {"exclude": ["docs/decisions/**"], "unchecked_commands": ["spec", "scope update"]}
    found = check(RULE, tmp_path, files, settings=settings)
    assert [(v.file, v.message) for v in found] == [
        ("docs/guide.md", "Unknown command 'finish' of 'devkit scope' in `devkit scope finish`")
    ]


@pytest.mark.parametrize("entry", ["", "Spec", "spec/list", "--spec"])
def test_unchecked_commands_must_be_command_paths(tmp_path: Path, entry: str) -> None:
    with pytest.raises(RulesRunError, match="unchecked_commands"):
        check(RULE, tmp_path, {"a.md": "x\n"}, settings={"unchecked_commands": [entry]})


def test_outside_a_devkit_invocation_nothing_is_checked(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("`devkit nope`\n")
    assert CliContractRule().check(RuleContext(workspace_root=tmp_path)) == []


def test_the_running_devkit_command_line_is_the_tree(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("`devkit lint`\n`devkit nope`\n")

    @click.group(name="devkit")
    def cli() -> None:
        """A command line whose own command runs the rule."""

    @cli.command()
    def lint() -> None:
        for violation in CliContractRule().check(RuleContext(workspace_root=tmp_path)):
            click.echo(violation.message)

    assert CliRunner().invoke(cli, ["lint"]).output == "Unknown command 'nope' of 'devkit' in `devkit nope`\n"
    cli.name = "other"  # another program's command line is not the contract
    assert CliRunner().invoke(cli, ["lint"]).output == ""


def test_the_devkit_command_line_itself(tmp_path: Path) -> None:
    from devkit.cli import cli

    text = (
        "`devkit rules check --staged`, `devkit rules explain RULE-cli-contract`, `devkit worktree start <slug>`,\n"
        "`devkit run -- uv run pytest -x`, `devkit rules lint`\n"
    )
    found = check(CliContractRule(cli), tmp_path, {"a.md": text})
    assert [v.message for v in found] == ["Unknown command 'lint' of 'devkit rules' in `devkit rules lint`"]
