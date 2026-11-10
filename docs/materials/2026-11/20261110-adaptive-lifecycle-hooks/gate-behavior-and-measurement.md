# Gate behavior, ledger needs and measurement for adaptive lifecycle hooks

Scope: what a gate needs from the assignment ledger (spike questions Q4 to Q6 of `MAT-adaptive-lifecycle-hooks`),
the behavior the sizing depends on, and the decision criteria and measurement plan for Q1 and Q8. The behavior is
specified only as far as the sizing and the delivery decision need.

## 1. Evidence boundary

- The ledger design is that of `PROP-adaptive-assignment-cli`, read with `git show` at commit
  `0cf00a403c208d432fba525cda81f8bdd6cdece6` of its Planning branch from
  `docs/proposals/PROP-adaptive-assignment-cli/proposal.md` and its two PADRs. The proposal has since been accepted
  on the base branch (commit `caa50fa7`). Read again there, the rows of section 2 are unchanged except N8, which the
  accepted design decides: Git calls inherit the environment. Section numbers below (§3.2, §3.6) are that
  proposal's and are the same in both versions.
- No ledger, command or package `devkit-adaptive` exists on this branch. Nothing here was run against one.
- Timings were taken on this machine in this worktree (4,760 tracked files, four worktrees), three runs each:
  `.venv/bin/devkit host hook --host codex --asset x:y` with a minimal event on stdin took 0.06 s wall time (the
  dispatch fails early, so this is process start, imports and the advisory path);
  `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` took 0.02 to 0.03 s. No larger repository
  was measured.

## 2. What the gate needs from the ledger and the commands

| # | Need | Assignment design | Supplied |
| --- | --- | --- | --- |
| N1 | A read interface a handler can call in process | The list use case is the read interface for other code and is declared in `public_modules` (§3.6) | Yes |
| N2 | A read that fits a hook timeout whatever the repository size | `list` observes every assignment that is not `closed`: one `git status --untracked-files=all` and the HEAD and commit-count reads per assignment (§3.2). The cost is linear in open assignments and in working-tree size, and that proposal's first Planning run lists it as unmeasured | **No.** A gate that needs statuses only wants the fold of the ledger with no worktree observation: the list use case accepts "do not observe", or a summary use case. At the 0.03 s measured here it is optional for a small repository |
| N3 | The assignments that belong to the session that is stopping | The ledger is one file per repository, shared by every worktree (§3.6). A record names the assignee's `owner` and `worktree` and a `parent`; nothing names the checkout or session that recorded it (§3.3) | **No.** Needed: the worktree root from which `new` ran, recorded with the assignment. The gate then reads the top-level assignments recorded from the checkout that contains the hook's `cwd`. Whether a host exposes its session identity to a shell command is not stated on the fetched pages, so a session key is not assumed |
| N4 | Tell a Host session from a worker | Not a ledger matter where the host separates the events: Claude Code documents `Stop` for the main agent only. On Codex it is unknown whether `Stop` fires inside a subagent thread (probe CX-4) | By the host on Claude Code; unknown on Codex |
| N5 | Map a stopping subagent to its assignment | The hook supplies `agent_id`, `agent_type` and `cwd`. The record has no host agent identity; `owner` is free text | **Partly.** The derivable key is the assignment whose `worktree` contains the hook's `cwd`. It covers an assignee in its own worktree, which `CAP-DLV-adaptive-development` rule 20 requires of concurrent writers, if the host reports the subagent's working directory there (probes CC-3b, CX-4b). It does not cover an assignee that shares the Host checkout |
| N6 | A condition that is true when a worker must not stop yet | The assignee runs no command; the delegating agent records `return` after the worker has stopped (§3.7). An assignment is therefore `open` at every `SubagentStop`, finished or not, and `verify` refuses an assignment without a return (`ADAPTIVE_ASSIGNMENT_NOT_RETURNED`) | **Partly.** The status carries no signal at that moment. Three conditions are derivable without one: a lead with a child that is not `closed` (ledger), and `no-changes` and `dirty` (the `list` observation). Paths outside the scope are not reported before a return; `list` reads worktrees "with the same Git commands as `verify`", so reporting them is an addition to that observation, not a command an assignee runs |
| N7 | Defined results for a missing, damaged or unreachable ledger | No ledger: an empty list, exit `0`. Unterminated fragment: `ADAPTIVE_LEDGER_FRAGMENT_IGNORED` warning and a result. Unparsable line or unknown schema: `ADAPTIVE_LEDGER_UNREADABLE`. No repository: `ADAPTIVE_REPOSITORY_UNSUPPORTED` (§3.5) | Yes |
| N8 | Git calls that ignore the hook process's Git environment | Decided otherwise there: "Git calls inherit the environment". The commands read the repository that `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` name when these are set, and the capability states this as a limit (§3.1, §3.4) | **No, by decision.** A hook process that a host starts with one of these variables set reads the repository it names |
| N9 | A stable read contract | The file format is private; the list use case and `list --format json` are the contract (§3.6) | Yes |
| N10 | Age or liveness of an assignment | Excluded by decision: no heartbeat, lease or age threshold; `assigned_at` is recorded (§3.1) | Not supplied, by design. The gate cannot tell a running assignee from an interrupted one from the ledger |

