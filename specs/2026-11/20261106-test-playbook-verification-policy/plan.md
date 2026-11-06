---
id: PLAN-test-playbook-verification-policy
spec: SPEC-test-playbook-verification-policy
---

# Technical Plan: SPEC-test-playbook-verification-policy

## 1. Constitution & Invariant Review

No architecture, dependency or ADR change is required. CAP-DLV-test-management and UC-assess-test-management own
this assessment behavior. The assessment is consultative: derive current facts from source, clarify only missing
user aims, then recommend an arrangement with explicit tradeoffs in the existing change-decision round. Preserve native checks and source-only bundle authoring. The prerequisite executor is
already present; this unit changes no runtime interface or feature edge.

## 2. Architecture Overview & Impact

Keep SKILL.md as the explicit-invocation router and owner of all shared constraints. Extend assessment.md with
actual command/coverage inventory and independent-group criteria. Add conditional execution.md for local/cloud
scheduling and optional generic executor usage. Extend pytest.md only to distinguish worker concurrency from
concurrent verification. Update the existing isolated deployment/self-containment test to include execution.md
and its conditional load. No new text-mirroring tests or consumer configuration are needed.

Reflect the recommendation, pending-result and evidence contracts in CAP-DLV-test-management and
UC-assess-test-management. Keep the concrete local merge procedure with the consumer's existing orchestrator.

## 6. Verification & Test Plan

Run the focused catalog test_bundles.py deployment/structure suite, catalog lint and type checks,
just test-affected --base 72dcf58181c421a2904cc6acde54d4f6a673788c with its full fallback, and
rules-ci against the same base. Run devkit sync after source edits, sync --check and generated check. Build the
catalog wheel offline and inspect packaged execution.md. Record exact commands, SHAs, results and limits in
verification.md. Use a labelled instruction walkthrough for all AC-01..12, including unclear/overlapping groups,
no E2E, non-Python/costly integration, local A-to-C pending/failure, cloud PR/nightly failures, existing required
postmerge checks, timeout/unknown/cleanup failure, optional devkit absence and insufficient tuning evidence. Include repo-known facts versus missing preferences, keeping the current
setup when favored, and a viable alternative without an obligatory option count.

The before/after baseline is the accepted head with this change disabled (b559c6df); record its missing guidance
by reading git show, then repeat the same walkthrough on the changed head. This is instruction reasoning, not
consumer execution or a performance measurement. Run separate medium code and reconcile reviewers with scoped
read-only payloads and boundary snapshots before the final change report.
