"""Scope registry policy independent of configuration storage."""

from dataclasses import dataclass
from pathlib import Path

SCOPE_TIMEOUT_DEFAULT = 10


@dataclass(frozen=True)
class ScopeConfig:
    """``[tool.spec.scope]``: where the work-scope registry lives and how long one command may wait.

    ``shared_path`` is absolute (``~`` expanded) or ``None`` for ``devkit-spec-scope/`` in the Git common directory;
    ``namespace`` ``None`` is a hash of that common directory; ``timeout`` is in seconds.
    """

    shared_path: Path | None = None
    namespace: str | None = None
    timeout: int = SCOPE_TIMEOUT_DEFAULT
