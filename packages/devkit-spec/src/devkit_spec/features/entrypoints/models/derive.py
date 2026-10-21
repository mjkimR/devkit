"""Derived document links and skipped input values."""

from dataclasses import dataclass
from enum import StrEnum


class State(StrEnum):
    NEW = "new"
    DECLARED = "declared"


class SkipKind(StrEnum):
    BOUNDARY = "boundary"
    TARGET = "target"
    BUNDLE = "bundle"
    APPLY = "apply"


class Reason(StrEnum):
    NOT_A_PATH = "not-a-path"
    INVALID_PATH = "invalid-path"
    EXCLUDED_TREE = "excluded-tree"
    EXCLUDED = "excluded"
    WAIVED = "waived"
    NOT_ENTRYPOINT_BEARING = "not-entrypoint-bearing"
    MISSING_DOC = "missing-doc"
    NOT_A_DOCUMENT = "not-a-document"
    INPUT_MISSING = "input-missing"
    INVALID_INPUT = "invalid-input"
    FOLDED = "folded"
    MISSING_PATH = "missing-path"


@dataclass(frozen=True)
class Pair:
    """One derived document-code link.

    A pair of one bundle has ``spec`` and ``task``; an aggregated pair (``aggregate``) has ``count`` and ``specs``
    instead. ``folded_into`` is the same-bundle ancestor candidate that covers ``code``.
    """

    doc: str
    doc_path: str
    code: str
    state: State
    exists: bool
    spec: str | None = None
    task: int | None = None
    folded_into: str | None = None
    count: int | None = None
    specs: tuple[str, ...] | None = None

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {"doc": self.doc, "doc_path": self.doc_path, "code": self.code}
        if self.count is None:
            data |= {"spec": self.spec, "task": self.task, "folded_into": self.folded_into}
        else:
            data |= {"count": self.count, "specs": list(self.specs or ())}
        return data | {"state": str(self.state), "exists": self.exists}


@dataclass(frozen=True)
class Skipped:
    """An input or candidate the derivation did not turn into a pair, or that ``--apply`` did not write."""

    kind: SkipKind
    value: str
    reason: Reason
    spec: str | None = None
    task: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": str(self.kind),
            "value": self.value,
            "spec": self.spec,
            "task": self.task,
            "reason": str(self.reason),
        }
