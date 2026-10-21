"""Declared harness features and expected lazy-command import footprints."""

import tomllib
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src/devkit_agt"
PYPROJECT = Path(__file__).resolve().parents[3] / "pyproject.toml"

DECLARATION = next(
    entry
    for entry in tomllib.loads((Path(__file__).resolve().parents[5] / ".devkit/architecture.toml").read_text())[
        "packages"
    ]
    if entry["namespace"] == "devkit_agt"
)
FEATURES = set(DECLARATION["features"])

# Behavioral lazy-loading expectations, not architectural import permissions.
LAZY_IMPORT_AREAS: dict[str, set[str]] = {
    "rules": {"compact"},
    "workflow": {"rules"},
    "gate": {"rules", "compact"},
    "integration": {"worktree"},
    "compact": set(),
    "worktree": set(),
    "generated": {"compact"},
}
DATA_AREAS = {"bundles/authoring", "bundles/harness"}
