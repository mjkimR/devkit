from pathlib import Path

import pytest
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.repositories.local_config import (
    LOCAL_CONFIG_PATH,
    merge_config,
    read_effective_config,
    resolve_execution_environment,
)
from devkit_dist.features.project.repositories.project import read_project_config


def project(tmp_path: Path, local: str = "", shared: str = "") -> Path:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/config.toml").write_text(shared)
    if local:
        (tmp_path / LOCAL_CONFIG_PATH).write_text(local)
    return tmp_path


def test_effective_provenance_and_explicit_execution_root(tmp_path: Path) -> None:
    base = project(
        tmp_path, '[execution]\nenvironment="cloud"\n[mcp]\nregister=false\n', '[execution]\nenvironment="local"\n'
    )
    config = read_effective_config(base)
    assert config.values["execution"]["environment"] == "cloud"
    assert config.values["mcp"]["register"] is False
    assert config.sources["execution.environment"] == LOCAL_CONFIG_PATH
    assert read_project_config(base)["execution"]["environment"] == "local"
    assert resolve_execution_environment(base).environment == "cloud"
    (base / LOCAL_CONFIG_PATH).unlink()
    assert resolve_execution_environment(base).environment == "local"
    with pytest.raises(ConfigError):
        resolve_execution_environment(base / "missing")


@pytest.mark.parametrize(
    "text,code",
    [
        ("[rules]\nx=false", "CONFIG_LOCAL_KEY_FORBIDDEN"),
        ("[workflow]\nx=false", "CONFIG_LOCAL_KEY_FORBIDDEN"),
        ("agents=[]", "CONFIG_LOCAL_KEY_FORBIDDEN"),
        ('[subagents]\ndefault_level="deep"', "CONFIG_LOCAL_KEY_FORBIDDEN"),
        ('[bundles.style]\npreset="all"', "CONFIG_LOCAL_KEY_FORBIDDEN"),
        ("schema=2", "CONFIG_INVALID"),
        ("schema=true", "CONFIG_INVALID"),
        ('[execution]\nenvironment="other"', "CONFIG_INVALID"),
        ('[mcp]\nregister="false"', "CONFIG_INVALID"),
        ("[playbooks]\nlimit=true", "CONFIG_INVALID"),
        ("[playbooks]\nmin_score=true", "CONFIG_INVALID"),
        ("[playbooks]\nmin_similarity=2", "CONFIG_INVALID"),
        ("[bundles.style.variables]\nlanguage=[]", "CONFIG_INVALID"),
        ("[[", "CONFIG_INVALID"),
    ],
)
def test_validate_every_local_field(tmp_path: Path, text: str, code: str) -> None:
    root = project(tmp_path, text)
    with pytest.raises(ConfigError) as caught:
        resolve_execution_environment(root)
    assert caught.value.code == code
    assert LOCAL_CONFIG_PATH in caught.value.target_files


@pytest.mark.parametrize("kind", ["directory", "symlink"])
def test_nonregular_local_input(tmp_path: Path, kind: str) -> None:
    root = project(tmp_path)
    path = root / LOCAL_CONFIG_PATH
    if kind == "directory":
        path.mkdir()
    else:
        path.symlink_to(root / ".devkit/config.toml")
    with pytest.raises(ConfigError):
        read_effective_config(root)


def test_recursive_merge_whole_array_replacement_and_type_refusal(tmp_path: Path) -> None:
    shared = {"a": {"x": 1, "y": ["a", "b"]}}
    assert merge_config(shared, {"a": {"y": ["c"]}}, path=tmp_path) == {"a": {"x": 1, "y": ["c"]}}
    assert shared["a"]["y"] == ["a", "b"]
    with pytest.raises(ConfigError):
        merge_config(shared, {"a": {"x": True}}, path=tmp_path)
