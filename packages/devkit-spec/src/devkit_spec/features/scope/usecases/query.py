"""Compare declared scopes and query a registry with local ownership evidence."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.base.errors import (
    ScopeRecordInvalidWarning,
    ScopeRecordMissingError,
    ScopeSpecNotFoundError,
    ScopeTokenMissingError,
)
from devkit_spec.features.scope import (
    PairResult,
    Problem,
    Record,
    ScopeSet,
    Session,
    compare_all,
    compare_with,
    from_proposal,
    from_spec,
    own,
)
from devkit_spec.features.scope.models.location import Location
from devkit_spec.utils.paths import _bundle_dir


def _spec_dir(root: Path, value: str | None) -> str:
    if not value:
        raise ArgumentError(
            "--spec <dir> is required",
            target_files=["--spec"],
            fix="Pass the bundle directory: --spec specs/<YYYY-MM>/<YYYYMMDD>-<slug>",
        )
    relative = _bundle_dir(root, value)
    if not (root / relative).is_dir():
        raise ScopeSpecNotFoundError(f"spec bundle not found: {relative}", target_files=[relative])
    return relative


def _overlapping(pairs: Sequence[PairResult]) -> int:
    return sum(pair.overlapping for pair in pairs)


def _record_warnings(
    location: Location, problems: Sequence[Problem], own_unreadable: AdvisoryError | None = None
) -> list[AdvisoryError]:
    """One ``SPEC_SCOPE_RECORD_INVALID`` warning for the unreadable record files; ``own_unreadable`` (this worktree's
    record may be one of them) adds its message as a detail."""
    if not problems:
        return []
    directory = location.shared_path / location.namespace
    own = [own_unreadable.message] if own_unreadable is not None else []
    return [
        ScopeRecordInvalidWarning(
            f"{len(problems)} record file(s) of the namespace could not be read and were left out",
            *(f"{problem.file}: {problem.reason}" for problem in problems),
            *own,
            target_files=[location.shown(directory / problem.file) for problem in problems],
        )
    ]


class CompareScopesUseCase(BaseUseCase):
    def execute(
        self, root: Path, proposals: tuple[str, ...], specs: tuple[str, ...]
    ) -> tuple[list[ScopeSet], list[PairResult], dict[str, int]]:
        sets: list[ScopeSet] = [from_proposal(root, slug) for slug in proposals]
        for value in specs:
            relative = _bundle_dir(root, value)
            sets.append(from_spec(root, relative))
        pairs = compare_all(sets)
        summary = {"sets": len(sets), "pairs": len(pairs), "overlapping": _overlapping(pairs)}
        return sets, pairs, summary


class QueryScopesUseCase(BaseUseCase):
    def execute(
        self, root: Path, session: Session, spec_dir: str | None
    ) -> tuple[Record | None, list[Record], list[Record], list[PairResult], dict[str, str | int], list[AdvisoryError]]:
        location = session.location
        mine: Record | None
        unreadable: ScopeRecordInvalidWarning | None = None
        try:
            found = own(session, cleanup=False)
            mine, others, problems = found.record, found.others, found.problems
        except (ScopeTokenMissingError, ScopeRecordMissingError, ScopeRecordInvalidWarning) as exc:
            # listing needs no own record: one that may be unreadable is reported with the other unreadable files
            unreadable = exc if isinstance(exc, ScopeRecordInvalidWarning) else None
            mine = None
            others, problems = session.registry.query(location.namespace, session.deadline)
        if spec_dir is not None:
            relative = _spec_dir(root, spec_dir)
            planned = from_spec(root, relative)
            # A record of the same bundle is the planned task itself, never an overlap with it.
            pairs = compare_with(
                planned,
                [record.to_set() for record in others if record.spec != relative and record.task_id != planned.id],
            )
        elif mine is not None:
            pairs = compare_with(mine.to_set(), [record.to_set() for record in others])
        else:
            pairs = compare_all([record.to_set() for record in others])
        notices = _record_warnings(location, problems, unreadable)
        records = [*([mine] if mine else []), *others]
        summary = {
            "namespace": location.namespace,
            "records": len(records),
            "pairs": len(pairs),
            "overlapping": _overlapping(pairs),
            "problems": len(problems),
        }
        return mine, others, records, pairs, summary, notices
