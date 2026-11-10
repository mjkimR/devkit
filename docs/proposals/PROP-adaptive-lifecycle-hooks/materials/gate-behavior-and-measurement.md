# Gate behavior, ledger needs and measurement for PROP-adaptive-lifecycle-hooks

Scope: what a gate needs from the assignment ledger (spike questions Q4 to Q6 of `PROP-adaptive-lifecycle-hooks`),
the behavior the sizing depends on, and the decision criteria and measurement plan for Q1 and Q8. The behavior is
specified only as far as the sizing and the delivery decision need.

## 1. Evidence boundary

- The ledger design is the candidate of `PROP-adaptive-assignment-cli` at commit
  `0cf00a403c208d432fba525cda81f8bdd6cdece6` of branch `plan-adaptive-assignment-cli`, read with `git show` from
  `docs/proposals/PROP-adaptive-assignment-cli/proposal.md` and its two PADRs. It is in Planning and not accepted; its
  two open questions (base dependency, command group name) do not affect this document. Section numbers below
  (§3.2, §3.6) are that proposal's.
- No ledger, command or package `devkit-adaptive` exists on this branch. Nothing here was run against one.
- Timings were taken on this machine in this worktree (4,760 tracked files, four worktrees), three runs each:
  `.venv/bin/devkit host hook --host codex --asset x:y` with a minimal event on stdin took 0.06 s wall time (the
  dispatch fails early, so this is process start, imports and the advisory path);
  `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` took 0.02 to 0.03 s. No larger repository
  was measured.

## 2. What the gate needs from the ledger and the commands

| # | Need | Candidate design | Supplied |
| --- | --- | --- | --- |
| N1 | A read interface a handler can call in process | The list use case is the read interface for other code and is declared in `public_modules` (§3.6) | Yes |
| N2 | A read that fits a hook timeout whatever the repository size | `list` observes every assignment that is not `closed`: one `git status --untracked-files=all` and the HEAD and commit-count reads per assignment (§3.2). The cost is linear in open assignments and in working-tree size, and the candidate's own run lists it as unmeasured | **No.** The gate needs statuses only: the fold of the ledger with no worktree observation. Needed: the list use case accepts "do not observe", or a summary use case |
| N3 | The assignments that belong to the session that is stopping | The ledger is one file per repository, shared by every worktree (§3.6). A record names the assignee's `owner` and `worktree` and a `parent`; nothing names the checkout or session that recorded it (§3.3) | **No.** Needed: the worktree root from which `new` ran, recorded with the assignment. The gate then reads the top-level assignments recorded from the checkout that contains the hook's `cwd`. A host session identity is not available to a command: no fetched page states that a host exposes it to shell commands |
| N4 | Tell a Host session from a worker | Not a ledger matter where the host separates the events: Claude Code documents `Stop` for the main agent only. On Codex it is unknown whether `Stop` fires inside a subagent thread (probe CX-4) | By the host on Claude Code; unknown on Codex |
| N5 | Map a stopping subagent to its assignment | The hook supplies `agent_id`, `agent_type` and `cwd`. The record has no host agent identity; `owner` is free text | **No.** The only derivable key is the assignment whose `worktree` contains the hook's `cwd`. It fails for assignees that share the Host checkout and when a host starts the subagent in the Host's directory (not stated by either host; needs a probe) |
| N6 | A condition that is true when a worker must not stop yet | The assignee runs no command; the delegating agent records `return` after the worker has stopped (§3.7). An assignment is therefore `open` at every `SubagentStop`, finished or not. `verify` refuses an assignment without a return (`ADAPTIVE_ASSIGNMENT_NOT_RETURNED`) | **No.** The ledger status carries no signal at that moment. Two conditions are derivable: a lead with a child that is not `closed`, and the repository facts `list` reports (`no-changes`, `dirty`). A scope check before the return does not exist |
| N7 | Defined results for a missing, damaged or unreachable ledger | No ledger: an empty list, exit `0`. Unterminated fragment: `ADAPTIVE_LEDGER_FRAGMENT_IGNORED` warning and a result. Unparsable line or unknown schema: `ADAPTIVE_LEDGER_UNREADABLE`. No repository: `ADAPTIVE_REPOSITORY_UNSUPPORTED` (§3.5) | Yes |
| N8 | Git calls that ignore the hook process's Git environment | Left to Development: "a hook consumer makes inheritance a risk" (§3.8) | **Open.** Needed: the list use case drops `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` |
| N9 | A stable read contract | The file format is private; the list use case and `list --format json` are the contract (§3.6) | Yes |
| N10 | Age or liveness of an assignment | Excluded by decision: no heartbeat, lease or age threshold; `assigned_at` is recorded (§3.1) | Not supplied, by design. The gate cannot tell a running assignee from an interrupted one from the ledger |

N2, N3 and N8 are small additions to the list use case and to `new` (one recorded field). They change the candidate
record, so they belong to `PROP-adaptive-assignment-cli` or to a follow-up that lands before any gate. N5 and N6 are
not additions: they follow from who records what, which that proposal settled on purpose.

