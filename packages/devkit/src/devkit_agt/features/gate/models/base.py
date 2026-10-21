from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from devkit_agt.features.gate.models.contracts import GateContext, GateResult, Stage


@dataclass
class BaseGate(ABC):
    """Base class for gates; deployed gate packages are scanned for its concrete subclasses.

    Subclasses take no constructor arguments, pass their metadata to
    ``super().__init__`` (as ``devkit_agt.features.rules.services.builtins.BaseRule`` subclasses do) and
    implement ``run``. A class that leaves ``run`` abstract is a shared base,
    not a gate, and is skipped when a gate package is loaded.
    """

    id: str
    description: str
    stage: Stage
    order: int = 100
    enabled_by_default: bool = True
    settings: Any = None

    @abstractmethod
    def run(self, ctx: GateContext) -> GateResult | None:
        """Return ``GateResult.passed``/``skipped`` (``None`` means passed) or raise ``GateRefusedError`` to refuse."""
