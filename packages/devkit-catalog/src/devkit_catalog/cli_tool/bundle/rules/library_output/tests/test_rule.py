"""``RULE-cli-tool-library-output``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Phase, Severity
from devkit_agt.features.rules.services.testing import check, load_rule, write_files

RULE = load_rule(__file__)

WRITES = "import click\n\n\ndef run():\n    print('x')\n    click.echo('y')\n"


def _found(found: list) -> list[tuple[str, int, str]]:
    return [(v.file, v.line, v.message) for v in found]


def test_print_everywhere_and_terminal_writes_outside_cli_modules_are_reported(tmp_path: Path) -> None:  # AC-14
    files = {"src/pkg/services/scan.py": WRITES, "src/pkg/cli.py": WRITES}
    found = check(RULE, tmp_path, files)
    assert _found(found) == [
        ("src/pkg/cli.py", 5, "print() writes output outside the output contract"),
        ("src/pkg/services/scan.py", 5, "print() writes output outside the output contract"),
        ("src/pkg/services/scan.py", 6, "click.echo() writes output outside a CLI module"),
    ]
    assert {(v.severity, v.phase) for v in found} == {(Severity.ERROR, Phase.LINTER)}


def test_import_aliases_are_resolved(tmp_path: Path) -> None:
    source = (
        "import click as c\nimport sys\nfrom click import secho as say\nfrom sys import stderr\n\n\n"
        "def run():\n    c.echo('a')\n    say('b')\n    sys.stdout.write('c')\n    stderr.write('d')\n"
        "    handle.write('e')\n    logger.info('f')\n"
    )
    found = check(RULE, tmp_path, {"src/pkg/report.py": source})
    assert [(v.line, v.message.split("(")[0]) for v in found] == [
        (8, "click.echo"),
        (9, "click.secho"),
        (10, "sys.stdout.write"),
        (11, "sys.stderr.write"),
    ]


def test_files_outside_include_and_tests_are_not_checked(tmp_path: Path) -> None:
    files = {"scripts/release.py": WRITES, "src/pkg/tests/test_scan.py": WRITES, "src/pkg/conftest.py": WRITES}
    assert check(RULE, tmp_path, files) == []


def test_a_renderer_declared_as_a_cli_module_may_write(tmp_path: Path) -> None:
    source = "import click\n\n\ndef render(lines):\n    click.echo(lines)\n"
    settings = {"cli_modules": ["**/cli.py", "**/cli/**", "**/__main__.py", "src/pkg/render.py"]}
    assert check(RULE, tmp_path, {"src/pkg/render.py": source}, settings=settings) == []


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
    files = {"src/pkg/services/scan.py": WRITES, "src/pkg/cli.py": WRITES}
    _parses_through_the_shared_cache(tmp_path, monkeypatch, files)


def test_a_file_that_does_not_parse_is_left_to_the_language_linter(tmp_path: Path) -> None:
    assert check(RULE, tmp_path, {"src/pkg/services/scan.py": "print('x')\ndef broken(:\n"}) == []