## 3. Behavior the sizing depends on

### 3.1 Host `Stop` gate

A `Stop` event is the end of a turn, not the end of the work: it fires when the Host asks the user a question, waits
for subagents it started in the background, or reports completion. The ledger cannot tell these apart (N10).

Block, once, when every condition holds:

1. The read succeeded and at least one top-level assignment recorded from this checkout (N3) is not `closed`.
2. The host's `stop_hook_active` is false.
3. The set of outstanding assignment IDs with their statuses differs from the set this session was last blocked for.

The reason names the outstanding IDs with their statuses and the two valid continuations: act on them
(`return`, `verify`, `close`, dispatch again), or, when the turn is a pause, name them in `.devkit/adaptive-dev.md`
(`CAP-DLV-adaptive-development` rule 14) and stop again. It states that no assignment needs closing to end a turn.

Release in every other case:

| Case | Behavior | Why |
| --- | --- | --- |
| Repeated stop in one turn | Release on `stop_hook_active` | The host's own loop signal; on Claude Code the host also overrides after eight continuations |
| Later turn with unchanged outstanding set | Release: condition 3 | Without it every turn of a long build ends with a block while any assignment is open. This needs one small record per session under `.devkit/transient/`, keyed by a hash of the session identity; the reference harness uses the same device (`MAT-adaptive-runtime-references` §2.1, "persisted stop signature") |
| Subagents still running (Claude Code) | Release when `background_tasks` lists running tasks | The pause is legitimate; depends on probe CC-4 |
| Explicit cancel | The second stop is the cancel; a user interrupt runs no `Stop` hook on Claude Code. No cancel command is added | A command adds surface and a state to maintain |
| No ledger, empty ledger, no repository | Release, no output | Nothing is outstanding |
| Unreadable ledger, handler error, timeout inside devkit | Release with the existing warning on stderr, `{}` on stdout, exit `0` | `CAP-HOST-lifecycle-observation` §4: failures are advisory |
| Stale assignments from an abandoned run | Block once per session, then release | The ledger has no age threshold (N10); the Host closes them as abandoned or leaves them |

Cost of each error:

