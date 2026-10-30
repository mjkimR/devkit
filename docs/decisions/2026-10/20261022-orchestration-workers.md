---
id: ADR-orchestration-workers
title: Orchestration workers deliver committed, recorded and inspectable runs
summary: "For delegated Planning and Development runs, we have workers commit self-contained results on activity branches with one worker envelope per run, the Host inspect the cumulative range, and Codex run them natively, to keep one contract, accepting Git writes and caller-checked bounds."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-worker-delivers-committed-result
  - ADR-run-records-and-activity-branches
  - ADR-codex-native-worker-execution
  - ADR-executor-neutral-planning-steps-in-a-spec-reference
  - ADR-planning-reference-fits-the-existing-byte-budgets
  - ADR-role-effort-presets
  - ADR-answer-envelopes-settle-worker-assumptions
  - ADR-informational-range-inspection-reuses-existing-checks
---

# [ADR-orchestration-workers] Orchestration workers deliver committed, recorded and inspectable runs

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @mjkimR
- **Involved Components/Capabilities**: `CAP-DLV-delivery-workflows`, `CAP-DLV-proposal-planning`,
  `CAP-DLV-project-policy`, `CAP-HARN-agent-guidance`, the `worker` role contract, `spec-delegate`,
  `spec-orchestrate`, `spec-tasks`

---

## 1. Context & Problem Statement

`SPEC-orchestration-mode` introduced the `worker` role with every role's Git rule: read only. The worker left its
build unstaged; the host compared the working-tree diff with the write scope, then staged and committed, and also had
to finish what the worker could not touch (the spec status `RULE-spec-progress` asks for once tasks are checked, and a
code-table row under `docs/` a test requires for a new advisory code). That hand-off only works when host and worker
share a working tree; when workers deliver through their own branch or pull request, their checks and the commit gate
run before any host can repair the result.

`ADR-delivery-classification` left Planning's question rounds, the problem and resolution records and the blocked
state to devkit envelope contracts adopted separately. Until they existed, the Host recorded its check of a worker's
committed range as a `validation` envelope and treated the latest failed one as the block, so two rules decided
whether a unit was blocked. Worktrees were named after the bare slug, so the Planning and the Development activity of
one slug could not each have a branch, and nothing verified that a resumed branch carried the unit it was resumed for.
devkit now ships the contracts (`question` fields in a `worker` envelope, `answer`, `resolution`, the hold on gates and
`worktree finish --merge`, activity branch names, `--no-worktree`, `--existing-branch` with the `devkit.attach_check`
extension point, stale-branch hygiene); the strategy layer's master flow (workbench
`docs/strategy-layer/01-master-flow.md` §4.7, §7.2 and §8) settles how spec-driven delivery uses them.

Further gaps followed on the same runs:

- The contracts marked Codex workers unsupported because default project writes do not include sibling worktrees or
  shared Git administration; `MAT-codex-native-worker-evidence` demonstrates native invocation with individual
  approved commands, while native spawning does not enforce a worker-specific path boundary.
- The ordered Planning steps existed only in the `planning-worker` contract's `## Procedure` (steps 2 to 6), so a Host
  running Planning in `direct` mode had to read a subagent prompt written for another actor
  (`FB-direct-planning-procedure-location`). `CAP-DLV-delivery-workflows` puts a procedure in the contract only "for a
  role whose procedure no main session runs" (`SPEC-subagent-procedure-in-contract`), and a `direct` Host does run
  Planning. Moving the steps had to fit the bundle's byte budgets:
  `packages/devkit-spec/tests/integration/bundles/spec/test_bundle_budgets.py` caps every skill and playbook document at 12288 bytes, holds
  `spec/SKILL.md` to 11776 bytes and requires every file under a skill's `references/` to be linked from that skill.
- Every spec role contract carried an abstract `x-model-profile` that nothing reads, so each projected subagent ran at
  the host's default reasoning effort (`medium` on the Claude 5.5 family). Naming models would need an update on every
  model release. Claude Code (`effort`) and Codex (`model_reasoning_effort`) both accept a per-agent effort in the
  host blocks devkit already projects; Antigravity has no such key (`materials/host-effort-semantics.md`).
