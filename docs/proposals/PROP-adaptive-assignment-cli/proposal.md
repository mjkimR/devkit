---
id: PROP-adaptive-assignment-cli
title: Assignment ledger and return verification commands for adaptive delegation
summary: "Add commands that record delegated assignments and verify a returned result against its assignment, so a Host resumes outstanding work from recorded state and checks scope, source identity and declared checks deterministically."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-adaptive-development-runtime
depends_on: [PROP-adaptive-package-extraction]
boundaries:
  owns:
    - packages/
    - docs/capabilities/delivery/
    - docs/usecases/delivery/UC-advance-an-idea.md
    - docs/architecture/ARCH-05-2-components.md
    - docs/decisions/2026-11/20261102-adaptive-development-and-research.md
    - docs/development/reference/
    - .devkit/architecture.toml
  excludes:
    - packages/devkit-spec/
    - packages/devkit-dist/src/devkit_dist/features/host/
    - packages/devkit/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-adaptive-assignment-cli] Assignment ledger and return verification commands for adaptive delegation

## 1. Background & Hypothesis

In adaptive development the Host delegates to swarm agents with a goal, source identity, exclusive write scope,
checks and return fields (`CAP-DLV-adaptive-development` rules 13 and 13a). The assignment board exists only in the
Host's context. `.devkit/adaptive-dev.md` is free Markdown the Host updates "when useful and before pausing", so an
unplanned interruption or context compaction loses outstanding assignments. The Host checks a returned result by
reading its diff; no command compares the result with the assignment.

`MAT-adaptive-runtime-references` records that comparable harnesses write assignment state in code when each event
happens and gate completion on it, and that their evidence checks stop at the shape of a file. Adaptive assignments
already carry a worktree, a base identity and a write scope, so a command can check the repository itself.

Hypothesis: a small command set that records assignments and verifies returns makes resume and completion checks
deterministic for large parallel builds without a scheduler, a process runner or per-change SDD records.

## 2. Technical Spike Questions

Planning answered each question; §3 holds the settled design and §3.10 the two questions left for the user.

| Question | Answer | Where |
| --- | --- | --- |
| Q1 Command surface | `devkit adaptive assignment new\|return\|verify\|close\|list\|show`; a failed verification, an out-of-scope write included, exits `1` | §3.2, §3.4, §3.5 |
| Q2 Ledger | Append-only JSON Lines under the shared Git directory; the delegating agent writes | §3.6, `PADR-adaptive-assignment-ledger-storage` |
| Q3 Verification | Ancestry, HEAD, commit grant, changed paths against literal path prefixes, declared checks against recorded outcomes, children; `new` refuses an overlapping scope | §3.3, §3.4 |
| Q4 Nesting | `--parent`; one level below the Host's assignment; child authority inside the parent's; the parent fails verification while a child is not closed | §3.3, §3.4 |
| Q5 Reuse | `devkit_core` and `devkit_dist` helpers; no `devkit_spec` import; harness features not needed | §3.8, `materials/planning-evidence.md` §3 |
| Q6 Resume | `list` reports repository facts per assignment and no liveness; a new context treats every open assignment as interrupted | §3.2 `list`, §3.7 |
| Q7 Current context | The Markdown names assignment IDs and the next action; the ledger holds scope, base and checks; no command reads or writes the Markdown | §3.7 |
| Q8 Guidance | The delegating agent runs the commands where available; the manual procedure stays as the fallback; archetypes and support roles need none | §3.7 |
| Q9 Evidence scorer | Kept unchanged as test support | §3.1 |

## 3. Proposed Design & Impact

### 3.1 Planning decisions

Decisions that meet the admission criteria are PADRs: `PADR-adaptive-assignment-commands` (the command group, what it
compares and what stays a Host judgment) and `PADR-adaptive-assignment-ledger-storage` (location and format). The
other choices:

- **Write scope is literal path prefixes.** An entry names a file or a directory with its subtree; `.` names the
  whole worktree. `*`, `?` and `[` are refused. Containment, overlap and narrowing are then exact, and the SDD worker
  inspection uses the same rule (`materials/planning-evidence.md` §6). Globs can be added later without invalidating
  an entry.
- **Verification runs no check.** It compares each declared check with the outcome the delegating agent recorded from
  the return. The user excluded a process runner.
- **Closing does not require a passed verification.** `close --outcome integrated` on an assignment that is not
  `verified` needs `--reason` and reports the `ADAPTIVE_CLOSED_UNVERIFIED` warning. The Host's judgment is recorded
  instead of blocked (root `AGENTS.md`, Proportionate Guardrails).