- **Wrong release** (the gate stays silent while work is outstanding): the outcome without a gate. The session ends,
  the ledger still holds the assignments, and the next `list` shows them. The harm is a completion claim the user
  reads as final. A gate that cannot run (hook not reviewed on Codex, `devkit` not on the host's PATH, a timeout) is a
  wrong release that nothing reports.
- **Wrong block** (the gate blocks a legitimate stop): one extra model turn each time. Three further costs exist only
  because a gate exists: an agent can clear the gate by closing assignments as `abandoned` or as `integrated` with a
  reason, which damages the record the gate reads; a headless run gains a turn after its final answer, which changes
  the output a script parses; and a session in the same checkout that has nothing to do with the delegation is
  blocked once.

A wrong release costs what the absence of the gate costs. A wrong block is a new cost. The gate is therefore biased
to release, and the measurement in section 4 has to show that the status quo cost is real before the gate is worth
its wrong blocks.

### 3.2 `SubagentStop` gate

The hypothesis of the proposal says a gate prevents workers "from ending with outstanding assignments". Under the
candidate ledger a worker always ends with its assignment `open` (N6), so that condition cannot be the block
condition. What can be checked, given a mapping from the subagent to an assignment (N5):

| Condition | Source | Limit |
| --- | --- | --- |
| A lead stops while a child it recorded is not `closed` | Ledger (`parent`) | Needs the lead's own assignment ID from the mapping |
| A writer stops with no change (`no-changes`) | `list` observation | A read-only or investigative assignment looks the same unless `write` is empty |
| A writer with a commit grant stops with uncommitted paths | `list` observation (`dirty`) | An assignment without the grant leaves uncommitted paths on purpose |
| A writer stops with paths outside its scope | Not available: `verify` needs a return | Needs a check before the return in the assignment feature |

The last row is the one with the largest expected value, because a worker that is still running can repair its own
scope violation, and it is the one the candidate does not offer. A `SubagentStop` gate is therefore not a consumer of
the candidate ledger; it requires a change to it.

### 3.3 `SessionStart` injection (Q5)

Inject only when the read finds top-level assignments recorded from this checkout that are not `closed`. Content,
within devkit's 4,096 character limit:

- one line with the counts per status;
- one line per assignment, in ledger order: ID, status, owner and the first 60 characters of the goal, for as many
  assignments as fit (about 30 at 120 characters each), then the count of the rest;
- one line naming `devkit adaptive assignment list` and `show <id>` and `.devkit/adaptive-dev.md` as the next reads.

What it adds over the guidance pointer: the pointer is static text that tells the Host to read the current context
on resume whether or not anything is outstanding. The injection is present only when the ledger holds outstanding
assignments and names them, so the Host does not have to decide to look. It blocks nothing, and a failed or skipped
injection leaves the pointer in force.

`SessionStart` also fires with `source` `compact` on Codex and Claude Code. The milestone excludes compaction
handling. Injecting after a compaction needs no handling of the compaction itself, and it is the moment when the
board held in context is lost, but whether it falls under the exclusion is the user's reading to give (question q3).

### 3.4 Applicability and opt-in (Q6)

- The hook assets ship in a preset of their own in the `adaptive-dev` bundle. No existing preset gains them:
  `CAP-DLV-adaptive-development` rule 1 fixes the content of `core`, `agents` and `import`.
- A project opts in by selecting that preset and out by deselecting it; sync adds and removes the registrations.
- A caller under SDD that selects only `adaptive-dev:agents` gets no hook. If it also selects the gate preset, the
  gate reads the same ledger; like the commands, it makes no approach check.
- A hook definition names one host (`CAP-HOST-lifecycle-observation` §2). A project that selects an agent the
  definition does not target gets one `unprojected` report per hook asset and agent
  (`packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/inventory.py:214-223`).

## 4. Decision criteria and measurement (Q1 and Q8)

No effect has been measured. None can be measured before the commands of `PROP-adaptive-assignment-cli` exist,
because the failures are defined against the ledger. The criteria below are fixed before any measurement is read.

### 4.1 What the commands and guidance already prevent

- The board survives an interruption or a compaction: the ledger is written at each event, outside the context.
- A resumed Host that follows the guidance runs `list` and treats every `open` assignment as interrupted.
- An out-of-scope write, a moved HEAD and a missing check outcome are reported by `verify`.

What they leave to the Host's attention, which is what a gate would address:

- F1: the Host ends a session, or claims completion, while assignments are not `closed` and it names them nowhere.
- F2: a resumed Host acts before it reads the ledger.
- F3: a worker's return is rejected for a reason the worker could have repaired before it stopped.

### 4.2 Observations

Each is mechanical and comes from the ledger or the working tree, not from a reading of the conversation.

| ID | Observation | Source |
| --- | --- | --- |
| O1 | At session end: the assignments that are not `closed`, by status | `devkit adaptive assignment list --format json` run by the observer after the session |
| O2 | At session end: which of those IDs `.devkit/adaptive-dev.md` names | Text search of the file for each ID |
| O3 | Whether the final message claimed completion | The `completion_claimed` field of the evidence format the scorer reads (`CAP-DLV-adaptive-development`, evidence-scoring test support) |
| O4 | In a resumed session: whether an assignment command ran before the first delegation, edit or completion claim | The ledger event times and `git reflog` of the worktrees against the session start time |
| O5 | Per return: the verification result and its codes | The `verified` events of the ledger |

Failure counts: F1 is a session with at least one ID in O1 that O2 does not name; it is severe when O3 is true. F2 is
a resumed session where O4 is false. F3 is a `rejected` verification whose codes are only
`ADAPTIVE_SCOPE_VIOLATION`, `ADAPTIVE_COMMIT_NOT_GRANTED`, `ADAPTIVE_UNCOMMITTED_CHANGES` or
`ADAPTIVE_CHILDREN_OUTSTANDING`.

### 4.3 Scenarios

Run on each host the user works on, with the commands and guidance and no hook:

| Scenario | Setup | Counts |
| --- | --- | --- |
| Observed runs | The next ten real adaptive sessions that record at least three assignments | F1, F2 (when resumed), F3 |
| `interrupted-writer` | Three assignments dispatched; the Host session is ended while one writer runs; a new session resumes with the prompt "continue" | F2, and F1 at the end of the resumed session |
| `combined-check` | Three assignments whose results pass alone and fail combined; the prompt asks for a report when the work is done | F1 with O3 |
| Pause for input | Three assignments, one returning `needs_input`; the Host must ask the user | F1 with O2, which measures how often a block on that turn would have been a wrong block |

Run each constructed scenario five times per host. A scenario run is one sample; the model and host version are
recorded with it.

### 4.4 Criteria

| Decision | Criterion, read after the measurement |
| --- | --- |
| Deliver a Host `Stop` gate on a host | F1 in at least 2 of the 10 observed runs on that host, or in at least 2 of 5 runs of `combined-check` with O3 true; and the probes for that host show delivery, the reason reaching the model, `stop_hook_active` on the second stop and a released stop on timeout and failure |
| Deliver `SessionStart` injection on a host | F2 in at least 2 of 5 runs of `interrupted-writer`, or in at least 2 observed resumed runs, on that host |
| Deliver a `SubagentStop` gate | F3 in at least 20% of recorded returns across the observed runs, and a design change to the assignment feature that supplies N5 and N6 is accepted first |
| Add a host adapter | A gate or an injection meets its criterion on that host and the host is not Codex |
| Do not deliver | No criterion met. The result and the counts are recorded as the reason |

After a delivery the same scenarios are repeated with the preset selected. The gate is kept when F1 falls and the
pause scenario shows at most one block per pause. The baseline is the same scenario with the preset deselected; the
Host or the user takes both measurements in live host sessions, because a development worker cannot run a host with a
hook registered.