Two groups of additions follow, both in the assignment feature:

- **W6**: N2 and N3. One recorded field on `new` and a list read without observation. N3 changes the accepted
  record. `PROP-adaptive-assignment-cli` is accepted, so W6 cannot enter its Planning: it is a follow-up to that
  unit, delivered before a `Stop` gate and before observed runs are counted in a repository with concurrent sessions
  (section 4.2). A session-start injection that blocks nothing works without W6: it then lists every outstanding
  assignment of the repository with its worktree.
- **W6b**: paths outside the scope in the `list` observation of an `open` assignment (N6). Only a `SubagentStop`
  gate needs it.

## 3. Behavior the sizing depends on

### 3.1 Host `Stop` gate

A `Stop` event is the end of a turn, not the end of the work: it fires when the Host asks the user a question, waits
for subagents it started in the background, or reports completion. The ledger cannot tell these apart (N10).

The failure the gate targets is F1 of section 4.1: the Host ends while assignments are outstanding and names them
nowhere. Two block conditions are possible. Both block only when the read succeeded, at least one top-level
assignment recorded from this checkout (N3) is not `closed`, and the host's `stop_hook_active` is false.

| | Name-aware condition | State-only condition |
| --- | --- | --- |
| Further condition | At least one outstanding ID does not occur as a whole token in `.devkit/adaptive-dev.md` | The set of outstanding IDs with their statuses differs from the set this session was last blocked for |
| Matches F1 | Yes: a Host that named the IDs before pausing (`CAP-DLV-adaptive-development` rule 14) is not blocked | No: it blocks a correct pause |
| Blocks in an active build | One per turn end until every outstanding ID is named or closed. Acting on an assignment, a cancel by second stop and continuation 3 release that stop only | About one per turn end, because every `new`, `return`, `verify` and `close` changes the set |
| State the gate keeps | None as stated. With none, a cancel is forgotten at the next turn end and an unrelated session in the checkout is blocked at every turn end. The record of the other column, applied to the unnamed set, makes a cancel last for the session; gap G11 then applies to both conditions | One record per session under `.devkit/transient/`, keyed by a hash of the session identity (gap G11) |
| Contract it touches | `CAP-DLV-adaptive-development` says the file is "not managed/transient state or a parsed lifecycle" (`:328`), and the accepted ledger storage decision says "No command reads or writes it". A token search by a hook handler reads it | None |
| What it misses | An ID named at an earlier pause whose status changed since | Nothing by construction |

The sizing of the gate handler (W8, size M) holds under both, with or without the record. What selects the
condition is one decision: whether a hook handler may read `.devkit/adaptive-dev.md`. Allowing it changes the
sentence of `CAP-DLV-adaptive-development` quoted above and needs a decision that supersedes the sentence "No
command reads or writes it" of the ledger storage decision in `PROP-adaptive-assignment-cli`, which is accepted.
That decision is not settled here; it belongs to the
specification if a gate is delivered. If it is refused, only the state-only condition remains, and by the
wrong-block criterion of section 4.4 that condition is not deliverable on a host where Hosts name their assignments
before pausing: no `Stop` gate is then delivered there.

The reason names the outstanding IDs with their statuses and three valid continuations:

