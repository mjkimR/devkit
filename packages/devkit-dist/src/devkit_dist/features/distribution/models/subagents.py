"""Immutable neutral subagent policy and resolved native model settings."""

from dataclasses import dataclass

LEVELS = ("inherit", "minimal", "compact", "lean", "standard", "deep", "maximal")


@dataclass(frozen=True)
class ModelSettings:
    model: str | None = None
    effort: str | None = None


@dataclass(frozen=True)
class SubagentPolicy:
    # None is absence, distinct from an explicit project-wide inherit reset.
    default_level: str | None = None
    mappings: tuple[tuple[str, str, ModelSettings], ...] = ()
    roles: tuple[tuple[str, str], ...] = ()
