from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_advisory.types import ActionMode, Actor, Retry

# Canonical directive texts; keep identical across implementations of the protocol.
ACTION_TEXT: dict[ActionMode, str] = {
    ActionMode.AUTO: (
        "AUTO — Run the [FIX] command once, then retry the operation once.\n"
        "This is the only mode that authorizes a retry. Stop after it either way."
    ),
    ActionMode.INTERACTION: (
        "INTERACTION — Stop and ask the user. Do not retry, and do not\n"
        "improvise a way around this. [FIX], when present, is the command\n"
        "for once they agree."
    ),
    ActionMode.DEFER: (
        "DEFER — Nothing is broken and nothing here is yours to fix.\n"
        "Do not retry now. Report the cause and when it can be retried."
    ),
    ActionMode.BLOCKED: (
        "BLOCKED — A deliberate guardrail refused this. Report it and stop.\n"
        "Do not propose or apply a way around it; changing the rule is the\n"
        "user's decision, not a fix."
    ),
    ActionMode.HALT: (
        "HALT — Unsafe to retry. Execution stopped to prevent state corruption.\n"
        "Report what happened, including anything left half-done. Do not retry or finish by hand."
    ),
    ActionMode.MAINTENANCE: (
        "MAINTENANCE — A codebase defect or tool failure occurred.\n"
        "Report it and stop; repairing the code/tool is a separate task.\n"
        "[TARGET] names the affected files."
    ),
    ActionMode.INPUT_ERROR: (
        "INPUT_ERROR — Do not retry with identical input. Retrying unchanged will\n"
        "fail identically. Correct the flag, argument, or input file before rerunning."
    ),
}

DEFAULT_CODE = "GENERAL_ERROR"
_CONTINUATION = " " * len("[ACTION] ")


@dataclass(frozen=True)
class Advisory:
    """Structured directive and metadata for calling agents and automated runners."""

    code: str = DEFAULT_CODE
    actor: Actor = Actor.NONE
    retry: Retry = Retry.UNSAFE
    guardrail: bool = False
    input_error: bool = False
    retry_after: str | None = None
    fix: str | None = None
    what_to_report: str | None = None
    target_files: tuple[str, ...] = ()
    details: tuple[str, ...] = ()

    @property
    def mode(self) -> ActionMode:
        """Derive the directive; the first matching rule wins."""
        if self.input_error:
            return ActionMode.INPUT_ERROR
        if self.guardrail:
            return ActionMode.BLOCKED
        if self.actor is Actor.DEVELOPER:
            return ActionMode.MAINTENANCE
        if self.retry is Retry.UNSAFE:
            return ActionMode.HALT
        if self.actor is Actor.TOOL:
            return ActionMode.AUTO
        if self.actor is Actor.USER:
            return ActionMode.INTERACTION
        if self.retry is Retry.SAFE:
            return ActionMode.DEFER
        return ActionMode.HALT

    def lines(self, message: str | None = None) -> list[str]:
        """Render the advisory block as sentinel lines for stderr."""
        rendered: list[str] = []
        if message:
            rendered.append(f"[ERROR]  ({self.code or DEFAULT_CODE}) {message}")
        head, *rest = ACTION_TEXT[self.mode].splitlines()
        rendered.append(f"[ACTION] {head}")
        rendered.extend(f"{_CONTINUATION}{line}" for line in rest)
        if self.retry_after:
            rendered.append(f"[WHEN]   Not before: {self.retry_after}")
        if self.target_files:
            rendered.append(f"[TARGET] {', '.join(self.target_files)}")
        if self.fix:
            rendered.append(f"[FIX]    {self.fix}")
        if self.what_to_report:
            rendered.append(f"[REPORT] {self.what_to_report}")
        rendered.extend(f"[DETAIL] {detail}" for detail in self.details)
        return rendered

    def to_dict(self) -> dict[str, Any]:
        """Serialize advisory metadata, including the derived mode."""
        return {
            "code": self.code,
            "mode": self.mode.value,
            "actor": self.actor.value,
            "retry": self.retry.value,
            "guardrail": self.guardrail,
            "input_error": self.input_error,
            "retry_after": self.retry_after,
            "fix": self.fix,
            "what_to_report": self.what_to_report,
            "target_files": list(self.target_files),
            "details": list(self.details),
        }
