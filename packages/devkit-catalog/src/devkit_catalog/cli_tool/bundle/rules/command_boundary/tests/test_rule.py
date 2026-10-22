"""``RULE-cli-tool-command-boundary``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Phase, RulesRunError, Severity
from devkit_agt.features.rules.services.testing import check, load_rule, write_files

RULE = load_rule(__file__)

HEAD = "import click\nfrom devkit_cli import Boundary\n\nboundary = Boundary('pkg')\n\n\n@click.group()\ndef cli():\n    pass\n"


def _found(found: list) -> list[tuple[str, int]]:
    return [(v.file, v.line) for v in found]


def test_a_command_without_a_boundary_is_reported(tmp_path: Path) -> None:  # AC-13
    source = (
        HEAD
        + "\n\n@click.command()\n@boundary\ndef guarded():\n    pass\n"
        + "\n\n@cli.command()\ndef bare():\n    pass\n"
    )
    found = check(RULE, tmp_path, {"src/pkg/cli.py": source})
    assert _found(found) == [("src/pkg/cli.py", 19)]
    assert found[0].message == (
        "Command bare has no boundary decorator (boundary); its errors bypass the output contract"
    )
    assert {(v.severity, v.phase) for v in found} == {(Severity.ERROR, Phase.LINTER)}


@pytest.mark.parametrize(
    "decorator", ["@boundary", "@boundary(json_only=True)", "@app.boundary", "@app.boundary(json_only=True)"]
)
def test_every_spelling_of_the_boundary_counts(tmp_path: Path, decorator: str) -> None:
    source = HEAD + f"\n\n@cli.command(name='x')\n{decorator}\nasync def run():\n    pass\n"
    assert check(RULE, tmp_path, {"src/pkg/cli/commands.py": source}) == []


def test_a_boundary_above_the_click_decorator_is_reported(tmp_path: Path) -> None:
    source = HEAD + "\n\n@boundary\n@cli.command()\ndef misplaced():\n    pass\n"
    found = check(RULE, tmp_path, {"src/pkg/cli.py": source})
    assert _found(found) == [("src/pkg/cli.py", 14)]
    assert found[0].message == (
        "Command misplaced has its boundary decorator above the click decorator; the group registers the command"
        " without it"
    )


def test_groups_and_files_outside_cli_modules_are_not_checked(tmp_path: Path) -> None:
    command = "import click\n\n\n@click.command()\ndef bare():\n    pass\n"
    files = {
        "src/pkg/cli.py": HEAD,  # a group without a boundary
        "src/pkg/services/scan.py": command,
        "src/pkg/tests/cli.py": command,
        "scripts/cli.py": command,
    }
    assert check(RULE, tmp_path, files) == []
    assert _found(check(RULE, tmp_path, {"src/pkg/__main__.py": command})) == [("src/pkg/__main__.py", 5)]


def test_boundary_names_and_paths_come_from_settings(tmp_path: Path) -> None:
    source = "import click\n\n\n@click.command()\n@guard\ndef run():\n    pass\n"
    files = {"src/pkg/cli.py": source, "tool/entry.py": source.replace("@guard\n", "")}
    settings = {
        "boundary_names": ["guard"],
        "include": ["**/src/**", "tool/**"],
        "cli_modules": ["**/cli.py", "tool/entry.py"],
    }
    assert _found(check(RULE, tmp_path, files, settings=settings)) == [("tool/entry.py", 5)]


def test_a_file_that_does_not_parse_is_left_to_the_language_linter(tmp_path: Path) -> None:
    assert check(RULE, tmp_path, {"src/pkg/cli.py": "def broken(:\n"}) == []


@pytest.mark.parametrize("settings", [{"boundary_names": []}, {"boundary_names": ["not a name"]}])
def test_invalid_settings_are_refused(tmp_path: Path, settings: dict) -> None:
    with pytest.raises(RulesRunError):
        check(RULE, tmp_path, {"src/pkg/cli.py": HEAD}, settings=settings)


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
    files = {"src/pkg/cli.py": HEAD + "\n\n@cli.command()\ndef bare():\n    pass\n", "src/pkg/cli/run.py": HEAD}
    _parses_through_the_shared_cache(tmp_path, monkeypatch, files)