1. act on them (`return`, `verify`, `close`, dispatch again);
2. when the turn is a pause, name them in `.devkit/adaptive-dev.md` and stop again;
3. when they are not this session's work, change nothing and stop again.

It states that no assignment needs closing to end a turn.

Release in every other case:

| Case | Behavior | Why |
| --- | --- | --- |
| Repeated stop with no tool call in between | Release on `stop_hook_active` | The host's own loop signal; on Claude Code the host also overrides after eight such continuations |
| Repeated stop after the model ran a tool | Under the name-aware condition: release only when every outstanding ID is named or closed; a `return`, a `verify` or a new dispatch leaves the IDs unnamed and the gate blocks again unless it keeps the record. Under the state-only condition: release when the set is unchanged | Whether `stop_hook_active` is still true then is unknown on both hosts (probes CC-2b, CX-3b) |
| Subagents still running (Claude Code) | Release when `background_tasks` lists a running subagent | The pause is legitimate. Only if subagent entries can be told from background shell entries (probe CC-4); otherwise the release is dropped, because a background shell would release every stop |
| Explicit cancel | The second stop is the cancel; a user interrupt runs no `Stop` hook on Claude Code. No cancel command is added | A command adds surface and a state to maintain |
| No ledger, empty ledger, no repository | Release, no output | Nothing is outstanding |
| Unreadable ledger, handler error, timeout inside devkit | Release with the existing warning on stderr, `{}` on stdout, exit `0` | `CAP-HOST-lifecycle-observation` §4: failures are advisory |
| Stale assignments from an abandoned run | Blocked until named or closed as abandoned (name-aware), or once per session (state-only) | The ledger has no age threshold (N10) |
| The Host's `cwd` is another worktree at the stop | Released silently: the project lookup and the checkout filter both follow `cwd` (gap G16) | Known limit |

Cost of each error:

- **Wrong release** (the gate stays silent while work is outstanding): the outcome without a gate. The session ends,
  the ledger still holds the assignments, and the next `list` shows them. The harm is a completion claim the user
  reads as final. A gate that cannot run (hook not reviewed on Codex; on Claude Code `devkit` not on the host's PATH, or
  a timeout) is a wrong release that nothing reports. This equality holds as long as the guidance a gate adds replaces no manual
  step.
- **Wrong block** (the gate blocks a legitimate stop): one extra model turn each time. Three further costs exist only
  because a gate exists: an agent can clear the gate by closing assignments as `abandoned` or as `integrated` with a
  reason, which damages the record the gate reads; a headless run gains a turn after its final answer, which changes
  the output a script parses; and a session in the same checkout that has nothing to do with the delegation is
  blocked, once with a record and at every turn end without one.

A wrong release costs what the absence of the gate costs. A wrong block is a new cost. The gate is therefore biased
to release, and the measurement in section 4 has to show that the status quo cost is real, and that the chosen
condition would not have blocked correct pauses, before the gate is worth delivering.

### 3.2 `SubagentStop` gate

The hypothesis of the proposal says a gate prevents workers "from ending with outstanding assignments". Under the
assignment ledger a worker always ends with its assignment `open` (N6), so the status cannot be the block condition.
Two gates of different cost follow.

**Narrow gate, for an assignee in its own worktree.** The assignment is the one whose `worktree` contains the hook's
`cwd` (N5). Conditions:

| Condition | Source | Limit |
| --- | --- | --- |
| A lead stops while a child it recorded is not `closed` | Ledger (`parent`) | The assignment guidance already has a lead close its children before it returns |
| A writer with a commit grant stops with uncommitted paths | `list` observation (`dirty`) | An assignment without the grant leaves uncommitted paths on purpose. `verify` reports this as a warning, not a failed check, so F3 does not count it |
| A writer without a commit grant stops with commits | `list` observation (`commits`) | Corresponds to the `commit` check |
| A writer stops with paths outside its scope | `list` observation with W6b | Needs the addition; the largest expected value, because a worker that still runs can repair its own violation |
| A writer stops with no change (`no-changes`) | `list` observation | Applied only to an assignment with a commit grant: without the grant the final commit is always the base and the recorded verification holds no changed paths, so an accepted no-change result cannot be counted (section 4.2). A read-only or investigative assignment looks the same unless `write` is empty. A correct result can be no change; the condition is kept only under the wrong-block term of section 4.4 |

