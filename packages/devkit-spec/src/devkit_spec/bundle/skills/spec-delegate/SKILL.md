---
name: spec-delegate
description: Delegate to Scout, Challenger, Code Reviewer, Reconcile Reviewer or a local-orchestrated worker with an explicit payload; verify the returned envelope and the actual diff against write boundaries.
---

# spec-delegate: Support Role Invocation Workflow

Use this skill when the main Developer session hands exploration, criticism, an independent review or a reconcile verification to an isolated context, or a worker one Planning or Development turn. A reviewer exists for neutrality, a different context than the author's. The role's result is an opinion with evidence; completion still rests on agreed AC, checks, the final diff and reconciliation.

---

## 1. Inputs

- Role contract: `challenger`, `reconcile-reviewer`, `code-reviewer`, `scout`, `planning-worker` or `development-worker` (the workers in `local-orchestrated` mode only). `devkit workflow next --unit <dir>` prints `[DELEGATE: role=<role> isolation=<level> contract=<path>]` for a stage that prefers isolation; `contract=` is the effective contract (managed or overridden). Otherwise the managed contract is `.devkit/managed/spec/subagents/<role>.md`. The body is the role's prompt, already in its projected agent file, read when the main session substitutes or a permitted generic subagent emulates the role.
- Stage context: `devkit workflow next --unit <dir>` (current stage) and `devkit workflow show --unit <dir>` (where returns go).

---

## 2. Invariants

1. **Read the contract frontmatter first (`MUST`)**: `x-git-actions` and `hosts.<host>.status` for the current host decide how you call it.
2. **No whole-tree injection (`MUST NOT`)**: pass `relevant_files`, not the repository.
3. **Boundaries are per task (`MUST`)**: inject the repository's actual declared paths into `allowed_boundaries`; contract paths are examples.
4. **Guarantee comes from the host and the diff (`MUST`)**: prompt limits are guidance. If the host status is `emulated` or `unverified`, say so in the call and rely on the post-run diff comparison.
5. **Support roles never touch index or HEAD (`MUST NOT`)**, except a worker, which commits on its activity branch ([worker](references/worker.md)).
6. **Zero findings is a valid result (`MUST`)**: never ask a role to produce a minimum number of objections.

---

## 3. Procedure

### Step 1: Decide whether to delegate
- The `activity-effort` decides which roles run and how: the `spec` skill's `references/effort.md`, and at `high` the bounded rounds of its `references/review-loop.md` (a fresh call per round). `[DELEGATE]` names the role. A `session` task gets a returned message, never an envelope or a worker.
- `local-orchestrated` (`spec-orchestrate`): a `planning-worker` runs one proposal Planning turn, a `development-worker` one Development turn of a spec unit, each in its worktree; never for `session`. A worker runs its role subagents nested (Host → worker → role). Before starting it, check native spawning, nested-role and necessary approval capabilities per [hosts](references/hosts.md); use the existing direct/needs_input fallback when unavailable.

### Step 2: Build the input payload
Fill all five fields: `task_goal`, `relevant_files`, `allowed_boundaries` (read scope, write scope, denied paths), `diff_scope` (base and head), `expected_output_format`, with the rows per role in [payload](references/payload.md). Record the head SHA you passed (`git rev-parse HEAD`).

### Step 3: Invoke in isolation
- Read the stage's `isolation` from `[DELEGATE: ... isolation=none|preferred|required ...]` and the role's `hosts.<host>.status`. State one of: spawn an isolated subagent (`native`, `emulated`, `unverified`); substitute in the main session (`unsupported`, or `preferred` without a fresh context); stop with `needs_input` (`required` and `unsupported`). Record the choice and the status in the envelope's `assumptions`.
- To spawn, use the host's isolated-context mechanism: read [hosts](references/hosts.md) for the tool, the projected file, role availability and trust-aware fallback. Do not fork the main context when a fresh context is what isolates the result.
- With a projected file, pass only the payload: the host loads the contract body as the system prompt. When a named role is unavailable, a generic native subagent may read the absolute effective contract only under the trust conditions in [hosts](references/hosts.md), and states emulation. When the main session substitutes, follow the contract body yourself. Pass the actual change and the intent, never the main session's narrative.

### Step 4: Validate the returned fields
- Required fields present; `status` is one of `completed | needs_input | failed`.
- Reviewer and Challenger findings each have `evidence` and `failure_condition`.
- `failed` or a stale `diff_scope` (a worker's own head aside) is not completion evidence; re-invoke only for a changed input or cause.

### Step 5: Compare the actual diff with the boundary
```bash
git status --short
git diff --name-only            # unstaged
git diff --name-only --cached   # staged (should be unchanged by the role)
```
- Scout, Challenger, Reviewer, Reconciler: expected diff is empty (Scout may add only to the agreed `materials/` path; the Reconciler verifies, never drafts).
- Worker: validate the committed range instead ([worker](references/worker.md)). One path outside the write scope rejects the whole result.
- A path outside `allowed_boundaries` or a change to the index or HEAD (a worker's own commits aside) is a violation: report the paths, revert it (a worker's: block it), and do not reuse earlier check results.

### Step 6: Fold the result back
- **Envelope file** (spec Unit): record a read-only role's return as `<unit>/envelopes/<kind>-<NN>.yaml` with kind `scout`, `challenger`, `review` or `reconcile-check`; a worker writes its own records, and a range you block is a problem in your own `worker` envelope. Never hand-edit YAML: `devkit workflow envelope new --unit <dir> --kind <kind> --stage <stage> ... --findings-file -` (`envelope review` for a review), then `devkit workflow envelope check --unit <dir>`. A review records findings as found (all open); `envelope reverify` (`--from latest --resolve N --waive N=<why>`) closes it. Authoring flags: section 6 of the `spec` skill's `references/envelope.md`. Keep only the summary and file path in the conversation; `session` depth writes no envelope files. For a proposal spike the unit is the proposal bundle: `--unit docs/proposals/PROP-<slug> --stage spike`.
- Scout/Challenger: write the comparison table and recommendation into the proposal bundle (`materials/` or `proposal.md`); keep `unverified_areas` visible for `plan-accept`.
- Reviewer: fix findings, then re-verify only the changed part (tests for touched packages, `devkit rules check --staged`).
- Worker: accept the range or block it, and handle a recorded problem ([worker](references/worker.md)).
- Reconcile reviewer: fix each omission or mismatch it found (a contract mismatch in code, never a waiver), then complete `reconcile.md` per the `spec-sync` skill.
- Commits are the Developer's, a worker's own aside, staging only this task's agreed paths.

---

## 4. Definition of Done

- [ ] Host projection status stated when not native; the payload was all a projected role received.
- [ ] Stale or failed results not used as evidence; the actual diff (a worker: its committed range) matched `allowed_boundaries`.
- [ ] Result folded back into the current stage's artifact; envelope file written for a spec Unit.
