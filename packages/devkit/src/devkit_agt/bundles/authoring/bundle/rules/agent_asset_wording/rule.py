"""``RULE-agent-asset-wording``: warn on hedges, emphatic capitals and time-relative words in agent assets.

Shipped by the ``authoring`` bundle (preset ``skill-authoring``) and loaded by
``devkit rules`` from the synchronized copy. It checks the mechanical part of
the ``agent-asset-writing`` instruction; judgment calls (a prohibition without
its alternative) stay with review. Quoted, code and template text is a mention,
not a use, and is never reported.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cache

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, match_path, validate_pattern
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_dist.features.project.repositories.receipt import load_receipt

# Project-native skills, and the agent-executed assets of bundles (in-repository bundles included).
DEFAULT_PATHS = (
    ".agents/skills/**",
    ".claude/skills/**",
    "**/bundle/skills/**",
    "**/bundle/playbooks/**",
    "**/bundle/instructions/**",
    "**/bundle/subagents/**",
)
HEDGES = ("likely", "might", "probably", "perhaps", "maybe", "possibly", "consider")
EMPHATIC = ("CRITICAL", "IMPORTANT", "ALWAYS", "NEVER", "ONLY", "NOTE", "WARNING", "DO NOT")
TIME_RELATIVE = ("recently", "currently", "nowadays", "as of now", "at the moment", "for now")

MENTION = " Put a word you mention rather than use in backticks or double quotes on one line."
CATEGORIES = (
    ("hedges", "Hedge", re.IGNORECASE, "State the condition under which the directive applies instead of hedging."),
    (
        "emphatic",
        "Emphatic capitals",
        0,
        "Give the rule force through its condition and reason; keep capitals for defined keywords (RFC 2119, EARS).",
    ),
    ("time_relative", "Time-relative word", re.IGNORECASE, "Name the version, date or ID instead."),
)

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
# Spans that may wrap: code spans within a paragraph, HTML comments (an unclosed one runs to the end).
WRAPPED = r"(?<!`)(`+)(?!`)(?:(?!\n[ \t]*\n).)+?(?<!`)\1(?!`)|<!--.*?(?:-->|\Z)"
# Jinja tags and comments, in templates only; a plain Markdown "{#anchor}" is prose.
JINJA = r"|\{\{.*?\}\}|\{%.*?%\}|\{#.*?(?:#\}|\Z)"
SPANS = re.compile(WRAPPED, re.DOTALL)
TEMPLATE_SPANS = re.compile(WRAPPED + JINJA, re.DOTALL)
# Straight and curly double quotes, on one line.
QUOTES = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”")


def _blank(found: re.Match[str]) -> str:
    return re.sub(r"[^\n]", " ", found.group())


@dataclass(frozen=True)
class AgentAssetWordingSettings:
    hedges: list[str] = field(default_factory=lambda: list(HEDGES))
    emphatic: list[str] = field(default_factory=lambda: list(EMPHATIC))
    time_relative: list[str] = field(default_factory=lambda: list(TIME_RELATIVE))
    suffixes: list[str] = field(default_factory=lambda: [".md", ".md.jinja"])
    paths: list[str] = field(default_factory=lambda: list(DEFAULT_PATHS))


@cache
def _pattern(words: tuple[str, ...], flags: int) -> re.Pattern[str] | None:
    if not words:
        return None
    phrases = sorted((r"\s+".join(map(re.escape, word.split())) for word in words), key=len, reverse=True)
    return re.compile(rf"(?<![\w-])(?:{'|'.join(phrases)})(?![\w-])", flags)


def prose_lines(text: str, *, template: bool = False) -> Iterator[tuple[int, str]]:
    """Each line number with the line's prose: fenced code, comments, quotes, code spans and Jinja tags blanked."""
    lines = text.splitlines()
    fence = ""
    for index, line in enumerate(lines):
        if fence:
            if re.fullmatch(rf"{re.escape(fence[0])}{{{len(fence)},}}", line.strip()):
                fence = ""
            lines[index] = ""
        elif opened := FENCE.match(line):
            fence = opened.group(1)
            lines[index] = ""
    prose = (TEMPLATE_SPANS if template else SPANS).sub(_blank, "\n".join(lines))
    for number, line in enumerate(prose.split("\n"), start=1):
        yield number, QUOTES.sub(" ", line)


class AgentAssetWordingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-agent-asset-wording",
            name="agent-asset-wording-check",
            description=(
                "Warn on hedges, emphatic capitals and time-relative words in skills, playbooks, instructions and"
                " role contracts."
            ),
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
            settings=AgentAssetWordingSettings(),
            guide="guide.md",
            related=("authoring:agent-asset-writing",),
        )

    def validate_settings(self, settings: AgentAssetWordingSettings) -> None:
        for name, *_ in CATEGORIES:
            for word in getattr(settings, name):
                if not word.strip() or "\n" in word:
                    raise ValueError(f"{name} entries must be non-empty single-line words, got {word!r}")
        for suffix in settings.suffixes:
            if len(suffix) < 2 or not suffix.startswith(".") or any(c in suffix for c in "/\\*?[]"):
                raise ValueError(f"suffixes must be literal dot-prefixed suffixes, got {suffix!r}")
        for pattern in settings.paths:
            validate_pattern(pattern)

    def check(self, ctx: RuleContext) -> list[Violation]:
        receipt = load_receipt(ctx.workspace_root)
        owned = set(receipt.file_records) if receipt is not None else set()
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=None):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if path.is_symlink() or rel in owned or not ctx.is_file_targeted(rel):
                continue
            settings: AgentAssetWordingSettings = ctx.settings(self, rel)
            if not rel.endswith(tuple(settings.suffixes)) or not any(match_path(p, rel) for p in settings.paths):
                continue
            checks = [
                (pattern, label, remediation)
                for name, label, flags, remediation in CATEGORIES
                if (pattern := _pattern(tuple(getattr(settings, name)), flags)) is not None
            ]
            for number, line in prose_lines(ctx.cache.read_text(path), template=rel.endswith(".jinja")):
                for pattern, label, remediation in checks:
                    violations.extend(
                        Violation(
                            rule_id=self.id,
                            file=rel,
                            line=number,
                            message=f'{label} "{" ".join(found.group().split())}"',
                            remediation=remediation + MENTION,
                            fixable=False,
                            severity=self.severity,
                            phase=self.phase,
                        )
                        for found in pattern.finditer(line)
                    )
        return violations
