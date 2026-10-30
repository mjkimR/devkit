"""Shared development approach values and validation."""

from dataclasses import dataclass
from typing import Any, Literal, cast

from devkit_dist.base.errors import ConfigError


class DevelopmentConfigError(ConfigError):
    code = "DEVELOPMENT_CONFIG_INVALID"
    fix = 'Use [development] approach = "sdd" or "adaptive-dev" in .devkit/config.toml'


@dataclass(frozen=True)
class DevelopmentApproach:
    approach: Literal["sdd", "adaptive-dev"] = "sdd"
    source: str = "default"


def development_approach(config: dict[str, Any]) -> DevelopmentApproach:
    table = config.get("development", {})
    if (
        not isinstance(table, dict)
        or set(table) - {"approach"}
        or table.get("approach", "sdd") not in ("sdd", "adaptive-dev")
    ):
        raise DevelopmentConfigError(
            "development requires only approach = sdd|adaptive-dev", target_files=[".devkit/config.toml"]
        )
    return DevelopmentApproach(
        cast(Literal["sdd", "adaptive-dev"], table.get("approach", "sdd")),
        ".devkit/config.toml" if "approach" in table else "default",
    )
