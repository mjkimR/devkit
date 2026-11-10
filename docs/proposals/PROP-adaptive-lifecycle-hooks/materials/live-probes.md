# Live probes for PROP-adaptive-lifecycle-hooks

Scope: the exact procedure for each host observation that documentation cannot settle
(`host-capability-matrix.md` §4). Planning ran none of them: registering a hook and running a host with it are outside
this Planning run's authority. Each probe uses a throwaway directory, installs no devkit asset and changes no
user-level host setting.

## 1. Rules for every probe

- Run it in a new directory outside every repository checkout. The directory holds the only files the probe creates.
- The hook command is the script below. It appends the hook input to `probe.log` and answers by event.
- Record, per observation, the host version, the event line from `probe.log` and what the host displayed.
- Remove the probe by deleting the directory. On Codex also remove the directory's trust entry if `/hooks` or the
  trust prompt recorded one.

`probe.py`, identical for Codex and Claude Code:

```python
#!/usr/bin/env python3
import json, pathlib, sys, time

raw = sys.stdin.read()
here = pathlib.Path(__file__).resolve().parent
with open(here / "probe.log", "a") as log:
    log.write(raw.strip() + "\n")
event = json.loads(raw)
name = event.get("hook_event_name")
mode = (here / "mode").read_text().strip() if (here / "mode").exists() else "normal"
if mode == "slow":
    time.sleep(20)
if mode == "fail":
    sys.exit(1)
if name == "SessionStart":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": "PROBE-CONTEXT-7391"}}))
elif name in ("Stop", "SubagentStop") and (mode == "always" or not event.get("stop_hook_active")):
    print(json.dumps({"decision": "block", "reason": f"PROBE-BLOCK {name}: reply with the word ACK, then stop."}))
else:
    print("{}")
```

The file `mode` selects a variant: absent or `normal` blocks the first stop only, `always` blocks every stop, `slow`
sleeps past the timeout, and `fail` exits 1.

## 2. Probe CC: Claude Code

Files: `probe.py` (executable) and `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/probe.py", "timeout": 10}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/probe.py", "timeout": 10}]}],
    "SubagentStop": [{"hooks": [{"type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/probe.py", "timeout": 10}]}]
  }
}
```

Start `claude` in the directory and accept the workspace trust prompt.

| # | Step | Observe |
| --- | --- | --- |
| CC-1 | Start the session, then ask "What is the probe context string?" | A `SessionStart` line with `session_id`, `cwd`, `source`; the model answers `PROBE-CONTEXT-7391` |
| CC-2 | Ask "Say hello." | Two `Stop` lines: `stop_hook_active` false, then true; the model writes `ACK` between them; the fields `background_tasks` and `agent_id` (expected absent) on each line |
| CC-3 | Ask "Start a subagent that replies with one word." | A `SubagentStop` line with `agent_id`, `agent_type`, `stop_hook_active`; the subagent writes `ACK` and stops; no `Stop` line carries an `agent_id` |
| CC-4 | Ask it to start a background subagent that waits ten seconds, then answer at once | The `Stop` line written while the subagent runs: the content of `background_tasks` |
| CC-5 | Write `always` to `mode`, ask "Say hello." | The number of `Stop` lines before the host ends the turn (documented: eight continuations) and the message shown |
| CC-6 | Write `slow` to `mode`, ask "Say hello." | The turn ends after about ten seconds; what the host shows |
| CC-7 | Write `fail` to `mode`, ask "Say hello." | The turn ends; what the host shows |
| CC-8 | Remove `mode`; run `claude -p "Say hello."` in the directory | Whether `SessionStart` and `Stop` lines appear, and whether the output contains `ACK` |
| CC-9 | Move the `hooks` object to `.claude/settings.local.json` and repeat CC-2 | Same delivery from the local settings file |

## 3. Probe CX: Codex

