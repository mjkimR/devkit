"""Read the project-shared development approach, never local or environment overlays."""

from pathlib import Path

from devkit_dist.features.project.models.development import DevelopmentApproach, development_approach
from devkit_dist.features.project.repositories.project import read_project_config


def read_development_approach(root: Path) -> DevelopmentApproach:
    return development_approach(read_project_config(root))