- **No heartbeat, lease or age threshold.** The Host assigns directly, so no claim needs to expire
  (`MAT-adaptive-runtime-references` §6). `list` prints `assigned_at` and repository facts; whether an agent still
  runs is not recorded.
- **CLI only.** No MCP service is added; no rule requires one (scout-02).
- **The command contract gets its own capability**, CAP-DLV-adaptive-assignments. `CAP-DLV-adaptive-development`
  holds 39 agent-guidance rules; the commands have a tested, deterministic contract that
  `PROP-adaptive-lifecycle-hooks` will cite. The ID is written without backticks in this bundle because the document
  does not exist yet (`RULE-document-reference`); Development backticks it in the promoted decisions once it does.
- **The evidence scorer stays unchanged.** `adaptive_behavior_scorer.py` scores supplied evidence of agent behavior
  (a completion claim against a combined result, retained ownership and recovery records). The commands compare a
  repository with an assignment. Neither replaces the other, and this unit does not edit the scorer or its test.
- **One spec, size L** stands: one feature, its guidance and its documents.
- **`dev_effort` stays `medium`.** The ledger is local, untracked state with no migration.

### 3.2 Commands

The group is `devkit adaptive assignment`, mounted by the entry point `adaptive = "devkit_adaptive.cli:cli"` in the
`devkit.commands` group of `devkit-adaptive` (`ARCH-05-3-command-plugins`). Every command:

- takes `--format text|json` and the standard `-q`, `-v`, `--strict` and `--workspace-root` options from
  `devkit_dist.adapters.cli`;
- resolves the repository from the workspace root (default: the current directory) and works from any worktree of it;
- performs no approach check and needs no bundle selection.

IDs match `^[a-z0-9][a-z0-9-]{0,39}$`. Revisions are stored as full commit IDs. Timestamps are UTC, ISO 8601 with
seconds and a `Z` suffix.

**`new`** records an assignment with status `open`.

```text
devkit adaptive assignment new --owner <text> --goal <text>
    [--id <id>] [--role <text>] [--worktree <path>] [--base <rev>]
    [--write <path>]... [--commit] [--check <name>[=<command>]]...
    [--governing <id-or-path>]... [--depends-on <id>]... [--parent <id>]
    [--evidence <text>] [--handoff <text>] [--stop <text>]
```

- `--id` defaults to `a<N>`, the first unused `N` counting from the number of recorded assignments plus one.
- `--worktree` defaults to the worktree containing the workspace root. It must be a worktree of the same repository.
- `--base` defaults to the HEAD of that worktree and must resolve to a commit; a repository without a commit gives
  `ADAPTIVE_REVISION_UNRESOLVED`. The base is the commit the assignee starts from, so record an assignment when it
  is dispatched: a dependent assignment after its dependency's result is in its worktree.
- `--write` is repeatable and takes a path relative to the worktree root, or an absolute path under it. No `--write`
  records a read-only assignment.
- `--commit` records that the assignee may commit. Without it the assignee must leave HEAD at the base.
- `--check` declares a check by name; the optional command text is recorded and never run.
- `--governing`, `--evidence`, `--handoff` and `--stop` are recorded text for resume and are not verified.
- `new` also records `dirty_at_assign`: the uncommitted and untracked paths of the worktree at that moment.
- Refusals, each exit `2`: an existing ID, an unknown `--parent` or `--depends-on` ID, a closed parent, a parent that
  itself has a parent, authority not inside the parent's, and a write scope that overlaps another assignment (§3.3).

**`return`** records what the assignee returned and sets status `returned`.

```text
devkit adaptive assignment return <id> --status completed|needs_input|failed
    [--final <rev>] [--check <name>=<outcome>]... [--unverified <text>]... [--summary <text>]
```

- `--final` defaults to the HEAD of the assignment's worktree; a given value must resolve to a commit.
- `<outcome>` is `pass`, `fail`, `skipped` or `unavailable`. An outcome for an undeclared name is recorded and never
  fails verification.
- A later `return` on an assignment that is not `closed` replaces the current return; the earlier one stays in the
  event history.

**`verify`** compares the current return with the repository (§3.4), records the result and sets status `verified`
or `rejected`. Exit `0` on `pass`, `1` on `fail`. It may be repeated; each run recomputes from the repository.

```text
devkit adaptive assignment verify <id>
```

**`close`** ends an assignment with status `closed`.

```text
devkit adaptive assignment close <id> --outcome integrated|abandoned [--reason <text>]
```

- `--reason` is required for `abandoned`, and for `integrated` when the status is not `verified`.
- `integrated` on a status other than `verified` succeeds with the `ADAPTIVE_CLOSED_UNVERIFIED` warning.
- A parent with a child that is not `closed` is refused (`ADAPTIVE_CHILDREN_OUTSTANDING`, exit `2`).

