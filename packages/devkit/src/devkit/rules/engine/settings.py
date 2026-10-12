"""Typed, per-rule settings with path-scoped overrides.

A rule declares its settings by assigning a dataclass instance to ``settings``
on the rule; the instance carries the defaults and its class carries the field
types. A project configures a rule in ``.devkit/config.toml``::

    [rules.settings.RULE-file-length]
    max_lines = 300

    [[rules.settings.RULE-file-length.overrides]]
    path = "docs/research/**"
    max_lines = 800

Every layer (base values and each override applied to the base values) is
validated against the dataclass before any rule runs: unknown keys, wrong
types and bad path patterns fail the run with the rule ID attached.
``SettingsResolver.for_file`` then applies the overrides whose pattern matches
a workspace-relative file, in declaration order, so later matching overrides
win. Overrides that are valid alone but invalid together can only be detected
for a file both match; ``for_file`` raises ``SettingsError`` for them and the
evaluator reports it as a settings error.
"""

from __future__ import annotations

import dataclasses
import fnmatch
import types
import typing
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from devkit.rules.engine.errors import PolicyError, SettingsError

if TYPE_CHECKING:
    from devkit.rules.engine.models import Rule


@dataclass(frozen=True)
class Override:
    path: str
    values: dict[str, Any]


@dataclass(frozen=True)
class RawSettings:
    """``[rules.settings.<id>]`` as configured, before it is matched to a rule."""

    values: dict[str, Any]
    overrides: tuple[Override, ...] = ()


def validate_pattern(pattern: str) -> None:
    """Accept workspace-relative ``/`` patterns; ``**`` must be a whole segment."""
    if not isinstance(pattern, str) or not pattern:
        raise ValueError("expected a nonempty workspace-relative path pattern")
    if pattern.startswith("/") or "\\" in pattern or ":" in pattern:
        raise ValueError(f"expected a workspace-relative '/' pattern: {pattern!r}")
    for segment in pattern.split("/"):
        if segment in {"", "."}:
            raise ValueError(f"empty or '.' segment in pattern: {pattern!r}")
        if segment == "..":
            raise ValueError(f"parent segment in pattern: {pattern!r}")
        if "**" in segment and segment != "**":
            raise ValueError(f"'**' must be a complete segment in pattern: {pattern!r}")


def match_path(pattern: str, file: str) -> bool:
    """Match ``file`` against ``pattern`` segment by segment.

    ``**`` matches zero or more segments; ``*``, ``?`` and character classes
    match within one segment. Both arguments are workspace-relative ``/`` paths.
    """
    parts = pattern.split("/")
    segments = file.replace("\\", "/").split("/")
    # Dynamic programming keeps repeated ``**`` bounded to O(pattern * path).
    nxt = [False] * (len(segments) + 1)
    nxt[len(segments)] = True
    for i in range(len(parts) - 1, -1, -1):
        cur = [False] * (len(segments) + 1)
        for j in range(len(segments), -1, -1):
            if parts[i] == "**":
                cur[j] = nxt[j] or (j < len(segments) and cur[j + 1])
            elif j < len(segments):
                cur[j] = fnmatch.fnmatchcase(segments[j], parts[i]) and nxt[j + 1]
        nxt = cur
    return nxt[0]


_SCALARS: dict[Any, str] = {int: "integer", float: "number", str: "string", bool: "boolean"}
SUPPORTED_TYPES_HINT = "int, float, str, bool or list[str], optionally `| None`"


def _optional_of(annotation: Any) -> Any | None:
    """``X`` for an ``X | None`` (``Optional[X]``) annotation, else ``None``."""
    if typing.get_origin(annotation) not in (typing.Union, types.UnionType):
        return None
    args = typing.get_args(annotation)
    inner = [arg for arg in args if arg is not type(None)]
    return inner[0] if len(args) == 2 and len(inner) == 1 else None


def describe_setting_type(annotation: Any) -> str:
    """How a supported settings field type reads in an error; raises ``TypeError`` for any other type.

    The one type vocabulary of rule and gate settings (``devkit.gate`` reuses
    it): ``int``, ``float``, ``str``, ``bool`` and ``list[str]``, each optionally
    ``| None``.
    """
    inner = _optional_of(annotation)
    if inner is not None:
        return f"{describe_setting_type(inner)} or null"
    if annotation in _SCALARS:
        return _SCALARS[annotation]
    if typing.get_origin(annotation) is list and typing.get_args(annotation) == (str,):
        return "array of strings"
    raise TypeError(f"unsupported settings field type {annotation!r}; use {SUPPORTED_TYPES_HINT}")


def check_setting_value(annotation: Any, value: Any) -> Any:
    """``value`` checked against a field's type and converted (an integer for a float becomes a float, a list is copied).

    ``null`` is accepted only by an ``| None`` field. Raises ``ValueError``
    (``expected <type>, got <value>``) for a value of the wrong type and
    ``TypeError`` for an unsupported annotation.
    """
    expected = describe_setting_type(annotation)
    inner = _optional_of(annotation)
    if inner is not None:
        if value is None:
            return None
        annotation = inner
    if value is None:
        raise ValueError("null is not allowed")
    if annotation is bool:
        ok = isinstance(value, bool)
    elif annotation is int:
        ok = isinstance(value, int) and not isinstance(value, bool)
    elif annotation is float:
        ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        if ok:
            value = float(value)
    elif annotation is str:
        ok = isinstance(value, str)
    else:
        ok = isinstance(value, list) and all(isinstance(item, str) for item in value)
        if ok:
            value = list(value)
    if not ok:
        raise ValueError(f"expected {expected}, got {value!r}")
    return value


