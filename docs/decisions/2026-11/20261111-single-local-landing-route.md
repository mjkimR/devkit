---
id: ADR-single-local-landing-route
title: Land task branches locally only through the integration service
summary: "For landing a task branch on the local base, we retire worktree finish --merge and its finish guard group so devkit integration integrate --route local is the one route, to keep every Git safeguard in one place, accepting that devkit no longer pushes the base after a local landing."
proposal: SPEC-retire-finish-merge
supersedes:
  - ADR-local-and-pull-request-integration
  - ADR-orchestration-workers
  - ADR-worktrees-and-scope
  - ADR-package-ownership-and-release-version
status: accepted
created_at: 2026-11-11
---

# [ADR-single-local-landing-route] Land task branches locally only through the integration service

Superseded in part by `ADR-remove-unused-cli-options-without-shims`: the clause that `--local-only` stays accepted, and the follow-up to retire the no-op `--local-only` flag. All other decisions remain in force.

- **Status**: Accepted
- **Date**: 2026-11-11
- **Deciders**: user
- **Involved Components/Capabilities**: `CAP-WT-task-worktrees`, `CAP-INT-mcp-services`,
  `CAP-DLV-workflow-envelopes`, `CAP-DLV-delivery-workflows`, `ARCH-04-2-delivery-policy`, `ARCH-05-2-components`,
  `devkit_agt.features.worktree`, `devkit_agt.features.integration`, `devkit_agt.features.workflow`

---

## 1. Context & Problem Statement

Two implementations landed a task branch on the local base: `devkit worktree finish --merge` and
`devkit integration integrate --route local`. They diverged. `finish --merge` ran the `devkit.finish_guard`
extensions, fetched the base upstream, pushed the base after landing and refused a moved target. The integration
route builds a merge onto a moved target, settles generated-file conflicts, binds an approval digest and runs no
content guard, fetch or push. Agents and documents chose between them inconsistently, and every Git safeguard had to
be kept twice.

The local route's boundaries are already decided: `ADR-post-merge-verification` removed content finish guards from
integration, and `ARCH-04-2-delivery-policy` excludes fetch and push from the local route. The only caller of the
`devkit.finish_guard` group was `finish --merge`.

---

## 2. Decision Drivers

- One landing path, so moved-target, generated-file, approval and cleanup handling are the same for every landing.
- No second copy of Git safeguards to keep in step.
- The accepted integration content boundary and the no-network local route stay as they are.
- An agent following older guidance learns the replacement from a stable code.

---

## 3. Considered Options

### Option 1: Retire `finish --merge` and the finish guard group (Selected)
- **Overview**: `finish --merge` refuses with `WORKTREE_MERGE_RETIRED` naming the integration commands; the library
  `finish` keeps cleanup only; the `devkit.finish_guard` group, its workflow extension, the base fetch and the base
  push are removed.
- **Pros**: one route; no unused extension group; nothing contradicts the integration content boundary.
- **Cons**: devkit no longer pushes the base after a local landing; the Host publishes it as a separate Git effect.

### Option 2: Retire `finish --merge` and keep the guard group dormant
- **Overview**: as Option 1, but the group and its workflow extension stay registered with no caller.
- **Cons**: documents a refusal that never happens; a public extension group nothing calls.

### Option 3: Move the guards and the push into the integration service
- **Overview**: the integration route gains the envelope hold check and the base push.
- **Cons**: reverses `ADR-post-merge-verification` and `ARCH-04-2-delivery-policy`.

### Option 4: Keep both routes
- **Cons**: keeps the divergence and the double maintenance this decision removes.

---

## 4. Decision Outcome

We decided to adopt **Option 1**.

- `devkit integration integrate --route local` is the only command that lands a task branch on the local base.
  → `CAP-WT-task-worktrees` §3 (MUST)
- `devkit worktree finish --merge` refuses with `WORKTREE_MERGE_RETIRED` (exit `2`) before reading or changing
  anything, and its `[FIX]` names `devkit integration prepare <branch> --route local` and
  `devkit integration integrate <branch> --route local --expected-digest <digest>`; the flag is hidden from help.
  → `CAP-WT-task-worktrees` §3 (MUST)
- The library `finish` removes the worktree and branch of a branch the base already contains and keeps no landing,
  guard, network, pull-request policy or merge-method parameter; its result has no `push` field.
  → `CAP-WT-task-worktrees` §3 (MUST)
- `finish` without `--merge` and `--local-only` make no fetch, push or `ls-remote` call; `--local-only` stays
  accepted. → `CAP-WT-task-worktrees` §3 (MUST)
- The `devkit.finish_guard` extension group, its runner and the workflow `workflow-envelopes` entry point are
  retired; the codes `WORKTREE_BLOCKED`, `WORKTREE_GUARD_FAILED`, `WORKTREE_BASE_BEHIND`, `WORKTREE_PUSH_FAILED` and
  `WORKTREE_PUSH_REJECTED` no longer exist. → `ARCH-05-2-components` §1.2 entry-point groups
- The envelope hold stays where the workflow puts it: `devkit workflow next` holds the gates from the holding run's
  stage on, and the Host runs `devkit workflow envelope check` before approving integration.
  → `CAP-DLV-workflow-envelopes` §4 (MUST)
- The finish guards are dropped, not moved, because `ADR-post-merge-verification` forbids content finish guards in
  integration.
- The base fetch and push are dropped, not moved, because the local route excludes fetch and push; publishing the
  base is a separate Git effect under the Host's publication authority. → `ARCH-04-2-delivery-policy` §4 (MUST)
- The moved-target refusal of `finish --merge` is replaced by the moved-target build of the integration route.

Supersedes in part `ADR-local-and-pull-request-integration`: the clauses that `[worktree] merge` applies to `devkit worktree finish --merge`, that the CLI `finish --merge` builds a merge commit only when the target did not advance and takes the integration lock, that `devkit worktree finish --merge` keeps refusing a moved target, and the mention of `finish --merge` among the callers that pass no conflict settler. All other decisions remain in force.

Supersedes in part `ADR-orchestration-workers`: the clause that devkit refuses `devkit worktree finish --merge` while a unit is held. All other decisions remain in force.

Supersedes in part `ADR-worktrees-and-scope`: the clause that `[worktree] pull_request = "required"` makes devkit refuse `devkit worktree finish --merge`. All other decisions remain in force.

Supersedes in part `ADR-package-ownership-and-release-version`: the clause that the `devkit.finish_guard` `workflow-envelopes` entry point stays with `devkit-agt`. All other decisions remain in force.

---

## 5. Consequences

- **Positive**: one landing route with one set of Git safeguards; guidance names one command pair.
- **Negative / Risks**: a project that relied on `finish --merge` pushing the base now publishes it separately; an
  out-of-tree `devkit.finish_guard` extension is no longer called.
- **Follow-ups**: retire the no-op `--local-only` flag when a cleanup of no-op flags is scheduled.

---

## 6. Confirmation

- `packages/devkit/tests/integration/features/worktree/test_cli.py`: the `WORKTREE_MERGE_RETIRED` refusal, the hidden
  flag and the network-free cleanup.
- `packages/devkit/tests/integration/features/integration/test_service.py`: local landing of a marked branch-only and
  a `plan-<slug>` branch without fetch or push.
- `packages/devkit/tests/integration/features/workflow/test_envelope_hold.py`: the hold through `envelope check` and
  `workflow next`.
- Restating documents: `CAP-WT-task-worktrees`, `CAP-DLV-workflow-envelopes`, `ARCH-04-2-delivery-policy`,
  `ARCH-05-2-components`.
