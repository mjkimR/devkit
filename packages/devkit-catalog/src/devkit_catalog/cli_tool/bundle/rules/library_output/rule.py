"""``RULE-cli-tool-library-output``: only CLI modules write output, and nothing writes with ``print``.

Shipped by the ``cli-tool`` bundle of ``devkit-catalog`` and loaded by ``devkit rules`` from the synchronized copy.
Source files are parsed, never imported; imports and their aliases are resolved per file.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, match_path, validate_pattern
from devkit_agt.features.rules.services.builtins import BaseRule

# Calls that write to the terminal; only a CLI module may make them.
WRITERS = frozenset({"click.echo", "click.secho", "sys.stdout.write", "sys.stderr.write"})

PRINT_REMEDIATION = (
    "Write a result with click.echo or devkit_cli.echo_json in the CLI module, return warnings and notices"
    " with the result for devkit_cli.echo_notices, and log diagnostics with logging (shown under -v)"
)
LIBRARY_REMEDIATION = (
    "Return the data (and its warnings and notices) to the command in the CLI module and print it there;"
    " raise an AdvisoryError for a failure and log diagnostics with logging"
)


@dataclass(frozen=True)
class LibraryOutputSettings:
    # Source files the rule reads, as workspace-relative patterns.
    include: list[str] = field(default_factory=lambda: ["**/src/**"])
    # Files that are CLI modules: the only place a tool writes to stdout and stderr.
    cli_modules: list[str] = field(default_factory=lambda: ["**/cli.py", "**/cli/**", "**/__main__.py"])
    exclude: list[str] = field(
        default_factory=lambda: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
    )


def _aliases(tree: ast.Module) -> dict[str, str]:
    """Local name -> dotted origin for every import of the file (``import click as c``, ``from sys import stdout``)."""
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    aliases[alias.asname] = alias.name
                else:
                    top = alias.name.split(".")[0]
                    aliases[top] = top
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


def _dotted(node: ast.expr, aliases: dict[str, str]) -> str | None:
    """The dotted origin of a call target (``c.echo`` -> ``click.echo``), or ``None`` for anything else."""
    attributes: list[str] = []
    while isinstance(node, ast.Attribute):
        attributes.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    return ".".join([aliases.get(node.id, node.id), *reversed(attributes)])


class LibraryOutputRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-cli-tool-library-output",
            name="cli-tool-library-output",
            description="Only CLI modules write to the terminal, and no module uses print.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=LibraryOutputSettings(),
            guide="guide.md",
            related=("cli-tool:cli-tool-structure",),
        )

    def validate_settings(self, settings: LibraryOutputSettings) -> None:
        for pattern in (*settings.include, *settings.cli_modules, *settings.exclude):
            validate_pattern(pattern)

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".py",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: LibraryOutputSettings = ctx.settings(self, rel)
            if not any(match_path(pattern, rel) for pattern in settings.include):
                continue
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            try:
                tree = ast.parse(ctx.cache.read_text(path), filename=rel)
            except SyntaxError:
                continue  # the linter of the language reports it
            cli_module = any(match_path(pattern, rel) for pattern in settings.cli_modules)
            aliases = _aliases(tree)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                target = _dotted(node.func, aliases)
                if target == "print":
                    message = "print() writes output outside the output contract"
                    remediation = PRINT_REMEDIATION
                elif target in WRITERS and not cli_module:
                    message = f"{target}() writes output outside a CLI module"
                    remediation = LIBRARY_REMEDIATION
                else:
                    continue
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=node.lineno,
                        column=node.col_offset + 1,
                        message=message,
                        remediation=remediation,
                    )
                )
        return violations
