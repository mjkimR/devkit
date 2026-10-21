---
id: PLAN-integration-rewritten-merge
spec: SPEC-integration-rewritten-merge
---

# Technical Plan: `SPEC-integration-rewritten-merge`

## 1. Constitution & Invariant Review

None. Keep layering and existing finish validation intact. The approved local integration contract in `CAP-INT-mcp-services` remains bounded by source identity and exact checked content.

## 2. Architecture Overview & Impact

`integration/service.py` observes the target immediately after `fast_forward` returns, including synchronous post-merge hooks. Compare tree and ordered parents against the built result before recording a replacement. No dependency or schema changes.

## 3. Component & Interface Design

Restrict replacement acceptance to no-ff merge results. ff-only must still contain the exact approved source. Preserve the built SHA on an invalid replacement, fail closed, and leave cleanup pending. Store the validated observed SHA in existing result state; subsequent validation and resume retain strict ancestry semantics.

## 4. Failure Modes

A hook can mutate content, parents, source or policy. Tree/parent checks reject structural replacements; existing post-landing validation rejects source and policy mutations. A later unrelated rewrite remains stale. Successful metadata replacement plus interrupted deletion resumes from the recorded identity.

## 5. Verification

Retain an executable post-merge hook regression: Red before production edits, Green afterward. Test content/parent/source/policy attacks, ordinary paths, ff-only and resumed cleanup. Run just lint-check agt, just check agt, just test-affected (including full fallback), cumulative governance, independent code review and reconciliation verification. Test fixtures use isolated temporary repositories outside checkouts.
