from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest
from devkit.rules import (
    ConfigError,
    Phase,
    RuleContext,
    SettingsError,
    SettingsResolver,
    Severity,
    Violation,
    default_registry,
    evaluate,
    load_rules_config,
    match_path,
)
from devkit.rules.engine.config import parse_rules_config
from devkit.rules.engine.settings import Override, RawSettings, build_resolvers, validate_pattern
from devkit.rules.rules import BaseRule, FileLengthRule, FileLengthSettings


def _write_config(root: Path, body: str) -> Path:
    path = root / ".devkit" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# --- pattern matching -------------------------------------------------------


@pytest.mark.parametrize(
    ("pattern", "file", "expected"),
    [
        ("docs/**", "docs/a.md", True),
        ("docs/**", "docs/x/y/z.md", True),
        ("docs/**", "docs", True),
        ("docs/**", "other/a.md", False),
        ("**/summary.md", "summary.md", True),
        ("**/summary.md", "docs/research/summary.md", True),
        ("docs/*.md", "docs/a.md", True),
        ("docs/*.md", "docs/x/a.md", False),
        ("docs/research/summary.md", "docs/research/summary.md", True),
        ("docs/[ab]?.md", "docs/a1.md", True),
        ("**/*.go", "cli/internal/x.go", True),
        ("**/*.go", "cli/internal/x.py", False),
    ],
)
def test_match_path(pattern: str, file: str, expected: bool) -> None:
    assert match_path(pattern, file) is expected


@pytest.mark.parametrize("pattern", ["", "/abs", "a//b", "../x", "docs/**x", "./docs", "a\\b"])
def test_validate_pattern_rejects(pattern: str) -> None:
    with pytest.raises(ValueError):
        validate_pattern(pattern)


# --- config parsing ---------------------------------------------------------


def test_parse_settings_table() -> None:
    config = parse_rules_config(
        {
            "rules": {
                "settings": {
                    "RULE-file-length": {
                        "max_lines": 300,
                        "overrides": [{"path": "docs/**", "max_lines": 800}],
                    }
                },
                "severity_overrides": {"RULE-file-length": "error"},
            }
        }
    )
    raw = config.settings["RULE-file-length"]
    assert raw.values == {"max_lines": 300}
    assert raw.overrides[0].path == "docs/**" and raw.overrides[0].values == {"max_lines": 800}
    assert config.severity_overrides == {"RULE-file-length": Severity.ERROR}


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
    with pytest.raises(ConfigError, match=match):
        load_rules_config(tmp_path)


# --- resolver ---------------------------------------------------------------


@dataclass(frozen=True)
class Demo:
    limit: int = 10
    ratio: float = 0.5
    label: str = "x"
    strict: bool = False
    tags: list[str] = field(default_factory=lambda: ["a"])


def test_resolver_layers_and_types() -> None:
    raw = RawSettings(
        {"limit": 20, "ratio": 1},
        (Override("docs/**", {"limit": 30, "tags": ["b", "c"]}), Override("docs/deep/**", {"strict": True})),
    )
    resolver = SettingsResolver("RULE-demo", Demo(), raw)
    assert resolver.resolve() == Demo(limit=20, ratio=1.0)
    assert resolver.for_file("src/a.py") == Demo(limit=20, ratio=1.0)
    assert resolver.for_file("docs/a.md") == Demo(limit=30, ratio=1.0, tags=["b", "c"])
    assert resolver.for_file("docs/deep/a.md") == Demo(limit=30, ratio=1.0, tags=["b", "c"], strict=True)
    assert resolver.to_dict()["overrides"][0] == {"path": "docs/**", "limit": 30, "tags": ["b", "c"]}


@pytest.mark.parametrize(
    ("values", "match"),
    [
        ({"nope": 1}, "unknown settings key 'nope'"),
        ({"limit": "10"}, "limit: expected integer"),
        ({"limit": True}, "limit: expected integer"),
        ({"limit": 1.5}, "limit: expected integer"),
        ({"strict": 1}, "strict: expected boolean"),
        ({"label": 3}, "label: expected string"),
        ({"tags": "a"}, "tags: expected array of strings"),
        ({"tags": [1]}, "tags: expected array of strings"),
        ({"ratio": "x"}, "ratio: expected number"),
    ],
)
def test_resolver_rejects_bad_values(values: dict[str, object], match: str) -> None:
    with pytest.raises(SettingsError, match=match) as info:
        SettingsResolver("RULE-demo", Demo(), RawSettings(values))
    assert str(info.value).startswith("RULE-demo: settings")


