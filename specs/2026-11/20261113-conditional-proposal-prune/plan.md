---
id: PLAN-conditional-proposal-prune
spec: SPEC-conditional-proposal-prune
---

# Technical Plan: `SPEC-conditional-proposal-prune`

## 1. Constitution & Invariant Review

None. `CAP-DLV-proposal-lifecycle` receives a bounded applicability condition. `CAP-INT-mcp-services` keeps exact cleanup identities, digest binding and source/target refusal checks. `ADR-worktrees-and-scope` keeps post-finish cleanup in devkit-spec; no package, layer, tier, dependency or extension is added. This implementation choice does not change an accepted architectural decision and needs no ADR.

## 2. Architecture Overview & Impact

Only the delivery scoped-cleanup extension changes. A shared helper derives its expected proposal target from a valid branch slug and a Git history read bounded to FinishPlan.source_sha and FinishPlan.target_sha. `integration_plan` and `_parse_targets` use the same helper; validate/run retain exact tuple equality and all scope checks. Use `git log -1 --format=%H <source_sha> <target_sha> -- <proposal-path>` to detect provenance. Checking only the pinned trees would miss cleanup-only preparation after a handoff already landed; checking the live directory would change validation after prune. No new stored state is needed.

## 3. Component & Interface Design

The existing CleanupTarget schema remains unchanged. The helper returns either an empty tuple or one `CleanupTarget(kind="proposal-prune", identity=proposal_unit(slug), revision=source_sha)`. Unknown kinds, duplicates, omitted applicable targets and extra inapplicable targets remain refusals. Git read failures propagate through the existing provider error boundary. Classic `after_finish` and standalone prune remain unchanged.

## 4. Verification & Test Plan

Integration tests cover spec-only cleanup, source-only and target-only proposal history, deletion/handoff, idempotent replay, permission failure recovery, path/source tampering, duplicates/omission and existing scope refusals. E2E integration tests cover the visible spec-only request, a committed proposal handoff followed by empty-directory prune, and partial post-finish behavior. Keep existing approval, network, branch and worktree assertions.

Measure a before/after outcome at the current head with the helper disabled to reproduce the accepted branch-slug behavior, using an ignored in-process probe: for a spec-only committed repository, count proposal-prune targets before=1 and after=0. For a deleted committed proposal, count remains 1 before and after; retry identity remains equal after prune.

Run targeted cleanup integration/E2E synchronously, `just lint-check devkit-spec`, `just check devkit-spec`, `just test-affected --base 8006563f2af4397048a9bd6871bc9a19bd8b3379 --tier all` with its full fallback, cumulative CI rules against a6872bf5ef7d99a10e8bc3799f88b615c03fd47e, sync, envelope and whitespace checks. Record source identities and reuse passing production checks after documentation-only changes. Apply medium effort: independent code review and a reconcile check of the exact capability restatement.
