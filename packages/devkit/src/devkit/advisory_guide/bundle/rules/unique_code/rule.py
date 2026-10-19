"""``RULE-advisory-unique-code``: an advisory code names one condition.

Shipped by the ``advisory`` bundle (preset ``python``) and loaded by ``devkit rules`` from the synchronized copy.
The workspace's Python files are read statically (``index.py``), never imported: the classes that declare a code,
in their body or through a ``code=`` keyword at a call, must lie on one inheritance line.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass, field

from devkit.rules import Phase, RuleContext, Severity, Violation, match_path, validate_pattern
from devkit.rules.rules import BaseRule

from .index import Index, Module, Target, parse_module

REMEDIATION = (
    "Give the condition a code of its own, or derive the class from the class that owns the code"
    " (a subclass may redeclare its base's code). Callers branch on codes, so one code must not name two conditions"
)


@dataclass(frozen=True)
class UniqueCodeSettings:
    # Classes deriving from these (dotted names, resolved like imports) are advisory classes.
    bases: list[str] = field(
        default_factory=lambda: ["devkit.advisory.AdvisoryError", "devkit.advisory.error.AdvisoryError"]
    )
    exclude: list[str] = field(
        default_factory=lambda: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
    )


@dataclass(frozen=True)
class _Declaration:
    code: str
    owner: Target  # an advisory class, or a configured base outside the workspace
    file: str
    line: int


class _Analysis:
    def __init__(self, index: Index, roots: dict[str, set[Target]]) -> None:
        self.index = index
        self.roots = roots  # per file: the configured bases, resolved
        self._advisory: dict[str, bool] = {}
        self._ancestors: dict[Target, frozenset[Target]] = {}

    def is_advisory(self, target: Target, file: str) -> bool:
        if target in self.roots[file]:
            return True
        if target.kind != "class":
            return False
        if target.name not in self._advisory:
            self._advisory[target.name] = False  # a cyclic hierarchy is not advisory
            module, _ = self.index.class_node(target.name)
            self._advisory[target.name] = any(
                self.is_advisory(base, module.file) for base in self.index.bases(target.name)
            )
        return self._advisory[target.name]

    def ancestors(self, target: Target) -> frozenset[Target]:
        """``target`` and everything it derives from."""
        if target not in self._ancestors:
            self._ancestors[target] = frozenset({target})
            if target.kind == "class":
                found = {target}
                for base in self.index.bases(target.name):
                    found |= self.ancestors(base)
                self._ancestors[target] = frozenset(found)
        return self._ancestors[target]

    def declarations(self, module: Module) -> list[_Declaration]:
        found: list[_Declaration] = []
        for name, node in module.classes.items():
            owner = Target("class", f"{module.name}.{name}")
            if not self.is_advisory(owner, module.file):
                continue
            for statement in node.body:
                targets = statement.targets if isinstance(statement, ast.Assign) else []
                if isinstance(statement, ast.AnnAssign) and statement.value is not None:
                    targets = [statement.target]
                value = statement.value if isinstance(statement, ast.Assign | ast.AnnAssign) else None
                if value is None or not any(isinstance(t, ast.Name) and t.id == "code" for t in targets):
                    continue
                code = self.index.string_value(module.name, value)
                if code:
                    found.append(_Declaration(code, owner, module.file, statement.lineno))
        for node in ast.walk(module.tree):
            if not isinstance(node, ast.Call):
                continue
            keyword = next((k for k in node.keywords if k.arg == "code"), None)
            if keyword is None:
                continue
            callee = self.index.resolve_expression(module.name, node.func)
            code = self.index.string_value(module.name, keyword.value)
            if callee is not None and code and self.is_advisory(callee, module.file):
                found.append(_Declaration(code, callee, module.file, keyword.value.lineno))
        return found


def _describe(target: Target, first: _Declaration) -> str:
    return f"{target.name} ({first.file}:{first.line})" if target.kind == "class" else target.name


class AdvisoryUniqueCodeRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-advisory-unique-code",
            name="advisory-unique-code",
            description="Advisory classes declaring the same code lie on one inheritance line.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=UniqueCodeSettings(),
            guide="guide.md",
            related=("advisory:agent-advisory-python",),
        )

    def validate_settings(self, settings: UniqueCodeSettings) -> None:
        for pattern in settings.exclude:
            validate_pattern(pattern)
        for base in settings.bases:
            if "." not in base.strip(".") or not all(part.isidentifier() for part in base.split(".")):
                raise ValueError(f"bases entry {base!r} is not a dotted name such as package.module.Class")

    def check(self, ctx: RuleContext) -> list[Violation]:
        modules: list[Module] = []
        bases: dict[str, list[str]] = {}
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".py",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            settings: UniqueCodeSettings = ctx.settings(self, rel)
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            module = parse_module(rel, ctx.cache.read_text(path))
            if module is not None:
                modules.append(module)
                bases[rel] = settings.bases
        index = Index(modules)
        roots = {rel: {index.resolve_dotted(name) for name in names} for rel, names in bases.items()}
        analysis = _Analysis(index, roots)
        by_code: dict[str, list[_Declaration]] = defaultdict(list)
        for module in index.modules.values():
            for declaration in analysis.declarations(module):
                by_code[declaration.code].append(declaration)

        violations: list[Violation] = []
        for code, declarations in by_code.items():
            owners = {d.owner for d in declarations}
            heads = {o for o in owners if not any(other != o and other in analysis.ancestors(o) for other in owners)}
            if len(heads) < 2:
                continue
            first = {
                head: min((d for d in declarations if d.owner == head), key=lambda d: (d.file, d.line))
                for head in heads
            }
            for declaration in declarations:
                if declaration.owner not in heads or not ctx.is_file_targeted(declaration.file):
                    continue
                others = sorted(_describe(head, first[head]) for head in heads if head != declaration.owner)
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=declaration.file,
                        line=declaration.line,
                        message=f'Code "{code}" is also declared by {", ".join(others)}; a code names one condition',
                        remediation=REMEDIATION,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )
        return sorted(violations, key=lambda v: (v.file, v.line, v.message))
