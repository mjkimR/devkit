from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from devkit.advisory.types import ActionMode, Actor, Level, Retry

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
        "[TARGET], when present, names the affected files."
    ),
    ActionMode.INPUT_ERROR: (
        "INPUT_ERROR — Do not retry with identical input. Retrying unchanged will\n"
        "fail identically. Correct the flag, argument, or input file before rerunning."
    ),
    ActionMode.CONTINUE: (
        "CONTINUE — The operation succeeded; this does not block it. Do not retry\n"
        "or undo it. Tell the user about it ([REPORT] when present); run [FIX]\n"
        "only when they ask for it."
    ),
    ActionMode.NOTE: (
        "NOTE — For awareness only; nothing needs doing now. Continue. Mention it\n"
        "when it bears on the task; run [FIX] only when the user asks for it."
    ),
}

HEADLINE: dict[Level, str] = {Level.ERROR: "[ERROR]  ", Level.WARNING: "[WARN]   ", Level.NOTICE: "[NOTICE] "}

# The sentinels a block's lines start with after its headline, and the indentation of a continued value.
FIELDS = ("[ACTION] ", "[WHEN]   ", "[TARGET] ", "[FIX]    ", "[REPORT] ", "[DETAIL] ")
CONTINUATION = " " * len("[ACTION] ")

DEFAULT_CODE = "GENERAL_ERROR"


def _field(sentinel: str, value: str) -> list[str]:
    """``value`` behind its sentinel; further lines are indented under it.

    Blank lines are dropped, so a block never contains one, and a blank value renders no line at all.
    """
    lines = [line.rstrip() for line in str(value).splitlines() if line.strip()]
    return [f"{CONTINUATION if index else sentinel}{line}" for index, line in enumerate(lines)]


@dataclass(frozen=True)
class Advisory:
    """Structured directive and metadata for calling agents and automated runners."""

    code: str = DEFAULT_CODE
    level: Level = Level.ERROR
    actor: Actor = Actor.NONE
    retry: Retry = Retry.UNSAFE
    guardrail: bool = False
    input_error: bool = False
    retry_after: str | None = None
    fix: str | None = None
    what_to_report: str | None = None
    target_files: tuple[str, ...] = ()
    details: tuple[str, ...] = ()
    brief: bool = False

    def __post_init__(self) -> None:
        if not self.code:
            object.__setattr__(self, "code", DEFAULT_CODE)

    @property
    def mode(self) -> ActionMode:
        """Derive the directive; the first matching rule wins. The level decides first; the error fields after it."""
        if self.level is Level.WARNING:
            return ActionMode.CONTINUE
        if self.level is Level.NOTICE:
            return ActionMode.NOTE
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
        """Render the advisory block as sentinel lines for stderr.

        The headline (``[ERROR]``, ``[WARN]`` or ``[NOTICE]`` by level) comes
        first when a message is given, even an empty one: it always carries the
        code. ``[ACTION]`` is left out only for a ``brief`` notice without
        ``fix``; any other line is left out when its value is blank. A value
        that spans several lines continues on lines indented like the
        ``[ACTION]`` continuation, without blank lines, so every line either
        starts with a sentinel or belongs to the sentinel above it.
        """
        rendered: list[str] = []
        if message is not None:
            rendered.extend(_field(HEADLINE[self.level], f"({self.code}) {message.lstrip()}"))
        if self.shows_action:
            rendered.extend(_field("[ACTION] ", ACTION_TEXT[self.mode]))
        if self.level is Level.ERROR and self.retry_after:
            rendered.extend(_field("[WHEN]   ", f"Not before: {self.retry_after}"))
        if self.target_files:
            rendered.extend(_field("[TARGET] ", ", ".join(target for target in self.target_files if target.strip())))
        if self.fix:
            rendered.extend(_field("[FIX]    ", self.fix))
        if self.what_to_report:
            rendered.extend(_field("[REPORT] ", self.what_to_report))
        for detail in self.details:
            rendered.extend(_field("[DETAIL] ", detail))
        return rendered

    @property
    def shows_action(self) -> bool:
        """Whether the advisory carries its ``[ACTION]`` directive: always, except a ``brief`` notice without ``fix``."""
        return not (self.level is Level.NOTICE and self.brief and not self.fix)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the advisory as JSON carries it: everything the block shows, and no more.

        ``action`` is the ``[ACTION]`` directive on one line, present exactly when
        the block shows it, so a JSON reader needs no second channel. The failure
        fields (``actor``, ``retry``, ``guardrail``, ``input_error``, and
        ``retry_after`` when set) appear for an ``ERROR`` only; ``fix``,
        ``what_to_report``, ``target_files`` and ``details`` only when they have
        a value. Every key that is absent means "none".
        """
        data: dict[str, Any] = {"code": self.code, "level": self.level.value, "mode": self.mode.value}
        if self.shows_action:
            data["action"] = " ".join(ACTION_TEXT[self.mode].split("\n"))
        if self.level is Level.ERROR:
            data |= {
                "actor": self.actor.value,
                "retry": self.retry.value,
                "guardrail": self.guardrail,
                "input_error": self.input_error,
            }
            if self.retry_after:
                data["retry_after"] = self.retry_after
        if self.fix:
            data["fix"] = self.fix
        if self.what_to_report:
            data["what_to_report"] = self.what_to_report
        targets = [target for target in self.target_files if target.strip()]
        if targets:
            data["target_files"] = targets
        if self.details:
            data["details"] = list(self.details)
        return data