- When the user's answers also settle assumptions a worker recorded (its `worker` envelope's `assumptions`), the
  `answer` envelope had no place for them: its items are `{question, choice, decision, constraints}`, each tied to a
  question, and a run recorded them as `constraints` prefixed "Settled by the user in the same round:"
  (`FB-answer-envelope-no-slot-for-settled-assumptions`), stretching `constraints` ("only for what the answer adds",
  `references/worker-records.md` section 2). Evidence:
  `docs/materials/2026-10/20261020-envelope-record-gaps/spike-evidence.md`.
- The Host validated every returned worker range by hand (`spec-delegate` `references/worker.md`): ancestry from the
  last accepted head, changed paths against the write scope, a clean worktree, envelope validity, the cumulative rules
  check and `devkit workflow next`. Each check already existed; what was missing is one invocation that runs them over
  the unit's range and returns one result, including the compared heads and changed paths a read-only reviewer needs
  (`FB-reconcile-reviewer-no-diff-list`). The inputs the Host supplied by hand are already determined by the worktree
  and the unit's committed records.

---

## 2. Decision Drivers

- One contract for local worktrees and pull-request-based (cloud) workers, so orchestration scales out.
- A clear cut between delegated and host work: the host validates and integrates; it does not finish builds.
- The commit gate and the unit's checks judge the worker's own output.
- Delegated work is never silently lost: a rejected result stays inspectable and fixable.
- One rule for blocked: a problem without a resolution that names it, whoever found it.
- A run's record is one file in every mode, so `cloud-pr`, where the run's container disappears, keeps the same trail.
- What another actor does later (answering, fixing) is its own record, written by that actor.
- devkit stays free of spec-driven knowledge; which unit belongs to which activity is checked in devkit-spec.
- Support the demonstrated native Codex mechanism, preserve host trust and approval controls, retain normal devkit
  worktrees and report partial failures truthfully; keep the change sized to existing contracts and instruction tests.
- One place to change the Planning steps; no copy that can drift. A `direct` Host reaches the steps from the `spec`
  skill's routing table; the worker contract keeps everything only a nested, one-shot worker needs.
- Byte budgets as measured at base `97cdcd8`: `spec/SKILL.md` 6531 bytes; the largest `spec` reference 6833 bytes
  (`completion.md`); the `planning-worker` contract 7953 bytes, of which steps 2 to 6 are 4277 bytes. No test or rule
  caps a role contract's size.
- No maintenance when models change: name no model, use only `low`, `medium` and `high`, which both hosts accept on
  current models.
- A worker takes over the Host's own work, so it should run at the effort the user chose for the session.
- `activity-effort` decides how thorough a review is; the reasoning effort stays independent of it, because Codex
  lets the agent file override a spawn value and an `emulated` role has no separate call at all.
- The plan-intent fixed a slot in the answer envelope for settled assumptions; a pure convention is out. Worker
  envelopes are never overwritten, so a position in their `assumptions` list is stable; consistency with
  `reverify --resolve N` / `--waive N=REASON`, which address findings by 1-based position. Settling an assumption
  holds nothing and releases nothing.
- Agent-first output (`ARCH-08-1-agent-output`): one JSON object or sentinel lines, stable codes, `0`/`1`/`2` exits.
- No new gate, approval, registration or override for range inspection: findings are evidence for the main agent.
- Reuse, not reimplementation: existing codes and actions of the wrapped checks are preserved.
- Derive, never guess: an input the records do not determine is a could-not-run with a stable code, and an explicit
  flag only overrides a derived value (user decision at the `plan-accept` review).

---

## 3. Considered Options

### Committed worker results (`ADR-worker-delivers-committed-result`)

- **The worker commits a complete result; failures are blocked** (selected): the worker stages only its write scope,
  commits on the unit branch through the commit gate and returns the head; the host validates the cumulative range
  from the last accepted head. Pros: the same result shape locally and in a pull request; the commit gate runs on the
  worker's work. Cons: the worker gains a Git write action; a rejected range stays in the branch history.
