"""Create a bound Development bundle and register its worktree scope in one operation."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.base.axes import DEFAULT_TASK_KIND, spec_workflow
from devkit_spec.features.proposals import CreatedSpec, create_spec
from devkit_spec.features.proposals.usecases.scaffold import require_task_kind
from devkit_spec.features.scope import Registered, auto_register


@dataclass(frozen=True)
class InitializedSpec:
    spec: CreatedSpec
    registered: Registered | None
    notices: list[AdvisoryError]


class CreateSpecUseCase(BaseUseCase):
    """Application entrypoint for create and register spec."""

    def execute(
        self,
        root: Path,
        slug: str,
        *,
        title: str | None = None,
        task_kind: str | None = None,
        workflow: str | None = None,
        namespace: str | None = None,
        summary: str | None = None,
        day: date | None = None,
        cwd: Path | None = None,
    ) -> InitializedSpec:
        """Register after successful creation; a failed registration preserves the bundle.

        ``task_kind`` (``--task-kind``) selects ``sdd-spec-<task_kind>``; the default kind binds like no option, as a
        proposal handoff does. Giving it with ``workflow`` or outside ``TASK_KINDS`` is ``ArgumentError`` before
        anything is written.
        """
        if task_kind is not None:
            workflow = _task_kind_workflow(task_kind, workflow)
        spec = create_spec(
            root, slug, title=title, workflow=workflow, namespace=namespace, summary=summary, day=day, cwd=cwd
        )
        registered = auto_register(root, spec.dir, source="spec-new")
        return InitializedSpec(spec, registered, list(spec.notices))


def _task_kind_workflow(task_kind: str, workflow: str | None) -> str | None:
    """The workflow ``--task-kind`` selects: ``None`` for the default kind, else ``sdd-spec-<task_kind>``."""
    if workflow is not None:
        raise ArgumentError(
            "--task-kind and --workflow both select the workflow; give one",
            target_files=["--task-kind"],
            fix="Pass --task-kind feature|bugfix, or --workflow <id> for another workflow, not both",
        )
    kind = require_task_kind(task_kind)
    return spec_workflow(kind) if kind != DEFAULT_TASK_KIND else None
