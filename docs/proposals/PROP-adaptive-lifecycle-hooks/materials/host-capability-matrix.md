# Host capability matrix for PROP-adaptive-lifecycle-hooks

Scope: what a `Stop`, `SubagentStop` or `SessionStart` gate needs from a host, and what Codex, Claude Code,
Antigravity and devkit's host feature provide. It answers spike question Q2 of `PROP-adaptive-lifecycle-hooks` as far
as documentation and code can; section 4 lists what only a live host session can settle.

## 1. Evidence boundary

Every cell carries one evidence class:

| Class | Meaning |
| --- | --- |
| `documented` | Stated on the vendor's own documentation page, retrieved 2026-11-10 through a fetch tool that returns a model-extracted summary. The wording is as extracted and was not compared byte for byte with the page. |
| `code` | Observed in devkit code or tests at commit `79156358` (the base of this Planning branch). |
| `probe` | Not stated on the fetched pages, or stated but decisive for the design: only a live host session settles it (`live-probes.md`). |

- No host was run. No hook was registered on any host and no host setting was read or changed.
- No record of a live hook delivery exists in the repository: a search of `docs/` and `specs/` finds only the
  capability's own statement that deployment and subprocess tests "verify the generated command, not interactive host
  trust or event delivery" (`CAP-HOST-lifecycle-observation` §1,
  `docs/capabilities/host/CAP-HOST-lifecycle-observation.md:36-38`). The existing Codex path is therefore also
  unobserved on a host.
- Locally installed versions at retrieval: Claude Code 2.1.321, codex-cli 0.167.0. The vendor pages name no version
  for the three events.

Sources:

| Key | Page |
| --- | --- |
| CC-H | <https://code.claude.com/docs/en/hooks> (hooks reference) |
| CC-SA | <https://code.claude.com/docs/en/sub-agents> |
| CC-S | <https://code.claude.com/docs/en/settings> |
| CX-H | <https://developers.openai.com/codex/hooks>, which redirects to <https://learn.chatgpt.com/docs/hooks> |
| CX-C | <https://developers.openai.com/codex/config-reference>, which redirects to <https://learn.chatgpt.com/docs/config-file/config-reference> |
| AG-H | <https://antigravity.google/docs/hooks/> |

The Gemini CLI hook pages were read as a neighbour product only and support no cell. The full extraction is recorded
in `envelopes/scout-01.yaml`.

## 2. Matrix

Cell format: **supported**, **unsupported** or **unknown**, then the evidence class and source.

