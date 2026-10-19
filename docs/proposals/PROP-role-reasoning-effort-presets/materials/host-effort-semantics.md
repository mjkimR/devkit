# Host reasoning effort semantics for projected agents

Checked 2026-10-19 against the hosts' official documentation (Q2).

## Claude Code

Source: <https://code.claude.com/docs/en/sub-agents>, <https://code.claude.com/docs/en/model-config>

- Agent frontmatter `effort` is optional: "Effort level when this subagent is active. Overrides the session effort
  level, but not the `CLAUDE_CODE_EFFORT_LEVEL` environment variable. Options: `low`, `medium`, `high`, `xhigh`,
  `max`; available levels depend on the model."
- A per-invocation `effort` parameter overrides the frontmatter field; `CLAUDE_CODE_EFFORT_LEVEL` overrides both.
- An unsupported level falls back to the highest supported level at or below it (`xhigh` runs as `high` on Opus 4.6).
- Model defaults differ: `high` on most models that support effort, `medium` on the 5.5 family. Without a preset a
  reviewer therefore runs at the session's level or the model's default.
- Not documented: behavior on a model that supports no effort at all, and any interaction with `model: inherit`.

## Codex

Source: <https://learn.chatgpt.com/docs/agent-configuration/subagents.md> (redirected from
<https://developers.openai.com/codex/subagents.md>)

- A custom agent TOML file may set `model_reasoning_effort`; accepted values come from the configuration reference
  (`low`, `medium`, `high`, `xhigh`, `max`, `ultra`), limited to what the client and selected model support.
- The file's value takes precedence; otherwise an explicit spawn value, then the `[agents]` default, then the
  parent's value. With neither set the subagent inherits the parent's model and effort.
- Not documented: behavior for a value the model does not support.

## Consequences for the presets

- `low`, `medium` and `high` are accepted by both hosts on current models; higher values depend on the model.
- On Codex a preset cannot be raised per call by the spawning agent; on Claude Code it can.
- An `emulated` Codex role run by the main session itself uses the session's effort; the preset applies only when the
  projected agent is spawned.
