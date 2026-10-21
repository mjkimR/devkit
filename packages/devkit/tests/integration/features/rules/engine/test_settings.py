from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest
from devkit.advisory import ActionMode
from devkit_agt.features.rules import (
    Phase,
    RuleContext,
    RulesConfigError,
    SettingsError,
    SettingsResolver,
    Severity,
    Violation,
    default_rule_registry,
    evaluate_rules,
    load_rules_config,
)
from devkit_agt.features.rules.models.errors import PolicyError
from devkit_agt.features.rules.models.settings import Override, RawSettings, build_resolvers
from devkit_agt.features.rules.services.builtins import BaseRule, FileLengthRule, FileLengthSettings


def _write_config(root: Path, body: str) -> Path:
    path = root / ".devkit" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("body", "match"),
    [
        ("[rules.settings]\nx = 1\n", "expected a table"),
        ('[rules.settings.RULE-x]\noverrides = "nope"\n', "expected an array"),
        ("[[rules.settings.RULE-x.overrides]]\nmax_lines = 1\n", "path"),
        ('[[rules.settings.RULE-x.overrides]]\npath = "../up"\n', "parent segment"),
        ('[[rules.settings.RULE-x.overrides]]\npath = "docs/**"\n', "no settings besides path"),
        ('[rules.severity_overrides]\nRULE-x = "fatal"\n', "is not one of"),
        ("[rules]\nbogus = 1\n", "unknown fields"),
    ],
)
def test_invalid_settings_config(tmp_path: Path, body: str, match: str) -> None:
    _write_config(tmp_path, body)
    with pytest.raises(RulesConfigError, match=match):
        load_rules_config(tmp_path)


@dataclass(frozen=True)
class Demo:
    limit: int = 10
    ratio: float = 0.5
    label: str = "x"
    strict: bool = False
    tags: list[str] = field(default_factory=lambda: ["a"])


def _long_doc(root: Path, rel: str, lines: int) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"line {i}" for i in range(lines)) + "\n", encoding="utf-8")


def test_file_length_settings_apply_per_path(tmp_path: Path) -> None:
    _long_doc(tmp_path, "docs/a.md", 50)
    _long_doc(tmp_path, "docs/research/b.md", 50)
    _long_doc(tmp_path, "notes.txt", 50)
    _write_config(
        tmp_path,
        "[rules.settings.RULE-file-length]\nmax_lines = 30\nextensions = ['.md', '.txt']\n"
        "[[rules.settings.RULE-file-length.overrides]]\npath = 'docs/research/**'\nmax_lines = 100\n",
    )
    config = load_rules_config(tmp_path)
    ctx = RuleContext(workspace_root=tmp_path, phase=Phase.HYGIENE, rule_settings=dict(config.settings))
    result = evaluate_rules(ctx, [FileLengthRule()])
    assert not result.errors
    assert sorted(v.file for v in result.violations) == ["docs/a.md", "notes.txt"]
    assert ctx.settings(FileLengthRule(), "docs/research/x.md") == FileLengthSettings(100, [".md", ".txt"])


def test_file_length_default_settings_without_config(tmp_path: Path) -> None:
    rule = FileLengthRule(max_lines=30)
    _long_doc(tmp_path, "docs/a.md", 50)
    ctx = RuleContext(workspace_root=tmp_path, phase=Phase.HYGIENE)
    assert ctx.settings(rule) == FileLengthSettings(max_lines=30)
    assert [v.file for v in evaluate_rules(ctx, [rule]).violations] == ["docs/a.md"]


def test_evaluate_fails_before_checks_on_bad_settings(tmp_path: Path) -> None:
    _long_doc(tmp_path, "docs/a.md", 500)
    ctx = RuleContext(
        workspace_root=tmp_path, phase=Phase.HYGIENE, rule_settings={"RULE-file-length": RawSettings({"max_lines": -1})}
    )
    result = evaluate_rules(ctx, [FileLengthRule()])
    assert result.violations == []
    assert [str(e) for e in result.errors] == ["RULE-file-length: settings: max_lines must be a positive integer"]
    assert result.errors[0].code == "RULES_SETTINGS_INVALID" and result.errors[0].mode is ActionMode.INPUT_ERROR


def test_severity_override_changes_reported_severity(tmp_path: Path) -> None:
    _long_doc(tmp_path, "docs/a.md", 500)
    ctx = RuleContext(
        workspace_root=tmp_path, phase=Phase.HYGIENE, severity_overrides={"RULE-file-length": Severity.ERROR}
    )
    result = evaluate_rules(ctx, [FileLengthRule()])
    assert result.violations and all(v.severity == Severity.ERROR for v in result.violations)
    assert not result.ok


def test_severity_override_validation(tmp_path: Path) -> None:
    ctx = RuleContext(workspace_root=tmp_path, severity_overrides={"RULE-nope": Severity.INFO})
    assert [str(e) for e in evaluate_rules(ctx, default_rule_registry().get_all()).errors] == [
        "severity override for unknown rule: RULE-nope"
    ]
    ctx = RuleContext(workspace_root=tmp_path, severity_overrides={"RULE-file-length": Severity.WARNING})
    assert "redundant" in str(evaluate_rules(ctx, default_rule_registry().get_all()).errors[0])


