---
id: PROP-test-playbook-verification-policy
title: Align the Test Playbook with Verification Policy
summary: "Align maintenance/test-management with the delivered synchronous and asynchronous verification policy. Preserve consumer-native gates while updating assessment, execution evidence, recovery and completion guidance."
status: draft
created_at: 2026-11-06
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
depends_on:
  - PROP-async-e2e-verification
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/
    - packages/devkit-catalog/tests/
    - docs/capabilities/delivery/
  excludes:
    - scripts/
    - packages/devkit/src/devkit_agt/features/
    - .github/workflows/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-test-playbook-verification-policy] Align the Test Playbook with Verification Policy

## 1. Background & Hypothesis

`PROP-async-e2e-verification` proposes frequent synchronous unit/integration checks and selective asynchronous
E2E with fixed-commit isolation, durable evidence and Host-owned recovery. This follow-up updates the existing
`maintenance/test-management` playbook after that policy and its actual execution interface are delivered.

The source is `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/SKILL.md`.
Its `references/assessment.md` separates iteration aids from completion checks and preserves affected-selection
fallbacks. Its `references/pytest.md` checks worker/run resource ownership and requires comparable evidence
before promoting tuning changes. These principles remain useful under asynchronous execution.

The hypothesis is that aligning the playbook with the retained verification contract will let agents assess
blocking time and E2E necessity without weakening coverage or mistaking a background launch for verification.
This work changes reusable assessment guidance, not the verification policy or runner implementation itself.

### Scope and non-goals

- Update the source playbook and relevant references, with focused guidance verification and capability alignment.
- Preserve explicit invocation, user-selected scope, one decision round and consumer workflow routing.
- Preserve consumer tier names, resource checks, required gates and optional-skip semantics.
- Exclude changes to the prerequisite's execution engine, test selector or delivery policy.
- Exclude a mandatory devkit CLI, pytest dependency, subagent or concurrency setting for every consumer.
- Exclude CI/branch redesign, application defect repairs and broad test-suite optimization.
- Exclude editing managed copies or projected agent files directly.

## 2. Technical Spike Questions

- **Q1:** Which delivered commands and states does `PROP-async-e2e-verification` retain? If it chooses a
  repository script, how does the playbook assess that interface without presenting a hypothetical CLI as real?
- **Q2:** Which guidance belongs in the main playbook, generic assessment reference or pytest-specific reference
  so that a non-Python consumer keeps its native execution and completion contract?
- **Q3:** How should findings distinguish unnecessary E2E frequency, blocking scheduling, environment setup cost
  and actual test execution cost while preserving the coverage each tier provides?
- **Q4:** Which guidance checks or walkthroughs prove that pending, failed, interrupted and unknown executions
  never become successful completion evidence, and that skipped E2E has an explicit reason?

## 3. Proposed Design & Impact

### 3.1 Assessment updates

Inventory test tier, affected scope, execution cost, resource isolation and required timing as separate facts.
Keep measured cost distinct from test semantics: an integration label does not prove cheap execution and a
long duration does not authorize reclassification or deletion.

Assess branch checks, synchronous landed checks and asynchronous required checks separately. Preserve full
fallback within the consumer's declared selection contract. Identify cases needing E2E before merge because
other tiers do not establish the changed behavior. Record justified omissions separately from passed tests.

Read the consumer's adopted policy before proposing background execution. Preserve existing synchronous
requirements until a separately authorized policy change alters them. This playbook does not grant that change.

### 3.2 Execution evidence and recovery

Assess whether background runs record their exact SHA, selection baseline and scope, commands, environment,
state, exit code and log location. Check whether advancing main can change files, dependencies or resources
used by an active run. Reuse the prerequisite's vocabulary and actual interfaces.

Assess Host result checks, bounded concurrency, accumulated verification and failure-priority handling. A
successful launch is pending verification. A successful result at one SHA does not establish a later HEAD.
Unknown or interrupted execution remains visible; an unavailable required check remains `not_run` and unmet.

Keep the Host responsible for scheduling, failure repair routing and completion. An optional verification
subagent changes who collects or diagnoses evidence, not the evidence requirements. Do not expand git-operator
into test supervision implicitly.

### 3.3 Decision and reporting updates

Present proposed changes with exact source paths, coverage consequences, measured evidence and required
validation. Keep the existing one decision round. Route approved changes through the consumer's workflow;
background execution is not permission to bypass a required completion check.

Extend report guidance to distinguish reduced blocking time from reduced total test time or execution count.
Retain pending runs and the next result-collection action in any incomplete report. Preserve the distinction
between completion of the assessment and completion of the product verification it assessed.

### 3.4 Expected acceptance scenarios

- **AC-1:** Given the prerequisite's delivered interface, the playbook names only actual commands or clearly
  labelled examples and preserves the consumer's native checks.
- **AC-2:** Given asynchronous E2E, an assessment identifies its SHA, outstanding coverage and collection action;
  launch success or an earlier SHA's pass cannot satisfy later required verification.
- **AC-3:** Given unavailable required tests, failed E2E or unknown execution, the report retains the unmet gate
  and routes follow-up work without silently weakening the policy.
- **AC-4:** Given a non-Python consumer or an expensive integration test, guidance separates cost from tier and
  preserves native ownership, resources and commands.
- **AC-5:** Given a tuning recommendation, the report distinguishes measured blocking time, execution cost and
  coverage. Missing comparable evidence does not produce a speedup claim or default promotion.
- **AC-6:** Given no invocation or no decision on proposed edits, no assessment or configuration change is
  automatically initiated by merely retrieving the playbook.

## 4. Lifecycle & Retirement Criteria

Keep this draft dependent on `PROP-async-e2e-verification`. Start its implementation only after the prerequisite's
policy and execution contract have landed and passed required verification. Follow the prerequisite identity
through normal proposal handoff rather than removing the dependency to start early.

Before asset edits, load the authoring context and the maintenance bundle's source instructions. Inspect the
then-current playbook and narrow changes to its actual gaps. Verify document references and focused guidance
checks; label walkthroughs separately from executed runtime tests. Graduate through the normal proposal workflow.