**`list`** prints the assignments that are not `closed`; `--all` adds the closed ones. For each one that is not
`closed` it observes the worktree and reports:

- `worktree_state`: `present` or `missing`;
- `head`: the worktree HEAD; `commits`: the number of commits in `<base>..HEAD`; `dirty`: the number of uncommitted
  and untracked paths not in `dirty_at_assign`;
- `waiting_on`: the `depends_on` assignments that are not `closed`;
- `attention`: zero or more of `worktree-missing`, `base-not-ancestor` (HEAD does not descend from the base),
  `head-moved` (a return exists and HEAD is not its final commit) and `no-changes` (status `open`, HEAD is the base
  and `dirty` is `0`).

With a missing worktree, `head`, `commits` and `dirty` are null (`-` in text) and `attention` is
`worktree-missing` alone. A closed assignment has `"observed": null` in JSON and `-` for the observed fields in
text. `list` reads worktrees with the same Git commands as `verify` (§3.4) and exits `0` whatever it lists.

**`show <id>`** prints one assignment with every recorded field, its current return and its event history. It is
the read a new context uses to dispatch an assignment again.

Text output, one sentinel per line, values rendered with `field_value`:

| Command | Lines |
| --- | --- |
| `new`, `return`, `close` | `[ASSIGNMENT: <id> status=<status> owner=<owner> role=<role> parent=<id> worktree=<path> base=<sha> final=<sha> outcome=<outcome>]`; `final` and `outcome` are `-` until set |
| `verify` | one `[CHECK: <name> status=pass\|fail\|not-run\|not-applicable]` per check in the order of §3.4, one `[OUT_OF_SCOPE: <path> change=committed\|uncommitted]` per offending path, then `[VERIFICATION: <id> result=pass\|fail final=<sha> changed=<n> out_of_scope=<n>]` |
| `list` | one `[ASSIGNMENT: <id> status=<status> owner=<owner> role=<role> parent=<id> worktree=<path> worktree_state=<state> head=<sha> commits=<n> dirty=<n> waiting_on=<ids> attention=<values> assigned_at=<timestamp>]` per assignment, lists comma-separated, then `[SUMMARY: open=<n> returned=<n> verified=<n> rejected=<n> closed=<n>]` |
| `show` | the `[ASSIGNMENT: ...]` line; `[GRANT: commit=yes\|no]`; one `[FIELD: <name> value=<text>]` for each of `goal`, `evidence`, `handoff`, `stop`, `return_summary` and `close_reason` that is set; one `[WRITE: <path>]` per scope entry; one `[GOVERNING: <id-or-path>]`, `[DEPENDS_ON: <id>]` and `[UNVERIFIED: <text>]` per entry; one `[DECLARED_CHECK: <name> command=<text> outcome=<outcome>]` per declared check; one `[EVENT: <type> at=<timestamp>]` per event |

JSON output is one compact object (`ARCH-08-1-agent-output` §4):

| Command | Object |
| --- | --- |
| `new`, `return`, `close`, `show` | `{"assignment": <assignment>, "notices": [...]}`; `show` adds `"events": [...]` |
| `verify` | `{"id", "result", "final", "checks": {...}, "changed_paths": {"committed": [...], "uncommitted": [...], "preexisting_dirty": [...]}, "errors": [...], "notices": [...]}`; `errors` holds one advisory per code that applies |
| `list` | `{"assignments": [<assignment> plus "observed": {"worktree_state", "head", "commits", "dirty", "waiting_on", "attention"}], "summary": {"open", "returned", "verified", "rejected", "closed"}, "notices": [...]}` |

The `checks` object of `verify` has exactly these keys and members:

| Key | Members |
| --- | --- |
| `return` | `status`, `returned` (the return status) |
| `base` | `status`, `base`, `final` |
| `head` | `status`, `head`, `final` |
| `commit` | `status` |
| `scope` | `status`, `outside`: list of `{"path", "change"}` with `change` `committed` or `uncommitted` |
| `checks` | `status`, `missing`: list of names, `not_passed`: list of `{"name", "outcome"}` |
| `children` | `status`, `outstanding`: list of IDs |

### 3.3 Records

An `<assignment>` object:

