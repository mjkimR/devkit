# Live probes for PROP-adaptive-lifecycle-hooks

Scope: the exact procedure for each host observation that documentation cannot settle
(`host-capability-matrix.md` §4). Planning ran none of them: registering a hook and running a host with it are outside
this Planning run's authority. Each probe uses a throwaway directory, installs no devkit asset and writes no
user-level host setting itself. The host's own trust and review prompts record the directory in user-level host
state; the cleanup of section 1 removes that.

Host behavior is bound to a host version. A probe that a delivery criterion names is repeated on the version current
when the criterion is read.

## 1. Rules for every probe

- Run it in a new parent directory outside every repository checkout. It holds `main/`, a new Git repository whose
  one commit contains a `README` only, and `wt/`, a linked worktree of it (`git -C main worktree add ../wt`). The
  probe files are created in `main/` after the commit and stay untracked, so `wt/` holds none of them. The host
  starts in `main/`. These are the only files the probe creates.
- The hook command is the script below. It appends the hook input to `probe.log` and answers by event.
- Record, per observation, the host version, the event line from `probe.log` and what the host displayed.
- Remove the probe by deleting the parent directory. On Codex also remove the directory's trust entry if `/hooks` or
  the trust prompt recorded one.

`probe.py`, identical for Codex and Claude Code:

```python
#!/usr/bin/env python3
import json, os, pathlib, sys, time

raw = sys.stdin.read()
here = pathlib.Path(__file__).resolve().parent
event = json.loads(raw)
with open(here / "probe.log", "a") as log:
    line = {"process_cwd": os.getcwd(), "project_dir": os.environ.get("CLAUDE_PROJECT_DIR"), "input": event}
    log.write(json.dumps(line) + "\n")
name = event.get("hook_event_name")
mode = (here / "mode").read_text().strip() if (here / "mode").exists() else "normal"
if mode == "slow":
    time.sleep(20)
if mode == "fail":
    sys.exit(1)
if name == "SessionStart":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": "PROBE-CONTEXT-7391"}}))
elif name in ("Stop", "SubagentStop") and (mode.startswith("always") or not event.get("stop_hook_active")):
    task = "run the shell command `echo PROBE-TOOL`, then stop" if mode.endswith("tool") else "reply with the word ACK, then stop"
    print(json.dumps({"decision": "block", "reason": f"PROBE-BLOCK {name}: {task}."}))
else:
    print("{}")
```

Each log line holds the hook input under `input`, the process's working directory and the project directory
variable. Planning ran the script with synthetic events in every mode under the proposal's ignored `.probe/`
directory: it prints one valid JSON object and exits `0`, or exits `1` in `fail` mode. No host ran it.

