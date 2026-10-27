"""Complete a proposal handoff and its optional worktree scope registration."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.features.proposals import HandoffResult, handoff_proposal
from devkit_spec.features.scope import SOURCE_HANDOFF, Registered, auto_register


@dataclass(frozen=True)
class CompletedHandoff:
    """The original proposal result, optional registration and their combined advisories."""

    handoff: HandoffResult
    registered: Registered | None
    notices: list[AdvisoryError]


def handoff_and_register(
    root: Path,
    slug: str,
    *,
    today: date | None = None,
    before_registration: Callable[[], None] | None = None,
) -> CompletedHandoff:
    """Compose the application entrypoint for internal callers."""
    return HandoffProposalUseCase().execute(root, slug, today=today, before_registration=before_registration)


class HandoffProposalUseCase(BaseUseCase):
    """Application entrypoint for handoff and register."""

    def execute(
        self,
        root: Path,
        slug: str,
        *,
        today: date | None = None,
        before_registration: Callable[[], None] | None = None,
    ) -> CompletedHandoff:
        """Hand off first, then register the new spec and merge its notices exactly once.

        The caller may guard the second mutation after handoff has completed. A refused
        guard leaves the completed handoff intact and does not touch the registry.
        A failed registration leaves a successful handoff without a scope record and only a verbose diagnostic.
        """
        handed = handoff_proposal(root, slug, today=today)
        if before_registration is not None:
            before_registration()
        registered = auto_register(root, handed.dir, source=SOURCE_HANDOFF)
        return CompletedHandoff(handed, registered, handed.notices)
