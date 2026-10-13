"""Built-in gates: the gate system's own integrations. Policy gates ship in content wheels as ``kind = "gate"`` assets."""

from devkit.gate.gates.commands import VerifyCommandsGate
from devkit.gate.gates.message import NonEmptyMessageGate

__all__ = ["NonEmptyMessageGate", "VerifyCommandsGate"]
