"""Shared project configuration and development approach inspection."""

from devkit_dist.features.project.models.development import (
    DevelopmentApproach,
    DevelopmentConfigError,
    development_approach,
)
from devkit_dist.features.project.repositories.development import read_development_approach

__all__ = ["DevelopmentApproach", "DevelopmentConfigError", "development_approach", "read_development_approach"]
