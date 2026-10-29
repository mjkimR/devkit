"""Offline policy behavior independently of native rendering or project I/O."""

import pytest
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.distribution.models.subagents import ModelSettings, SubagentPolicy
from devkit_dist.features.distribution.services.subagents import parse_subagents, resolve_settings


@pytest.mark.parametrize(
    ("level", "host", "model", "effort"),
    [
        ("minimal", "claude-code", "haiku", "low"),
        ("compact", "claude-code", "haiku", None),
        ("lean", "claude-code", "sonnet", "medium"),
        ("standard", "claude-code", "sonnet", None),
        ("deep", "claude-code", "opus", None),
        ("maximal", "claude-code", "opus", "high"),
        ("minimal", "codex", "gpt-6-luna", "low"),
        ("compact", "codex", "gpt-6-luna", None),
        ("lean", "codex", "gpt-6.1-terra", "medium"),
        ("standard", "codex", "gpt-6.1-sol", None),
        ("deep", "codex", "gpt-6-astra", None),
        ("maximal", "codex", "gpt-6-astra", "high"),
        ("minimal", "antigravity", None, None),
        ("compact", "antigravity", "flash", None),
        ("lean", "antigravity", "flash", None),
        ("standard", "antigravity", None, None),
        ("deep", "antigravity", None, None),
        ("maximal", "antigravity", None, None),
    ],
)
def test_builtin_pair(level: str, host: str, model: str | None, effort: str | None) -> None:
    assert resolve_settings(SubagentPolicy(), "team:review", level, host) == ModelSettings(model, effort)


def test_absence_explicit_inheritance_and_precedence() -> None:
    assert resolve_settings(SubagentPolicy(), "team:r", None, "codex") is None
    assert resolve_settings(SubagentPolicy(), "team:r", "inherit", "codex") == ModelSettings()
    policy = parse_subagents({"default_level": "inherit", "roles": {"team:r": {"level": "minimal"}}})
    assert resolve_settings(policy, "other:r", "deep", "codex") == ModelSettings()
    assert resolve_settings(policy, "team:r", "deep", "codex") == ModelSettings("gpt-6-luna", "low")


def test_partial_mapping_and_field_reset_do_not_leak() -> None:
    policy = parse_subagents({"levels": {"deep": {"codex": {"model": "custom", "effort": "inherit"}}}})
    assert resolve_settings(policy, "t:r", "deep", "codex") == ModelSettings("custom")
    assert resolve_settings(policy, "t:r", "deep", "claude-code") == ModelSettings("opus")
    assert resolve_settings(policy, "t:r", "standard", "codex") == ModelSettings("gpt-6.1-sol")
    policy = parse_subagents({"levels": {"deep": {"codex": {"model": "inherit"}}}})
    assert resolve_settings(policy, "t:r", "deep", "codex") == ModelSettings()
    policy = parse_subagents({"levels": {"deep": {"codex": {"model": "custom"}}}})
    assert resolve_settings(policy, "t:r", "deep", "codex") == ModelSettings("custom")


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        {"unknown": 1},
        {"default_level": False},
        {"default_level": "foo"},
        {"default_level": "light"},
        {"levels": {"light": {}}},
        {"levels": {"inherit": {}}},
        {"levels": {"deep": {"bad-host": {}}}},
        {"levels": {"deep": {"codex": {"bad": 1}}}},
        {"roles": []},
        {"roles": {"unqualified": {"level": "deep"}}},
        {"roles": {"t:r": {}}},
        {"roles": {"t:r": {"level": "deep", "model": "x"}}},
    ],
)
def test_invalid_policy(value: object) -> None:
    with pytest.raises(ConfigError):
        parse_subagents(value)


@pytest.mark.parametrize(
    ("host", "field", "value"),
    [
        ("antigravity", "model", "gpt-6-astra"),
        ("antigravity", "model", "por"),
        ("antigravity", "effort", "high"),
        ("codex", "effort", "ultra"),
        ("codex", "effort", "minimal"),
        ("claude-code", "effort", "none"),
        ("claude-code", "effort", "High"),
        ("codex", "model", ""),
        ("codex", "model", "bad\nmodel"),
        ("codex", "model", 1),
        ("codex", "effort", False),
    ],
)
def test_invalid_mapping_even_when_unused(host: str, field: str, value: object) -> None:
    with pytest.raises(ConfigError):
        parse_subagents({"levels": {"deep": {host: {field: value}}}})


@pytest.mark.parametrize("model", ["gpt-6.1-sol", "gpt-6-astra"])
def test_exact_known_codex_none_is_rejected(model: str) -> None:
    with pytest.raises(ConfigError, match="does not support effort none"):
        parse_subagents({"levels": {"minimal": {"codex": {"model": model, "effort": "none"}}}})


@pytest.mark.parametrize(
    "host,model",
    [("codex", "gpt-6-luna"), ("codex", "custom"), ("codex", "gpt-6-astra-custom"), ("claude-code", "haiku")],
)
def test_unknown_models_and_provider_aliases_stay_runtime_owned(host: str, model: str) -> None:
    effort = "none" if host == "codex" else "max"
    parse_subagents({"levels": {"minimal": {host: {"model": model, "effort": effort}}}})


def test_partial_overrides_of_inherited_and_bounded_effort() -> None:
    inherited = parse_subagents({"levels": {"compact": {"codex": {"model": "custom"}}}})
    bounded = parse_subagents({"levels": {"maximal": {"codex": {"model": "custom"}}}})
    assert resolve_settings(inherited, "t:r", "compact", "codex") == ModelSettings("custom")
    assert resolve_settings(bounded, "t:r", "maximal", "codex") == ModelSettings("custom", "high")
    explicit = parse_subagents({"levels": {"deep": {"codex": {"effort": "high"}}}})
    assert resolve_settings(explicit, "t:r", "deep", "codex") == ModelSettings("gpt-6-astra", "high")


def test_lean_selection_precedence_overrides_and_reset() -> None:
    policy = parse_subagents(
        {
            "default_level": "standard",
            "roles": {"team:r": {"level": "lean"}},
            "levels": {"lean": {"codex": {"model": "custom"}}},
        }
    )
    assert resolve_settings(policy, "team:r", "compact", "codex") == ModelSettings("custom", "medium")
    assert resolve_settings(policy, "other:r", "lean", "codex") == ModelSettings("gpt-6.1-sol")
    policy = parse_subagents({"default_level": "lean", "levels": {"lean": {"codex": {"effort": "inherit"}}}})
    assert resolve_settings(policy, "team:r", None, "codex") == ModelSettings("gpt-6.1-terra")


def test_explicit_antigravity_override_does_not_use_builtin_fallback() -> None:
    policy = parse_subagents({"levels": {"deep": {"antigravity": {"model": "pro"}}}})
    assert resolve_settings(policy, "t:r", "deep", "antigravity") == ModelSettings("pro")