| Field | Type | Meaning |
| --- | --- | --- |
| `id`, `status` | string | `status` is `open`, `returned`, `verified`, `rejected` or `closed` |
| `owner`, `role`, `goal` | string | `role` may be null |
| `worktree`, `base` | string | Absolute worktree path; full commit ID |
| `write` | list of strings | Normalized POSIX paths relative to the worktree root; empty for read-only |
| `commit` | boolean | Whether the assignee may commit |
| `checks` | list of `{"name", "command"}` | `command` may be null |
| `governing`, `depends_on` | list of strings | |
| `parent`, `evidence`, `handoff`, `stop` | string or null | |
| `assigned_at` | timestamp | |
| `dirty_at_assign` | list of strings | |
| `return` | null or `{"status", "final", "checks": [{"name", "outcome"}], "unverified": [...], "summary", "returned_at"}` | The current return |
| `verification` | null or `{"result", "final", "checks": {<name>: <status>}, "verified_at"}` | Result of the latest `verify` of the current return; null after a later `return` |
| `close` | null or `{"outcome", "reason", "closed_at"}` | |

Status transitions: `new` gives `open`; `return` gives `returned` from any status but `closed`; `verify` gives
`verified` or `rejected` from `returned`, `verified` or `rejected`; `close` gives `closed` from any other status.
Every other command on a `closed` assignment is refused (`ADAPTIVE_ASSIGNMENT_CLOSED`).

Write-scope rules:

- An entry covers a path when the path equals the entry or starts with the entry followed by `/`; `.` covers every
  path.
- Two entries overlap when one covers the other.
- `new` refuses a scope with an entry that overlaps an entry of another assignment that is not `closed`
  (`ADAPTIVE_SCOPE_OVERLAP`), whatever their worktrees. Two assignments are exempt: the parent, and each assignment
  named in `--depends-on`, because a dependent assignment is sequenced after it. The advisory names the other
  assignment and both entries, and its `[FIX]` lists the three routes: narrow the scope, close the other
  assignment when its work is finished, or name it in `--depends-on` when this work is sequenced after it.
- With `--parent`, each write entry must be covered by an entry of the parent, and `--commit` requires the parent's
  commit grant (`ADAPTIVE_AUTHORITY_NOT_NARROWED`). The parent must have no parent (`ADAPTIVE_NESTING_DEPTH`), which
  keeps the depth at Host, lead, child.

### 3.4 Verification

`verify` evaluates these checks in order. The result is `pass` when no check is `fail` or `not-run`.

| Check | Passes when | Code on failure |
| --- | --- | --- |
| `return` | The return status is `completed` | `ADAPTIVE_RETURN_NOT_COMPLETED` |
| `base` | The base is an ancestor of the final commit (`git merge-base --is-ancestor`) | `ADAPTIVE_BASE_NOT_ANCESTOR` |
| `head` | The worktree HEAD is the final commit | `ADAPTIVE_HEAD_MOVED` |
| `commit` | The final commit is the base; `not-applicable` when the assignment grants commits | `ADAPTIVE_COMMIT_NOT_GRANTED` |
| `scope` | A write entry covers every changed path; `not-run` when `base` failed | `ADAPTIVE_SCOPE_VIOLATION` |
| `checks` | Every declared check has the outcome `pass`; `not-applicable` without declared checks | `ADAPTIVE_CHECK_OUTCOME_MISSING` for a declared check without an outcome, `ADAPTIVE_CHECK_NOT_PASSED` for `fail`, `skipped` or `unavailable` |
| `children` | Every assignment naming this one as parent is `closed`; `not-applicable` without children | `ADAPTIVE_CHILDREN_OUTSTANDING` |

Changed paths are the union of:

- committed: `git diff --no-renames --name-only -z <base> <final>`, so a rename counts under both names;
- uncommitted: `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` in the worktree, both names
  of a rename or copy, minus the paths in `dirty_at_assign`. `--no-optional-locks` keeps the command from taking
  `index.lock` in a worktree where an assignee is working.

Stated limits, which the capability and the reference page repeat:

- Ignored files and writes outside the worktree are not observed.
- A path in `dirty_at_assign` is excluded even when the assignee changed it again; `verify` lists such paths under
  `preexisting_dirty` with the `ADAPTIVE_PREEXISTING_DIRTY` notice.
- Paths brought in by merging another branch into the assignment's branch count as changed.
- In a checkout that the Host or another agent edits at the same time, changed paths cannot be attributed; the Host
  judges that result and records its reason at `close`.
- A recorded outcome repeats the assignee's report; no check is run.

In-scope uncommitted paths do not fail `scope`. When the assignment grants commits, `verify` reports them with the
`ADAPTIVE_UNCOMMITTED_CHANGES` warning, because the final commit does not contain them. Without the grant they are
the expected result and no warning is raised.

### 3.5 Codes and exit codes

Exit `0`: success, warnings and notices included. Exit `1`: `verify` with a failed check, or a warning under
`--strict`. Exit `2`: the command could not run or refused. `CAP-HARN-command-mount` §4.7 describes `devkit spec` and
`devkit docs` only and does not change.

