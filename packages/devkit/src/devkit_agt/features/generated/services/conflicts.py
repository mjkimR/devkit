"""Which artifact settles each conflicted path, and which conflicts no artifact can settle.

``resolve`` and the in-memory merge of a local integration (``ADR-generated-conflicts-in-prepared-merge``) share this
classification: a conflict in a path an artifact owns is settled from that artifact's ``seed`` side; any other
conflict is left to a person, and blocks the artifacts to regenerate that read or update it.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from devkit_agt.features.generated.repositories.registry import Artifact, Registry


@dataclass(frozen=True)
class ConflictPlan:
    """The conflicts of one operation, classified against a registry.

    ``owned`` maps each owning artifact's id to the conflicts it owns (sorted); ``plan`` holds those artifacts and the
    artifacts after them, in registry order; ``unowned`` the conflicts no artifact owns; ``readers`` maps each unowned
    conflict that an artifact of ``plan`` reads or updates to those artifacts' ids.
    """

    owned: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    plan: tuple[Artifact, ...] = ()
    unowned: tuple[str, ...] = ()
    readers: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    @property
    def owners(self) -> tuple[Artifact, ...]:
        """The artifacts that own a conflict, in registry order."""
        return tuple(item for item in self.plan if item.id in self.owned)

    def sides(self) -> dict[str, str]:
        """Each owned conflict with its artifact's ``seed`` side (``"ours"`` or ``"theirs"``)."""
        return {path: item.seed for item in self.owners for path in self.owned[item.id]}


def classify(registry: Registry, paths: Iterable[str]) -> ConflictPlan:
    """Classify the conflicted ``paths`` against ``registry`` (see ``ConflictPlan``).

    An artifact reads a conflict when it declares no ``inputs`` (it may read anything), when the path matches its
    ``inputs``, or when it ``updates`` or owns it: its command rewrites such a file in place, conflict markers included.
    Raises ``GeneratedConfigError`` when two artifacts own one path.
    """
    owned: dict[str, list[str]] = {}
    unowned: list[str] = []
    for path in sorted(set(paths)):
        owner = registry.owner(path)
        if owner is None:
            unowned.append(path)
        else:
            owned.setdefault(owner.id, []).append(path)
    plan = registry.closure(owned)
    readers: dict[str, tuple[str, ...]] = {}
    for path in unowned:
        ids = tuple(
            artifact.id
            for artifact in plan
            if not artifact.inputs or artifact.may_read(path) or artifact.may_write(path)
        )
        if ids:
            readers[path] = ids
    return ConflictPlan({key: tuple(value) for key, value in owned.items()}, plan, tuple(unowned), readers)
