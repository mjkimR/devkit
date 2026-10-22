"""``RULE-cli-tool-layout``: a tool's package keeps the feature layout.

Shipped by the ``cli-tool`` bundle of ``devkit-catalog`` and loaded by ``devkit rules`` from the synchronized copy.
Only paths are read. The package is the directory directly below the last ``src`` segment of a file's path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, match_path, validate_pattern
from devkit_agt.features.rules.services.builtins import BaseRule

# __about__ and _version: version modules packaging tools generate or read.
ROOT_MODULES = ("__init__", "__main__", "__about__", "_version", "cli", "errors", "base", "utils", "features")
FEATURE_MODULES = ("__init__", "cli", "mcp", "usecases", "services", "repositories", "models", "errors", "utils")

REMEDIATION = (
    "Move the code into features/<feature>/ under the layer it belongs to (cli, mcp, usecases, services,"
    " repositories, models, errors, utils); package-wide contracts go to base/, technical helpers to utils/"
)


@dataclass(frozen=True)
class LayoutSettings:
    # Source files the rule reads, as workspace-relative patterns.
    include: list[str] = field(default_factory=lambda: ["**/src/**"])
    exclude: list[str] = field(
        default_factory=lambda: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
    )
    # Further module or directory names allowed directly in the package, or in a feature, for a justified exception.
    extra_root_modules: list[str] = field(default_factory=list)
    extra_feature_modules: list[str] = field(default_factory=list)


def _below_package(rel: str) -> list[str] | None:
    """The path segments below the tool's package (``src/<package>/``), without the ``.py`` suffix; ``None`` when the
    file is not inside a package below ``src``."""
    parts = rel.split("/")
    if "src" not in parts:
        return None
    start = len(parts) - 1 - parts[::-1].index("src")
    if start > len(parts) - 3:
        return None  # the last src is not followed by a package directory and a file
    below = parts[start + 2 :]
    below[-1] = below[-1].removesuffix(".py")
    return below


def _problem(below: list[str], settings: LayoutSettings) -> str | None:
    roots = {*ROOT_MODULES, *settings.extra_root_modules}
    if below[0] not in roots:
        return f"{below[0]} is not a package-level module of the feature layout ({', '.join(sorted(roots))})"
    if below[0] != "features" or len(below) == 1:
        return None
    if len(below) == 2:
        if below[1] == "__init__":
            return None
        return f"features/{below[1]} is a module directly in features/; a feature is a directory features/<feature>/"
    layers = {*FEATURE_MODULES, *settings.extra_feature_modules}
    if below[2] not in layers:
        return f"features/{below[1]}/{below[2]} is not a layer of a feature ({', '.join(sorted(layers))})"
    return None


class LayoutRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-cli-tool-layout",
            name="cli-tool-layout",
            description="A tool's package holds only the package-level modules and features/<feature>/<layer>.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=LayoutSettings(),
            guide="guide.md",
            related=("cli-tool:cli-tool-structure",),
        )

    def validate_settings(self, settings: LayoutSettings) -> None:
        for pattern in (*settings.include, *settings.exclude):
            validate_pattern(pattern)
        for name in (*settings.extra_root_modules, *settings.extra_feature_modules):
            if not name.isidentifier():
                raise ValueError(f"{name!r} is not a module name")

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".py",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: LayoutSettings = ctx.settings(self, rel)
            if not any(match_path(pattern, rel) for pattern in settings.include):
                continue
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            below = _below_package(rel)
            problem = _problem(below, settings) if below else None
            if problem:
                violations.append(
                    Violation(rule_id=self.id, file=rel, line=1, message=problem, remediation=REMEDIATION)
                )
        return violations
