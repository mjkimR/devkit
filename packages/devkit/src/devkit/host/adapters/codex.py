"""Codex CLI's project hook format. No trust or permission settings are changed."""

from __future__ import annotations

import shlex
from typing import Any

from devkit.core.receipt import HostHookRecord
from devkit.host.errors import HookDefinitionError, HookDispatchError
from devkit.host.hooks import HookDefinition, HookResponse


class CodexAdapter:
    name = "codex"
    config_path = ".codex/hooks.json"
    events = ("SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop", "SessionEnd")
    context_events = frozenset({"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse"})
    matcher_events = frozenset({"SessionStart", "PreToolUse", "PostToolUse", "SessionEnd"})

    @staticmethod
    def command(asset: str) -> str:
        # Resolved by the host's PATH. No shell interpolation of event input or machine-specific receipt paths.
        return shlex.join(["devkit", "host", "hook", "--host", "codex", "--asset", asset])

    def validate(self, hook: HookDefinition, target: str) -> None:
        if hook.host != self.name or hook.event not in self.events:
            raise HookDefinitionError("unsupported host or Codex lifecycle event", target_files=[target])
        if hook.matcher and hook.event not in self.matcher_events:
            raise HookDefinitionError(f"Codex ignores matchers for {hook.event}; omit matcher", target_files=[target])
        if hook.event == "SessionEnd" and hook.timeout > 3:
            raise HookDefinitionError("Codex SessionEnd timeout must be at most 3 seconds", target_files=[target])

    def record(self, asset: str, hook: HookDefinition) -> HostHookRecord:
        return HostHookRecord(
            self.name, asset, hook.event, hook.handler, self.command(asset), hook.matcher, hook.timeout
        )

    @staticmethod
    def group(record: HostHookRecord) -> dict[str, Any]:
        group: dict[str, Any] = {"hooks": [{"type": "command", "command": record.command, "timeout": record.timeout}]}
        if record.matcher:
            group["matcher"] = record.matcher
        return group

    def response(self, event: str, result: HookResponse) -> dict[str, Any]:
        context = result.additional_context
        if context is None:
            return {}
        if event not in self.context_events or not isinstance(context, str) or len(context) > 4096:
            raise HookDispatchError("handler context must fit 4096 characters and be supported by the event")
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
