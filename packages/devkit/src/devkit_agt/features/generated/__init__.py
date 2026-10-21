"""devkit_agt.features.generated: tracked generated files (``devkit generated list|check|regen|resolve``).

A project registers the files a command generates (lockfiles, receipts, generated clients) with the command that
regenerates them; devkit's own receipt is registered by default. ``resolve`` settles a merge, rebase or
cherry-pick conflict in those files by regenerating them instead of merging their text, ``check`` reports files
that differ from what their command produces, and ``regen`` rewrites them. SDD-agnostic and trigger-agnostic: a
merge driver, a hook or a CI job calls the same commands. See ``docs/capabilities/generated/CAP-GEN-tracked-artifacts.md``.
"""

from devkit_agt.features.generated.models.errors import (
    CommandFailedError,
    ConflictsRemainWarning,
    GeneratedConfigError,
    GeneratedError,
    InputsConflictedError,
    OutputUndeclaredError,
    StaleError,
    UnmergedError,
)
from devkit_agt.features.generated.repositories.registry import (
    Artifact,
    Registry,
    builtin_artifacts,
    load_registry,
    matches,
)
from devkit_agt.features.generated.usecases.engine import (
    ArtifactRun,
    CheckArtifacts,
    Checkout,
    RegenerateArtifacts,
    ResolveArtifacts,
    ResolveResult,
    RunResult,
    open_checkout,
    operation,
    unmerged,
)

__all__ = [
    "Artifact",
    "ArtifactRun",
    "CheckArtifacts",
    "Checkout",
    "CommandFailedError",
    "ConflictsRemainWarning",
    "GeneratedConfigError",
    "GeneratedError",
    "InputsConflictedError",
    "OutputUndeclaredError",
    "RegenerateArtifacts",
    "Registry",
    "ResolveArtifacts",
    "ResolveResult",
    "RunResult",
    "StaleError",
    "UnmergedError",
    "builtin_artifacts",
    "load_registry",
    "matches",
    "open_checkout",
    "operation",
    "unmerged",
]
