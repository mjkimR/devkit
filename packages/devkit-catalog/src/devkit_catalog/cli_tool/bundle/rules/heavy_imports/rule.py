"""``RULE-cli-tool-heavy-imports``: CLI modules import heavy libraries inside the command, not at module level.

Every invocation of a tool, ``--help`` included, imports its CLI modules. A heavy library imported at module level is
paid by every command, also by the ones that never use it. Shipped by the ``cli-tool`` bundle of ``devkit-catalog``
and loaded by ``devkit rules`` from the synchronized copy. Source files are parsed, never imported.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, match_path, validate_pattern
from devkit_agt.features.rules.services.builtins import BaseRule

# Libraries whose import alone typically costs tens to hundreds of milliseconds, or pulls in a large dependency tree.
HEAVY_MODULES = [
    "aiohttp",
    "alembic",
    "anthropic",
    "asyncpg",
    "boto3",
    "botocore",
    "django",
    "fastapi",
    "flask",
    "google.cloud",
    "googleapiclient",
    "grpc",
    "httpx",
    "jax",
    "langchain",
    "langchain_core",
    "langgraph",
    "litellm",
    "llama_index",
    "matplotlib",
    "numpy",
    "openai",
    "pandas",
    "plotly",
    "polars",
    "psycopg",
    "psycopg2",
    "pyarrow",
    "pydantic",
    "pymongo",
    "redis",
    "requests",
    "rich",
    "scipy",
    "sklearn",
    "sqlalchemy",
    "starlette",
    "tensorflow",
    "tokenizers",
    "torch",
    "transformers",
    "uvicorn",
]

REMEDIATION = (
    "Import the module inside the command function (or the use case it calls) that needs it, or under"
    " `if TYPE_CHECKING:` for annotations, so other commands and --help do not pay for it"
)


@dataclass(frozen=True)
class HeavyImportsSettings:
    # Source files the rule reads, as workspace-relative patterns.
    include: list[str] = field(default_factory=lambda: ["**/src/**"])
    # Files that are CLI modules: imported by every invocation of the tool.
    cli_modules: list[str] = field(default_factory=lambda: ["**/cli.py", "**/cli/**", "**/__main__.py"])
    exclude: list[str] = field(
        default_factory=lambda: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
    )
    # Dotted module names (a name covers its submodules); replace the list to change the defaults.
    heavy_modules: list[str] = field(default_factory=lambda: list(HEAVY_MODULES))
    # Further names added to heavy_modules, such as the tool's own modules that load models or connect at import.
    extra_heavy_modules: list[str] = field(default_factory=list)


def _is_type_checking(test: ast.expr) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _module_level(statements: list[ast.stmt]) -> Iterator[ast.Import | ast.ImportFrom]:
    """The imports executed when the module is imported: module and class bodies, branches and handlers,
    not function bodies and not ``if TYPE_CHECKING:`` blocks."""
    for node in statements:
        if isinstance(node, ast.Import | ast.ImportFrom):
            yield node
        elif isinstance(node, ast.If):
            if not _is_type_checking(node.test):
                yield from _module_level(node.body)
            yield from _module_level(node.orelse)
        elif isinstance(node, ast.Try | ast.TryStar):
            yield from _module_level(node.body)
            for handler in node.handlers:
                yield from _module_level(handler.body)
            yield from _module_level(node.orelse)
            yield from _module_level(node.finalbody)
        elif isinstance(node, ast.With | ast.ClassDef):
            yield from _module_level(node.body)


def _package(rel: str) -> list[str]:
    """The package a file belongs to, from its path below the last ``src`` segment (else the workspace root)."""
    parts = rel.split("/")
    if "src" in parts[:-1]:
        parts = parts[len(parts) - 1 - parts[::-1].index("src") + 1 :]
    return parts[:-1]


def _names(node: ast.Import | ast.ImportFrom, rel: str) -> list[str]:
    """The dotted modules an import may load: ``import a.b`` -> ``a.b``; ``from a import b`` -> ``a``, ``a.b``."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if node.level:
        package = _package(rel)
        base = package[: len(package) - (node.level - 1)] if node.level - 1 <= len(package) else []
        module = ".".join([*base, *([node.module] if node.module else [])])
    else:
        module = node.module or ""
    return [module, *(f"{module}.{alias.name}" if module else alias.name for alias in node.names)]


class HeavyImportsRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-cli-tool-heavy-imports",
            name="cli-tool-heavy-imports",
            description="CLI modules import heavy libraries inside the commands that use them.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=HeavyImportsSettings(),
            guide="guide.md",
            related=("cli-tool:cli-tool-structure",),
        )

    def validate_settings(self, settings: HeavyImportsSettings) -> None:
        for pattern in (*settings.include, *settings.cli_modules, *settings.exclude):
            validate_pattern(pattern)
        for name in (*settings.heavy_modules, *settings.extra_heavy_modules):
            if not name or not all(part.isidentifier() for part in name.split(".")):
                raise ValueError(f"{name!r} is not a dotted module name such as numpy or google.cloud")

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".py",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: HeavyImportsSettings = ctx.settings(self, rel)
            if not any(match_path(pattern, rel) for pattern in settings.include):
                continue
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            if not any(match_path(pattern, rel) for pattern in settings.cli_modules):
                continue
            try:
                tree = ctx.cache.get_python_ast(path)
            except (SyntaxError, ValueError):
                continue  # the linter of the language reports it
            heavy = [*settings.heavy_modules, *settings.extra_heavy_modules]
            for node in _module_level(tree.body):
                found = next(
                    (
                        module
                        for name in _names(node, rel)
                        for module in heavy
                        if name == module or name.startswith(f"{module}.")
                    ),
                    None,
                )
                if found is None:
                    continue
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=node.lineno,
                        message=f"{found} is imported at module level of a CLI module; every command pays for it",
                        remediation=REMEDIATION,
                    )
                )
        return violations
