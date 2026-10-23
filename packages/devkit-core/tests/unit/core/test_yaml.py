from __future__ import annotations

import pytest
import yaml
from devkit_core.core import YamlBindingUnavailableError, safe_compose, safe_load


def test_safe_load_and_compose_use_c_safe_loader() -> None:
    assert safe_load("answer: 42\n", source="example.yaml") == {"answer": 42}
    node = safe_compose("answer: 42\n", source="example.yaml")
    assert isinstance(node, yaml.MappingNode)


def test_safe_load_rejects_python_object_tags() -> None:
    with pytest.raises(yaml.YAMLError):
        safe_load("!!python/object:builtins.object {}\n")


def test_safe_load_rejects_non_c_loader_overrides() -> None:
    with pytest.raises(TypeError, match=r"must subclass yaml.CSafeLoader"):
        safe_load("key: value\n", loader=yaml.SafeLoader)


def test_missing_binding_is_checked_lazily(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delattr(yaml, "CSafeLoader", raising=False)
    with pytest.raises(YamlBindingUnavailableError) as error:
        safe_load("key: value\n", source="example.yaml")
    assert error.value.code == "YAML_BINDING_UNAVAILABLE"
    assert "example.yaml" in error.value.message
    assert error.value.exit_code == 2
    assert error.value.fix and "binary wheel" in error.value.fix
