"""Lazy, safe YAML reads through PyYAML's LibYAML implementation."""

from __future__ import annotations

from typing import Any

import yaml

from devkit_core.base.errors import YamlBindingUnavailableError


def require_libyaml(*, source: str = "YAML input") -> type[Any]:
    """Return PyYAML's C safe loader or raise an actionable runtime dependency error."""
    loader = getattr(yaml, "CSafeLoader", None)
    if loader is None:
        raise YamlBindingUnavailableError(source)
    return loader


def safe_load(text: str, *, source: str = "YAML input", loader: type[Any] | None = None) -> Any:
    """Load a YAML value with LibYAML, optionally using a C-safe-loader subclass."""
    selected = loader or require_libyaml(source=source)
    return yaml.load(text, Loader=selected)


def safe_compose(text: str, *, source: str = "YAML input") -> yaml.Node | None:
    """Compose a YAML node with LibYAML, preserving native parser errors and marks."""
    return yaml.compose(text, Loader=require_libyaml(source=source))
