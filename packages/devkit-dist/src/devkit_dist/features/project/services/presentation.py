"""Explicit workspace presentation preferences; no transport or domain dependencies."""

from __future__ import annotations

from pathlib import Path

from devkit.advisory import AdvisoryError

from devkit_dist.features.project.models.presentation import (
    PRESENTATION_LANGUAGES,
    PresentationLanguage,
    PresentationLanguageUnsupportedNotice,
)
from devkit_dist.features.project.repositories.local_config import read_effective_config


def resolve_language(root: Path, *, effective: bool = True) -> PresentationLanguage:
    """Resolve exact values, retaining unsupported requests as diagnostic evidence."""
    config = read_effective_config(root, local=effective)
    requested = config.values["presentation"]["language"]
    source = config.sources["presentation.language"]
    fallback = requested not in PRESENTATION_LANGUAGES
    return PresentationLanguage(requested, "en" if fallback else requested, source, fallback)


def language_notices(root: Path) -> list[AdvisoryError]:
    """``PRESENTATION_LANGUAGE_UNSUPPORTED`` warnings for each configuration file whose value fell back to ``en``.

    Both the effective value (personal rendering) and the shared-only value (canonical tracked output) are checked;
    a file is reported once.
    """
    notices: list[AdvisoryError] = []
    sources: set[str] = set()
    for effective in (True, False):
        language = resolve_language(root, effective=effective)
        if language.fallback and language.source not in sources:
            sources.add(language.source)
            notices.append(PresentationLanguageUnsupportedNotice.of(language))
    return notices


def approval_language(executor: Path) -> str:
    """Snapshot owned form language; the runtime binding owns configuration identity.

    The private context belongs to the project execution repository. This lookup neither creates a binding
    nor replaces the independent environment and identity guards at domain boundaries.
    """
    from devkit_dist.features.project.repositories.invocation import _BINDING

    binding = _BINDING.get()
    return resolve_language(binding.workspace if binding is not None else executor).approval_language
