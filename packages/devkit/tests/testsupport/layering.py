"""The module layering of the devkit-agt wheel: its areas and the edges they may use, shared by the layering and
lazy-import tests. Each area may also use the devkit-dist areas listed for it; the scanner is devkit-dist's
(``distsupport.layering``), applied to this wheel's sources.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src/devkit"
PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def dist_src() -> Path:
    """The ``devkit`` sources of the installed devkit-dist wheel, which every devkit-agt environment has."""
    spec = importlib.util.find_spec("devkit.distribution")
    assert spec is not None and spec.origin is not None, "devkit-dist is not installed"
    return Path(spec.origin).resolve().parents[1]


# ``advisory`` is the separate devkit-advisory distribution, below every area; ``core``, ``search``, ``host`` and
# ``distribution`` are devkit-dist areas. The ``*_guide`` areas (``DATA_AREAS``) hold built-in bundle content:
# ``authoring_guide`` ships rule code under ``bundle/rules/``, built on the public rule API and loaded by
# ``devkit rules`` from the synchronized copies, never imported through the package; ``harness_guide`` is text only.
ALLOWED: dict[str, set[str]] = {
    "authoring_guide": {"core", "advisory", "rules"},
    "harness_guide": set(),
    "rules": {"core", "advisory", "compact"},
    "workflow": {"core", "advisory", "rules"},
    "gate": {"core", "advisory", "rules", "compact"},
    "integration": {"core", "advisory", "host", "worktree"},
    "compact": {"core", "advisory"},
    "worktree": {"core", "advisory"},
    "generated": {"core", "advisory", "compact"},
}
DATA_AREAS = {"authoring_guide", "harness_guide"}
# The edges of the devkit-dist areas that load entry-point groups devkit-agt registers in.
DIST_ALLOWED: dict[str, set[str]] = {
    "core": {"advisory"},
    "search": {"core", "advisory"},
    "host": {"core", "advisory"},
    "distribution": {"core", "advisory", "search", "host"},
}
