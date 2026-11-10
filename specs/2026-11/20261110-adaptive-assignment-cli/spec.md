---
id: SPEC-adaptive-assignment-cli
title: Assignment ledger and return verification commands for adaptive delegation
summary: Add commands that record delegated assignments and verify a return against its assignment, and make devkit-adaptive require the document system, so a Host resumes from recorded state and checks scope, source identity, declared checks and governing documents deterministically.
status: planned
created: 2026-11-10
depends_on:
  - SPEC-adaptive-package-extraction
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-adaptive-assignment-cli] Assignment ledger and return verification commands for adaptive delegation

## 1. Problem Statement & Motivation

Handed off from proposal PROP-adaptive-assignment-cli on 2026-11-10.
- **Preserved Materials**: `docs/materials/2026-11/20261110-adaptive-assignment-cli`
- Target Docs Blueprint: `PROP-adaptive-assignment-cli-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

In adaptive development the Host delegates to swarm agents with a goal, source identity, exclusive write scope,
governing documents, checks and return fields (`CAP-DLV-adaptive-development` rules 13, 13a and 26). The assignment
board exists only in the Host's context. `.devkit/adaptive-dev.md` is free Markdown the Host updates "when useful and
before pausing", so an unplanned interruption or context compaction loses outstanding assignments. The Host checks a
returned result by reading its diff; no command compares the result with the assignment.

`MAT-adaptive-runtime-references` records that comparable harnesses write assignment state in code when each event
happens and gate completion on it, and that their evidence checks stop at the shape of a file. Adaptive assignments
already carry a worktree, a base identity and a write scope, so a command can check the repository itself.

Adaptive development is being raised from a content bundle to a package: `SPEC-adaptive-package-extraction` moves
the bundle into the `devkit-adaptive` distribution, and this proposal gives that distribution its first feature and
its requirement on the document system.

Hypothesis: a small command set that records assignments and verifies returns makes resume and completion checks
deterministic for large parallel builds without a scheduler, a process runner or per-change SDD records.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Assignment ledger and return verification commands for adaptive delegation so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

Planning answered each question. §3 holds the settled design; historical Git `f0434e6ed0c981340754256022750527f8887e7a:docs/proposals/PROP-adaptive-assignment-cli/envelopes/answer-01.yaml` holds the user's two
answers, and no question is open.

| Question | Answer | Where |
| --- | --- | --- |
| Q1 Command surface | `devkit adaptive assignment new\|return\|verify\|close\|list\|show`; a failed verification, an out-of-scope write included, exits `1` | §3.2, §3.4, §3.5 |
| Q2 Ledger | Append-only JSON Lines under the shared Git directory; the delegating agent writes | §3.6, `ADR-adaptive-assignment-ledger-storage` |
| Q3 Verification | Ancestry, HEAD, commit grant, changed paths against literal path prefixes, declared checks against recorded outcomes, children; `new` refuses an overlapping scope and an unresolved governing document | §3.2, §3.3, §3.4 |
| Q4 Nesting | `--parent`; one level below the Host's assignment; child authority inside the parent's; the parent fails verification while a child is not closed | §3.3, §3.4 |
| Q5 Reuse | `devkit_core`, `devkit_dist` and the document index of `devkit_docs`; no public harness module fits, so no `devkit_agt` edge; no `devkit_spec` import | §3.8, `docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §10 |
| Q6 Resume | `list` reports repository facts per assignment and no liveness; a new context treats every open assignment as interrupted | §3.2 `list`, §3.7 |
| Q7 Current context | The Markdown names assignment IDs and the next action; the ledger holds scope, base and checks; no command reads or writes the Markdown | §3.7 |
| Q8 Guidance | The delegating agent records and verifies as its standard delegation step; the manual procedure is the fallback when a command cannot record; document steps lose their installation condition | §3.7 |
| Q9 Evidence scorer | Kept unchanged as test support | §3.1 |
| Base dependency (user's answer) | `devkit-adaptive` requires `devkit-docs` | §3.8, §3.9, `ADR-adaptive-requires-document-system` |
| Command group name (user's answer) | `devkit adaptive assignment` | §3.2, `ADR-adaptive-assignment-commands` |

### 3. Proposed Design & Impact

#### 3.1 Planning decisions

Three decisions meet the admission criteria and are PADRs:

- `ADR-adaptive-assignment-commands`: the command group, what it compares and what stays a Host judgment.
- `ADR-adaptive-assignment-ledger-storage`: location and format of the ledger.
- `ADR-adaptive-requires-document-system`: the requirement on `devkit-docs` and what it makes unconditional.

The user's direction for this turn, recorded as decisions:

- **`devkit-adaptive` requires `devkit-docs`** (answer q1). This unit introduces the requirement. The prerequisite
  ships the wheel bundle-only with `dependencies = []` and does not presume it.
- **The command group is `devkit adaptive assignment`** (answer q2).
- **The scope may be generous.** The unit includes what the package-level design needs: the requirement, the
  installation statements that follow from it, and the guidance wording it makes unconditional.
- **Compatibility with existing consumers is not a concern**, because nothing uses the bundle outside this
  repository. No migration path, alias or deprecation period is designed.
- **Hooks stay out** (`PROP-adaptive-lifecycle-hooks`).

The other choices, each with its reason:

- **Requirement form.** `packages/devkit-adaptive/pyproject.toml` declares `devkit-core==<version>`,
  `click>=8.1.7` and `devkit-docs==<version>`, with a workspace source for each sibling. `devkit-spec` and
  `devkit-docs` declare theirs the same way, and the release inventory accepts no other form for an internal
  requirement (`docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §11). No release script changes: the inventory, the pin rewrite and
  the lockstep test read every `packages/*/pyproject.toml`. No release install variant is added.
- **Accepted cost: release coupling.** The wheel takes a new version whenever `devkit-docs`, `devkit-agt`,
  `devkit-dist` or `devkit-core` does.
- **Accepted cost: no snapshot.** `devkit bundle snapshot` refuses a source project that declares a runtime
  requirement or an entry-point group other than `devkit.bundles`
  (`packages/devkit-dist/src/devkit_dist/features/distribution/services/snapshots/source.py:55-65`,
  `BUNDLE_SNAPSHOT_UNSUPPORTED`). After this unit `devkit-adaptive` is not a snapshot source. No guide offers the
  `adaptive-dev` bundle as one, and a test states the refusal.
- **Reuse, re-decided with `devkit_agt` and `devkit_docs` importable.** The feature reuses `devkit_core`,
  `devkit_dist` and the document index. It still writes its own worktree-list parser, status parser and prefix
  functions, because no public module holds them: the harness parser is a private function, the status parser lives
  in a feature without a public module, and the literal containment helper of `devkit-docs` is outside its
  `public_modules`. No source file under `packages/devkit/src/` or `packages/devkit-docs/` changes, and the feature
  declares no `devkit_agt` edge (`docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §10).
- **Governing documents are validated when an assignment is recorded**, in the assignment's worktree, so a document
  the assignee cannot read is refused (`docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §12). `verify` and `list` do not check them
  again.
- **Guidance loses its installation conditions.** The commands ship in the same wheel as the guidance, and the
  document system and the harness are requirements of that wheel. The conditions "where the commands are
  available", "when the docs bundle is selected" and "without assuming a harness is installed" are removed (§3.7).
  The fallback is tied to a command that cannot record, and to a project that opted out of the docs bundle.
- **Worktrees follow the accepted order.** `ADR-worktree-isolated-parallel-workers` decides "Use the existing
  harness lifecycle when available, otherwise the consuming project's documented Git procedure." The harness is
  installed with every adaptive installation after this unit, so the guidance names `uv run devkit worktree` first
  and the project's documented Git procedure for the case where that lifecycle cannot be used. The ADR is not
  superseded and its file does not change.
- **Only a `swarm-worker` lead records children.** `swarm-verifier` keeps "product sources and Git read-only" and
  writes only assigned ignored outputs (`ADR-skill-local-swarm-roles`); a ledger write under the shared Git
  directory does not fit that contract. `swarm-planner` has no shell. The Host records the children of such a lead
  from its return, or leaves them unrecorded.
- **Recording stays a SHOULD.** The Host may leave a bounded experiment unrecorded, and a failed verification never
  blocks `close` (root `AGENTS.md`, Proportionate Guardrails).
- **Documents are still written only where the subject warrants.** With the document system always installed, "a
  project that maintains no document tree gains no document system" becomes "a project that has no document yet
  gets no seeded tree": the first document is written when a retained subject warrants one, in the document
  system's kinds. No per-change record is added.
- **Write scope is literal path prefixes.** An entry names a file or a directory with its subtree; `.` names the
  whole worktree. `*`, `?` and `[` are refused. Containment, overlap and narrowing are then exact
  (`docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §6). Globs can be added later without invalidating an entry.
- **Verification runs no check.** It compares each declared check with the outcome the delegating agent recorded
  from the return. The user excluded a process runner.
- **Closing does not require a passed verification.** `close --outcome integrated` on an assignment that is not
  `verified` needs `--reason` and reports the `ADAPTIVE_CLOSED_UNVERIFIED` warning.
- **No heartbeat, lease or age threshold.** The Host assigns directly, so no claim needs to expire
  (`MAT-adaptive-runtime-references` §6). `list` prints `assigned_at` and repository facts; whether an agent still
  runs is not recorded.
- **Git calls inherit the environment.** `devkit_core.core.run_git` takes no environment argument, and the commands
  are run by an agent from a shell, never from a Git hook. With `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` set,
  the commands read the repository those variables name; the capability states this limit.
- **CLI only.** No MCP service is added; no rule requires one (scout-02).
- **The command contract gets its own capability**, CAP-DLV-adaptive-assignments. `CAP-DLV-adaptive-development`
  holds 39 agent-guidance rules; the commands have a tested, deterministic contract that
  `PROP-adaptive-lifecycle-hooks` will cite. The ID is written without backticks in this bundle because the document
  does not exist yet (`RULE-document-reference`); Development backticks it in the promoted decisions under
  `docs/decisions/` once it does.
- **The evidence scorer stays unchanged.** `adaptive_behavior_scorer.py` scores supplied evidence of agent behavior.
  The commands compare a repository with an assignment. Neither replaces the other.
- **One spec, size `L`.** The requirement exists because the feature imports the document index, the guidance
  names the commands, and one installed-consumer test asserts both. A split into "requirement and guidance" and
  "commands" would land a requirement without importing code and edit the same capability, bundle references and
  consumer test twice (`docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §13). §3.11 gives an order of work that keeps each part
  verifiable.
- **`dev_effort` stays `medium`.** The ledger is local, untracked state with no migration, and no consumer outside
  this repository depends on the installation statements.

#### 3.2 Commands

The group is `devkit adaptive assignment`, mounted by the entry point `adaptive = "devkit_adaptive.cli:cli"` in the
`devkit.commands` group of `devkit-adaptive` (`ARCH-05-3-command-plugins`). Every command:

- takes `--format text|json` and the standard `-q`, `-v`, `--strict` and `--workspace-root` options from
  `devkit_dist.adapters.cli`, and resolves the workspace root with its `resolve_root`;
- resolves the repository as the Git work tree containing that root and works from any worktree of it; a root that
  is in no work tree, the bare directory of a repository included, is `ADAPTIVE_REPOSITORY_UNSUPPORTED`;
- performs no approach check and needs no bundle selection and no `.devkit/` directory.

IDs match `^[a-z0-9][a-z0-9-]{0,39}$`. Revisions are stored as full commit IDs, resolved with
`git rev-parse --verify --quiet <rev>^{commit}`. Timestamps are UTC, ISO 8601 with seconds and a `Z` suffix. Paths
are compared after symlink resolution.

**`new`** records an assignment with status `open`.

```text
devkit adaptive assignment new --owner <text> --goal <text>
    [--id <id>] [--role <text>] [--worktree <path>] [--base <rev>]
    [--write <path>]... [--commit] [--check <name>[=<command>]]...
    [--governing <id-or-path>]... [--depends-on <id>]... [--parent <id>]
    [--evidence <text>] [--handoff <text>] [--stop <text>]
```

- `--id` defaults to `a<N>`, the first unused `N` counting from the number of recorded assignments plus one.
- `--worktree` defaults to the worktree containing the workspace root. It must be a worktree of the same repository
  whose directory exists: a path that `git worktree list --porcelain -z` does not list, lists as `bare` or lists
  with `prunable` is `ADAPTIVE_WORKTREE_UNAVAILABLE`.
- `--base` defaults to the HEAD of that worktree and must resolve to a commit; a repository without a commit gives
  `ADAPTIVE_REVISION_UNRESOLVED`. The base is the commit the assignee starts from, so record an assignment when it
  is dispatched: a dependent assignment after its dependency's result is in its worktree.
- `--write` is repeatable and takes a path relative to the worktree root, or an absolute path under it. No `--write`
  records a read-only assignment.
- `--commit` records that the assignee may commit. Without it the assignee must leave HEAD at the base.
- `--check` declares a check by name; the optional command text is recorded and never run.
- `--governing` is repeatable and names a document the assignee treats as a constraint. Each value is validated in
  the assignment's worktree before anything is appended:
  - The single value `none` records an empty list. `none` beside another value is `ARGUMENT_INVALID`. Omitting the
    option records an empty list as well.
  - A value that matches the document ID grammar (`is_id` of `devkit_docs`) is resolved through the document index
    of the worktree (`DocumentIndex.load(<worktree root>).resolve(<value>)`). The document's own ID is recorded,
    also when the value was an alias.
  - Any other value is a path. A relative path is relative to the worktree root and must exist inside it; an
    absolute path must exist. A path under the worktree root is recorded relative and normalized, any other path
    absolute.
  - Every value that fails is collected into one `ADAPTIVE_GOVERNING_UNRESOLVED` with a `[DETAIL]` per value and its
    reason: `unknown-id`, `duplicate-id` or `missing-path`. Its `[FIX]` names the three routes: correct the value,
    bring the document into the assignment's worktree, or pass the absolute path of a copy the assignee can read.
  - The index is loaded once per command and only when a value is an ID.
- `--evidence`, `--handoff` and `--stop` are recorded text for resume and are not verified.
- `new` also records `dirty_at_assign`: the uncommitted and untracked paths of the worktree at that moment.
- Refusals, each exit `2`: an existing ID, an unknown `--parent` or `--depends-on` ID, a closed parent, a parent that
  itself has a parent, authority not inside the parent's, a write scope that overlaps another assignment (§3.3) and
  an unresolved governing document.

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

- `worktree_state`: `present`, or `missing` when the directory does not exist, the path is no longer a worktree of
  the repository, or its record carries `prunable`;
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

#### 3.3 Records

An `<assignment>` object:

| Field | Type | Meaning |
| --- | --- | --- |
| `id`, `status` | string | `status` is `open`, `returned`, `verified`, `rejected` or `closed` |
| `owner`, `role`, `goal` | string | `role` may be null |
| `worktree`, `base` | string | Absolute worktree path; full commit ID |
| `write` | list of strings | Normalized POSIX paths relative to the worktree root; empty for read-only |
| `commit` | boolean | Whether the assignee may commit |
| `checks` | list of `{"name", "command"}` | `command` may be null |
| `governing` | list of strings | Document IDs, and paths relative to the worktree root or absolute (§3.2); empty for none |
| `depends_on` | list of strings | Assignment IDs |
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

#### 3.4 Verification

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

- committed: `git diff --no-renames --name-only -z <base> <final> --`, so a rename counts under both names;
- uncommitted: `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` in the worktree, minus the
  paths in `dirty_at_assign`. `--no-optional-locks` keeps the command from writing the index of a worktree where an
  assignee is working.

Reading the status output (observed with Git 2.49.0, `docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §9):

- A record is `XY <path>`, terminated by NUL. When `X` or `Y` is `R` or `C`, the next NUL-terminated record is the
  original path without a status prefix. Both names count as changed.
- An untracked nested repository is one record with a trailing `/`. The parser strips the trailing `/`, so a write
  entry covers the nested repository by its directory name.

Stated limits, which the capability and the reference page repeat:

- Ignored files and writes outside the worktree are not observed.
- A path in `dirty_at_assign` is excluded even when the assignee changed it again; `verify` lists such paths under
  `preexisting_dirty` with the `ADAPTIVE_PREEXISTING_DIRTY` notice.
- Paths brought in by merging another branch into the assignment's branch count as changed.
- In a checkout that the Host or another agent edits at the same time, changed paths cannot be attributed; the Host
  judges that result and records its reason at `close`.
- A recorded outcome repeats the assignee's report; no check is run.
- Governing documents are validated when the assignment is recorded and not again.
- The commands read the repository that `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` name when these are set.
- The content of a submodule is not observed; a changed submodule appears as its one path.

In-scope uncommitted paths do not fail `scope`. When the assignment grants commits, `verify` reports them with the
`ADAPTIVE_UNCOMMITTED_CHANGES` warning, because the final commit does not contain them. Without the grant they are
the expected result and no warning is raised.

#### 3.5 Codes and exit codes

Exit `0`: success, warnings and notices included. Exit `1`: `verify` with a failed check, or a warning under
`--strict`. Exit `2`: the command could not run or refused. `CAP-HARN-command-mount` §4.7 describes `devkit spec` and
`devkit docs` only and does not change.

Every code is one `AdvisoryError` subclass of a package base error, prefixed `ADAPTIVE_`
(`RULE-advisory-unique-code`). The mode is the derived `[ACTION]` mode of `CAP-ADV-agent-advisory-protocol` §5; each
class sets the fields that derive it (`input_error = True` for `INPUT_ERROR`, `actor = Actor.USER` for
`INTERACTION`) and a `fix`. `packages/devkit-spec/src/devkit_spec/base/errors.py` is the model for the module.

| Code | Level, exit, mode | Raised when |
| --- | --- | --- |
| `ADAPTIVE_REPOSITORY_UNSUPPORTED` | error, `2`, `INPUT_ERROR` | The workspace root is not inside a Git work tree |
| `ADAPTIVE_LEDGER_UNREADABLE` | error, `2`, `INTERACTION` | A newline-terminated line cannot be parsed, or an event has an unknown schema number; the report asks whether to move the damaged ledger aside |
| `ADAPTIVE_LEDGER_UNWRITABLE` | error, `2`, `INTERACTION` | The ledger directory, lock or file cannot be created or written; the report says the assignments stay unrecorded |
| `ADAPTIVE_ASSIGNMENT_UNKNOWN` | error, `2`, `INPUT_ERROR` | An ID, `--parent` or `--depends-on` names no assignment |
| `ADAPTIVE_ASSIGNMENT_EXISTS` | error, `2`, `INPUT_ERROR` | `new --id` names a recorded assignment |
| `ADAPTIVE_ASSIGNMENT_CLOSED` | error, `2`, `INPUT_ERROR` | `return`, `verify` or `close` on a closed assignment, or `new --parent` naming one |
| `ADAPTIVE_ASSIGNMENT_NOT_RETURNED` | error, `2`, `INPUT_ERROR` | `verify` on an assignment without a return |
| `ADAPTIVE_WORKTREE_UNAVAILABLE` | error, `2`, `INPUT_ERROR` | `new`, a `return` without `--final`, or `verify` cannot read the assignment's worktree, or `--worktree` is not a present worktree of this repository |
| `ADAPTIVE_REVISION_UNRESOLVED` | error, `2`, `INPUT_ERROR` | `--base` or `--final`, given or defaulted, does not resolve to a commit |
| `ADAPTIVE_GOVERNING_UNRESOLVED` | error, `2`, `INPUT_ERROR` | `new`: a `--governing` ID resolves to no document or to several, or a path does not exist (§3.2) |
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

Codes of other packages pass through unchanged: `ARGUMENT_INVALID` (a malformed ID, a write entry with `*`, `?` or
`[` or outside the worktree, a malformed `--check`, an unknown outcome, a missing required `--reason`, `none` beside
another `--governing` value, a `--workspace-root` that is a subdirectory of a work tree), `LOCK_HELD`, `GIT_FAILED`,
`DEVKIT_ROOT_NESTED` and `YAML_BINDING_UNAVAILABLE` (the document index without LibYAML). The document index's
`DOCS_ID_UNRESOLVED` and `DOCS_ID_DUPLICATE` are caught and reported as `ADAPTIVE_GOVERNING_UNRESOLVED`. With the
distribution absent, `devkit adaptive` is click's usage error, exit `2`, without a code.

#### 3.6 Ledger

`ADR-adaptive-assignment-ledger-storage` decides location and format. The details Development implements:

- Directory `<git common dir>/devkit/adaptive/`, created on the first write; files `ledger.jsonl` and `lock`. The
  common directory is the output of `git rev-parse --path-format=absolute --git-common-dir`. For a linked worktree
  of a bare repository it is the bare directory.
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

#### 3.7 Guidance

The delegating agent runs the commands: the Host for its assignments and a `swarm-worker` lead for its children. An
assignee never runs them. The bundle text states each step without an installation condition. Before editing the bundle,
Development runs `uv run devkit get-context authoring` and applies its `agent-asset-writing` instruction; the rows
below give the content each asset must carry, not its final wording.

| Asset | Change |
| --- | --- |
| `skills/adaptive-dev/references/delegation.md` | Before dispatching a deliverable, record it with `new`, passing its governing documents as `--governing`, and put the ID in the payload. After the return, record it with `return`, then run `verify`; treat `result=fail` (status `rejected`) as a rejected return (existing step 15) and route its codes to repair, and do not read exit `1` alone as a failure, because `--strict` also gives it. On `ADAPTIVE_SCOPE_OVERLAP`, narrow the scope, close the finished assignment, sequence with `--depends-on`, or leave a bounded experiment unrecorded; never name a dependency that does not exist. On `ADAPTIVE_GOVERNING_UNRESOLVED`, correct the value, bring the document into the assignee's worktree, or pass the absolute path of a copy the assignee can read. Close with `close` after integrating or abandoning. The fallback paragraph below. |
| `skills/adaptive-dev/references/orchestration.md` | Step 5 drops "without assuming a harness is installed" and states the order of `ADR-worktree-isolated-parallel-workers`: create each writer's worktree with the installed harness lifecycle (`uv run devkit worktree start\|status\|finish` on a `dev-<slug>` branch); where that lifecycle cannot be used (it refuses the layout, or permission is missing), use the project's documented Git procedure; without either, serialize writers. The assignment commands accept any worktree of the repository, however it was created. A `swarm-worker` lead records each child with `--parent <its ID>` when the payload supplies that ID and permits it, and closes its children before it returns. A `swarm-verifier` or `swarm-planner` lead records nothing: the Host records its children from the returned partition or leaves them unrecorded. On interruption and before a pause, run `list`. |
| `skills/adaptive-dev/references/current-context.md` | On resume run `list` beside reading `.devkit/adaptive-dev.md`. In a new context treat every `open` assignment as interrupted: no agent from an earlier context is assumed to run. For each one, read `worktree_state`, `commits`, `dirty` and `attention` from `list` and the goal, stop condition, commit grant, governing documents and checks from `show <id>`, then record a return from the retained state, dispatch it again, or close it as abandoned. Before pausing, name the outstanding assignment IDs and the next recovery action in the Markdown; the ledger holds their scope, base and checks. An ID the ledger lacks is stale context. |
| `skills/adaptive-dev/references/documents.md` | Step 1 becomes unconditional: read `uv run devkit get-context docs` and the relevant writing instruction before authoring, and locate documents with `uv run devkit docs search\|list\|resolve\|refs`; keep the project's existing document destinations and formats where it has its own. One exception stays: in a project that opted out of the docs bundle, follow the project's own conventions. Step 2 becomes: if the project has no document yet, record that in current context, seed no document tree, and write the first document only when a retained subject warrants one (step 8), in the document system's kind and destination. Step 4 adds that the same documents are passed as `--governing` when the assignment is recorded. Step 12 becomes: include `uv run devkit rules check` on the changed documents in combined checks, with any further document check the project defines; report a check that could not run as unverified. Steps 3, 5 to 11 and 13 to 15 keep their content, the rule that documents are written only where the subject warrants and the rule that no per-change record is added included. |
| `templates/current-context.md` | Under "Documents": "When the project has no document yet, say so here." Under "Next useful action": name outstanding assignments by ledger ID. |
| `subagents/swarm-planner.md`, `swarm-worker.md`, `swarm-verifier.md` | One procedure sentence in each: when the payload supplies an assignment ID, return it with the result. `swarm-worker` alone adds, self-contained: as a lead, when the payload permits it, record each child with `uv run devkit adaptive assignment new --parent <ID>` and close it before returning; if the command cannot record, report the children as unrecorded. `swarm-verifier` and `swarm-planner` gain no command and keep their read-only Git contract. No prerequisite is added (`CAP-DLV-adaptive-development` rule 19). |
| `AGENTS.md` (bundle constitution) | One line: record and verify delegated deliverables with `uv run devkit adaptive assignment`; a command that cannot record leaves the manual board in force. The existing line on `get-context docs` stays as it is. |

Fallback, stated once in `delegation.md` and cited by the other files: when a recording command exits `2` with
`ADAPTIVE_REPOSITORY_UNSUPPORTED`, `ADAPTIVE_LEDGER_UNWRITABLE` or `ADAPTIVE_LEDGER_UNREADABLE`, the host denies the
write, or the command is missing (click's usage error, an installed wheel older than the deployed bundle), the Host
keeps the board in its context and `.devkit/adaptive-dev.md`, checks returns by reading the diff, reports the
assignments as unrecorded, and does not reroute a denied write.

Callers and roles:

- **SDD callers that select only `adaptive-dev:agents`** have the commands, because the archetypes ship in the same
  wheel. The archetypes work without them. Such a caller may use them; they write no SDD record and replace none,
  and `devkit spec worker inspect` stays the SDD check.
- **The three product-support roles** (`product-clarifier`, `product-researcher`, `usage-reviewer`) keep their
  contracts and run no command. The Host may record such an assignment without `--commit`, with the researcher's
  scratch or prototype paths as `--write`. `verify` then checks that HEAD stayed at the base and that no path
  outside the scope changed. When the role shares the Host's checkout, the attribution limit of §3.4 applies.

The `adaptive-import` skill and the conversion playbook do not name the commands.

#### 3.8 Package, requirement and reuse

Paths below use the names this proposal expects from the prerequisite (§3.11): the distribution `devkit-adaptive`
in `packages/devkit-adaptive/`, the import package `devkit_adaptive`.

**Requirement.** `packages/devkit-adaptive/pyproject.toml`:

```toml
dependencies = [
    "devkit-core==<version of devkit-core>",
    "click>=8.1.7",
    "devkit-docs==<version of devkit-docs>",
]

[project.entry-points."devkit.commands"]
adaptive = "devkit_adaptive.cli:cli"

[tool.uv.sources]
devkit-core = { workspace = true }
devkit-docs = { workspace = true }
```

- The versions are the literal `version` values of the two sibling `pyproject.toml` files at implementation time.
- `devkit-agt` and `devkit-dist` arrive through `devkit-docs` and are not declared, as `devkit-docs` and
  `devkit-spec` do not declare `devkit-dist`.
- `devkit-spec` is never a requirement, in any group or extra.
- `uv.lock` is regenerated with `uv lock`.
- The `devkit.bundles` entry point and the build configuration stay as the prerequisite left them.

**Architecture declaration.** The `devkit_adaptive` entry of `.devkit/architecture.toml` becomes:

```toml
[[packages]]
namespace = "devkit_adaptive"
root = "packages/devkit-adaptive/src/devkit_adaptive"
kind = "features"
features = ["assignment"]
feature_dependencies.assignment = ["devkit_dist.features.project", "devkit_docs.features.documents"]
root_modules = ["cli"]
data_roots = ["bundles"]
dependencies = ["devkit_docs", "devkit_dist", "devkit_core", "devkit.advisory"]
public_modules = ["devkit_adaptive.features.assignment.usecases.listing"]
```

`root_modules` and `data_roots` keep whatever further entries the prerequisite declared. `devkit_agt` and
`devkit_spec` are not dependencies: the feature imports neither.

**Feature.** `features/assignment/` with `cli`, `usecases`, `services`, `repositories` and `models`; one
`BaseUseCase` per verb; errors in `devkit_adaptive/base/errors.py`. `devkit_adaptive/cli.py` assembles the
`adaptive` group and its `assignment` subgroup.

| Layer | Holds | Imports from other packages |
| --- | --- | --- |
| `cli` | The six commands, option parsing, sentinels and JSON | `devkit_dist.adapters.cli` (`BOUNDARY`, `workspace_option`, `resolve_root`, `field_value`, the format and output helpers) |
| `usecases` | One class per verb; `listing` is the public read | `devkit_dist.features.project.repositories.project.git_toplevel` |
| `services` | The event fold, the verification checks, scope and authority validation | none |
| `repositories` | Git reads, the ledger file and lock, governing document resolution | `devkit_core.core` (`run_git`, `run_git_text`, `is_ancestor`, `file_lock`, `normalize_relpath`, `resolve_within`), `devkit_docs.features.documents.repositories.index.DocumentIndex`, `devkit_docs.features.documents.models.ids.is_id` |
| `models` | The assignment, return, verification and event values; `covers(entry, path)` and `overlaps(a, b)` | none |

- A CLI module calls a use case's `execute` and no repository, service or use-case function
  (`RULE-usecase-boundaries`); `resolve_root` is the one bootstrap call, as in `devkit-spec` and `devkit-docs`.
- Written in the feature, because no public module holds them (`docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §10): the
  worktree-list parser (records `worktree`, `HEAD`, `branch`, `bare`, `prunable`; model:
  `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py:179-198`), the status parser (§3.4), the
  revision resolver, the common-directory lookup, the prefix functions and the JSON Lines append.
- No import of `devkit_spec` or `devkit_agt`. No use of `devkit worktree` or `devkit exec` by the commands: they
  create no worktree and run no process.
- No source file under `packages/devkit/src/`, and no file under `packages/devkit-docs/`,
  `packages/devkit-core/`, `packages/devkit-dist/` or `packages/devkit-spec/`, changes. The one edit under
  `packages/devkit/` is the affected-test assertion named below.

**Tests.**

- Unit tests for the fold, the prefix rules, the two parsers and each check.
- Integration tests on temporary repositories with a linked worktree through the CLI, one per scenario of §3.10.
- A documented-codes test like `packages/devkit-spec/tests/integration/package/test_documented_codes.py`,
  registered under `docs/` in the `DATA` list of `scripts/affected_tests.py` so that a docs-only change selects it;
  `packages/devkit/tests/e2e/package/test_affected_tests.py` asserts that list and gains the same path.
- An import test over every module of the package, run in a fresh interpreter (a `python -c` subprocess, as
  `packages/devkit-dist/tests/integration/cli/test_cli_imports.py` does), because a shared pytest process may
  already hold `devkit_spec`.
- A package metadata test: the `dependencies` of `pyproject.toml` name `devkit-docs` at the version of
  `packages/devkit-docs/pyproject.toml` and no `devkit-spec`.
- A snapshot refusal test: `devkit bundle snapshot` on the package source exits `2` with
  `BUNDLE_SNAPSHOT_UNSUPPORTED`.
- The installed-consumer test of the bundle (today
  `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`; the prerequisite moves it),
  extended as AC-18 states.
- Bundle content tests for the guidance sentences of §3.7; the assertion of
  `test_adaptive_dev_documents.py` on "no document tree" and "no document system" is replaced by one on the new
  step 2.
- `tests/e2e/smoke.sh`: where the script adds the adaptive wheel to a consumer, it names the sibling wheels by file
  beside it, as it does for the spec wheel, because no index serves them; it then runs
  `uv run devkit adaptive assignment list`.

#### 3.9 Installation statements

After this unit a consumer installs adaptive development with the one requirement `devkit-adaptive`. That
requirement brings the document system and the harness; the `docs` and `harness` bundles are selected by their own
`auto_select`, and `adaptive-dev` still deploys only after `uv run devkit add adaptive-dev`. `devkit-spec` is not
installed. `target-docs.md` lists, per document, the statement that must hold. The prerequisite rewrites the same
passages for the move out of the catalog; where its wording names `devkit-docs` beside the adaptive wheel as a second
requirement the consumer declares, this unit replaces it.

Statements that stay true and are not edited:

- `devkit-docs` remains a valid installation of its own for document formats without adaptive development.
- The `deep-research` bundle stays in `devkit-catalog`; its installation statements ("devkit-docs plus
  devkit-catalog" in `CAP-DLV-deep-research` and the deep-research row of
  `guides/install/bundle-recommendations.md`) do not change.
- The catalog's content-only rule.

#### 3.10 Acceptance scenarios

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
  offending path with `change=committed` or `change=uncommitted`, and the status is `rejected`. Given an uncommitted
  rename from inside the scope to outside it, then the new name is listed. Given an untracked nested repository
  `vendor/x` and the write entry `vendor`, then `scope` passes.
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
- **AC-12**: Given three open assignments, one whose worktree directory was moved away without `git worktree
  prune`, one with a commit and one untouched, when `list` runs in a fresh process, then it reports
  `attention=worktree-missing`, `commits=1` and `attention=no-changes` respectively and exits `0`; closed
  assignments appear only with `--all`. In the same process `show <id>` prints the goal, the stop condition, the
  commit grant, the write scope, the governing documents and the declared checks that `new` recorded, in text and
  in JSON.
- **AC-13**: Given two processes that run `new` at the same time, then both assignments are recorded with distinct
  IDs and every ledger line parses. Given a ledger that ends with an unterminated fragment, then `list` succeeds with
  `ADAPTIVE_LEDGER_FRAGMENT_IGNORED`; after a following `new`, `list` exits `0` without the warning and every line
  of the file parses. A newline-terminated line that does not parse gives `ADAPTIVE_LEDGER_UNREADABLE`, exit `2`.
- **AC-14**: Given a directory outside a Git work tree, then every command exits `2` with
  `ADAPTIVE_REPOSITORY_UNSUPPORTED`. Given a repository without a commit, then `list` exits `0` with an empty list
  and `new` exits `2` with `ADAPTIVE_REVISION_UNRESOLVED`. Given a ledger directory that cannot be written, then
  `new` exits `2` with `ADAPTIVE_LEDGER_UNWRITABLE`. Given a linked worktree of a bare repository, then `new` and
  `list` succeed there and the ledger lies under the bare directory.
- **AC-15**: For every command, `--format json` prints exactly one compact object with the keys of §3.2, a failure
  prints `{"error": ..., "notices": ...}`, and text mode prints only the sentinels of §3.2 on stdout.
- **AC-16**: Every `ADAPTIVE_` code declared in the package appears in a document under `docs/` (documented-codes
  test), and `devkit rules check` reports no `RULE-architecture`, `RULE-usecase-boundaries` or
  `RULE-advisory-unique-code` finding for the package.
- **AC-17**: The bundle content tests find, without an installation condition: the recording, verification and
  closing steps and the fallback in `delegation.md`; the resume rule in `current-context.md`; the unconditional
  step 1, the new step 2 and the `devkit rules check` step in `documents.md`; and no "without assuming a harness is
  installed" in `orchestration.md`. They find no command name in the product-support role contracts, the
  `adaptive-import` skill or the conversion playbook. The three archetypes state no prerequisite.
- **AC-18**: The installed-consumer test builds the `devkit-adaptive` wheel and its sibling wheels, installs them
  into a fresh environment and shows:
  - the installed metadata of `devkit-adaptive` requires `devkit-docs` at exactly the built version and names no
    `devkit-spec`;
  - `devkit-spec` is not an installed distribution (the sibling wheels are named by file, so their presence shows
    nothing; the metadata check above carries the requirement);
  - after `devkit sync` in a consumer repository with one commit, the receipt's `selection.presets` holds
    `docs == ["core"]` and `harness == ["core"]`, and `.devkit/managed/adaptive-dev` does not exist until
    `devkit add adaptive-dev`;
  - `devkit adaptive assignment list --format json` exits `0` with an empty `assignments` list;
  - `devkit adaptive assignment new --owner o --goal g --governing CAP-NOPE-missing` exits `2` with
    `ADAPTIVE_GOVERNING_UNRESOLVED`, which shows the document index imports in the installed environment.
- **AC-19**: A test starts a fresh interpreter that imports every module of the package
  (`pkgutil.walk_packages`), the CLI module included, and prints the loaded module names; the test finds no
  `devkit_spec` module among them.
- **AC-20**: Given a worktree that holds a document with a valid ID (written `<ID>` here) and the file
  `docs/notes.md`, when `new` records `--governing <ID> --governing docs/notes.md`, then `show` lists both and the
  JSON `governing` is `["<ID>", "docs/notes.md"]`. An alias of the document records `<ID>`. `--governing none` and
  no `--governing` both record `[]`. `--governing none --governing <ID>` exits `2` with `ARGUMENT_INVALID`.
- **AC-21**: Given `--governing <an ID no document declares> --governing docs/absent.md`, then `new` exits `2` with one
  `ADAPTIVE_GOVERNING_UNRESOLVED` that names both values and appends nothing. Given a document that exists
  uncommitted in the main worktree and not in the linked worktree of the assignment, then `--governing <its ID>`
  exits `2` with `ADAPTIVE_GOVERNING_UNRESOLVED`, and `--governing <absolute path of the main worktree's copy>`
  succeeds and records the absolute path. Given two documents that declare the same ID, then that ID is refused with
  the reason `duplicate-id`.
- **AC-22**: The package metadata test passes (§3.8), `packages/devkit/tests/integration/package/test_lockstep.py`
  passes, `uv lock --check` passes, and the snapshot refusal test shows `BUNDLE_SNAPSHOT_UNSUPPORTED`.
- **AC-23**: Each statement of `target-docs.md` §1 to §4 is present in its document (checked in the reconcile
  review, one document at a time). As a search aid, `rg -nU "devkit-docs\s+(plus|and)\s+devkit-(catalog|adaptive)"
  docs/capabilities docs/architecture guides README.md` then prints only statements about installing
  `deep-research`, and `rg -n "docs/catalog" docs/capabilities docs/architecture guides` prints no statement about
  adaptive development.

#### 3.11 Prerequisite and order of work

Development starts only after `SPEC-adaptive-package-extraction` has landed. This design assumes of it:

- the distribution `devkit-adaptive` in `packages/devkit-adaptive/` with the import package `devkit_adaptive`, the
  `adaptive-dev` bundle and its tests inside that package, `dependencies = []` and a `devkit.bundles` entry point;
- a `devkit_adaptive` entry in `.devkit/architecture.toml`, the package's test paths in the root `pyproject.toml`,
  and the package installed in the repository environment;
- the catalog no longer shipping `adaptive-dev`.

If a landed name or path differs, Development substitutes it; nothing else in this design depends on the names. If
the package is not importable in the repository environment or its tests are not collected, Development adds the
missing entry to the root `pyproject.toml`, which this proposal owns for that purpose.

An order that keeps each part verifiable:

1. The requirement: the `dependencies` and `[tool.uv.sources]` lines of `pyproject.toml`, `uv.lock`, the
   `dependencies` line of the architecture declaration, the package metadata test and the snapshot refusal test.
2. Models, the event fold, the ledger repository and `new`, `list`, `show`, with governing validation; in the same
   commit as the modules they name, the `devkit.commands` entry point and the `kind`, `features`,
   `feature_dependencies` and `public_modules` lines of the architecture declaration (`RULE-architecture` reports
   a declared module that does not exist).
3. `return`, `verify`, `close` and nesting.
4. The installed-consumer test and the smoke script.
5. The bundle guidance and its content tests.
6. The Living Spec of `target-docs.md`, the reference page and the READMEs.

#### 3.12 Exclusions and assumptions

Excluded: host lifecycle hooks (`PROP-adaptive-lifecycle-hooks`), a scheduler or process runner, model routing, SDD
Units or envelopes, an MCP service, glob write scopes, ledger pruning, a release install variant, a migration path
for an existing consumer, a shared public Git-observation helper in `devkit-core`, and any change to `devkit-spec`,
`devkit-agt`, `devkit-docs`, `devkit-core` or `devkit-dist`.

Assumptions the user confirms at `plan-accept`:

- Recording an assignment is a SHOULD for the Host, not a MUST, and a failed verification never blocks `close`.
- Governing documents are resolved in the assignment's worktree, so a document that exists only in the Host's
  checkout is refused unless its absolute path is passed.
- With the document system always installed, the first document of a project that has none is written in the
  document system's kinds when a subject warrants one; no tree is seeded.
- The guidance names the harness worktree lifecycle first and the project's documented Git procedure second, as
  `ADR-worktree-isolated-parallel-workers` decides for an installed harness. Adaptive guidance did not name
  `uv run devkit worktree` before this unit.
- Only a `swarm-worker` lead records its children; children of a verifier or planner lead are recorded by the Host
  or not at all.
- One spec at size `L`.

### 4. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr adaptive-assignment-cli "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept adaptive-assignment-cli --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff adaptive-assignment-cli.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->

Development starts only after `SPEC-adaptive-package-extraction` has landed, because the feature and the
requirement are added to the package that proposal creates. Retire through acceptance, handoff and Living Spec
reconciliation once the scenarios of §3.10 pass.