def test_custom_rule_with_settings(tmp_path: Path) -> None:
    @dataclass(frozen=True)
    class Words:
        banned: list[str] = field(default_factory=lambda: ["TODO"])

    class BannedWords(BaseRule):
        def __init__(self) -> None:
            super().__init__(id="RULE-banned", name="banned", description="banned words", settings=Words())

        def check(self, ctx: RuleContext) -> list[Violation]:
            out = []
            for p in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
                rel = p.relative_to(ctx.workspace_root).as_posix()
                words: Words = ctx.settings(self, rel)
                if any(w in ctx.cache.read_text(p) for w in words.banned):
                    out.append(Violation(self.id, rel, 1, "banned word"))
            return out

    (tmp_path / "a.md").write_text("TODO\n")
    (tmp_path / "b.md").write_text("FIXME\n")
    ctx = RuleContext(
        workspace_root=tmp_path,
        rule_settings={"RULE-banned": RawSettings({}, (Override("b.md", {"banned": ["FIXME"]}),))},
    )
    assert sorted(v.file for v in evaluate_rules(ctx, [BannedWords()]).violations) == ["a.md", "b.md"]


@dataclass(frozen=True)
class Range:
    lo: int = 0
    hi: int = 100


class RangeRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-range", name="range", description="range", settings=Range())

    def validate_settings(self, settings: Range) -> None:
        if settings.lo > settings.hi:
            raise ValueError("lo must be <= hi")

    def check(self, ctx: RuleContext) -> list[Violation]:
        ctx.settings(self, "docs/a.md")
        return []


def test_overrides_that_conflict_only_together_are_reported_as_settings_errors(tmp_path: Path) -> None:
    raw = RawSettings({}, (Override("docs/**", {"lo": 50}), Override("**/a.md", {"hi": 10})))
    resolver = SettingsResolver("RULE-range", Range(), raw, RangeRule().validate_settings)
    assert resolver.for_file("docs/b.md") == Range(50, 100)
    assert resolver.for_file("src/a.md") == Range(0, 10)
    with pytest.raises(
        SettingsError, match=r"docs/a.md: the overrides matching this file \('docs/\*\*', '\*\*/a.md'\)"
    ):
        resolver.for_file("docs/a.md")

    ctx = RuleContext(workspace_root=tmp_path, rule_settings={"RULE-range": raw})
    result = evaluate_rules(ctx, [RangeRule()])
    assert len(result.errors) == 1 and str(result.errors[0]).startswith(
        "Invalid settings (RULE-range): RULE-range: docs/a.md"
    )


@dataclass(frozen=True)
class NonNegative:
    n: int = 0

    def __post_init__(self) -> None:
        if self.n < 0:
            raise ValueError("n must be >= 0")


class NonNegativeRule(BaseRule):
    def __init__(self, settings: object) -> None:
        super().__init__(id="RULE-nonneg", name="nonneg", description="nonneg", settings=settings)

    def check(self, ctx: RuleContext) -> list[Violation]:
        return []


def test_post_init_value_error_on_project_values_is_an_input_error(tmp_path: Path) -> None:
    resolvers, errors = build_resolvers([NonNegativeRule(NonNegative())], {"RULE-nonneg": RawSettings({"n": -1})})
    assert resolvers == {}
    assert [str(e) for e in errors] == ["RULE-nonneg: settings: n must be >= 0"]
    assert errors[0].rule_id == "RULE-nonneg"
    assert errors[0].code == "RULES_SETTINGS_INVALID" and errors[0].mode is ActionMode.INPUT_ERROR

    ctx = RuleContext(workspace_root=tmp_path, rule_settings={"RULE-nonneg": RawSettings({"n": -1})})
    result = evaluate_rules(ctx, [NonNegativeRule(NonNegative())])
    assert [e.code for e in result.errors] == ["RULES_SETTINGS_INVALID"]


def _assert_declaration_fix(error: PolicyError, owner: str) -> None:
    """A declaration defect points at the rule's declaration, never at the project's config table."""
    assert error.fix is not None and "config.toml" not in error.fix
    assert error.fix.startswith(f"Fix the settings declaration of RULE-nonneg ({owner} in ")
    assert __file__ in error.fix and error.fix.endswith("or report it to the rule's author")


@dataclass(frozen=True)
class Unresolvable:
    n: MissingType = 0  # type: ignore[name-defined]  # noqa: F821


@dataclass(frozen=True)
class NotInit:
    n: int = 0
    derived: int = field(default=0, init=False)


@dataclass(frozen=True)
class RaisesTypeError:
    n: int = 0

    def __post_init__(self) -> None:
        if self.n == 7:
            raise TypeError("seven is unlucky")


@pytest.mark.parametrize(
    ("settings", "raw", "match"),
    [
        (Unresolvable(), None, r"cannot resolve the field types of Unresolvable: NameError"),
        (NotInit(), None, r"settings fields must be init fields; init=False: \['derived'\]"),
        (RaisesTypeError(), RawSettings({"n": 7}), r"settings: TypeError: seven is unlucky"),
    ],
)
def test_declaration_defects_are_maintenance_errors_for_the_rule(
    tmp_path: Path, settings: object, raw: RawSettings | None, match: str
) -> None:
    configured = {"RULE-nonneg": raw} if raw is not None else {}
    resolvers, errors = build_resolvers([NonNegativeRule(settings)], configured)
    assert resolvers == {} and len(errors) == 1
    assert errors[0].rule_id == "RULE-nonneg" and str(errors[0]).startswith("RULE-nonneg: ")
    assert errors[0].code == "RULES_SETTINGS_INVALID" and errors[0].mode is ActionMode.MAINTENANCE
    _assert_declaration_fix(errors[0], type(settings).__qualname__)
    with pytest.raises(SettingsError, match=match) as info:
        SettingsResolver("RULE-nonneg", settings, raw)
    _assert_declaration_fix(info.value, type(settings).__qualname__)

    ctx = RuleContext(workspace_root=tmp_path, rule_settings=configured)
    result = evaluate_rules(ctx, [NonNegativeRule(settings)])
    assert [e.code for e in result.errors] == ["RULES_SETTINGS_INVALID"]
