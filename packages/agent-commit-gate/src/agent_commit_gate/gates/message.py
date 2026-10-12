from __future__ import annotations

from agent_commit_gate.base import BaseGate
from agent_commit_gate.models import GateContext, GateError, GateResult, Stage

# ``git commit -v`` appends the diff below this line; Git strips it from the message.
SCISSORS = "# ------------------------ >8 ------------------------"


class NonEmptyMessageGate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="message-nonempty",
            description="Refuse a commit message that is empty once comment lines are removed.",
            stage=Stage.COMMIT_MSG,
            order=900,
        )

    def run(self, ctx: GateContext) -> GateResult:
        text = ctx.message_file.read_text("utf-8", errors="replace")
        for line in text.splitlines():
            if line == SCISSORS:
                break
            if line.strip() and not line.startswith("#"):
                return GateResult.passed()
        raise GateError.blocked(
            "commit message is empty",
            "Write a subject line describing the change.",
            code="GATE_MESSAGE_EMPTY",
        )
