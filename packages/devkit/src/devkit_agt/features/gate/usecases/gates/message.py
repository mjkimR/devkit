"""Built-in ``commit-msg`` gate: refuse a blank commit message.

The hook sees the message before Git's cleanup, and whether Git will strip
comment lines depends on how the commit was made (``-m`` keeps a leading
``#``; the editor template strips it; ``core.commentChar`` changes the
character). The gate therefore only refuses a message that is blank above the
scissors line; a message that is empty only after comment stripping is left to
Git, which aborts such a commit itself unless ``--allow-empty-message`` is given.
"""

from __future__ import annotations

from devkit_agt.features.gate.models.base import BaseGate
from devkit_agt.features.gate.models.contracts import GateContext, GateResult, Stage
from devkit_agt.features.gate.models.errors import GateFindingsError

# ``git commit -v`` appends the diff below this line (after the comment string); Git strips it from the message.
SCISSORS = "------------------------ >8 ------------------------"


def _is_scissors(line: str) -> bool:
    prefix, separator, rest = line.rstrip().partition(" " + SCISSORS)
    return bool(separator) and not rest and bool(prefix) and not any(char.isalnum() for char in prefix)


def message_body(text: str) -> str:
    """The message above Git's scissors line, if any."""
    lines: list[str] = []
    for line in text.splitlines():
        if _is_scissors(line):
            break
        lines.append(line)
    return "\n".join(lines)


class NonEmptyMessageGate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="message-nonempty",
            description="Refuse a commit message that is blank (whitespace only above any scissors line).",
            stage=Stage.COMMIT_MSG,
            order=900,
        )

    def run(self, ctx: GateContext) -> GateResult:
        text = ctx.message_file.read_text("utf-8", errors="replace")
        if message_body(text).strip():
            return GateResult.passed()
        raise GateFindingsError(
            "commit message is empty", code="GATE_MESSAGE_EMPTY", fix="Write a subject line describing the change"
        )
