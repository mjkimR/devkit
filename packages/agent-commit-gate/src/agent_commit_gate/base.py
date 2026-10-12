from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_commit_gate.models import GateContext, GateResult, Stage


@dataclass
class BaseGate:
    """Base class for gates; deployed gate files are scanned for its concrete subclasses.

    Subclasses take no constructor arguments and pass their metadata to
    ``super().__init__``, as ``agent_rule_engine.rules.BaseRule`` subclasses do.
    """

    id: str
    description: str
    stage: Stage
    order: int = 100
    enabled_by_default: bool = True
    settings: Any = None

    def run(self, ctx: GateContext) -> GateResult | None:
        raise NotImplementedError
