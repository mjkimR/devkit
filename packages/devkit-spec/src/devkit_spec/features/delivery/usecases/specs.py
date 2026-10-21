"""Create a bound Development bundle and register its worktree scope in one operation."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.features.proposals import CreatedSpec, create_spec
from devkit_spec.features.scope import Registered, auto_register


@dataclass(frozen=True)
class InitializedSpec:
    spec: CreatedSpec
    registered: Registered | None
    notices: list[AdvisoryError]


def create_and_register_spec(
    root: Path,
    slug: str,
    *,
    title: str | None = None,
    workflow: str | None = None,
    namespace: str | None = None,
    summary: str | None = None,
    day: date | None = None,
    cwd: Path | None = None,
) -> InitializedSpec:
    """Compose the application entrypoint for internal callers."""
    return CreateSpecUseCase().execute(
        root, slug, title=title, workflow=workflow, namespace=namespace, summary=summary, day=day, cwd=cwd
    )


class CreateSpecUseCase(BaseUseCase):
    """Application entrypoint for create and register spec."""

    def execute(
        self,
        root: Path,
        slug: str,
        *,
        title: str | None = None,
        workflow: str | None = None,
        namespace: str | None = None,
        summary: str | None = None,
        day: date | None = None,
        cwd: Path | None = None,
    ) -> InitializedSpec:
        """Register after successful creation; registration failures preserve the bundle for recovery."""
        spec = create_spec(
            root, slug, title=title, workflow=workflow, namespace=namespace, summary=summary, day=day, cwd=cwd
        )
        registered, notices = auto_register(root, spec.dir, source="spec-new")
        return InitializedSpec(spec, registered, [*spec.notices, *notices])
