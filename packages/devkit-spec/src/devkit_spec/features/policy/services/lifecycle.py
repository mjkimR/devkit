"""Applicability boundary for explicit SDD mutations."""

from pathlib import Path

from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project import read_development_approach


class LifecycleInactiveError(ConfigError):
    code = "SPEC_LIFECYCLE_INACTIVE"
    fix = "Inspect `uv run devkit config show`; choose SDD explicitly before creating SDD lifecycle records"


def require_sdd(root: Path) -> None:
    if read_development_approach(root).approach != "sdd":
        raise LifecycleInactiveError(
            "SDD lifecycle mutation is inactive for the incubation development approach",
            target_files=[".devkit/config.toml"],
        )
