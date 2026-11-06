---
id: CAP-DLV-test-management
title: Test-management assessment
summary: "An explicitly invoked test consultation combines repository evidence and user aims to recommend coverage, resources, runner settings and scheduling while preserving native checks and one change-decision round."
area: delivery
status: active
usecases:
  - UC-assess-test-management
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/SKILL.md
created_at: 2026-11-05
---

# [CAP-DLV-test-management] Test-management assessment

## 1. Summary

The maintenance playbook consults on selected suites using actual consumer code/tests, fixtures, scripts, runner
configuration and CI. It clarifies missing user aims and recommends an arrangement with coverage, latency,
resource and failure-detection tradeoffs. Conditional assessment, pytest and execution references support that
recommendation without standardizing tiers, requiring devkit or adding a policy selector.
SPEC-test-playbook-verification-policy retains the instruction walkthrough; executed catalog tests prove asset
structure and isolated deployment, not consumer behavior or performance.

## 2. Scope & Boundary

- **In-Scope**: bounded repository assessment, missing-preference clarification, prioritized recommendations,
  resource inspection, optional comparable runner evidence, independent-group assessment, local/cloud scheduling
  examples, one change-decision round and native-workflow routing.
- **Out-of-Scope**: application repair and consumer CI/branch implementation (separate consumer work),
  performance-only passes (CAP-DLV-performance-pass), integration authority (CAP-DLV-delivery-workflows),
  mandatory history (CAP-DLV-maintenance-history), publication (separate authority), executor implementation
  (CAP-HARN-isolated-execution), global completion policy and configuration/profile selectors.

## 3. Business Rules & Policies

1. **Deployment**: WHEN testing or all is selected, the bundle MUST deploy the complete directory-form playbook
   while existing individual presets retain their asset sets. Tests: `packages/devkit-catalog/tests/integration/bundles/test_bundles.py`.
2. **Entry**: WHEN the user explicitly invokes or confirms the playbook, the agent MUST treat that authority as
   assessment only. Retrieval and selection start no assessment; proposed edits need the decision below.
3. **Repository evidence**: WHEN establishing current facts, the agent MUST read actual code, tests, fixtures,
   scripts, runner configuration and CI before asking for facts available from the repository.
4. **User aims**: WHERE relevant aims remain missing, the agent SHOULD ask concise bundled questions about
   responsiveness, resources, delayed-detection tolerance and observer/repair availability needed for its recommendation.
   Preference clarification is neither edit consent, integration approval nor a policy-mode choice.
5. **Recommendation**: WHEN evidence and aims are established, the agent MUST synthesize a concrete recommended
   arrangement with prioritized aims, reasons, coverage/latency/resource/failure-detection tradeoffs, meaningful
   alternatives and remaining constraints. Evidence favoring the current setup supports a keep recommendation.
6. **Resource safety**: BEFORE execution including collection, the agent MUST inspect hooks and prerequisites;
   an unresolved resource boundary leaves the affected command unexecuted. Keep disposable data/services and
   credential-free evidence; never infer permission for paid providers or product-data modification.
7. **Inventory**: WHEN assessing tests, the agent MUST record coverage, exclusions, overlap, commands/triggers,
   required checks, measured cost and resource isolation separately. Directory names and tier labels establish
   neither E2E existence, cost nor independent execution; non-Python commands and costly integration retain ownership.
8. **Independent groups**: IF complete required coverage cannot be mapped to supported independently runnable
   groups, THEN the agent MUST keep existing required commands synchronous. Proposed restructuring uses the same
   change-decision round; the assessment fabricates neither E2E nor empty coverage.
9. **Native verification**: WHEN recommending iteration or scheduling, the agent MUST preserve native required
   checks, affected-selection fallback and final integrated-result checks. Frequent existing unit/integration
   iteration and necessary selective E2E retain lint/types/rules/frontend checks without a blanket full-E2E policy.
10. **Incomplete evidence**: IF a required prerequisite is unavailable or execution is failed, pending or unknown,
    THEN the report MUST preserve that state and unmet coverage. Optional skips name coverage they do not establish;
    intentionally absent checks differ from unavailable required checks.
