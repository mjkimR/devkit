---
id: MS-refactoring-and-prevention-rules
title: Refactoring activity for AI slop removal and prevention rules
summary: "Establishes a periodic refactoring activity on the shared job scheduler that prioritizes AI slop removal, proposes recurrence-prevention rules, and improves reuse through commonization and usage rules."
status: planned
created_at: 2026-10-18
depends_on: [MS-scheduled-jobs]
---

# [MS-refactoring-and-prevention-rules] Refactoring activity for AI slop removal and prevention rules

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3 (Delivery Workflow Orchestration), and §3.3 (Strict Layering) by establishing a refactoring activity whose first priority is removing AI slop: redundant code or prose, unnecessary abstractions, speculative compatibility paths, and boilerplate without a demonstrated purpose. The activity uses repository evidence and engineering judgment beyond the deterministic checks of hygiene (`CAP-GOV-evaluation-lifecycle`) and connects cleanup to prevention through `CAP-GOV-rule-authoring`.

## Exit condition

- The refactoring activity has a defined intake, scope, review, verification, and completion path and runs periodically through `MS-scheduled-jobs`. Successive scheduled occurrences are verified, with findings, changes, and pending proposals carried forward without duplicate work. Direct invocation uses the same activity path.
- AI slop removal is the first priority in candidate selection. Findings cite concrete locations and explain the unnecessary complexity or duplication; changes preserve agreed behavior and pass relevant verification.
- Each identified AI slop pattern receives a recurrence-prevention rule proposal alongside its cleanup recommendation. The proposal states the detectable condition, affected scope, examples, and false-positive limits. When a deterministic rule is unsuitable, the record explains why and proposes review guidance instead.
- Commonization consolidates demonstrated repeated behavior into a shared implementation with a usable interface and updated callers. Each commonization result includes a rule proposal that directs callers to the shared implementation and detects renewed duplication or misuse where deterministically checkable.
- Rule proposals have a recorded disposition and follow-up destination when deferred. Adopted rules include positive and negative examples and run through the existing governance lifecycle, including hygiene-first rollout when existing debt requires it.
- Completion evidence links findings, code changes, verification, and rule proposals so reporting can distinguish cleanup performed from prevention adopted or still pending.

## Non-goals

- **Scope Excluded**: Cosmetic churn without an evidenced problem, speculative commonization, behavior-changing feature work disguised as refactoring, and automatic adoption of every proposed rule.
