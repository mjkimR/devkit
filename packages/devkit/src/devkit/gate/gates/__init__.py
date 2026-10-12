"""Built-in gates: the gate system's own integrations. Policy gates ship in content wheels as ``kind = "gate"`` assets."""

from devkit.gate.gates.message import NonEmptyMessageGate
from devkit.gate.gates.rules import StagedRulesGate

__all__ = ["NonEmptyMessageGate", "StagedRulesGate"]
