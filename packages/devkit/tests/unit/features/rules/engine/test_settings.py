from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from devkit.advisory import ActionMode
from devkit_agt.features.rules import (
    RuleContext,
    SettingsError,
    SettingsResolver,
    Severity,
    Violation,
    default_rule_registry,
    match_path,
)
from devkit_agt.features.rules.models.errors import PolicyError
from devkit_agt.features.rules.models.settings import Override, RawSettings, build_resolvers, validate_pattern
from devkit_agt.features.rules.repositories.config import parse_rules_config
from devkit_agt.features.rules.services.builtins import BaseRule


@dataclass(frozen=True)
class Demo:
    limit: int = 10
    ratio: float = 0.5
    label: str = "x"
    strict: bool = False
    tags: list[str] = field(default_factory=lambda: ["a"])


@dataclass(frozen=True)
class Range:
    lo: int = 0
    hi: int = 100


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


def _assert_declaration_fix(error: PolicyError, owner: str) -> None:
    """A declaration defect points at the rule's declaration, never at the project's config table."""
    assert error.fix is not None and "config.toml" not in error.fix
    assert error.fix.startswith(f"Fix the settings declaration of RULE-nonneg ({owner} in ")
    assert __file__ in error.fix and error.fix.endswith("or report it to the rule's author")


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
        value: tuple[str, ...] = ()

    with pytest.raises(SettingsError, match="unsupported settings field type"):
        SettingsResolver("RULE-bad", Bad())


def test_optional_fields_accept_null_and_others_reject_it() -> None:
    from devkit_agt.features.rules.models.settings import check_setting_value, describe_setting_type

    assert describe_setting_type(int | None) == "integer or null"
    assert check_setting_value(int | None, None) is None
    assert check_setting_value(float | None, 2) == 2.0
    with pytest.raises(ValueError, match="null is not allowed"):
        check_setting_value(int, None)
    with pytest.raises(ValueError, match="expected array of strings"):
        check_setting_value(list[str] | None, ["a", 1])


def test_build_resolvers_reports_unknown_and_settings_less_rules() -> None:
    rules = default_rule_registry().get_all()
    resolvers, errors = build_resolvers(
        rules, {"RULE-nope": RawSettings({"x": 1}), "RULE-markdown-link": RawSettings({"x": 1})}
    )
    assert sorted(str(e) for e in errors) == [
        "settings for RULE-markdown-link: the rule declares no settings",
        "settings for unknown rule: RULE-nope",
    ]
    assert "RULE-file-length" in resolvers and "RULE-markdown-link" not in resolvers


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
    assert [str(e) for e in errors] == ["RULE-dict: settings must be a dataclass instance carrying the defaults"]
    assert errors[0].rule_id == "RULE-dict"
    assert errors[0].code == "RULES_SETTINGS_INVALID" and errors[0].mode is ActionMode.MAINTENANCE
    assert errors[0].fix is not None and "config.toml" not in errors[0].fix and "DictSettings" in errors[0].fix


def test_post_init_value_error_on_an_override_is_an_input_error() -> None:
    raw = RawSettings({}, (Override("docs/**", {"n": -1}),))
    with pytest.raises(SettingsError, match=r"overrides\[0\]: n must be >= 0") as info:
        SettingsResolver("RULE-nonneg", NonNegative(), raw)
    assert info.value.mode is ActionMode.INPUT_ERROR


def test_project_value_errors_keep_the_config_fix() -> None:
    _, errors = build_resolvers([NonNegativeRule(NonNegative())], {"RULE-nonneg": RawSettings({"n": -1})})
    assert errors[0].fix is not None and ".devkit/config.toml" in errors[0].fix


def test_defaults_rejected_by_validate_settings_are_a_declaration_defect() -> None:
    class StrictRule(NonNegativeRule):
        def validate_settings(self, settings: NonNegative) -> None:
            if settings.n == 0:
                raise ValueError("n must not be 0")

    _, errors = build_resolvers([StrictRule(NonNegative())], {})
    assert [str(e) for e in errors] == ["RULE-nonneg: defaults: n must not be 0"]
    assert errors[0].code == "RULES_SETTINGS_INVALID" and errors[0].mode is ActionMode.MAINTENANCE
    _assert_declaration_fix(errors[0], "NonNegative")


def test_validate_settings_raising_other_than_value_error_is_a_declaration_defect() -> None:
    def validate(settings: NonNegative) -> None:
        raise KeyError("oops")

    with pytest.raises(SettingsError, match=r"defaults: KeyError") as info:
        SettingsResolver("RULE-nonneg", NonNegative(), None, validate)
    assert info.value.mode is ActionMode.MAINTENANCE