- **Unstaged result, the host repairs and commits** (status quo, rejected): impossible where the worker's branch is
  checked before the host sees it; the host keeps finishing delegated work.
- **The worker commits; failures are reset or the pull request is closed** (rejected): discards delegated work and its
  evidence; differs between local and pull-request delivery.

### Run records (`ADR-run-records-and-activity-branches`)

- **One worker envelope per run, references for answers and resolutions** (selected): one record per run, one blocked
  rule, answers and fixes traceable to the run that needed them. Cons: a Host that blocks a range writes a `worker`
  envelope although it is not a worker role.
- **Separate question and problem kinds** (rejected): the same questions in two files, and two places that can
  disagree about why a run stopped.

### Codex worker execution (`ADR-codex-native-worker-execution`)

- **Native subagent with emulated boundaries** (selected): named projection or generic effective-contract loading,
  individual command approvals; the caller verifies boundaries and unavailable approvals can stop work.
- **Keep Codex unsupported** (retained as runtime fallback only): the Host performs all work in direct mode, which
  discards demonstrated native execution with approved commands.
- **Separate process worker** (excluded): process launcher, permission configuration and output capture; new
  lifecycle and settings work without a demonstrated need.

### Where the Planning steps live (`ADR-executor-neutral-planning-steps-in-a-spec-reference`)

- **Move the neutral steps to `spec/references/planning.md`; the contract cites it** (selected).
- **Copy the steps into a reference and keep them in the contract** (rejected): two texts to keep in step.
- **Point the routing table at the contract for `direct` Hosts** (rejected): the FB's workaround, still a prompt for
  another actor.

### Byte budget for the Planning reference (`ADR-planning-reference-fits-the-existing-byte-budgets`)

- **New `references/planning.md`, linked once from the routing table's proposal row** (selected).
- **Append the steps to `worker-records.md`** (6791 bytes, rejected): about 11 KB, near the budget edge, and mixes
  record mechanics with the activity's order.

### Role reasoning effort (`ADR-role-effort-presets`)

- **Reviewers only** (selected): `scout` and `reconcile-reviewer` (`light-medium`) `medium`; `code-reviewer`
  (`general-high`) and `challenger` (`high-reasoning`) `high`; `planning-worker` and `development-worker` unset.
- **By profile** (rejected): as above, plus both workers `high` after their `general-high` profile; it overrides the
  session effort the user picked for the work the worker takes over.
- **Per call, tied to `activity-effort`** (rejected in Backlog): it works only on Claude Code.

### Settled worker assumptions (`ADR-answer-envelopes-settle-worker-assumptions`)

- **A. `settles` items by position** (selected): `settles: [{assumption: 2, decision: "..."}]`, the 1-based position
  in the `answers_to` worker's `assumptions`.
- **B. `settles` items by text** (not chosen): the assumption string copied exactly.
- **C. Assumption ids** (rejected): give worker assumptions ids (`{id, text}`), referenced by `settles`; it would
  change every worker envelope's schema.

### Range inspection (`ADR-informational-range-inspection-reuses-existing-checks`)

- **A thin `devkit-spec` command that derives its inputs, calls the existing checks and aggregates their results**
  (selected; the explicit-input variant was superseded at the `plan-accept` review), named
  `devkit spec worker inspect`; `devkit spec range inspect` and `devkit spec scope inspect` (mixing it with the scope
  registry) were the alternatives.
- **A new check class in the workflow engine evaluated at a stage's exit** (rejected): it would become a gate.
- **Documentation-only (a shell recipe in `spec-delegate`)** (rejected): the hand-written scope pattern stays per run
  and the reviewer payload still lacks a generated path list.

---

## 4. Decision Outcome

### Committed results and their validation

`ADR-drop-the-base-checkout-equality-from-worker-validation` supersedes the base-checkout clauses below and in the Decision Outcome's Range inspection; the rest stays in force.

- The `worker` role's Git actions are `[read, commit]`: stage write-scope paths, commit on its unit branch through the
  commit gate, leave the worktree clean. It never pushes, merges, rebases, resets, amends, stashes or checks out;
  publishing a branch or pull request belongs to the execution environment. Every other role stays `[read]`.
  (ADR-worker-delivers-committed-result)
