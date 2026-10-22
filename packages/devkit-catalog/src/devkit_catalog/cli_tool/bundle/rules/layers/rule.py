"""``RULE-cli-tool-layers``: imports in a tool's package go one way, and click stays in CLI modules.

A module's layer comes from its path (the feature layout ``RULE-cli-tool-layout`` keeps), not from a base class:
``src/<package>/features/<feature>/<layer>`` or a package-level module. Imports are read statically and resolved
against the package (absolute imports with the package's name, relative ones against the file's position).
Shipped by the ``cli-tool`` bundle of ``devkit-catalog`` and loaded by ``devkit rules`` from the synchronized copy.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, match_path, validate_pattern
from devkit_agt.features.rules.services.builtins import BaseRule

# Feature layers by rank: a module imports its own rank or lower. Transports (cli, mcp) are the top; utils are
# technical helpers any layer may use.
RANK = {"models": 0, "errors": 0, "utils": 0, "repositories": 1, "services": 2, "usecases": 3, "cli": 4, "mcp": 4}
CLI_LIBRARIES = frozenset({"click", "devkit_cli"})

REMEDIATION = (
    "Keep imports downward: models, errors and utils <- repositories <- services <- usecases <- cli/mcp; click and"
    " devkit_cli only in CLI modules; the root cli names feature commands through LazyGroup strings; package-level"
    " base/, utils/ and errors import no feature"
)


@dataclass(frozen=True)
class LayersSettings:
    # Source files the rule reads, as workspace-relative patterns.
    include: list[str] = field(default_factory=lambda: ["**/src/**"])
    exclude: list[str] = field(
        default_factory=lambda: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
    )


@dataclass(frozen=True)
class _Place:
    """Where a module sits in the package: ``kind`` is ``root`` (package-level ``part``) or ``feature``."""

    kind: str
    part: str  # the package-level module, or the feature layer
    feature: str = ""


def _split(rel: str) -> tuple[str, list[str]] | None:
    """The package name and the module path below it (``.py`` removed), or ``None`` outside ``src/<package>/``."""
    parts = rel.split("/")
    if "src" not in parts:
        return None
    start = len(parts) - 1 - parts[::-1].index("src")
    if start > len(parts) - 3:
        return None  # the last src is not followed by a package directory and a file
    below = parts[start + 2 :]
    below[-1] = below[-1].removesuffix(".py")
    return parts[start + 1], below


def _place(below: list[str]) -> _Place | None:
    if below[0] == "features":
        if len(below) < 3 or below[2] == "__init__":
            return None  # features/__init__ and a feature's __init__: package management
        return _Place("feature", below[2], below[1]) if below[2] in RANK else None
    return _Place("root", below[0])


def _is_type_checking(test: ast.expr) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _imports(nodes: list[ast.AST], top: bool) -> Iterator[tuple[ast.Import | ast.ImportFrom, bool]]:
    """Every import with whether it runs when the module is imported; ``if TYPE_CHECKING:`` bodies are skipped."""
    for node in nodes:
        if isinstance(node, ast.Import | ast.ImportFrom):
            yield node, top
        elif isinstance(node, ast.If) and _is_type_checking(node.test):
            yield from _imports(list(node.orelse), top)
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            yield from _imports(list(ast.iter_child_nodes(node)), False)
        else:
            yield from _imports(list(ast.iter_child_nodes(node)), top)


def _targets(node: ast.Import | ast.ImportFrom, package: str, below: list[str]) -> list[str]:
    """Dotted names an import may load (``from a import b``: ``a`` and ``a.b``), relative ones resolved."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if node.level:
        position = [package, *below[:-1]]  # the file's package (an __init__ names its own package)
        base = position[: len(position) - (node.level - 1)] if node.level - 1 < len(position) else []
        module = ".".join([*base, *([node.module] if node.module else [])])
    else:
        module = node.module or ""
    return [module, *(f"{module}.{alias.name}" if module else alias.name for alias in node.names)]


def _problem(place: _Place | None, target: str, package: str, top: bool, cli_module: bool) -> str | None:
    head = target.split(".")[0]
    if head in CLI_LIBRARIES:
        return None if cli_module else f"{head} is imported outside a CLI module"
    parts = target.split(".")
    if place is None or parts[0] != package or len(parts) < 2:
        return None  # a file without a layer is checked for the command line libraries only
    if parts[1] in {"cli", "__main__"}:
        if cli_module:
            return None
        return f"{'.'.join(parts[:2])} is the command line; only CLI modules import it"
    if parts[1] != "features" or len(parts) < 4:
        return None  # a package-level module (base, utils, errors) or the features package itself
    layer, feature = parts[3], parts[2]
    if place.kind == "root":
        if place.part in {"base", "utils", "errors"}:
            return f"{place.part} imports the feature module {target}; package-level modules sit below features"
        if place.part == "cli" and top:
            return f"the root cli imports {target} at module level; name it in LazyGroup lazy_commands instead"
        return None
    if layer not in RANK:
        return None  # a feature's __init__ or a module the layout rule reports
    if RANK[layer] > RANK[place.part]:
        where = "its own feature" if feature == place.feature else f"feature {feature}"
        return f"{place.part} imports the higher layer {layer} of {where} ({target})"
    return None


class LayersRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-cli-tool-layers",
            name="cli-tool-layers",
            description="Imports go from transports down to models, and click stays in CLI modules.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=LayersSettings(),
            guide="guide.md",
            related=("cli-tool:cli-tool-structure",),
        )

    def validate_settings(self, settings: LayersSettings) -> None:
        for pattern in (*settings.include, *settings.exclude):
            validate_pattern(pattern)

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".py",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: LayersSettings = ctx.settings(self, rel)
            if not any(match_path(pattern, rel) for pattern in settings.include):
                continue
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            split = _split(rel)
            if split is None:
                continue
            package, below = split
            place = _place(below)  # None: a features or feature __init__, or a module outside the layers
            cli_module = place is not None and (
                (place.kind == "root" and place.part in {"cli", "__main__"})
                or (place.kind == "feature" and place.part == "cli")
            )
            try:
                tree = ast.parse(ctx.cache.read_text(path), filename=rel)
            except SyntaxError:
                continue  # the linter of the language reports it
            for node, top in _imports(list(tree.body), True):
                for target in _targets(node, package, below):
                    problem = _problem(place, target, package, top, cli_module)
                    if problem:
                        violations.append(
                            Violation(
                                rule_id=self.id, file=rel, line=node.lineno, message=problem, remediation=REMEDIATION
                            )
                        )
                        break  # one violation per import statement
        return violations