It depends on four things that are not established: the host reports the subagent's working directory as `cwd`
(probes CC-3b, CX-4b); devkit dispatches correctly for a `cwd` in another worktree (gap G16); W6b is added to the
assignment feature; and the host bounds repeated blocks of a subagent. None of these conditions has a naming
release, a blocked worker runs tools before it stops again, and no host states a cap for `SubagentStop`. If
`stop_hook_active` is false after a tool call (probes CC-3c, CX-4c), the gate keeps a record per subagent (gap G11)
and blocks each condition once. It needs no command run by an assignee and makes no command block a session.

**Every-assignee gate.** An assignee that shares the Host checkout, or a host that reports the Host's directory,
cannot be mapped to an assignment. Covering it needs a host agent identity in the record, written by the delegating
agent after the subagent starts. That changes who records what in the assignment design.

### 3.3 `SessionStart` injection (Q5)

Inject only when the read finds assignments that are not `closed`: those recorded from this checkout when N3 exists,
otherwise all of the repository with their worktrees. Content, within devkit's 4,096 character limit:

- one line with the counts per status;
- one line per assignment, in ledger order: ID, status, owner and the first 60 characters of the goal, for as many
  assignments as fit (about 30 at 120 characters each), then the count of the rest;
- one line naming `devkit adaptive assignment list` and `show <id>` and `.devkit/adaptive-dev.md` as the next reads.

What it adds over the guidance pointer: the pointer is static text that tells the Host to read the current context
on resume whether or not anything is outstanding. The injection is present only when the ledger holds outstanding
assignments and names them, so the Host does not have to decide to look. It blocks nothing, and a failed or skipped
injection leaves the pointer in force.

Both documented hosts list `compact` among the `source` values of `SessionStart`. The user excluded compaction
handling from this work. Injecting after a compaction handles nothing about the compaction itself, and it is the
moment when the board held in context is lost; whether the exclusion covers it is the user's to say (question q4).
That the event fires after a compaction is extracted from documentation, not observed (probes CC-10, CX-11).

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
- F3: a worker's return fails verification for a reason the worker could have repaired before it stopped.

### 4.2 Observations

Each observation names its source and whether it is computed or read by a rule. None is taken from the Host's own
account of what it did.

| ID | Observation | Source | Kind |
| --- | --- | --- | --- |
| O1 | At session end: the session's assignments that are not `closed`, by status | `devkit adaptive assignment list --format json` after the session. In a constructed scenario: every assignment, because the scenario has a repository of its own. In an observed run: the assignments whose `assigned_at` lies inside the session window and, for a resumed run, inside the window of the session it resumes; or those recorded from the session's checkout once N3 exists | Computed |
| O2 | At session end: which of those IDs `.devkit/adaptive-dev.md` names | Each ID as a whole token (not preceded or followed by a letter, digit or hyphen) in a file modified after the session started | Computed |
| O3 | Whether the final message claimed completion | The observer reads the last assistant message of the host transcript and sets `completion_claimed` in the evidence format the scorer reads (`CAP-DLV-adaptive-development`, evidence-scoring test support). Rule: true when the message says the requested work is done and names no outstanding assignment | Read by rule |
| O4 | In a resumed session: whether an assignment command ran before the first edit or subagent call | The host transcript: the position of the first tool call whose command contains `devkit adaptive assignment` against the first file edit or subagent tool call. The ledger cannot show it, because `list` and `show` write no event | Computed from the transcript |
| O5 | Per return: the verification result and its per-check statuses | The `verified` events of the ledger (`show <id> --format json`) | Computed |
| O6 | At each turn end with outstanding assignments: whether every outstanding ID was named (O2 taken at that moment) | The transcript's turn boundaries, and the file as of each one | Read by rule; taken in the constructed scenarios only |

The session window (start and end time) comes from the first and last entries of the host transcript. The transcript
formats are the hosts' own and not a contract; the observer records the host version with each sample.

Failure counts:

- F1 is a session with at least one ID in O1 that O2 does not name. It is counted by status: `open`, action due
  (`returned` or `rejected`), and `verified` but not closed. Only the first two count toward a criterion; a verified
  assignment left unclosed is bookkeeping. F1 is severe when O3 is true.