Every code is one `AdvisoryError` subclass of a package base error, prefixed `ADAPTIVE_`
(`RULE-advisory-unique-code`). The mode is the derived `[ACTION]` mode of `CAP-ADV-agent-advisory-protocol` §5; each
class sets the fields that derive it (`input_error` for `INPUT_ERROR`, `actor = USER` for `INTERACTION`) and a `fix`.

| Code | Level, exit, mode | Raised when |
| --- | --- | --- |
| `ADAPTIVE_REPOSITORY_UNSUPPORTED` | error, `2`, `INPUT_ERROR` | The workspace root is not inside a non-bare Git work tree |
| `ADAPTIVE_LEDGER_UNREADABLE` | error, `2`, `INTERACTION` | A newline-terminated line cannot be parsed, or an event has an unknown schema number; the report asks whether to move the damaged ledger aside |
| `ADAPTIVE_LEDGER_UNWRITABLE` | error, `2`, `INTERACTION` | The ledger directory, lock or file cannot be created or written; the report says the assignments stay unrecorded |
| `ADAPTIVE_ASSIGNMENT_UNKNOWN` | error, `2`, `INPUT_ERROR` | An ID, `--parent` or `--depends-on` names no assignment |
| `ADAPTIVE_ASSIGNMENT_EXISTS` | error, `2`, `INPUT_ERROR` | `new --id` names a recorded assignment |
| `ADAPTIVE_ASSIGNMENT_CLOSED` | error, `2`, `INPUT_ERROR` | `return`, `verify` or `close` on a closed assignment, or `new --parent` naming one |
| `ADAPTIVE_ASSIGNMENT_NOT_RETURNED` | error, `2`, `INPUT_ERROR` | `verify` on an assignment without a return |
| `ADAPTIVE_WORKTREE_UNAVAILABLE` | error, `2`, `INPUT_ERROR` | `new`, a `return` without `--final`, or `verify` cannot read the assignment's worktree, or `--worktree` belongs to another repository |
| `ADAPTIVE_REVISION_UNRESOLVED` | error, `2`, `INPUT_ERROR` | `--base` or `--final`, given or defaulted, does not resolve to a commit |
| `ADAPTIVE_SCOPE_OVERLAP` | error, `2`, `INPUT_ERROR` | `new`: a write entry overlaps another open assignment (§3.3) |
| `ADAPTIVE_AUTHORITY_NOT_NARROWED` | error, `2`, `INPUT_ERROR` | `new --parent`: a write entry or the commit grant exceeds the parent's |
| `ADAPTIVE_NESTING_DEPTH` | error, `2`, `INPUT_ERROR` | `new --parent`: the parent has a parent |
| `ADAPTIVE_CHILDREN_OUTSTANDING` | error, `1` from `verify`, `2` from `close`, `INPUT_ERROR` | A child is not closed |
| `ADAPTIVE_RETURN_NOT_COMPLETED`, `ADAPTIVE_BASE_NOT_ANCESTOR`, `ADAPTIVE_HEAD_MOVED`, `ADAPTIVE_COMMIT_NOT_GRANTED`, `ADAPTIVE_SCOPE_VIOLATION`, `ADAPTIVE_CHECK_OUTCOME_MISSING`, `ADAPTIVE_CHECK_NOT_PASSED` | error, `1`, `INPUT_ERROR`, collected by `verify` | The check of §3.4 failed; `ADAPTIVE_SCOPE_VIOLATION` names at most 20 paths and the count of the rest |
| `ADAPTIVE_UNCOMMITTED_CHANGES` | warning | `verify`: the assignment grants commits and in-scope uncommitted paths exist |
| `ADAPTIVE_CLOSED_UNVERIFIED` | warning | `close --outcome integrated` on a status other than `verified` |
| `ADAPTIVE_LEDGER_FRAGMENT_IGNORED` | warning | A reader skipped an unterminated final fragment |
| `ADAPTIVE_PREEXISTING_DIRTY` | notice | `verify`: paths in `dirty_at_assign` are still dirty |

A verification failure is `INPUT_ERROR` because the Host corrects the returned work and verifies again
(`CAP-ADV-agent-advisory-protocol` §6, the note under `BLOCKED`). No code derives `MAINTENANCE`.

devkit's own codes pass through: `ARGUMENT_INVALID` (a malformed ID, a write entry with `*`, `?` or `[` or outside
the worktree, a malformed `--check`, an unknown outcome, a missing required `--reason`), `LOCK_HELD` and
`GIT_FAILED`. With the distribution absent, `devkit adaptive` is click's usage error, exit `2`, without a code.

