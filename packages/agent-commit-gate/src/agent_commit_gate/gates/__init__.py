"""Built-in gates. Deliberately minimal: policy gates ship in content wheels as ``kind = "gate"`` assets."""

from agent_commit_gate.gates.message import NonEmptyMessageGate

__all__ = ["NonEmptyMessageGate"]