- The result is self-contained: tasks checked, the spec's `status` set only through `devkit rules fix <unit>/spec.md`,
  `docs/` written only where a task's `_Boundary:` names it, every given check passing.
  (ADR-worker-delivers-committed-result)
- The host validates the cumulative range from the last accepted head (initially the head recorded before spawning)
  to the returned head: it descends from that head, every changed path is in the write scope, `spec.md` changes only
  in `status`, the worktree is clean and the base checkout unchanged. (ADR-worker-delivers-committed-result)
- A failed validation blocks the unit from review and integration. The commits stay (no reset; a pull request stays
  open and blocked); further commits by the worker or the host fix it, reverting out-of-scope changes, and the next
  validation covers the cumulative range. (ADR-worker-delivers-committed-result)
- The Host's failed range check is a problem in the Host's own `worker` envelope (a `failed` worker envelope); an
  accepted range writes nothing; it is cleared by a resolution that names it, not by a later check. There is no
  `question` or `validation` kind. (ADR-run-records-and-activity-branches)

### Run records and the hold

- Every run ends with exactly one `worker` envelope holding its `questions` and `problem`; an `answer` names it in
  `answers_to`, a `resolution` in `resolves`. (ADR-run-records-and-activity-branches)
- A `planning-worker` writes its questions with `--questions-file` in its `worker` envelope; the run that processes the
  answers records them first as an `answer` envelope. Any run that stops on a problem records `--problem`, `--tried`
  and `--recovery`; whoever actually fixes it commits a `resolution` with the fix.
  (ADR-run-records-and-activity-branches)
- devkit holds the gates from the holding run's stage on, and the handoff, while a problem is unresolved or a question
  unanswered (gates passed before stay passed) and refuses `devkit worktree finish --merge`; a pull request merges only
  while `devkit workflow envelope check` reports neither. (ADR-run-records-and-activity-branches)
- An `answer` envelope may carry `settles`, a list of `{assumption, decision}`: `assumption` a 1-based position into
  the `assumptions` of the `answers_to` worker envelope, each at most once, `decision` one sentence. Positions outside
  that list make the envelope malformed (a reference that does not fit, `ENVELOPE_REFERENCE_INVALID` when authoring).
  (ADR-answer-envelopes-settle-worker-assumptions)
- `answers` stays required when `settles` is absent; with `settles`, `answers` may be empty. Whatever `answers` holds,
  `answers_to` must name a well-formed worker envelope that has questions for each answer and at least as many
  assumptions as the highest `settles` position. (ADR-answer-envelopes-settle-worker-assumptions)
- A wrong position makes the whole answer envelope malformed, like any reference that does not fit; its answers then
  stop counting and their questions are pending again (fail closed, as for answers). The authoring command refuses it
  before writing. (ADR-answer-envelopes-settle-worker-assumptions)
- `settles` is written after `answers` in the key order; the hold reads only `answers`. Only `answer` carries
  `settles`; it affects no hold, check or exit code. Authoring: `devkit workflow envelope answer --settle N=DECISION`
  (repeatable), like `--waive`. (ADR-answer-envelopes-settle-worker-assumptions)
- `references/worker-records.md` section 2 says a decision that settles a worker assumption goes into `settles`, never
  into `constraints`. (ADR-answer-envelopes-settle-worker-assumptions)

### Activity branches

- Every `spec` and `proposal` activity runs on `plan-<slug>` or `dev-<slug>`, in a worktree or, in `direct` mode
  without one, on a branch started with `--no-worktree`. (ADR-run-records-and-activity-branches)
- A branch that exists is continued only with `--existing-branch <branch> --unit <dir>`; devkit-spec's
  `devkit.attach_check` extension refuses a unit that is not the branch's (`plan-<slug>`: `PROP-<slug>` bound to
  `sdd-proposal`; `dev-<slug>`: the spec bundle bound to an `sdd-spec-*` workflow, or the accepted proposal before its
  handoff). The handoff runs only on `dev-<slug>`. (ADR-run-records-and-activity-branches)

### Codex native execution

