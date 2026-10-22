"""Explicit workspace presentation preferences; no transport or domain dependencies."""

from __future__ import annotations

from pathlib import Path

from devkit_dist.features.project.models.presentation import PresentationLanguage
from devkit_dist.features.project.repositories.local_config import read_effective_config


def resolve_language(root: Path, *, effective: bool = True) -> PresentationLanguage:
    """Resolve the validated value; configuration validation refuses unsupported values, so none falls back."""
    config = read_effective_config(root, local=effective)
    requested = config.values["presentation"]["language"]
    return PresentationLanguage(requested, requested, config.sources["presentation.language"], False)


def approval_language(executor: Path) -> str:
    """Snapshot owned form language; the runtime binding owns configuration identity.

    The private context belongs to the project execution repository. This lookup neither creates a binding
    nor replaces the independent environment and identity guards at domain boundaries.
    """
    from devkit_dist.features.project.repositories.invocation import _BINDING

    binding = _BINDING.get()
    return resolve_language(binding.workspace if binding is not None else executor).approval_language