| What a gate needs | Codex | Claude Code | Antigravity | devkit host feature |
| --- | --- | --- | --- | --- |
| Register a hook for `Stop` | **supported**; `documented` CX-H Hook Events | **supported**; `documented` CC-H Events table | **supported** ("Fires when execution terminates"); `documented` AG-H | **supported for Codex only**; `code` `repositories/adapters/codex.py:16`, `models/hooks/model.py:15` (`SUPPORTED_HOSTS = ("codex",)`) |
| Register a hook for `SubagentStop` | **supported**; `documented` CX-H Hook Events, CX-C | **supported**; `documented` CC-H Events table | **unsupported**: absent from the event table; `documented` AG-H | **unsupported** on every host: the event is not in `CodexAdapter.events`, so the definition is `HOST_HOOK_INVALID`; `code` `codex.py:16,26-27` |
| Register a hook for `SessionStart` | **supported**, matcher on `source` (`startup`, `resume`, `clear`, `compact`, `fork`); `documented` CX-H | **supported**, same five `source` values; `documented` CC-H SessionStart | **supported**, no matcher stated; `documented` AG-H | **supported for Codex only**, matcher passed through untranslated; `code` `codex.py:16-18` |
| Receive the session identity | **supported**: `session_id`, `turn_id`, `transcript_path`, `cwd`; `documented` CX-H Common stdin fields | **supported**: `session_id`, `prompt_id`, `transcript_path`, `cwd`; `documented` CC-H Common input fields | **supported with other names**: `conversationId`, `workspacePaths`, `transcriptPath`; no `cwd`; `documented` AG-H | **passed through**: the handler receives the native payload unchanged and no field is normalized; `code` `usecases/runner.py:80`. The command requires an absolute `cwd` (`cli.py:89-95`), which Antigravity's input does not carry |
| Receive the subagent identity | **supported on `SubagentStop`**: `agent_id`, `agent_type`, `agent_transcript_path`; `documented` CX-H Per-Event fields | **supported**: `agent_id` and `agent_type` on `SubagentStop` and on any hook that fires inside a subagent; `documented` CC-H Common input fields, SubagentStop input | **unknown**: not stated; `probe` | **passed through** when the host sends it; `code` `runner.py:80` |
| Return a blocking decision with a reason the agent sees | **supported**: `{"decision":"block","reason":...}` at exit 0, or exit 2 with the reason on stderr; the reason "creates a new continuation prompt"; plain text on stdout is invalid for `Stop`; same contract for `SubagentStop`; `documented` CX-H Stop Output Contract | **supported**: `{"decision":"block","reason":...}` or exit 2 with stderr; the model receives the reason as why it should keep going; on `SubagentStop` the reason is the subagent's next instruction; `documented` CC-H Stop decision control, SubagentStop | **supported with another shape**: `decision: "continue"` keeps the agent running and an optional `reason` is injected as a system message; exit codes are not documented; `documented` AG-H Output contract | **unsupported**: `HookResponse` has one field, `additional_context` (`model.py:39-42`); the adapter raises for context on `Stop` (`codex.py:49-50`); `CAP-HOST-lifecycle-observation` §4 says "Other events accept an empty response only" |
| Detect a repeated stop | **supported as a field**: `stop_hook_active` on `Stop` ("whether this turn was already continued by `Stop`") and on `SubagentStop`; `documented` CX-H. A host-side cap on consecutive blocks is **unknown**; `probe` | **supported**: `stop_hook_active`, and a host cap: after eight consecutive stop-hook continuations the next block is overridden; the counter resets on a tool call; `documented` CC-H Stop. Whether the cap covers `SubagentStop` is **unknown**; `probe` | **unknown**: not stated; `Stop` carries `executionNum` and `fullyIdle`; `probe` | **passed through**; devkit keeps no state between hook calls and has no helper; `code` `runner.py`, `services/observation.py` (the observer stores no session identity) |
| Inject context at session start | **supported**: plain stdout or `hookSpecificOutput.additionalContext`, added as developer context; `documented` CX-H SessionStart | **supported**: plain stdout or `hookSpecificOutput.additionalContext`, added before the first prompt; `documented` CC-H SessionStart | **supported with another shape**: `injectSteps`; `documented` AG-H | **supported for Codex**: `HookResponse(additional_context=...)` rendered as `hookSpecificOutput`; `code` `codex.py:45-51`; test `test_handler_context_and_failures_do_not_corrupt_protocol` |
| Size limit of injected context | About 2,500 tokens per hook output message by default; larger output is saved to disk with a preview; `additionalContextLimit` per handler; `documented` CX-H, CX-C | 10,000 characters for `additionalContext` and plain stdout; larger output is saved to a file with a 2,000 character preview; `documented` CC-H Common output | **unknown**: not stated; `probe` | 4,096 characters, devkit's own limit, below both host limits; `code` `codex.py:49`; `CAP-HOST-lifecycle-observation` §4 |
| Timeout | Seconds; 600 when omitted "for most hooks"; behavior on a timeout or on an exit code other than 0 and 2 for `Stop` and `SubagentStop` is **unknown**; `documented` CX-H Hook Shape for the default, `probe` for the behavior | Seconds; 600 by default for a command hook; a timed-out hook is cancelled and "renders no decision"; an exit code other than 0 and 2 is a non-blocking error; `documented` CC-H Timeouts. The outcome is a released stop; a `Stop`-specific sentence was not captured; `probe` | Seconds; default 30; behavior on timeout **unknown**; `documented` AG-H for the default, `probe` for the behavior | Writes an explicit timeout of 1 to 600 seconds, default 10, into the registration (`model.py:60-61`, `codex.py:40`). Every devkit-side failure prints `{}` and exits 0 (`cli.py:97-103`), so a failed dispatch releases. A process the host kills has host-defined behavior (§4 of the capability) |
| Distinguish the Host session from a subagent | By event on `SubagentStop`. Whether `Stop` also fires inside a subagent thread is **unknown**; `probe` | By event: `Stop` runs for the main agent, and a `Stop` hook in subagent frontmatter is converted to `SubagentStop`; `agent_id` is present inside a subagent; hooks from settings files also run inside subagents; `documented` CC-H Stop, CC-SA | **unknown**; `probe` | No distinction; payload passed through |
| Project-level registration and file owner | `<repo>/.codex/hooks.json` or `<repo>/.codex/config.toml`; loaded only when the project `.codex/` layer is trusted; all sources load together; `documented` CX-H Registration Locations | `.claude/settings.json` (shared) or `.claude/settings.local.json`; the `hooks` key shares the file with permissions, environment and other settings the user owns; entries merge across levels and an identical handler runs once; edits are picked up by a file watcher; `documented` CC-H Hook locations, CC-S | Workspace `.agents/hooks.json`, a map of named hooks, not event to matcher groups; `documented` AG-H Config file and shape | Owns only receipt-recorded matcher groups in `.codex/hooks.json` (`services/configuration.py:52-86`; `CAP-HOST-lifecycle-observation` §3). Writes no other host file for hooks (`CAP-DIST-agent-projections`, host configuration boundary) |
| User-level registration | `~/.codex/hooks.json`, `~/.codex/config.toml`, plugins, managed `requirements.toml`; `documented` CX-H | `~/.claude/settings.json`, managed policy, plugin `hooks/hooks.json`, skill and subagent frontmatter; `documented` CC-H | `~/.gemini/config/hooks.json`, plugin `hooks.json`; `documented` AG-H | **unsupported** and excluded: devkit never writes user-level host settings (`CAP-DIST-agent-projections`) |
| Enablement before a hook runs | Enabled by default; `features.hooks = false` disables. Hooks that are not managed "must be reviewed and trusted before they run"; trust is recorded per hook hash and a changed hook is skipped until reviewed with `/hooks`; `documented` CX-H Trust and Review, Feature Flag | Workspace trust; no hook review step and no feature flag stated; `documented` CC-SA, CC-H | **unknown**: not stated; `probe` | `devkit host status` reports `trust` and `execution_permissions` as `unknown` and cannot see the host's PATH (`usecases/status.py:27-37`; §5 of the capability) |
| Runs without an interactive session | **unknown** for `codex exec`; `probe` | **unknown** for `claude -p` on `Stop` and `SubagentStop`; `probe` | **unknown**; `probe` | Not applicable |

