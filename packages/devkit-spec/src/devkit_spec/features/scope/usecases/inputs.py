"""Checkout declaration operations: the declared scope of a proposal or a spec bundle in the working tree."""

from __future__ import annotations

from pathlib import Path

from devkit_spec.features.proposals.usecases.scaffold import clean_slug
from devkit_spec.features.scope.models.model import ScopeSet
from devkit_spec.features.scope.services.declarations import from_proposal as declared_proposal
from devkit_spec.features.scope.services.declarations import from_spec as declared_spec
from devkit_spec.features.scope.services.declarations import kind_of

__all__ = ["from_proposal", "from_spec", "kind_of"]


def from_proposal(root: Path, slug: str) -> ScopeSet:
    return declared_proposal(root, clean_slug(slug))


def from_spec(root: Path, spec_dir: str) -> ScopeSet:
    return declared_spec(root, spec_dir)
