from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest
from devkit.gate import BaseGate, GateConfigError, GateContext, GateResult, Stage, load_gates_config, resolve_settings
from devkit.gate.config import merge


@dataclass(frozen=True)
class Settings:
    limit: int = 1
    ratio: float = 0.5
    name: str = "x"
    paths: tuple[str, ...] = ()
    strict: bool = False


class SettingsGate(BaseGate):
    def __init__(self, enabled_by_default: bool = True) -> None:
        super().__init__(
            id="g", description="", stage=Stage.PRE_COMMIT, enabled_by_default=enabled_by_default, settings=Settings()
        )

    def run(self, ctx: GateContext) -> GateResult | None:
        return None


class PlainGate(BaseGate):
    def __init__(self, settings: object = None) -> None:
        super().__init__(id="plain", description="", stage=Stage.COMMIT_MSG, settings=settings)

    def run(self, ctx: GateContext) -> GateResult | None:
        return None


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_merge_deep_merges_tables_and_replaces_values() -> None:
    base = {"settings": {"a": {"enabled": True, "items": [1, 2], "n": 1}, "b": {"n": 1}}}
    top = {"settings": {"a": {"items": [3], "n": 2}}}
    assert merge(base, top) == {"settings": {"a": {"enabled": True, "items": [3], "n": 2}, "b": {"n": 1}}}


def test_local_config_overrides_project_config(tmp_path: Path) -> None:
    git_dir = tmp_path / ".git"
    _write(
        tmp_path / ".devkit/config.toml",
        'schema = 1\n[presets]\nx = "all"\n[gates.settings.g]\nenabled = false\nlimit = 3\nname = "team"\n',
    )
    _write(git_dir / "devkit.config", "[gates.settings.g]\nenabled = true\nlimit = 7\n")
    config = load_gates_config(tmp_path, git_dir)
    assert config.sources == (tmp_path / ".devkit/config.toml", git_dir / "devkit.config")
    entry = config.gates["g"]
    assert entry.enabled is True and entry.values == {"limit": 7, "name": "team"}
    assert config.enabled(SettingsGate(enabled_by_default=False))


def test_missing_files_and_unset_enabled_keep_gate_default(tmp_path: Path) -> None:
    config = load_gates_config(tmp_path, tmp_path / ".git")
    assert config.gates == {} and config.sources == ()
    assert not config.enabled(SettingsGate(enabled_by_default=False))
    assert config.enabled(SettingsGate())


@pytest.mark.parametrize(
    ("project", "local", "message"),
    [
        ("[gates]\nverbose = true\n", "", "unknown fields: ['verbose']"),
        ("[gates.settings.g]\nenabled = 'yes'\n", "", "expected true or false"),
        ("", "[rules]\nx = 1\n", "unknown fields: ['rules']"),
        ("[gates\n", "", "invalid config"),
    ],
)
def test_invalid_config_is_rejected(tmp_path: Path, project: str, local: str, message: str) -> None:
    _write(tmp_path / ".devkit/config.toml", project)
    _write(tmp_path / ".git/devkit.config", local)
    with pytest.raises(GateConfigError, match=re.escape(message)):
        load_gates_config(tmp_path, tmp_path / ".git")


def test_resolve_settings_applies_and_converts_values() -> None:
    resolved = resolve_settings(SettingsGate(), {"limit": 4, "ratio": 2, "paths": ["a", "b"], "strict": True})
    assert resolved == Settings(limit=4, ratio=2, name="x", paths=("a", "b"), strict=True)
    assert resolve_settings(SettingsGate(), {}) == Settings()


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"nope": 1}, "unknown settings"),
        ({"limit": True}, "expected int"),
        ({"strict": 1}, "expected bool"),
        ({"paths": "a"}, "expected tuple"),
        ({"name": 3}, "expected str"),
    ],
)
def test_resolve_settings_rejects_bad_values(values: dict[str, object], message: str) -> None:
    with pytest.raises(GateConfigError, match=message):
        resolve_settings(SettingsGate(), values)


def test_base_gate_requires_run() -> None:
    with pytest.raises(TypeError, match="abstract"):
        BaseGate(id="x", description="", stage=Stage.PRE_COMMIT)  # type: ignore[abstract]


def test_settings_must_be_a_dataclass_instance() -> None:
    with pytest.raises(GateConfigError, match="settings must be a dataclass instance"):
        resolve_settings(PlainGate({"limit": 1}), {})


def test_unreadable_project_config_is_a_gate_config_error(tmp_path: Path) -> None:
    _write(tmp_path / ".devkit/config.toml", "[gates\n")
    with pytest.raises(GateConfigError) as caught:
        load_gates_config(tmp_path, tmp_path / ".git")
    assert caught.value.target_files == (".devkit/config.toml",)


def test_gate_without_settings_rejects_values() -> None:
    gate = PlainGate()
    assert resolve_settings(gate, {}) is None
    with pytest.raises(GateConfigError, match="gate has no settings"):
        resolve_settings(gate, {"x": 1})