- Both worker contracts declare Codex `status: emulated` and `sandbox_mode: workspace-write` (SHOULD). Their native
  invocation mechanism is `collaboration.spawn_agent`; the status describes contract enforcement, not the existence of
  native spawning. Workers inherit session reasoning effort and set no model or approval-policy key; the existing
  renderer/allowlist needs no change. (ADR-codex-native-worker-execution)
- The caller SHOULD prefer the projected named role and pass only its payload. If it is unavailable, diagnose
  projection/session-root availability separately from trust. A generic native subagent MAY read the effective
  managed or override contract when host project-instruction loading is permitted; the payload identifies that
  contract by absolute path and labels the call emulated. An explicit host trust restriction MUST NOT be bypassed by a
  generic role, another tool or a settings edit. Role absence alone does not prove the root is untrusted. Missing
  required capabilities select existing Host direct execution or `needs_input` for required isolation before spawning.
  (ADR-codex-native-worker-execution)
- Every worker command MUST set its cwd to the absolute worktree path and every Git command MUST use
  `git -C <worktree>`; absolute paths also apply to nested-role read scopes. The default cwd may be the base checkout.
  Scratch files remain in an ignored path inside the worker's allowed unit/worktree boundary. The prompt and caller
  diff checks enforce the task boundary; `workspace-write` is not per-worker confinement and Git administration is
  shared. (ADR-codex-native-worker-execution)
- When an operation needs access beyond the active sandbox (sibling files, shared Git index/commit administration,
  registry writes, verification requiring unavailable network access), the worker MUST request a command-scoped
  approval with its exact operation, target and justification. No broad persistent prefix, host settings change or
  success-based grant is introduced; an approved call authorizes that operation only, and safe optional checks are
  diagnostics, never access promises for the next call. (ADR-codex-native-worker-execution)
- On unavailable or refused approval the worker MUST stop that operation and preserve the actual result; it SHOULD
  write its failed worker record and emergency commit through still-permitted, scoped operations. It MUST NOT retry a
  denied action with an alternate tool, path, process or broader request to evade refusal. A command that failed for
  another cause can be retried only after the cause/input changes and authorization permits it. Only an ordinary
  commit-gate refusal permits the existing emergency `--no-verify` exception; approval or filesystem denial does not.
  (ADR-codex-native-worker-execution)
- If the record or emergency commit also cannot run, the worker MUST return `failed` to the Host with the cause,
  commands tried, recommended recovery, actual last commit SHA, dirty paths and which record/commit is absent or
  uncommitted. It MUST NOT invent a committed envelope, clean tree or final HEAD containing the record. The Host blocks
  acceptance and owns a subsequent recovery run and its records. The clean committed range remains the
  successful-worker contract; failure reporting does not weaken it. (ADR-codex-native-worker-execution)
- Keep the one-shot worker lifecycle, normal sibling worktrees, mandatory nested roles, stage gates, one worker record
  per run and Host cumulative range validation. No bounded-turn mechanism is required; that requirement of the
  replaced process-worker direction is retired. Claude Code metadata/behavior stay unchanged; Antigravity stays
  unverified. (ADR-codex-native-worker-execution)

### Planning procedure location and budget

- The executor-neutral Planning steps live in `spec/references/planning.md`; the `planning-worker` contract keeps only
  the worker-specific obligations. To the reference: the first turn's `status: reviewing` commit and the
  `needs_decompose` return with the closing `answer` envelope; answers recorded first in their own commit, then
  folded, PADRs with `--summary` after reading the scaffold; review depth per effort (citing `effort.md` and
  `review-loop.md`), recording each `scout`/`challenger` return as its envelope with evidence in `materials/`;
  questions in one round with a recommended option, ambiguity becoming a new question, the `dev_effort` check;
  observed feedback, the `collect-feedback` sweep before the single `worker` envelope and its fields. In the contract:
  starting roles as nested subagents (Host -> worker -> role), waiting for every one and never ending the turn while
  one runs; worktree only, absolute paths and `git -C <worktree>`, scratch inside the worktree; Input, Return
  (`final_head`), Write boundaries, On a problem (emergency commit, `--no-verify` rule).
  (ADR-executor-neutral-planning-steps-in-a-spec-reference)
