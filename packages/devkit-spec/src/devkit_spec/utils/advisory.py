"""Restore a serialized advisory (``AdvisoryError.to_dict``) so a CLI boundary renders it again."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry


def restore_advisory(
    item: Mapping[str, Any],
    *,
    actor: Actor,
    retry: Retry,
    message: str = "",
    restore_brief: bool = False,
    restore_exit_code: bool = False,
) -> AdvisoryError:
    """Rebuild ``item`` with every field it carried.

    ``actor`` and ``retry`` stand in when the advisory omits them (it does below ``ERROR``) and ``message`` when the
    item has none. ``restore_brief`` restores a block without ``[ACTION]`` as brief (``action`` absent);
    ``restore_exit_code`` keeps an ``ERROR``'s ``exit_code``.
    """
    envelope = item.get("advisory") or {}
    level = Level(item.get("level", envelope.get("level", "ERROR")))
    exit_code = item.get("exit_code") if restore_exit_code and level is Level.ERROR else None
    return AdvisoryError(
        item.get("message", message),
        *envelope.get("details", ()),
        code=item.get("code"),
        level=level,
        actor=Actor(envelope.get("actor", actor.value)),
        retry=Retry(envelope.get("retry", retry.value)),
        guardrail=bool(envelope.get("guardrail", False)),
        input_error=bool(envelope.get("input_error", False)),
        retry_after=envelope.get("retry_after"),
        fix=envelope.get("fix"),
        what_to_report=envelope.get("what_to_report"),
        target_files=envelope.get("target_files"),
        brief="action" not in envelope if restore_brief else None,
        exit_code=ExitCode(exit_code) if exit_code else None,
    )
