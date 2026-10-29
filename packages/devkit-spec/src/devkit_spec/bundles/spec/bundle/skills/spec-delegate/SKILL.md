---
name: spec-delegate
description: Delegate to Scout, Challenger, Code Reviewer, Reconcile Reviewer, UX Reviewer, Triage, Decomposer or a local-orchestrated worker with an explicit payload; verify the returned envelope and the actual diff against write boundaries.
---

# spec-delegate: Support Role Invocation

Hand one isolated task to a support role (`scout`, `challenger`, `code-reviewer`, `reconcile-reviewer`, `ux-reviewer`, `triage`, `decomposer`) or, in `local-orchestrated` mode, to a worker (`planning-worker`, `development-worker`). A role's result is an opinion with evidence; completion rests on the agreed AC, checks, the final diff and reconciliation.

## Constraints

- Read the contract frontmatter first: `x-git-actions` and `hosts.<host>.status` decide how you call the role. The contract is the `contract=` path of `[DELEGATE: ...]`, else `.devkit/managed/spec/subagents/<role>.md`.
- Fill `allowed_boundaries` with the task's actual declared paths; the post-run diff, not the prompt, enforces them.
- A support role never touches the index or HEAD; a worker commits only on its activity branch.
- Zero findings is a valid result.
- A `session` task's role returns a message: no envelope, no worker. A Backlog role (`triage`, `decomposer`) also returns a message: no envelope; the Backlog commit body names the role used.

## Procedure

1. **Choose the route** from the stage's `isolation` (`[DELEGATE: ... isolation=none|preferred|required ...]`) and the host status; record it in the envelope's `assumptions`:
   - `native`, `emulated` or `unverified`: spawn an isolated subagent per [hosts](references/hosts.md); if not `native`, say so in the call.
   - `unsupported` with isolation `required`: stop with `needs_input`.
   - `unsupported`, or `preferred` without a fresh context: substitute in the main session and follow the contract body yourself.
2. **Build the payload** per [payload](references/payload.md) and record the head SHA you passed. Give a projected role only the payload, with the actual change and intent instead of the main session's narrative. For a support role, also record this snapshot (it covers tracked edits and untracked files, so a write to an already-modified file shows too):

   ```bash
   index="$(git rev-parse --git-path devkit-delegate.index)"
   GIT_INDEX_FILE="$index" git read-tree HEAD && GIT_INDEX_FILE="$index" git add -A && GIT_INDEX_FILE="$index" git write-tree
   ```

   The temporary index lives in the checkout's Git directory; the real index and `git status` stay unchanged.
3. **Validate the return**: `status` is `completed | needs_input | failed`, and each finding has `evidence` and `failure_condition`. A `failed` result or a stale `diff_scope` is not evidence; re-invoke only after the input or the cause changed.
4. **Check the diff**: a support role leaves HEAD unchanged, and `git diff --name-only <before> <after>` between the snapshots taken before and after the run lists nothing, except a Scout's agreed `materials/` path. For a worker, validate the committed range per [worker](references/worker.md). On a path outside `allowed_boundaries`, report it, revert it (block a worker's range instead) and discard earlier check results.
5. **Fold back**:
   - Record a read-only role's return with `devkit workflow envelope new --unit <dir> --kind scout|challenger|review|reconcile-check --stage <stage> ...` (`envelope review` for a review), then run `devkit workflow envelope check --unit <dir>`; flags and closing a round: the `spec` skill's `references/envelope.md`, Where envelopes live. A proposal spike's unit is `docs/proposals/PROP-<slug>`.
   - Scout or Challenger: put the comparison and recommendation into the proposal bundle; keep `unverified_areas` visible for `plan-accept`.
   - Code Reviewer: fix the findings and re-verify only the changed part.
   - Reconcile Reviewer: fix each finding (a contract mismatch in code, never by waiver), then complete `reconcile.md` per `spec-sync`.
   - Triage or Decomposer: verify the return and apply only what the user decides, per the `spec` skill's `references/backlog.md` (Backlog roles).
   - Commit as the Developer; stage only the task's agreed paths.

## Completion

- The actual diff (a worker: its committed range) stayed inside `allowed_boundaries`, and no failed or stale result served as evidence.
- For a spec Unit, `devkit workflow envelope check --unit <dir>` lists the new envelope.