### 3.6 Ledger

`PADR-adaptive-assignment-ledger-storage` decides location and format. The details Development implements:

- Directory `<git common dir>/devkit/adaptive/`, created on the first write; files `ledger.jsonl` and `lock`.
- One event per line: `{"schema": 1, "at": <timestamp>, "event": "assigned"|"returned"|"verified"|"closed", "id":
  <id>, "data": {...}}`. `data` holds the fields that event sets (§3.3).
- A write takes the exclusive lock (`devkit_core.core.file_lock`, 10 second bound), reads and folds the ledger,
  validates, then appends one newline-terminated line and flushes it to disk.
- Bytes after the last newline are a fragment of an interrupted append, not an event. A reader skips the fragment
  with the `ADAPTIVE_LEDGER_FRAGMENT_IGNORED` warning. A writer, holding the lock, truncates the file back to the
  last newline before it appends, so a fragment never becomes an earlier line.
- `list` and `show` read without the lock.
- The file format is private. `devkit adaptive assignment list --format json` and the list use case are the read
  interface for other code, `PROP-adaptive-lifecycle-hooks` included; the list use case module is declared in
  `public_modules`.
- No command deletes or rewrites an event, and no pruning command is added.

### 3.7 Guidance

The delegating agent runs the commands: the Host for its assignments and a role lead for its children. An assignee
never runs them. Bundle text changes, each conditional on the commands being available:

| Asset | Change |
| --- | --- |
| `skills/adaptive-dev/references/delegation.md` | Before dispatching a deliverable, record it with `new` and put the ID in the payload. After the return, record it with `return`, then run `verify`; treat `result=fail` (status `rejected`) as a rejected return (existing step 15) and route its codes to repair, and do not read exit `1` alone as a failure, because `--strict` also gives it. On `ADAPTIVE_SCOPE_OVERLAP`, narrow the scope, close the finished assignment, sequence with `--depends-on`, or leave a bounded experiment unrecorded; never name a dependency that does not exist. Close with `close` after integrating or abandoning. |
| `skills/adaptive-dev/references/orchestration.md` | A `swarm-worker` or `swarm-verifier` lead records each child with `--parent <its ID>` when the payload supplies that ID, and closes its children before it returns. A `swarm-planner` lead has no shell and records nothing; the Host records its children from the returned partition or leaves them unrecorded. On interruption and before a pause, run `list`. |
| `skills/adaptive-dev/references/current-context.md` | On resume run `list` beside reading `.devkit/adaptive-dev.md`. In a new context treat every `open` assignment as interrupted: no agent from an earlier context is assumed to run. For each one, read `worktree_state`, `commits`, `dirty` and `attention` from `list` and the goal, stop condition, commit grant and checks from `show <id>`, then record a return from the retained state, dispatch it again, or close it as abandoned. Before pausing, name the outstanding assignment IDs and the next recovery action in the Markdown; the ledger holds their scope, base and checks. An ID the ledger lacks is stale context. |
| `templates/current-context.md` | One sentence under "Next useful action": name outstanding assignments by ledger ID when the commands are in use. |
| `subagents/swarm-planner.md`, `swarm-worker.md`, `swarm-verifier.md` | One procedure sentence in each: when the payload supplies an assignment ID, return it with the result. `swarm-worker` and `swarm-verifier` add, self-contained: as a lead, when the payload permits it, record each child with `uv run devkit adaptive assignment new --parent <ID>` and close it before returning; if the command cannot run, report the children as unrecorded. No prerequisite is added (`CAP-DLV-adaptive-development` rule 19). |
| `AGENTS.md` (bundle constitution) | One line naming the command group as optional delegation support. |

