---
id: PLAN-post-merge-verification
spec: SPEC-post-merge-verification
---

# Technical plan: post-merge verification

## 1. Constitution & Invariant Review

`ADR-post-merge-verification` authorizes the changed verification lifecycle and partially supersedes the named readiness and deferred-testing clauses. Retain Git identity, source pinning, target advance, policy authority, platform PR checks and scoped cleanup. No new feature edge is permitted.

## 2. Architecture Overview & Impact

Integration prepares and executes Git effects without interpreting branch content. The Host checks branch workflows before approval and synchronizes the landed environment before final checks. Proposal acceptance retains its eligibility preview but yields before handoff. No new runtime installer or persisted verification state is introduced.

## 3. Component & Interface Design

- Integration contracts and CLI remove task inputs and readiness from generic merge requests; acceptance keeps only the internal types it needs. Both result serializers and text expose `verification` derived from confirmed landing.
- Integration service and PR route retain policy, digest, Git/concurrency and cleanup validation while removing content checks. PR bodies and merge messages derive from the explicit source branch.
- Policy accepts absent integration configuration and ignores legacy provider values; unknown keys still fail with corrective diagnostics.
- Proposal acceptance validates direction before the acceptance commit, preserves exact commit and scope authority, and returns a continuation with mode, effort and authorized scope. The fresh handoff command runs only after Host final verification.
- Spec bundle instructions and project references specify branch checks, approved merge/cleanup, fresh setup, regeneration, final checks, target repair and completion. Batches retain the premerge target SHA.

```text
integration prepare <branch> [--route local|pull-request]
integration integrate <branch> [--route local|pull-request] [--expected-digest <digest>]
verification = pending | not_started
```

## 5. Error Handling & Edge Cases

Unknown PR outcomes prohibit cleanup and merge replay. Confirmed landing remains pending when cleanup or final checks fail. Source-tip changes and disallowed target changes invalidate scope. Current base policy cannot be self-authorized by source changes. Missing runtime setup or imports leave verification unfinished.

## 6. Verification & Test Plan

Use integration CLI/service/PR regression tests for AC-02/05/06/09 and proposal composition tests for AC-07. Add spies proving zero content-check calls and unsupported-runtime fixtures. Guidance tests and a recorded walkthrough cover AC-01/03/04/08. Run relevant lint and Pyright, `just test-affected --base main` with its full fallback, document/rule checks and sync check. Host final verification uses batch-start `9c8c6eecc4febefa699408daa105f814b144d649`, never main against itself. Review and reconcile each use independent high-effort review loops.
