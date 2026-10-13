from __future__ import annotations

from enum import IntEnum, StrEnum


class ExitCode(IntEnum):
    """Process exit codes, following the checker convention of grep, diff and ruff."""

    OK = 0  # Success; nothing found
    FINDINGS = 1  # The command ran and reports a negative result (violations, a needed sync, a refused commit)
    ERROR = 2  # The command could not do its job (usage, unreadable input or configuration, unexpected failure)


class Level(StrEnum):
    """Whether the operation failed (``ERROR``) or succeeded with something to report."""

    ERROR = "ERROR"  # The operation did not do its job, or refused
    WARNING = "WARNING"  # It succeeded; the user must learn or decide something
    NOTICE = "NOTICE"  # It succeeded; something is worth knowing


class Actor(StrEnum):
    """Who takes the next step to resolve the error."""

    TOOL = "TOOL"  # The agent or automated tool itself (e.g. running the fix command)
    USER = "USER"  # A human user (permission, decision, architectural sign-off)
    DEVELOPER = "DEVELOPER"  # A code-editing agent or software engineer
    NONE = "NONE"  # Nobody at present (e.g. transient condition)


class Retry(StrEnum):
    """Whether retrying the operation is safe."""

    SAFE = "SAFE"  # Safe to retry without changing state
    AFTER_FIX = "AFTER_FIX"  # Safe only after the fix has been applied
    UNSAFE = "UNSAFE"  # Not safe to retry (risk of corruption or duplicate run)


class ActionMode(StrEnum):
    """Behavioral directive for the calling agent, derived from advisory fields."""

    AUTO = "AUTO"  # Run the fix command once, then retry once
    INTERACTION = "INTERACTION"  # Stop and ask the user; do not improvise workarounds
    DEFER = "DEFER"  # Error mode: nothing is broken, but the operation did not happen; retry later
    BLOCKED = "BLOCKED"  # Deliberate guardrail refused; do not bypass
    HALT = "HALT"  # Unsafe failure; stop immediately and report
    MAINTENANCE = "MAINTENANCE"  # Codebase or tool defect; needs code repair
    INPUT_ERROR = "INPUT_ERROR"  # Malformed input/flag; fix input before rerunning
    CONTINUE = "CONTINUE"  # A warning: the operation succeeded; tell the user
    NOTE = "NOTE"  # A notice: the operation succeeded; for awareness