11. **Exact revision**: WHEN reporting asynchronous verification, the agent MUST retain tested SHA, command,
    selection baseline where applicable, run ID, outstanding coverage and collection action. Launch success or an
    ancestor's pass establishes no required descendant coverage.
12. **Local example**: WHERE an active Host uses independently runnable groups, the recommendation SHOULD overlap
    selected asynchronous E2E after light required synchronous landed checks within existing completion rules.
    The direct Host owns bounded batches, collection, outstanding intervals and repair priority on failed/unknown
    results; an optional verifier assists and Git operators remain restricted to Git lifecycle work.
13. **Cloud example**: WHERE PR CI and nightly repair operate without an active Host, the recommendation SHOULD
    explain required PR CI including existing required E2E coverage, failed-CI rework, automatic merge under existing authority and accepted
    nightly detection of potentially broken combined main. The example adds no latest-base prospective testing,
    forced refresh, merge queue, immediate postmerge CI or always-on Host prerequisite. Combined synchronous/CI
    commands and suites without E2E can still receive consultation and scheduling recommendations.
14. **Existing requirements**: WHEN a scheduling recommendation would alter an existing required check, the agent
    MUST route that requirement change through the same decision round and native approvals. The cloud example's
    intentionally absent immediate check does not silently remove consumer-required integrated-result checks.
15. **Repair routing**: WHEN recommending nightly detection, the agent MUST identify the consumer's existing
    repair mechanism or report its absence as a proposed candidate. No adapter/recipient schema is required.
16. **Observation**: WHERE optional devkit execution is used, the agent MUST distinguish native outcome, observer
    completion and cleanup result. Timeout/interruption ends observation only; confirmed managed cancellation
    retains the checkout; guarded cleanup requires an eligible inactive environment and retains original
    outcomes/logs. Diagnostic artifacts favor retaining the checkout by default.
17. **Result delivery**: WHEN recommending background waiting, the agent MUST name tool completion delivery or a
    later collection action instead of promising push notification. One outstanding run is contention advice,
    not an executor limit; native-compatible alternatives remain valid without harness/spec installation.
18. **Comparable evidence**: WHERE tuning is proposed, the agent MUST require comparable revision/selection,
    identities, outcomes/skips, isolation and cleanup before default promotion. Report Host blocking separately
    from run count, native duration, setup and resource contention; incomplete evidence supports no speedup claim.
19. **Decision**: WHEN presenting proposed edits, the agent MUST combine recommendation, reasons, meaningful
    alternatives, exact scope and validation in the existing single change-decision round. An unattended assessment
    stops with no edits; unanswered candidates stay pending and approved work retains native integration approvals.
20. **Evidence limits**: WHEN reporting results, the agent MUST distinguish executed tests from examples,
    instruction walkthroughs and performance evidence. Keep raw logs outside versioned reports and identify
    retained evidence locations. Walkthrough: SPEC-test-playbook-verification-policy.

## 4. Interfaces & Data Contracts

Select with `devkit add maintenance:testing` or existing default `devkit add maintenance` (all).
Retrieve with `devkit playbook get maintenance/test-management`; explicit user invocation/confirmation remains the
entry condition (CAP-DIST-context-and-playbooks). The package contains `SKILL.md`, `references/assessment.md`,
`references/pytest.md` and `references/execution.md`. The main router loads execution only for asynchronous
execution or scheduling recommendations and pytest only for that runner's configuration/concurrency assessment.
Every reference is one level deep and bundle-contained. Catalog integration tests check these structural facts.

The optional fixed-commit execution example uses `devkit exec start --ref <full-commit-sha> -- <native argv>` and
background `devkit exec wait <run-id> --clean --format json` with the consumer's invocation prefix. These are
labelled generic examples; CAP-HARN-isolated-execution owns runtime semantics. Consumers can use native-compatible
runners instead. Concrete merge scheduling remains consumer/orchestrator-owned.

The local report records inspected revision/dirty paths, roots/goal, prioritized aims, repository evidence,
native checks/triggers/coverage, recommended arrangement/reasons/alternatives, resource constraints, exact command
outcomes and pending collection, decisions, candidate paths/validation and routed destinations. Outcome is
`stopped at decision round`, `routed`, `partially routed` or `kept`. Assessment completion is separate from actual
test passes and native delivery completion. Publication and history capture require their own authority.