Fallback, stated once in `delegation.md` and cited by the other files: when `devkit adaptive assignment` is missing
(click's usage error), exits `2` with `ADAPTIVE_REPOSITORY_UNSUPPORTED`, `ADAPTIVE_LEDGER_UNWRITABLE` or
`ADAPTIVE_LEDGER_UNREADABLE`, or the host denies the write, the Host keeps the board in its context and `.devkit/adaptive-dev.md`, checks returns by reading
the diff, reports the assignments as unrecorded, and does not reroute a denied write.

Callers and roles:

- **SDD callers that select only `adaptive-dev:agents`** receive the commands with the distribution. The archetypes
  work without them. Such a caller may use them; they write no SDD record and replace none, and
  `devkit spec worker inspect` stays the SDD check.
- **The three product-support roles** (`product-clarifier`, `product-researcher`, `usage-reviewer`) keep their
  contracts and run no command. The Host may record such an assignment without `--commit`, with the researcher's
  scratch or prototype paths as `--write`. `verify` then checks that HEAD stayed at the base and that no path
  outside the scope changed. When the role shares the Host's checkout, the last limit of §3.4 applies.

The `adaptive-import` skill and the conversion playbook do not name the commands.

### 3.8 Package, feature and reuse

- Feature `assignment` in `devkit-adaptive`: `features/assignment/` with `cli`, `usecases`, `services`,
  `repositories` and `models`; one `BaseUseCase` per verb; errors in the package's base error module, following
  `devkit-spec`. The package and directory names are those `PROP-adaptive-package-extraction` settles; this document
  writes `devkit_adaptive` and `packages/devkit-adaptive/`.
- `.devkit/architecture.toml`: the feature, its `feature_dependencies` entry
  (`devkit_dist.features.project` for repository lookup, nothing else) and the public list use case module.
- Git access through `devkit_core.core.run_git`, `run_git_text` and `is_ancestor`, with the worktree as the working
  directory. Development decides whether to drop `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` from the
  environment as the spec scope collector does (`collection_git.py:23-29`); a hook consumer makes inheritance a risk.
- Locking and paths through `devkit_core.core.file_lock`, `normalize_relpath` and `resolve_within`.
- Written in the feature: changed-path collection, the worktree-list parser, the prefix matcher and the event fold.
  The equivalents live in `devkit_spec` or in private `devkit_agt` modules (`materials/planning-evidence.md` §3).
- No import of `devkit_spec`. No use of `devkit worktree` or `devkit exec`: the commands create no worktree and run
  no process. The guidance keeps "the project's documented worktree procedure".
- Tests: unit tests for the fold, the prefix rules and each check; integration tests on temporary repositories with
  a linked worktree through the CLI; a documented-codes test like
  `packages/devkit-spec/tests/integration/package/test_documented_codes.py`; one command call in the installed
  consumer test of the bundle; bundle content tests for the guidance sentences.

Whether the package depends on `devkit-dist` only or on `devkit-agt` is question q1. The design above needs
`devkit-dist` only and is valid under both answers.

### 3.9 Acceptance scenarios

Each scenario is a test on a temporary repository unless it says otherwise.

- **AC-01**: Given a repository with a linked worktree, when `new` runs in the main worktree with `--worktree`,
  `--write src/a` and `--check tests`, then the assignment is `open` with the worktree HEAD as base, and `list` run
  from the linked worktree prints it.
- **AC-02**: Given any command of the group has run, then `git status --porcelain` of every worktree is unchanged
  and no tracked file changed.
- **AC-03**: Given an open assignment with `--write src/a`, when `new` records `--write src/a/x.py` or `--write .`
  for another assignment, then it exits `2` with `ADAPTIVE_SCOPE_OVERLAP` and appends nothing; with
  `--depends-on <the first ID>` it succeeds; `--write src/ab` succeeds.
- **AC-04**: Given a returned assignment whose commits changed only paths under its write scope and whose declared
  checks all have `pass`, when `verify` runs, then it exits `0`, prints `result=pass` and the status is `verified`.
- **AC-05**: Given a return whose commit renamed a file from inside the scope to outside it, or left an untracked
  file outside the scope, when `verify` runs, then it exits `1` with `ADAPTIVE_SCOPE_VIOLATION`, lists each
  offending path with `change=committed` or `change=uncommitted`, and the status is `rejected`.
- **AC-06**: Given a return whose final commit does not descend from the base, then `verify` exits `1` with
  `ADAPTIVE_BASE_NOT_ANCESTOR` and `scope` is `not-run`. Given the worktree HEAD moved after `return`, then `verify`
  exits `1` with `ADAPTIVE_HEAD_MOVED`.
- **AC-07**: Given declared checks `tests` and `lint` and a return with `tests=pass` only, then `verify` exits `1`
  with `ADAPTIVE_CHECK_OUTCOME_MISSING`; with `lint=skipped` it exits `1` with `ADAPTIVE_CHECK_NOT_PASSED`.
- **AC-08**: Given an assignment without `--commit` and a return whose final commit is not the base, then `verify`
  exits `1` with `ADAPTIVE_COMMIT_NOT_GRANTED`. Given the same assignment with only uncommitted in-scope paths and
  HEAD at the base, then `verify --strict` exits `0` with `result=pass` and no warning; with `--commit` granted the
  same state reports `ADAPTIVE_UNCOMMITTED_CHANGES` and `verify --strict` exits `1` with `result=pass`.
- **AC-09**: Given a parent with `--write src` and `--commit`, when a child is recorded with `--write docs`, then
  `new` exits `2` with `ADAPTIVE_AUTHORITY_NOT_NARROWED`; a child of a child exits `2` with `ADAPTIVE_NESTING_DEPTH`;
  while a child is not closed, `verify` of the parent exits `1` and `close` of the parent exits `2`, both with
  `ADAPTIVE_CHILDREN_OUTSTANDING`.
- **AC-10**: Given a `rejected` assignment, when the worktree is repaired, `return` is recorded again and `verify`
  passes, then the status is `verified` and `show` lists both returns in its events.
- **AC-11**: Given a `rejected` assignment, when `close --outcome integrated` runs without `--reason`, then it exits
  `2` with `ARGUMENT_INVALID`; with `--reason` it exits `0` with the `ADAPTIVE_CLOSED_UNVERIFIED` warning, and `1`
  under `--strict`.
- **AC-12**: Given three open assignments, one whose worktree was removed, one with a commit and one untouched, when
  `list` runs in a fresh process, then it reports `attention=worktree-missing`, `commits=1` and
  `attention=no-changes` respectively and exits `0`; closed assignments appear only with `--all`. In the same
  process `show <id>` prints the goal, the stop condition, the commit grant, the write scope and the declared checks
  that `new` recorded, in text and in JSON.
- **AC-13**: Given two processes that run `new` at the same time, then both assignments are recorded with distinct
  IDs and every ledger line parses. Given a ledger that ends with an unterminated fragment, then `list` succeeds with
  `ADAPTIVE_LEDGER_FRAGMENT_IGNORED`; after a following `new`, `list` exits `0` without the warning and every line
  of the file parses. A newline-terminated line that does not parse gives `ADAPTIVE_LEDGER_UNREADABLE`, exit `2`.
- **AC-14**: Given a directory outside a Git work tree, then every command exits `2` with
  `ADAPTIVE_REPOSITORY_UNSUPPORTED`. Given a repository without a commit, then `list` exits `0` with an empty list
  and `new` exits `2` with `ADAPTIVE_REVISION_UNRESOLVED`. Given a ledger directory that cannot be written, then `new` exits `2` with
  `ADAPTIVE_LEDGER_UNWRITABLE`.
- **AC-15**: For every command, `--format json` prints exactly one compact object with the keys of §3.2, a failure
  prints `{"error": ..., "notices": ...}`, and text mode prints only the sentinels of §3.2 on stdout.
- **AC-16**: Every `ADAPTIVE_` code declared in the package appears in a document under `docs/` (documented-codes
  test), and `devkit rules check` reports no `RULE-architecture`, `RULE-usecase-boundaries` or
  `RULE-advisory-unique-code` finding for the package.
- **AC-17**: The bundle content tests find the conditional command steps and the fallback in `delegation.md`, the
  resume rule in `current-context.md`, and no command name in the product-support role contracts, the
  `adaptive-import` skill or the conversion playbook. The three archetypes state no prerequisite.
- **AC-18**: The installed-consumer test installs `devkit-adaptive` without `devkit-spec`, runs
  `devkit adaptive assignment list --format json` and gets an empty `assignments` list with exit `0`.
- **AC-19**: A test imports every module of the package (`pkgutil.walk_packages`), the CLI module included, and then
  finds no `devkit_spec` module in `sys.modules`.

### 3.10 Open questions

- **q1 Base dependency of `devkit-adaptive`** (shared with `PROP-adaptive-package-extraction`): `devkit-dist` only
  (recommended) or `devkit-agt`. `materials/planning-evidence.md` §7 states what each allows and forbids.
- **q2 Command group name**: `devkit adaptive assignment` (recommended) or `devkit adaptive-dev assignment`.
  `CAP-DLV-adaptive-development` rule 18 says commands use `adaptive-dev`; the distribution is `devkit-adaptive`.
  `PADR-adaptive-assignment-commands` is written for the recommended name and supersedes the naming clause of
  `ADR-adaptive-development-and-research` in part. Under the other answer, the next Planning turn renames the group
  in this bundle, removes the PADR's `supersedes` and its naming clause, and drops the ADR file from
  `boundaries.owns`.

Excluded: host lifecycle hooks (`PROP-adaptive-lifecycle-hooks`), a scheduler or process runner, model routing, SDD
Units or envelopes, an MCP service, glob write scopes, ledger pruning, and any change to `devkit-spec`, `devkit-agt`
or the host feature of `devkit-dist`.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr adaptive-assignment-cli "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept adaptive-assignment-cli --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff adaptive-assignment-cli.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->

Development starts only after `PROP-adaptive-package-extraction` has landed, because the feature is added to the
package that proposal creates. Retire through acceptance, handoff and Living Spec reconciliation once the scenarios
of §3.9 pass.
