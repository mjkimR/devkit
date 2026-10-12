"""Built-in gates: the gate system's own integrations. Policy gates ship in content wheels as ``kind = "gate"`` assets."""

from agent_commit_gate.gates.message import NonEmptyMessageGate
from agent_commit_gate.gates.rules import StagedRulesGate

__all__ = ["NonEmptyMessageGate", "StagedRulesGate"]
