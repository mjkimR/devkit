"""Explicit Markdown templates and their declared scalar inputs; Jinja loads only on render."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from devkit.core.errors import ConfigError
from devkit.distribution.errors import BundleError

Scalar = str | bool | int
NAME = re.compile(r"[a-z][a-z0-9_]*\Z")
TYPES = {"string": str, "boolean": bool, "integer": int}
TEMPLATE_KINDS = frozenset({"instruction", "guidance", "document", "skill", "subagent"})


@dataclass(frozen=True)
class Variable:
    kind: str
    default: Scalar | None = None
    default_from: str | None = None


def declarations(raw: Any) -> dict[str, Variable]:
    if not isinstance(raw, dict):
        raise BundleError("variables: expected a table")
    result = {}
    for name, item in raw.items():
        if not NAME.fullmatch(name) or not isinstance(item, dict) or set(item) - {"type", "default", "default_from"}:
            raise BundleError(f"variables.{name}: expected an identifier and type/default declaration")
        kind = item.get("type")
        if not isinstance(kind, str) or kind not in TYPES:
            raise BundleError(f"variables.{name}: type must be string, boolean or integer")
        default = item.get("default")
        if "default" in item and type(default) is not TYPES[kind]:
            raise BundleError(f"variables.{name}: default must be {kind}")
        reference = item.get("default_from")
        if "default_from" in item and (kind != "string" or reference != "presentation.language"):
            raise BundleError(f"variables.{name}: default_from requires string presentation.language")
        result[name] = Variable(kind, default, reference)
    return result


def resolve_variables(
    declared: dict[str, Variable], supplied: dict[str, Scalar], bundle: str, *, language: str | None = None
) -> dict[str, Scalar]:
    if unknown := supplied.keys() - declared.keys():
        raise ConfigError(f"{bundle}: undeclared template variables: {sorted(unknown)}")
    result = {}
    for name, variable in declared.items():
        default = language if variable.default_from is not None and language is not None else variable.default
        value = supplied.get(name, default)
        if value is None:
            raise ConfigError(f"{bundle}: missing required template variable: {name}")
        if type(value) is not TYPES[variable.kind]:
            raise ConfigError(f"{bundle}: variable {name} must be {variable.kind}")
        result[name] = value
    return result


def output_path(source: str) -> str:
    return source.removesuffix(".jinja") if source.endswith(".md.jinja") else source


def render_template(data: bytes, variables: dict[str, Scalar], context: str, *, environment: str = "local") -> bytes:
    if environment not in {"local", "cloud"}:
        raise BundleError(f"{context}: execution environment must be local or cloud")
    # Keeping these imports here preserves CLI startup and non-template sync import costs.
    from jinja2 import StrictUndefined
    from jinja2.sandbox import SandboxedEnvironment

    class ScalarEnvironment(SandboxedEnvironment):
        def getattr(self, obj: Any, attribute: str) -> Any:
            # Mapping keys such as "items" must not resolve to Python methods.
            if isinstance(obj, dict) and attribute in obj:
                return obj[attribute]
            return self.undefined(obj=obj, name=attribute)

        def is_safe_attribute(self, obj: Any, attr: str, value: Any) -> bool:
            return False

        def is_safe_callable(self, obj: Any) -> bool:
            return False

    env = ScalarEnvironment(undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)
    env.globals.clear()
    # No attribute/call filters that could escape the scalar-only interface.
    env.filters = {name: env.filters[name] for name in ("lower", "upper", "trim", "default", "replace", "length")}
    try:
        return (
            env.from_string(data.decode("utf-8"))
            .render(vars=variables, execution={"environment": environment})
            .encode("utf-8")
        )
    except Exception as exc:
        raise BundleError(f"{context}: template rendering failed: {exc}") from exc
