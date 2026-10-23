"""``RULE-advisory-unique-code``: an advisory code names one condition.

Shipped by the ``advisory`` bundle (preset ``python``) and loaded by ``devkit rules`` from the synchronized copy.
The workspace's Python files are read statically (``index.py``), never imported: a code is declared by one advisory
class and its subclasses, in their bodies or through ``code=`` keywords at calls.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from devkit_agt.features.rules import (
    FileFactsDescriptor,
    Phase,
    RuleContext,
    Severity,
    Violation,
    capture_facts_dependency,
    match_path,
    validate_pattern,
)
from devkit_agt.features.rules.services.builtins import BaseRule

from .facts import SOURCE, Expression, decode, encode, extract
from .index import SOURCE as INDEX_SOURCE
from .index import Imports, Index, Module, Target, function_imports, parse_module

FACTS = FileFactsDescriptor(
    "RULE-advisory-unique-code",
    1,
    (
        capture_facts_dependency("RULE-advisory-unique-code.rule", __file__, module_name=__name__),
        SOURCE,
        INDEX_SOURCE,
    ),
    extract,
    encode,
    decode,
)

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
    in_body: bool  # declared in the owner's class body, not passed at a call


def _calls(module: Module):
    for call in module.facts.calls:
        local: Imports = {}
        for scope in call.scopes:
            local = {**local, **function_imports(module, scope)}
        yield call, local


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
            for value, line in node.codes:
                code = self.index.string_value(module.name, value)
                if code:
                    found.append(_Declaration(code, owner, module.file, line, in_body=True))
        for node, local in _calls(module):
            code = self.index.string_value(module.name, node.code, local) if node.code is not None else None
            callee = self.callee(module, node.function, local) if code else None
            if code and callee is not None:
                found.append(_Declaration(code, callee, module.file, node.line, in_body=False))
        return found

    def callee(self, module: Module, func: Expression, local: Imports) -> Target | None:
        """The advisory class a call constructs or calls a classmethod of (``Error(...)``, ``Error.blocked(...)``)."""
        target = self.index.resolve_expression(module.name, func, local)
        if target is not None and self.is_advisory(target, module.file):
            return target
        if func.kind == "attribute" and func.parent is not None:  # a classmethod of a base outside the workspace
            owner = self.index.resolve_expression(module.name, func.parent, local)
            if owner is not None and owner.kind == "external" and self.is_advisory(owner, module.file):
                return owner
        return None

    def heads(self, declarations: list[_Declaration]) -> set[Target]:
        """The owners no other owner absorbs.

        An owner absorbs its subclasses; one that declares the code only at calls absorbs only owners that do too, so
        a code passed when raising a base never hides two subclasses declaring it.
        """
        owners = {d.owner for d in declarations}
        in_body = {d.owner for d in declarations if d.in_body}
        return {
            owner
            for owner in owners
            if not any(
                other != owner and other in self.ancestors(owner) and (other in in_body or owner not in in_body)
                for other in owners
            )
        }


def _describe(target: Target, first: _Declaration) -> str:
    return f"{target.name} ({first.file}:{first.line})" if target.kind == "class" else target.name


class AdvisoryUniqueCodeRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-advisory-unique-code",
            name="advisory-unique-code",
            description="A code is declared by one advisory class and its subclasses.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=UniqueCodeSettings(),
            guide="guide.md",
            related=("advisory:agent-advisory-python",),
            inputs=("**/*.py",),
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
        complete = True
        fact_paths: list[str] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".py",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            settings: UniqueCodeSettings = ctx.settings(self, rel)
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            try:
                facts = ctx.cache.get_file_facts(path, FACTS)
                fact_paths.append(rel)
            except (SyntaxError, ValueError):
                complete = False
                continue  # the linter of the language reports it
            module = parse_module(rel, facts)
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
            heads = analysis.heads(declarations)
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
        if complete:
            ctx.cache.complete_file_facts(FACTS, fact_paths)
        return sorted(violations, key=lambda v: (v.file, v.line, v.message))