def test_resolver_validates_each_override_layer_and_custom_validation() -> None:
    def validate(settings: Demo) -> None:
        if settings.limit <= 0:
            raise ValueError("limit must be positive")

    with pytest.raises(SettingsError, match=r"overrides\[0\]: limit must be positive"):
        SettingsResolver("RULE-demo", Demo(), RawSettings({}, (Override("docs/**", {"limit": 0}),)), validate)
    with pytest.raises(SettingsError, match=r"overrides\[1\].path"):
        SettingsResolver("RULE-demo", Demo(), RawSettings({}, (Override("a/**", {"limit": 1}), Override("", {}))))


def test_resolver_rejects_unsupported_field_types() -> None:
    @dataclass(frozen=True)
    class Bad:
        value: int | None = None

    with pytest.raises(SettingsError, match="unsupported settings field type"):
        SettingsResolver("RULE-bad", Bad())


def test_build_resolvers_reports_unknown_and_settings_less_rules() -> None:
    rules = default_registry().get_all()
    resolvers, errors = build_resolvers(
        rules, {"RULE-nope": RawSettings({"x": 1}), "RULE-markdown-link": RawSettings({"x": 1})}
    )
    assert sorted(errors) == [
        "settings for RULE-markdown-link: the rule declares no settings",
        "settings for unknown rule: RULE-nope",
    ]
    assert "RULE-file-length" in resolvers and "RULE-markdown-link" not in resolvers


# --- evaluation -------------------------------------------------------------


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
    result = evaluate(ctx, [FileLengthRule()])
    assert not result.errors
    assert sorted(v.file for v in result.violations) == ["docs/a.md", "notes.txt"]
    assert ctx.settings(FileLengthRule(), "docs/research/x.md") == FileLengthSettings(100, [".md", ".txt"])


def test_file_length_default_settings_without_config(tmp_path: Path) -> None:
    rule = FileLengthRule(max_lines=30)
    _long_doc(tmp_path, "docs/a.md", 50)
    ctx = RuleContext(workspace_root=tmp_path, phase=Phase.HYGIENE)
    assert ctx.settings(rule) == FileLengthSettings(max_lines=30)
    assert [v.file for v in evaluate(ctx, [rule]).violations] == ["docs/a.md"]


def test_evaluate_fails_before_checks_on_bad_settings(tmp_path: Path) -> None:
    _long_doc(tmp_path, "docs/a.md", 500)
    ctx = RuleContext(
        workspace_root=tmp_path, phase=Phase.HYGIENE, rule_settings={"RULE-file-length": RawSettings({"max_lines": -1})}
    )
    result = evaluate(ctx, [FileLengthRule()])
    assert result.violations == []
    assert result.errors == ["RULE-file-length: settings: max_lines must be a positive integer"]


def test_severity_override_changes_reported_severity(tmp_path: Path) -> None:
    _long_doc(tmp_path, "docs/a.md", 500)
    ctx = RuleContext(
        workspace_root=tmp_path, phase=Phase.HYGIENE, severity_overrides={"RULE-file-length": Severity.ERROR}
    )
    result = evaluate(ctx, [FileLengthRule()])
    assert result.violations and all(v.severity == Severity.ERROR for v in result.violations)
    assert result.has_errors


def test_severity_override_validation(tmp_path: Path) -> None:
    ctx = RuleContext(workspace_root=tmp_path, severity_overrides={"RULE-nope": Severity.INFO})
    assert evaluate(ctx, default_registry().get_all()).errors == ["severity override for unknown rule: RULE-nope"]
    ctx = RuleContext(workspace_root=tmp_path, severity_overrides={"RULE-file-length": Severity.WARNING})
    assert "redundant" in evaluate(ctx, default_registry().get_all()).errors[0]


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
    assert sorted(v.file for v in evaluate(ctx, [BannedWords()]).violations) == ["a.md", "b.md"]


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
    result = evaluate(ctx, [RangeRule()])
    assert len(result.errors) == 1 and result.errors[0].startswith(
        "Invalid settings (RULE-range): RULE-range: docs/a.md"
    )


def test_for_file_is_memoized_per_override_combination() -> None:
    resolver = SettingsResolver("RULE-range", Range(), RawSettings({"hi": 90}, (Override("docs/**", {"lo": 5}),)))
    first = resolver.for_file("docs/a.md")
    assert resolver.for_file("docs/b.md") is first
    assert resolver.for_file("src/c.md") == Range(0, 90)


def test_non_dataclass_settings_with_config_is_a_policy_error() -> None:
    class DictSettings(BaseRule):
        def __init__(self) -> None:
            super().__init__(id="RULE-dict", name="dict", description="dict", settings={"a": 1})

        def check(self, ctx: RuleContext) -> list[Violation]:
            return []

    resolvers, errors = build_resolvers([DictSettings()], {"RULE-dict": RawSettings({"a": 2})})
    assert resolvers == {}
    assert errors == ["RULE-dict: settings must be a dataclass instance carrying the defaults"]
    assert errors[0].rule_id == "RULE-dict"