## 3. What the matrix establishes

1. **The two hosts with a documented `SubagentStop` share one contract.** Codex and Claude Code document the same
   event names, the same matcher-group registration shape, `session_id` and `cwd`, `stop_hook_active`, the
   `decision: "block"` response and `hookSpecificOutput.additionalContext`. One host-neutral blocking response can
   render to both. This closes the open item of `MAT-adaptive-runtime-references` §7 at the level of documentation.
2. **devkit's event set is narrower than Codex's.** Codex documents `SubagentStop` and `SubagentStart`; devkit's Codex
   adapter lists six events without them. A subagent gate on Codex needs no new host, only an event added.
3. **The missing blocking response is a devkit gap, not a host gap.** Both hosts accept it for `Stop` and
   `SubagentStop`.
4. **Claude Code has no devkit hook adapter.** Its registration lives in a settings file that also holds permission
   settings, which the host configuration boundary of `CAP-DIST-agent-projections` reserves to the host.
5. **Antigravity needs its own adapter and offers no subagent gate.** Its registration file, input fields and stop
   response differ from the other two, and it documents no subagent event.
6. **A gate that cannot run releases silently on both hosts.** An unreviewed hook on Codex is skipped; a command
   missing from PATH, a timeout or a failed dispatch releases the stop on Claude Code and inside devkit. No host
   reports this to the agent, and `devkit host status` cannot establish it.
7. **A sync that changes a registration disables it on Codex until the user reviews it.** Trust is per hook hash.
   devkit's registration text is stable across syncs (`devkit host hook --host codex --asset <bundle:id>` plus
   matcher and timeout), so only a changed timeout, matcher or asset ID triggers a new review.

## 4. What only a live session settles

`live-probes.md` gives the procedure for each. None blocks the sizing; each can change the gate's behavior or value.

| Item | Host | Why it matters |
| --- | --- | --- |
| A project hook is delivered at all, with the documented fields | Codex, Claude Code | Every cell above is `documented`, none observed |
| `Stop` fires inside a subagent thread | Codex | A Host gate would otherwise block workers |
| Behavior on timeout and on an exit code other than 0 and 2 | Codex | Decides whether a slow or broken gate holds a session |
| A consecutive-block cap | Codex | Without one the gate's own loop breaker is the only release |
| `stop_hook_active` on the second stop | Codex, Claude Code | The loop breaker relies on it |
| The shape of `background_tasks` on `Stop` | Claude Code | Lets a gate tell a pause that waits for running subagents from an end with nothing running |
| Hooks under `codex exec` and `claude -p` | Codex, Claude Code | Headless runs are where a lost assignment is least visible |
| Any Antigravity behavior beyond the event table | Antigravity | Only needed if Antigravity is carried forward |