Files: `probe.py` (executable) and `.codex/hooks.json` with the same three events; the command is the absolute path of
`probe.py`, because no project directory variable is documented:

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "/ABSOLUTE/PATH/probe.py", "timeout": 10}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "/ABSOLUTE/PATH/probe.py", "timeout": 10}]}],
    "SubagentStop": [{"hooks": [{"type": "command", "command": "/ABSOLUTE/PATH/probe.py", "timeout": 10}]}]
  }
}
```

Start `codex` in the directory, trust the project and review the three hooks with `/hooks`.

| # | Step | Observe |
| --- | --- | --- |
| CX-1 | Before reviewing the hooks, ask "Say hello." | No line in `probe.log`: an unreviewed hook is skipped; what the host shows about it |
| CX-2 | After the review, start a new session and ask "What is the probe context string?" | A `SessionStart` line with `session_id`, `cwd`, `source`; the model answers `PROBE-CONTEXT-7391` |
| CX-3 | Ask "Say hello." | Two `Stop` lines with `stop_hook_active` false, then true; `ACK` between them |
| CX-4 | Ask it to start a subagent that replies with one word | A `SubagentStop` line with `agent_id` and `agent_type`; whether a `Stop` line is also written for the subagent thread (compare `session_id` and `turn_id`) |
| CX-5 | Write `always` to `mode`, ask "Say hello."; interrupt after ten blocks | Whether the host ends the turn by itself, and after how many blocks |
| CX-6 | Write `slow` to `mode`, ask "Say hello." | Whether the turn ends or continues after the ten second timeout; what the host shows |
| CX-7 | Write `fail` to `mode`, ask "Say hello." | Whether the turn ends; what the host shows |
| CX-8 | Remove `mode`; run `codex exec "Say hello."` in the directory | Whether `SessionStart` and `Stop` lines appear |
| CX-9 | Change `timeout` to `11` for `Stop` in `.codex/hooks.json`, start a new session, ask "Say hello." | Whether the changed hook is skipped until reviewed again |

## 4. Probe DK: the existing devkit path on Codex

This probe observes what `CAP-HOST-lifecycle-observation` §1 leaves to "a real Codex session": that a hook devkit
registers is delivered. It uses the built-in `observe` handler and needs no code change.

1. Create a directory with a virtual environment that has `devkit-dist` installed, and run `devkit init` in it with
   the agent `codex`.
2. Add a project bundle with one hook asset whose source is `host = "codex"`, `event = "Stop"`, `handler = "observe"`,
   select it and run `devkit sync`.
3. Start `codex` with the environment's `bin` directory first on PATH, trust the project, review the hook with
   `/hooks` and ask "Say hello."
4. Run `devkit host status --format json`.

Observe: `last_received` names the `Stop` event. Then start `codex` without the PATH change and repeat: the hook
command is not found; record what the host shows and that `last_received` does not change.

## 5. Probe AG: Antigravity

Run it only if Antigravity is carried forward. Follow the registration example on
<https://antigravity.google/docs/hooks/> for the workspace file `.agents/hooks.json` with a `Stop` and a
`SessionStart` hook whose command appends its input to a log. Observe the input fields, whether a subagent run
produces a `Stop` input, the effect of `decision: "continue"` with a `reason`, and the behavior on timeout. The script
above does not apply: the input has no `hook_event_name` documented and the response shape differs.

## 6. Reading the results

| Result | Consequence for the design |
| --- | --- |
| CC-2 or CX-3 shows no second `Stop` line with `stop_hook_active` true | The loop breaker cannot rely on the host field; the gate needs its own per-session record, which adds a work item |
| CX-4 shows `Stop` inside a subagent thread | The Host gate on Codex must tell subagent threads apart before it reads the ledger, or it is not delivered on Codex |
| CX-6 or CX-7 shows a held turn | The gate needs a self-imposed deadline below the host timeout, and a failed dispatch must still print a valid release |
| CX-5 shows no host cap | The gate's own release on `stop_hook_active` is the only loop breaker on Codex |
| CC-4 shows running subagents in `background_tasks` | The gate releases without a block while assigned subagents still run, which removes the most frequent wrong block on Claude Code |
| CC-8 or CX-8 shows no hook in headless mode | The gate has no effect on headless runs; the measurement plan uses interactive sessions only |
| CX-1 and CX-9 as documented | Every installation and every changed registration needs a user review on Codex; the installation guide says so |
