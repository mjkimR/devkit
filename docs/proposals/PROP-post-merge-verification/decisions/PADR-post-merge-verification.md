---
id: PADR-post-merge-verification
title: Complete integration after verifying the landed runtime
summary: "For integration and tool upgrades, we verify landed content with its resulting runtime after branch checks, to simplify completion and remove old-runtime incompatibility, accepting temporary failures on the target."
proposal: PROP-post-merge-verification
supersedes:
  - ADR-local-and-pull-request-integration
  - ADR-delivery-approval-and-lifecycle-authority
  - ADR-test-selection-and-ci
status: draft
created_at: 2026-11-04
---

# [PADR-post-merge-verification] Complete integration after verifying the landed runtime

## 1. Context & Problem Statement

The target's devkit currently evaluates source/merged content before landing. Tool upgrades and self-development
can require interfaces that runtime lacks. Final application tests are not run by that readiness check.
Source rules and settings already come from the changed snapshot; retaining an old engine does not freeze all
verification policy. A personal project's deliberate owner bypass is outside the threat model.

## 2. Decision Drivers

- Verify the code and dependencies that actually remain on the target.
- Keep routine upgrades free of separately built integration runtimes.
- Retain concrete Git/approval safeguards and observable partial effects.
- Minimize commands, repeated checks and runtime orchestration machinery.

## 3. Considered Options

- Keep target-runtime readiness: preserves existing pre-land refusals but retains upgrade incompatibility.
- Add an automatic fresh-runtime verifier: can check before or after landing but adds installation, subprocess,
  output and retry contracts to the merge tool.
- Host-led final checks, with cleanup postponed: retains the task checkout but adds another cleanup phase; the
  landed commit already contains the code needed for repair.
- Host-led final checks, with existing scoped cleanup: selected; uses existing project commands and keeps the Git
  operation bounded, accepting that final failures are repaired on the target after cleanup.

## 4. Decision Outcome

- Branch verification precedes Git integration; the Host verifies final landed content with its synchronized
  runtime before reporting delivery completion. → `CAP-DLV-delivery-workflows` integration completion (MUST).
- Integration reports Git/cleanup effects and pending final verification separately. It runs no target-runtime
  source-content readiness check. → `CAP-INT-mcp-services` CLI/result contract (MUST).
- Approval preparation, source/target identity, permitted target advance and scoped cleanup remain part of the Git
  operation. → `CAP-INT-mcp-services` approval and partial recovery (MUST).
- The Host repairs a failing target within scope and rechecks, or performs an authorized revert. A final-check
  failure never causes an automatic merge replay or rollback. → `CAP-DLV-delivery-workflows` recovery (MUST).
- Repository affected-test policy applies to the final head using the target SHA saved before integration; an
  orchestrated batch can verify once before reporting its units complete. → `CAP-HARN-agent-guidance` verification (MUST).
- This replaces `ADR-local-and-pull-request-integration` requirements for target-runtime readiness, content finish
  guards and receipt consistency before landing, readiness evidence equality/disclosure, and mandatory provider
  binding in the integration digest. Its Git identity, conflict, route, approval and unknown-outcome clauses remain.
- This replaces `ADR-delivery-approval-and-lifecycle-authority` merge-time readiness/report-engine revalidation
  requirements only. Direction acceptance and retained-base approval authority remain.
- This replaces `ADR-test-selection-and-ci` permission to leave non-batch integrated-head testing to a later batch
  or nightly run. Affected selection, full fallback and full nightly/release CI remain.

## 5. Consequences

Tool upgrades and ordinary development share one completion procedure. Integration loses provider-only CLI inputs
and repeated content checks. The target can fail checks temporarily, and the Host owns recovery and truthful final
reporting. There is no automatic assertion that external tests passed. Cleanup may precede final verification.

## 6. Confirmation

Development verifies the proposal's AC-01 through AC-09 with integration/CLI fixtures, command-call assertions,
proposal-acceptance regression tests and a Host-led walkthrough. Guidance review checks required final verification
and failure repair. `CAP-INT-mcp-services`, `CAP-DLV-delivery-workflows` and `CAP-HARN-agent-guidance` restate the clauses.