- The reference addresses "you" as the executor of the Planning turn and names the `direct` Host and the worker alike;
  `worker-records.md` stays the source for envelope mechanics and is cited, not restated. The contract's
  `## Procedure` keeps step 1, the nested-role rule and one step "Follow
  `.devkit/managed/spec/skills/spec/references/planning.md`", by the managed path the contract already uses for
  `review-loop.md` and `sweep.md`. (ADR-executor-neutral-planning-steps-in-a-spec-reference)
- `references/planning.md` is new and linked once from the `spec` routing table's proposal row: the moved text, with a
  short opening for both executors, is about 4.5 KB, well under 12288; the link adds about 100 bytes to
  `spec/SKILL.md` (about 6.6 KB of 11776); the contract shrinks to about 4 KB. No reference is trimmed.
  (ADR-planning-reference-fits-the-existing-byte-budgets)

### Role reasoning effort presets

This decision alone is superseded by `ADR-subagent-level-projection`; the other decisions in this consolidated
ADR remain in force. The preset-specific consequences and confirmation below are historical for this decision.

- Reviewer presets: `scout` and `reconcile-reviewer` `medium`; `code-reviewer` and `challenger` `high`. The
  `claude-code` block sets `effort` and the `codex` block sets `model_reasoning_effort` to the role's value; a `codex`
  block whose status is `unsupported` gets none. Antigravity stays unset. The workers set no preset.
  (ADR-role-effort-presets)
- The preset applies only when the projected agent is spawned. A role the main session runs itself (Codex `emulated`,
  or a main-session substitute) uses the session's effort; `CAP-DLV-delivery-workflows` §4.6 states this in one
  sentence. (ADR-role-effort-presets)
- `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` pins the mapping for every role contract: each role's
  `x-model-profile` and its expected preset per host, so a changed profile, a changed preset or a new contract without
  an entry fails the test. (ADR-role-effort-presets)

### Range inspection

- The command is `devkit spec worker inspect [--unit <dir>] [--base <accepted>] [--head <returned>]
  [--scope <prefix>... | --scope-file <path>] [--base-checkout <path>]`, in a small `worker` group of `devkit spec`,
  run in the unit's worktree. Every input is derived as below; a flag replaces only its own input. The unit's records
  are read as committed at the worktree HEAD; uncommitted files are never read as records.
  (ADR-informational-range-inspection-reuses-existing-checks)
- **Unit**: `--unit`, else the unit bound to the worktree's activity branch: the `branch.<branch>.devkitUnit` marker
  `devkit worktree start --existing-branch --unit` records, else the activity-branch correspondence of the
  `devkit.attach_check` extension (`plan-<slug>` to `docs/proposals/PROP-<slug>`; `dev-<slug>` to its spec bundle
  `specs/<YYYY-MM>/<YYYYMMDD>-<slug>`, or before the handoff the proposal bundle `docs/proposals/PROP-<slug>`). A
  detached HEAD, a branch that is not an activity branch, or no or more than one matching unit directory:
  `WORKER_UNIT_UNRESOLVED`. (ADR-informational-range-inspection-reuses-existing-checks)
- **Returned head**: `--head`, else the commit that added the unit's latest `worker` envelope (the highest
  `envelopes/worker-NN.yaml`), found with `git log --diff-filter=A` on that file. No `worker` envelope, or a file that
  more than one commit added: `WORKER_HEAD_UNRESOLVED`. (ADR-informational-range-inspection-reuses-existing-checks)
