"""Shared project configuration and development approach inspection."""

from devkit_dist.features.project.models.development import (
    DevelopmentApproach,
    DevelopmentConfigError,
    development_approach,
)
from devkit_dist.features.project.models.settings import (
    PLAYBOOK_KEYS,
    PLAYBOOK_LIMIT_MAX,
    PLAYBOOK_LIMIT_MIN,
    PLAYBOOK_MAX_BYTES_MAX,
    PLAYBOOK_MAX_BYTES_MIN,
    PLAYBOOK_MODES,
    SLUG,
    playbook_value,
)
from devkit_dist.features.project.repositories.development import read_development_approach

__all__ = [
    "PLAYBOOK_KEYS",
    "PLAYBOOK_LIMIT_MAX",
    "PLAYBOOK_LIMIT_MIN",
    "PLAYBOOK_MAX_BYTES_MAX",
    "PLAYBOOK_MAX_BYTES_MIN",
    "PLAYBOOK_MODES",
    "SLUG",
    "DevelopmentApproach",
    "DevelopmentConfigError",
    "development_approach",
    "playbook_value",
    "read_development_approach",
]
