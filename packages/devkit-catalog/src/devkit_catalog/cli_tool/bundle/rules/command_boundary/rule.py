"""``RULE-cli-tool-command-boundary``: every click command of a CLI module goes through a boundary decorator.

Shipped by the ``cli-tool`` bundle of ``devkit-catalog`` and loaded by ``devkit rules`` from the synchronized copy.
Source files are parsed, never imported.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, match_path, validate_pattern
from devkit_agt.features.rules.services.builtins import BaseRule

REMEDIATION = (
    "Decorate the command with the tool's devkit_cli.Boundary instance, below the click decorators"
    " (@cli.command() / @FORMAT_OPTION / @boundary), so its errors, JSON output and exit codes follow the contract"
)


@dataclass(frozen=True)
class CommandBoundarySettings:
    # Source files the rule reads, as workspace-relative patterns.
    include: list[str] = field(default_factory=lambda: ["**/src/**"])
    # Files that are CLI modules: transport adapters where click commands live.
    cli_modules: list[str] = field(default_factory=lambda: ["**/cli.py", "**/cli/**", "**/__main__.py"])
    exclude: list[str] = field(
        default_factory=lambda: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
    )
    # Decorator names that count as the boundary: a name, an attribute's last part, called or not.
    boundary_names: list[str] = field(default_factory=lambda: ["boundary"])


def _decorator_name(node: ast.expr) -> str | None:
    """``boundary``, ``app.boundary``, ``boundary(json_only=True)`` and ``cli.command()`` by their last name."""
    if isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


class CommandBoundaryRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-cli-tool-command-boundary",
            name="cli-tool-command-boundary",
            description="Every click command in a CLI module is wrapped by a devkit_cli boundary decorator.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=CommandBoundarySettings(),
            guide="guide.md",
            related=("cli-tool:cli-tool-structure",),
        )

    def validate_settings(self, settings: CommandBoundarySettings) -> None:
        for pattern in (*settings.include, *settings.cli_modules, *settings.exclude):
            validate_pattern(pattern)
        if not settings.boundary_names or not all(name.isidentifier() for name in settings.boundary_names):
            raise ValueError("boundary_names must list one or more Python identifiers")

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".py",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: CommandBoundarySettings = ctx.settings(self, rel)
            if not any(match_path(pattern, rel) for pattern in settings.include):
                continue
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            if not any(match_path(pattern, rel) for pattern in settings.cli_modules):
                continue
            try:
                tree = ast.parse(ctx.cache.read_text(path), filename=rel)
            except SyntaxError:
                continue  # the linter of the language reports it
            names = set(settings.boundary_names)
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    continue
                decorators = [_decorator_name(decorator) for decorator in node.decorator_list]
                if "command" not in decorators or names & set(decorators):
                    continue
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=node.lineno,
                        message=(
                            f"Command {node.name} has no boundary decorator "
                            f"({', '.join(sorted(names))}); its errors bypass the output contract"
                        ),
                        remediation=REMEDIATION,
                    )
                )
        return violations