- **Base** (the last accepted head): `--base`, else from the previous `worker` envelope (the next-highest number) and
  the unit's state at the commit that added it, `P`, which is the state the latest run was spawned from: not blocked
  at `P` (no problem without a resolution among the records at `P`): the base is `P`; blocked at `P`: the
  `diff_scope.base` that the unresolved problem envelopes at `P` record (the Host's blocking `worker` envelope records
  its `--base`; a failed worker's records the base it was given), so the blocked range keeps its start and a Host fix
  or resolution committed since stays inside the range; no previous `worker` envelope: the merge base of the worktree
  HEAD with the base branch, which is the branch's `devkitBase` marker or else the base checkout's current branch.
  Unresolved problem envelopes that record no `diff_scope.base` or different ones, a base checkout that is detached or
  on the activity branch itself with no `devkitBase`, or no single merge base: `WORKER_BASE_UNRESOLVED`. The latest
  envelope's own state (a problem it records now) does not move the base.
  (ADR-informational-range-inspection-reuses-existing-checks)
- **Write scope**: `--scope`/`--scope-file` replace the derived scope entirely (no union: the Host passes its payload
  scope whole when it differs). Otherwise, by the unit's workflow: `sdd-proposal` the proposal directory; `sdd-spec-*`
  the unit directory, each literal `_Boundary:` path of `tasks.md` (the existing `devkit_spec.entrypoints.bundle`
  parser), the unit's materials directory `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`, each `file` of
  `reconcile.md` `targets` and the feedback file of each FB ID the spec's `Source feedback` section links. Each entry
  carries its source (`unit`, `boundary` with its task, `materials`, `reconcile`, `source-feedback` with its ID,
  `argument`). A `tasks.md` or `reconcile.md` that the parser refuses, an FB ID with no file or another workflow leaves
  the outside-scope check `not-run` with that cause (the other checks still run). The derived scope is never widened:
  a follow-up draft proposal a Planning worker adds, or a link repair outside the declared paths, is reported outside
  the scope for the Host to judge. (ADR-informational-range-inspection-reuses-existing-checks)
- **Base checkout**: `--base-checkout`, else the worktree's registered base checkout (the one whose Git directory is
  the common one, as `devkit worktree` locates it); absent when the command runs in the base checkout itself. Its HEAD
  and dirty paths are information, not a check: comparing them with what the Host recorded before spawning stays the
  Host's step. (ADR-informational-range-inspection-reuses-existing-checks)
- A could-not-run code's action is to pass the named flag. Each input in the result names its value and its source
  (`argument` or the derivation used). (ADR-informational-range-inspection-reuses-existing-checks)
- Each check reports `pass`, `fail` or `not-run` (with its cause), so a check that could not run is distinct from a
  negative result. The checks: ancestry of base to returned head; worktree HEAD equals the returned head; changed paths
  of `git diff --name-only <base> <head>` with those outside the scope (`not-run` when no scope could be derived and
  none was given, leaving the judgment to the Host); worktree status; `devkit workflow envelope check` results
  (malformed files, `blocked`, `pending_questions`); the cumulative rules check over the range (the
  `devkit rules check --ci --base <base>` evaluation, run only when the worktree HEAD equals the returned head,
  otherwise `not-run`); and the stage `devkit workflow next` names.
  (ADR-informational-range-inspection-reuses-existing-checks)
- Exit codes: `0` every check passed, `1` at least one check failed (a negative result, not a refusal), `2` the command
  could not run (bad arguments, not a Git worktree, unknown refs, or an input neither given nor derivable:
  `WORKER_UNIT_UNRESOLVED`, `WORKER_HEAD_UNRESOLVED`, `WORKER_BASE_UNRESOLVED`). A `not-run` check alone does not make
  the exit `1`; it is reported as a notice. (ADR-informational-range-inspection-reuses-existing-checks)
- Structured output (`--format json`) is one object with the `inputs` (`unit`, `base`, `head`, `base_checkout`, each
  with its value and source), `scope` (its entries with their sources), the compared `base` and `head`,
  `changed_paths`, `outside_scope` (absent when the scope check is `not-run`), `base_checkout` (its `head` and
  `dirty_paths`, absent without one) and the per-check results; this object, or its `base`, `head` and
  `changed_paths`, is what the Host passes a read-only reviewer.
  (ADR-informational-range-inspection-reuses-existing-checks)
- The command modifies no file, writes no record, runs no `devkit sync`, merges nothing, retries nothing and enlarges
  no scope. Whether a finding blocks the worker's result stays the Host's decision under the existing `spec-delegate`
  procedure. (ADR-informational-range-inspection-reuses-existing-checks)

---

## 5. Consequences

