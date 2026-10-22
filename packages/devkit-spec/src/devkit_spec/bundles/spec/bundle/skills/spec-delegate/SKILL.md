---
name: spec-delegate
description: Delegate to Scout, Challenger, Code Reviewer, Reconcile Reviewer or a local-orchestrated worker with an explicit payload; verify the returned envelope and the actual diff against write boundaries.
---

# spec-delegate: Support Role Invocation

Use this skill when the main Developer session hands work to an isolated context:

- exploration, criticism, an independent review or a reconcile verification, to a support role;
- one Planning or Development turn, to a worker (`local-orchestrated` mode, `spec-orchestrate`).

A reviewer runs outside the author's context, for neutrality. Treat a role's result as an opinion with evidence; completion rests on the agreed AC, checks, the final diff and reconciliation.

## Inputs

- Role contract: `scout`, `challenger`, `code-reviewer`, `reconcile-reviewer`, `planning-worker` or `development-worker` (the workers only in `local-orchestrated` mode).
  - If the stage prefers isolation, `devkit workflow next --unit <dir>` prints `[DELEGATE: role=<role> isolation=<level> contract=<path>]`; `contract=` is the effective contract (managed or overridden).
  - Otherwise use the managed contract `.devkit/managed/spec/subagents/<role>.md`.
  - The contract body is the role's prompt and is already in its projected agent file. Read it only when you substitute for the role or a permitted generic subagent emulates it.
- Stage context: `devkit workflow next --unit <dir>` (current stage) and `devkit workflow show --unit <dir>` (where returns go).

## Constraints

1. Read the contract frontmatter first: `x-git-actions` and `hosts.<host>.status` for the current host decide how you call the role.
2. Pass `relevant_files`, never the whole repository.
3. Fill `allowed_boundaries` with the task's actual declared paths; the paths in a contract are examples.
4. Rely on the host and the post-run diff for enforcement; prompt limits are guidance. If the host status is `emulated` or `unverified`, say so in the call.
5. A support role never touches the index or HEAD, except a worker, which commits on its activity branch ([worker](references/worker.md)).
6. Accept zero findings as a valid result; never ask a role for a minimum number of objections.

## Procedure

### Step 1: Decide whether to delegate

- `[DELEGATE]` names the role.
- The `activity-effort` decides which roles run and how: the `spec` skill's `references/effort.md`; at `high`, the bounded rounds of its `references/review-loop.md`, with a fresh call per round.
- For a `session` task, the role returns a message: write no envelope and start no worker.
- A `planning-worker` runs one proposal Planning turn and a `development-worker` one Development turn of a spec unit, each in its own worktree, with its role subagents nested (Host → worker → role).
- Before starting a worker, check native spawning, the nested roles and the approval capabilities its operations need ([hosts](references/hosts.md)). If one is unavailable, run the unit in `direct` when allowed, or stop with `needs_input` when isolation is required.

### Step 2: Build the input payload

Fill `task_goal`, `relevant_files`, `allowed_boundaries` (read scope, write scope, denied paths), `diff_scope` (base and head) and `expected_output_format`, plus `changed_paths` for the review roles, with the rows per role in [payload](references/payload.md). Record the head SHA you passed (`git rev-parse HEAD`).

### Step 3: Invoke in isolation

1. Read the stage's `isolation` from `[DELEGATE: ... isolation=none|preferred|required ...]` and the role's `hosts.<host>.status`.
2. Choose one route and record it with the status in the envelope's `assumptions`:
   - If the status is `native`, `emulated` or `unverified`, spawn an isolated subagent.
   - If isolation is `required` and the status is `unsupported`, stop with `needs_input`.
   - If the status is `unsupported`, or isolation is `preferred` and no fresh context is available, substitute in the main session.
3. To spawn, use the host's isolated-context mechanism; [hosts](references/hosts.md) names the tool, the projected file, role availability and the trust-aware fallback. When a fresh context is what isolates the result, start one instead of forking the main context.
4. Pass the role its input:
   - With a projected file, pass only the payload: the host loads the contract body as the system prompt.
   - If a named role is unavailable, a generic native subagent reads the absolute effective contract only under the trust conditions in [hosts](references/hosts.md), and states emulation.
   - When the main session substitutes, follow the contract body yourself.
   - Pass the actual change and the intent, not the main session's narrative.

### Step 4: Validate the returned fields

- Required fields are present, and `status` is one of `completed | needs_input | failed`.
- Each Code Reviewer, Reconcile Reviewer and Challenger finding has `evidence` and `failure_condition`.
- A `failed` result or a stale `diff_scope` (a worker's own head aside) is not completion evidence. Re-invoke only after the input or the cause changed.

### Step 5: Compare the actual diff with the boundary

```bash
git status --short
git diff --name-only            # unstaged
git diff --name-only --cached   # staged (should be unchanged by the role)
```

- Scout, Challenger, Code Reviewer, Reconcile Reviewer: the expected diff is empty. A Scout adds only to the agreed `materials/` path; the Reconcile Reviewer verifies and never drafts.
- Worker: validate the committed range instead ([worker](references/worker.md)); one path outside the write scope rejects the whole result.
- A path outside `allowed_boundaries`, or an index or HEAD change other than a worker's own commits, is a violation. On a violation, report the paths, revert the change (block a worker's range instead) and do not reuse earlier check results.

### Step 6: Fold the result back

- Envelope file (spec Unit; `session` depth writes none):
  - Record a read-only role's return as `<unit>/envelopes/<kind>-<NN>.yaml`, kind `scout`, `challenger`, `review` or `reconcile-check`. For a proposal spike, the unit is the proposal bundle: `--unit docs/proposals/PROP-<slug> --stage spike`.
  - Write it with the CLI, not by editing YAML: `devkit workflow envelope new --unit <dir> --kind <kind> --stage <stage> ... --findings-file -` (`envelope review` for a review), then `devkit workflow envelope check --unit <dir>`. Flags: section 6 of the `spec` skill's `references/envelope.md`.
  - A review records findings as found (all open); `envelope reverify` (`--from latest --resolve N --waive N=<why>`) closes it, and `--from envelopes/challenger-NN.yaml` closes a Planning `challenger` round the same way.
  - A worker writes its own records; a range you block is a problem in your own `worker` envelope.
  - Keep only the summary and the file path in the conversation.
- Scout or Challenger: write the comparison table and recommendation into the proposal bundle (`materials/` or `proposal.md`); keep `unverified_areas` visible for `plan-accept`.
- Code Reviewer: fix the findings, then re-verify only the changed part (tests for touched packages, `devkit rules check --staged`).
- Reconcile Reviewer: fix each omission or mismatch it found, a contract mismatch in code and never by waiver; then complete `reconcile.md` per the `spec-sync` skill.
- Worker: accept or block the range and handle a recorded problem ([worker](references/worker.md)).
- Commit as the Developer, except a worker's own commits; stage only this task's agreed paths.

## Completion

- [ ] If the host status is not `native`, the call stated it; a projected role received only the payload.
- [ ] No failed or stale result served as evidence; the actual diff (a worker: its committed range) stayed inside `allowed_boundaries`.
- [ ] The result is folded into the current stage's artifact; for a spec Unit, `devkit workflow envelope check --unit <dir>` lists its envelope file.