The file `mode` selects a variant: absent or `normal` blocks the first stop only and asks for a word; `tool` blocks
the first stop only and asks for a shell command, as the real gate's reason asks for commands or an edit; `always`
and `always-tool` block every stop; `slow` sleeps past the timeout; `fail` exits 1.

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
| CC-2b | Write `tool` to `mode`, ask "Say hello." | The `Stop` line after the model ran `echo PROBE-TOOL`: whether `stop_hook_active` is true. If it is false the script blocks again: when a third block appears, record it and interrupt |
| CC-3 | Remove `mode`. Ask "Start a subagent that replies with one word." | A `SubagentStop` line with `agent_id`, `agent_type`, `stop_hook_active`, `cwd`; the subagent writes `ACK` and stops; no `Stop` line carries an `agent_id` |
| CC-3b | Ask "Start a subagent that creates the file `note.txt` in the directory `../wt` and replies with one word." | The `cwd` on that `SubagentStop` line: `main/` or `wt/` |
| CC-3c | Write `tool` to `mode` and repeat CC-3; then `always-tool` | For a subagent: whether `stop_hook_active` is true on the `SubagentStop` after the tool call, and under `always-tool` whether the host ever ends the subagent by itself (interrupt after twelve blocks) |
| CC-4 | Ask it to start a background subagent that waits ten seconds, then answer at once. Repeat with a background shell command that sleeps thirty seconds and no subagent | The `Stop` line written while each runs: the entries of `background_tasks` and how a subagent entry differs from a shell entry |
| CC-5 | Write `always` to `mode`, ask "Say hello."; then `always-tool` | The number of `Stop` lines before the host ends the turn (documented: eight continuations without a tool call) and the message shown; under `always-tool`, whether the host ever ends the turn by itself (interrupt after twelve blocks) |
| CC-6 | Write `slow` to `mode`, ask "Say hello." | The turn ends after about ten seconds; what the host shows |
| CC-7 | Write `fail` to `mode`, ask "Say hello." | The turn ends; what the host shows |
| CC-8 | Remove `mode`; run `claude -p "Say hello."` in the directory | Whether `SessionStart` and `Stop` lines appear, and whether the output contains `ACK` |
| CC-9 | Move the `hooks` object to `.claude/settings.local.json` and repeat CC-2 | Same delivery from the local settings file |
| CC-10 | In a session with several turns, run the host's manual compaction command | Whether a `SessionStart` line with `source` `compact` is written, and whether the model can then state the probe context string |

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
| CX-3b | Write `tool` to `mode`, ask "Say hello." | The `Stop` line after the model ran `echo PROBE-TOOL`: whether `stop_hook_active` is true. If it is false the script blocks again: when a third block appears, record it and interrupt |
| CX-4 | Remove `mode`. Ask it to start a subagent that replies with one word | A `SubagentStop` line with `agent_id`, `agent_type` and `cwd`; whether a `Stop` line is also written for the subagent thread (compare `session_id` and `turn_id`) |
| CX-4b | Ask it to start a subagent that creates the file `note.txt` in the directory `../wt` and replies with one word | The `cwd` on that `SubagentStop` line: `main/` or `wt/` |
| CX-4c | Write `tool` to `mode` and repeat CX-4; then `always-tool` | For a subagent: whether `stop_hook_active` is true on the `SubagentStop` after the tool call, and under `always-tool` whether the host ever ends the subagent by itself (interrupt after twelve blocks) |
| CX-5 | Write `always` to `mode`, ask "Say hello."; interrupt after ten blocks; then `always-tool` | Whether the host ends the turn by itself, and after how many blocks, in each mode |
| CX-6 | Write `slow` to `mode`, ask "Say hello." | Whether the turn ends or continues after the ten second timeout; what the host shows |
| CX-7 | Write `fail` to `mode`, ask "Say hello." | Whether the turn ends; what the host shows |
| CX-8 | Remove `mode`; run `codex exec "Say hello."` in the directory | Whether `SessionStart` and `Stop` lines appear |
| CX-9 | Change `timeout` to `11` for `Stop` in `.codex/hooks.json`, start a new session, ask "Say hello." | Whether the changed hook is skipped until reviewed again |
| CX-10 | Copy `.codex/hooks.json` unchanged into `wt/` (the command still names `main/probe.py`), start `codex` there, ask "Say hello." | Whether the same registration in a second checkout needs its own trust and review |
| CX-11 | In a session with several turns, run the host's manual compaction command | Whether a `SessionStart` line with `source` `compact` is written |

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
| CC-2 or CX-3 shows no second `Stop` line with `stop_hook_active` true | The loop breaker cannot rely on the host field; the gate needs its own per-turn record |
| CC-2b or CX-3b shows `stop_hook_active` false after the tool call | The host field covers only a stop with no tool call in between. A gate whose reason asks for work must bound its blocks itself. The name-aware condition does so only when the Host names or closes the assignments; for every other continuation, and for the state-only condition, the gate keeps a per-session record (`gate-behavior-and-measurement.md` §3.1) |
| CC-3c or CX-4c shows `stop_hook_active` false after the tool call, or no host cap | The narrow `SubagentStop` gate keeps a record per subagent and blocks each condition once |
| CC-3b or CX-4b shows `cwd` in `main/` | A subagent cannot be mapped to its assignment by worktree on that host, and the narrow `SubagentStop` gate is not buildable there |
| CC-3b or CX-4b shows `cwd` in `wt/` | The mapping works, and devkit's project lookup then reads the worker checkout's receipt and host file (gap G16) |
| CC-10 or CX-11 shows no `SessionStart` after a compaction | Question q4 has no effect on that host |
| CX-10 shows a new review | Every worktree needs a review before its hooks run on Codex |
| CX-4 shows `Stop` inside a subagent thread | The Host gate on Codex must tell subagent threads apart before it reads the ledger, or it is not delivered on Codex |
| CX-6 shows a held turn | The gate handler gets a self-imposed deadline below the host timeout |
| CX-7 shows a held turn | A hook command that fails before devkit runs, as when `devkit` is not on the host's PATH, holds every stop. Either the generated command gains a fallback that prints `{}`, which changes `CAP-HOST-lifecycle-observation` §4 and the command the receipt records, or no `Stop` gate is delivered on Codex |
| CX-5 shows no host cap | The gate's own release on `stop_hook_active` is the only loop breaker on Codex |
| CC-4 shows subagent entries that differ from shell entries in `background_tasks` | The gate releases without a block while subagents still run. If the entries cannot be told apart, the release is dropped: a background shell would otherwise release every stop |
| CC-8 or CX-8 shows no hook in headless mode | The gate has no effect on headless runs; the measurement plan uses interactive sessions only |
| CX-1 and CX-9 as documented | Every installation and every changed registration needs a user review on Codex; the installation guide says so |