- **Positive**:
  - The host no longer repairs worker output; a worker's branch is reviewable as is; the pilot's three worker
    frictions are resolved by the contract.
  - The Host's per-range validation becomes one call, usually without arguments; its decision and recording (accept,
    or block with a `worker` envelope) are unchanged. Reviewer payloads can carry a generated changed-path list
    instead of the caller's selection.
  - Codex roles become projected by normal sync and can use tested native mechanisms where scoped approvals work.
  - Reviewers run at a fixed effort on Claude Code and Codex with no model names to maintain; on Claude Code a
    per-call `effort` or `CLAUDE_CODE_EFFORT_LEVEL` still overrides the preset, on Codex the preset wins over a spawn
    value.
- **Negative / Risks**:
  - A rejected range remains in the unit branch's history until it is fixed; a worker with Git write access must be
    trusted not to bypass the commit gate (the range check catches out-of-scope paths).
  - Approval refusal and inability to preserve a committed result remain visible failure modes. Named-role loading and
    denied approvals have not been live validated, and no general host/version or persistent-grant guarantee follows.
  - The worker reads one more file at spawn (about 4.5 KB), as it already does for `review-loop.md` and `sweep.md`.
  - A derived scope can differ from the payload scope the Host wrote (a payload that adds paths the documents do not
    declare); the Host then passes its scope with `--scope`, and the result names the scope's source either way.
  - Deriving the base reads the unit's records at an earlier commit, so the envelope check must run on a committed
    tree, not only on the working directory. The rules check over the range is as costly as
    `devkit rules check --ci`; the command runs it once per call.
- **Follow-ups and effects on other records**:
  - `devkit spec proposal handoff` refuses any checkout on another branch than `dev-<slug>`
    (`SPEC_PROPOSAL_WRONG_WORKTREE`); `ADR-worktrees-branches-and-scope` extends the guard to the base checkout.
  - `/spec-next` reports `[PENDING_QUESTION]`, `[BLOCKED]` and stale activity branches; the feedback hygiene playbook
    lists stale branches for the user to resume or discard. A stale branch's unit is shown only when an attach recorded
    it; the Host maps the slug otherwise.
  - The `planning-worker` row of the `CAP-DLV-delivery-workflows` role table names its procedure in
    `spec/references/planning.md`, with the sentence on where worker procedures live; `CAP-HARN-agent-guidance` lists
    only the asset ids and needs no change. If the Planning reference grows past about 8 KB, split it rather than
    trimming another reference.
  - The model-selection non-goal of `CAP-DLV-delivery-workflows` narrows: model choice stays with the runtime, while
    role contracts preset a reasoning effort per role. Raising a reviewer above `high` later is a contract edit plus
    the test table, once both hosts accept the value on the models in use.
  - `settles` touches the `Answer`/envelope model, `_check_kind_fields`, reference validation and the `answer`
    command; `envelope check --format json` entries carry `settles`; `CAP-DLV-workflow-envelopes` section 1.1 (table
    and example) and section 2 (flag table, key order).

---

## 6. Confirmation

- `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` pins the reasoning-effort mapping per role and host.
- `packages/devkit-spec/tests/integration/bundles/spec/test_bundle_budgets.py` holds the byte budgets and the link coverage of
  `references/planning.md`.
- Phrase tests follow the moved Planning text: `test_the_planning_worker_collects_questions_in_one_round` and the
  planning half of `test_a_run_records_its_questions_and_problem_in_one_worker_envelope` read the reference;
  `test_a_worker_commits_its_result_and_records_in_its_worktree` keeps its contract assertions (`git -C <worktree>`,
  `MUST NOT`, `final_head`, `devkit workflow envelope worker`); `test_every_restatement_cites_the_loop` keeps
  `review-loop.md` in the contract only if the contract still names it, otherwise the reference joins `CITING`.
- Envelope engine tests for valid, out-of-range, duplicate and settles-only answers.
- Deterministic contract and projection tests cover the Codex instruction branches; live generic-role execution
  evidence came from the Planning and Development runs of `SPEC-codex-native-workers`.
- The Host's range validation (`spec-delegate` `references/worker.md`, `devkit spec worker inspect`) checks every
  returned range.