- F2 is a resumed session where O4 is false.
- F3 is a failed verification whose failed checks are only among `scope`, `commit` and `children`.
- A would-be wrong block is a turn end in O6 at which a block condition of section 3.1 would block although every
  outstanding ID is named. It is zero by definition for the name-aware condition, so it measures the state-only
  condition only.
- A would-be wrong block of the narrow `SubagentStop` gate is a return of an assignment with a write scope and a
  commit grant whose final commit is its base, that passed verification and was closed as `integrated`: a result
  accepted with no committed change, which the `no-changes` condition would have blocked. It is read from the
  record `show <id> --format json` prints.

Another session recording during the window shows as an assignment inside the window whose `new` call is absent
from the session transcript. An observed run with such an assignment is counted only once N3 exists. Constructed
scenarios run in a repository of their own with an empty ledger.

### 4.3 Scenarios

Run on each host the user works on, with the commands and guidance and no hook:

| Scenario | Setup | Counts |
| --- | --- | --- |
| Observed runs | Real adaptive sessions that record at least three assignments, until ten are collected on a host or 30 days have passed since the commands were delivered, whichever comes first | F1, F2 (when resumed), F3 |
| `interrupted-writer` | Three assignments dispatched; the Host session is ended while one writer runs; a new session resumes with the prompt "continue" | F2, and F1 at the end of the resumed session |
| `combined-check` | Three assignments whose results pass alone and fail combined; the prompt asks for a report when the work is done | F1 with O3 |
| Pause for input | Three assignments, one returning `needs_input`; the Host must ask the user. Run only while the state-only condition is a candidate | O6: would-be wrong blocks of the state-only condition |

Run each constructed scenario five times per host. A scenario run is one sample; the model and host version are
recorded with it.

### 4.4 Criteria

The thresholds are conventions, not estimates: two occurrences is the smallest count that is not a single accident,
and samples of five and ten show that a failure recurs but do not estimate its rate. A host with fewer than five
observed runs at the end of the window is judged on the constructed scenarios alone.

| Decision | Criterion, read after the measurement |
| --- | --- |
| Deliver a Host `Stop` gate on a host | F1 (`open` or action due) in at least 2 observed runs on that host, or in at least 2 of 5 runs of `combined-check` with O3 true; and the probes for that host show the hook delivered, the reason reaching the model, a release on the repeated stop, and a released stop when the hook command fails (CC-7, CX-7) or, where CX-7 shows a held turn, a fallback in the generated command that probe CX-7b shows to release it. With the name-aware condition the decision rests on these alone. The state-only condition also needs fewer than 3 of the 5 pause runs to show a would-be wrong block |
| Deliver `SessionStart` injection on a host | F2 in at least 2 of 5 runs of `interrupted-writer`, or in at least 2 observed resumed runs, on that host |
| Deliver the narrow `SubagentStop` gate on a host | F3 in at least 20% of recorded returns across the observed runs, with at least ten returns; and probes CC-3b or CX-4b show the subagent's own worktree as `cwd`. Its `no-changes` condition is included only if no would-be wrong block of that gate occurred in the window |
| Add a host adapter | A gate or an injection meets its criterion on that host and the host is not Codex |
| Do not deliver | No criterion met at the end of the window. The counts are recorded as the reason |

A held turn on a timeout inside the handler (probe CX-6) is not a criterion: it adds a self-imposed deadline to the
gate handler. A held turn when the hook command itself fails (probe CX-7) is one: a host started without `devkit`
on its PATH (gap G12) would then hold every stop, and neither a deadline nor devkit's own failure path runs in that
case. The remedy is a fallback in the generated command that prints `{}`, which changes
`CAP-HOST-lifecycle-observation` §4 and the command the receipt records and is added to W1; without it no `Stop`
gate is delivered on that host (`live-probes.md` §6).

After a delivery the same scenarios are repeated with the preset selected, the pause scenario included. The gate is
kept when F1 falls and the pause scenario shows fewer than 3 wrong blocks in 5 runs. The baseline is the same scenario with the preset
deselected; the Host or the user takes both measurements in live host sessions, because a development worker cannot
run a host with a hook registered.
