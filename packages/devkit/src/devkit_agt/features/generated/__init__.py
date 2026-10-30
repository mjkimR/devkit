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
    load_registry_at,
    matches,
)
from devkit_agt.features.generated.services.conflicts import ConflictPlan, classify
from devkit_agt.features.generated.usecases.engine import (
    ArtifactRun,
    CheckArtifacts,
    RegenerateArtifacts,
    ResolveArtifacts,
    ResolveResult,
    RunResult,
    operation,
    unmerged,
)

__all__ = [
    "Artifact",
    "ArtifactRun",
    "CheckArtifacts",
    "CommandFailedError",
    "ConflictPlan",
    "ConflictsRemainWarning",
    "GeneratedConfigError",
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
    "classify",
    "load_registry",
    "load_registry_at",
    "matches",
    "operation",
    "unmerged",
]