def _describe(annotation: Any) -> str:
    try:
        return describe_setting_type(annotation)
    except TypeError as exc:
        raise SettingsError(str(exc), input_error=False, target_files=[]) from None


def _check_value(name: str, annotation: Any, value: Any) -> Any:
    _describe(annotation)
    try:
        return check_setting_value(annotation, value)
    except ValueError as exc:
        raise SettingsError(f"{name}: {exc}") from None


def declared_settings(rule: Rule) -> Any | None:
    """The rule's default settings instance, or ``None`` when it declares none."""
    value = getattr(rule, "settings", None)
    if value is None:
        return None
    if not dataclasses.is_dataclass(value) or isinstance(value, type):
        raise SettingsError(
            f"{rule.id}: settings must be a dataclass instance carrying the defaults",
            rule_id=rule.id,
            input_error=False,
            target_files=[],
        )
    return value


class SettingsResolver:
    """Resolved settings of one rule: defaults, project values and path overrides."""

    def __init__(self, rule_id: str, default: Any, raw: RawSettings | None = None, validate: Any = None) -> None:
        self.rule_id = rule_id
        self.default = default
        self._cls = type(default)
        self._fields = {f.name: f for f in dataclasses.fields(default)}
        self._hints = typing.get_type_hints(self._cls)
        self._validate = validate
        for name, hint in self._hints.items():
            if name in self._fields:
                _describe(hint)
        self.base: dict[str, Any] = {f.name: getattr(default, f.name) for f in dataclasses.fields(default)}
        self.overrides: list[Override] = []
        self._by_match: dict[tuple[int, ...], Any] = {}
        try:
            self._decode(self.base, "defaults")
            if raw is not None:
                self.base = self._merge(self.base, raw.values, "settings")
                self._decode(self.base, "settings")
                for index, override in enumerate(raw.overrides):
                    try:
                        validate_pattern(override.path)
                    except ValueError as exc:
                        raise SettingsError(f"overrides[{index}].path: {exc}") from exc
                    candidate = self._merge(self.base, override.values, f"overrides[{index}]")
                    self._decode(candidate, f"overrides[{index}]")
                    self.overrides.append(Override(override.path, dict(override.values)))
        except SettingsError as exc:
            raise _for_rule(rule_id, f"{rule_id}: {exc}", exc) from None

    def _merge(self, base: dict[str, Any], values: dict[str, Any], context: str) -> dict[str, Any]:
        merged = dict(base)
        for key in sorted(values):
            if key not in self._fields:
                raise SettingsError(f"{context}: unknown settings key {key!r}; known: {sorted(self._fields)}")
            merged[key] = _check_value(f"{context}.{key}", self._hints[key], values[key])
        return merged

    def _decode(self, values: dict[str, Any], context: str) -> Any:
        instance = self._cls(**values)
        if self._validate is not None:
            try:
                self._validate(instance)
            except ValueError as exc:
                raise SettingsError(f"{context}: {exc}") from None
        return instance

    def resolve(self) -> Any:
        """Settings without any path override applied."""
        return self._decode(self.base, "settings")

    def for_file(self, file: str) -> Any:
        """Settings for a workspace-relative file after applying matching overrides.

        Each override is validated against the base values before any rule
        runs; overrides that only conflict when several match the same file
        (for example ``lo`` from one and ``hi`` from another) are detected
        here and raise ``SettingsError`` naming the file and the overrides.
        Results are memoized per combination of matching overrides.
        """
        matched = tuple(index for index, override in enumerate(self.overrides) if match_path(override.path, file))
        if matched not in self._by_match:
            values = self.base
            for index in matched:
                values = self._merge(values, self.overrides[index].values, f"overrides[{index}]")
            try:
                self._by_match[matched] = self._decode(values, "settings")
            except SettingsError as exc:
                paths = ", ".join(repr(self.overrides[index].path) for index in matched)
                raise _for_rule(
                    self.rule_id,
                    f"{self.rule_id}: {file}: the overrides matching this file ({paths}) combine to invalid settings: "
                    f"{exc}",
                    exc,
                ) from None
        return self._by_match[matched]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "defaults": dataclasses.asdict(self.default),
            "settings": dict(self.base),
            "overrides": [{"path": o.path, **o.values} for o in self.overrides],
        }


def build_resolvers(
    rules: Sequence[Rule], configured: Mapping[str, RawSettings]
) -> tuple[dict[str, SettingsResolver], list[PolicyError]]:
    """Resolve every rule's settings; configuration for unknown or settings-less rules is an error."""
    resolvers: dict[str, SettingsResolver] = {}
    errors: list[PolicyError] = []
    by_id = {rule.id: rule for rule in rules}
    for rule_id in sorted(configured):
        if rule_id not in by_id:
            errors.append(PolicyError(f"settings for unknown rule: {rule_id}", rule_id=rule_id))
            continue
        try:
            declared = declared_settings(by_id[rule_id])
        except SettingsError:
            continue  # reported once by the loop below
        if declared is None:
            errors.append(PolicyError(f"settings for {rule_id}: the rule declares no settings", rule_id=rule_id))
    for rule in rules:
        try:
            default = declared_settings(rule)
            if default is None:
                continue
            resolvers[rule.id] = SettingsResolver(
                rule.id, default, configured.get(rule.id), getattr(rule, "validate_settings", None)
            )
        except SettingsError as exc:
            errors.append(exc if exc.rule_id == rule.id else _for_rule(rule.id, str(exc), exc))
    return resolvers, errors


def _for_rule(rule_id: str, message: str, cause: SettingsError) -> SettingsError:
    """``cause`` attributed to ``rule_id`` with a new message, keeping whether it is an input or a declaration defect."""
    return SettingsError(message, rule_id=rule_id, input_error=cause.input_error, target_files=cause.target_files)
