"""The conflict settler of a local integration build: generated files keep their artifact's seed side.

``ADR-generated-conflicts-in-prepared-merge``: when every conflict of the in-memory merge is in a path an enabled
generated artifact owns, and no artifact to regenerate reads or updates another conflict, the build keeps each such
path from the artifact's ``seed`` side and records the artifact for the result's disclosure. Nothing is regenerated.
The registry is the one committed at the build target, so the prospective build at prepare and the real build at
integrate of one source and target settle alike.
"""

from __future__ import annotations

from pathlib import Path

from devkit_agt.features.generated import classify, load_registry_at
from devkit_agt.features.integration.models.contracts import SeededArtifact, regenerate_command
from devkit_agt.features.integration.models.errors import GeneratedSeededWarning
from devkit_agt.features.worktree import MergeConflictError

LISTED = 20  # conflicts listed in a refusal's details


class GeneratedSeeding:
    """A ``ConflictSettler`` for one build onto ``target``; ``seeded`` holds what its call kept from one side."""

    def __init__(self, root: Path, target: str) -> None:
        self.root = root
        self.target = target
        self.seeded: tuple[SeededArtifact, ...] = ()

    def __call__(self, paths: tuple[str, ...], /) -> dict[str, str]:
        plan = classify(load_registry_at(self.root, self.target), paths)
        if plan.unowned:
            lines = [
                f"{path}: read by {', '.join(plan.readers[path])}"
                if path in plan.readers
                else f"{path}: owned by no generated artifact"
                for path in plan.unowned
            ]
            extra = len(lines) - LISTED
            raise MergeConflictError(
                f"the target's later commits conflict with the task branch in {len(plan.unowned)} file(s) no generated"
                " artifact settles; nothing was changed on the target",
                *lines[:LISTED],
                *([f"... and {extra} more"] if extra > 0 else []),
            )
        self.seeded = tuple(SeededArtifact(item.id, plan.owned[item.id], item.seed) for item in plan.owners)
        return plan.sides()


def seeded_warning(seeded: tuple[SeededArtifact, ...]) -> GeneratedSeededWarning:
    """The disclosure of ``seeded``: one detail per artifact and the command that regenerates them on the target."""
    return GeneratedSeededWarning(
        f"the merge kept {len(seeded)} generated artifact(s) from one side without regenerating them: "
        f"{', '.join(item.id for item in seeded)}",
        *(f'{item.id}: {", ".join(item.paths)} kept from the {item.kept} (seed = "{item.seed}")' for item in seeded),
        target_files=[path for item in seeded for path in item.paths],
        fix=f"After the integration lands, run `{regenerate_command(seeded)}` on the target branch and commit the"
        " regenerated files",
    )
