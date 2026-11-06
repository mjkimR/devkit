---
id: PROP-test-playbook-verification-policy
title: Align the Test Playbook with Verification Policy
summary: "Extend maintenance/test-management with asynchronous test assessment and recommended local/cloud operating examples. Preserve native project checks and use direct commands without a devkit delivery-policy selector or test-profile map."
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

`PROP-async-e2e-verification` provides fixed-commit asynchronous execution, persistent run evidence, direct native
command passing and local-orch skill integration. This follow-up teaches the existing test-management playbook
how to assess that capability and recommend practical test arrangements.

The source is `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/SKILL.md`.
Its `references/assessment.md` preserves coverage, resources and completion checks. Its `references/pytest.md`
requires comparable evidence before promoting tuning changes. Retain those principles.

Devkit itself uses local-orchestrated development. A client repository can have different CI and delivery habits.
Local/cloud examples help explain scheduling tradeoffs; they are recommendations, not product policy alternatives
that a consumer must select or register. The executor needs neither that distinction nor a configuration setting.

### Scope and non-goals

- Update the source playbook and relevant references, with focused guidance checks and capability alignment.
- Preserve explicit invocation, user-selected assessment scope, one decision round and consumer workflow routing.
- Preserve native tier names, resource prerequisites, required checks and documented optional skips.
- Include recommended local and cloud arrangements, including accepted nightly detection of broken combinations.
- Exclude a local/cloud policy selector, route registry, new global completion contract and test-profile config.
- Exclude changes to the prerequisite executor, test selector or local-orch implementation.
- Exclude mandatory devkit commands, pytest, a verifier subagent or a concurrency setting for every consumer.
- Exclude client CI/branch implementation, application defect repairs and broad test-suite optimization.
- Exclude editing managed copies or projected agent files directly.

## 2. Technical Spike Questions

- **Q1:** Which delivered execution commands and states does the prerequisite retain? Keep native argv passing
  and existing setup conventions; do not invent profile mappings or hypothetical commands.
- **Q2:** Which recommendations belong in the main playbook, generic assessment reference or pytest reference
  so that non-Python consumers retain native commands and ownership?
- **Q3:** How should findings distinguish E2E frequency, blocked Host time, environment preparation and actual
  command cost without treating an integration label as a cheap-test guarantee?
- **Q4:** Which focused checks and walkthroughs show that launch, pending, interrupted and unknown execution
  never become passing evidence, and omitted E2E retains its reason?
- **Q5:** How should local/cloud examples explain their tradeoffs without adding policy selection or imposing
  a missing postmerge check on a consumer that accepts nightly detection?

## 3. Proposed Design & Impact

### 3.1 Assessment and recommendations

Inventory test semantics, affected scope, measured cost, resource isolation and execution timing separately.
Read the actual commands, CI triggers and required checks of the repository being assessed. Do not infer its
requirements from devkit's own local-orch habits or from where its worker runs.

Recommend frequent unit/integration checks during worktree/PR iteration, with E2E when needed to establish the
changed behavior. Preserve required lint, types, rules, frontend and other native checks. Use conservative full
fallback within the repository's selection contract. Explain E2E omissions separately from passing results.

Present the following as operating examples, not mandatory modes or a configuration decision:

| Example | Suggested arrangement | Tradeoff to explain |
| :--- | :--- | :--- |
| Active local Host | Worker unit/integration and selective E2E; merge; synchronous unit/integration; selective E2E asynchronously while independent work proceeds | Host collects required results and prioritizes repair when a failure is observed |
| Cloud PR without an active Host | Worker unit/integration and selective E2E; required PR CI including E2E; rework on failure; automatic merge on pass; nightly later | No immediate postmerge CI; passing PRs can break main in combination until nightly detection and repair |

The cloud example accepts that broken combinations reach main. Do not add latest-base prospective merge testing,
forced base refresh, a merge queue or immediate postmerge CI as prerequisites for that recommendation. Explain
nightly timing and how failures reach the repository's repair process, without prescribing an adapter or recipient
schema. A later nightly failure is follow-up repair, not proof that the merged combination had passed earlier.

Assess actual project requirements when reporting gaps. An intentionally absent check is not an unavailable
required check. Failed required PR CI still blocks merge. If a recommendation would change an existing project
requirement, route that change through the normal decision round; the playbook does not silently apply it.

### 3.2 Execution evidence and local use

Assess exact tested SHA, native command, selection baseline where applicable, environment, state, exit code and
logs. Confirm that advancing main cannot change files/dependencies used by an active run. Reuse the delivered
interfaces; do not add test-profile mappings or local/cloud flags to the executor.

For local scheduling recommendations, explain direct Host launch and result collection, bounded batches,
outstanding changes and repair priority. Start with one E2E run when resource contention warrants it; keep this
as advice rather than a mandatory executor limit. The local-orch skill owns the concrete workflow procedure,
so the playbook links it rather than duplicating its full instructions.

A verification subagent can help diagnose results but is not required for asynchrony or process persistence.
Git-operator retains Git lifecycle duties. Without an active Host, discuss existing CI/rework and nightly repair
arrangements rather than assuming a local agent will observe every failure.

### 3.3 Decision and reporting

Present proposed changes with source evidence, exact paths, coverage consequences and validation. Keep the
existing one decision round for proposed edits, not an extra local/cloud policy-selection round. Route approved
changes through the consumer workflow and keep unanswered candidates pending.

Separate reduced blocking from reduced test execution time or run count. Report preparation cost and resource
contention where measured; missing comparable evidence supports no speedup claim or default tuning promotion.
Keep pending runs, coverage gaps and next collection actions visible. Distinguish assessment completion from
actual test evidence and the repository's own delivery requirements. No executor launch establishes a test pass.

### 3.4 Expected acceptance scenarios

- **AC-1:** Given the delivered prerequisite, the playbook uses actual commands or labelled examples and preserves
  native checks. Direct command passing requires no test-profile map or local/cloud configuration.
- **AC-2:** Given asynchronous E2E, assessment identifies its SHA, outstanding coverage and collection action;
  launch success and an ancestor's pass cannot satisfy later required verification.
- **AC-3:** Given a missing required check, failed test or unknown execution, the report preserves the gap and
  routes proposed follow-up through the consumer workflow without weakening coverage.
- **AC-4:** Given non-Python tests or an expensive integration suite, recommendations preserve native ownership,
  commands and resources, and separate measured cost from tier semantics.
- **AC-5:** Given a tuning recommendation, the report distinguishes blocked time, execution cost and coverage;
  missing comparable results produce no speedup claim or default promotion.
- **AC-6:** Given no invocation or no decision on proposed edits, no assessment or configuration change starts
  automatically from retrieving the playbook.
- **AC-7:** Given the cloud example's accepted nightly risk, the recommendation requires no latest-base merged
  result, merge queue or immediate postmerge CI. Explain combination failures and later repair.
- **AC-8:** Given required PR CI failure, preserve the existing merge block and rework arrangement; given nightly
  failure, discuss follow-up repair without inventing a continuously available Host.
- **AC-9:** Given devkit itself, assess its local-orch usage; given a client, inspect its actual setup instead of
  requiring a declared policy mode. Examples remain recommendations and introduce no selector or extra decision round.

## 4. Lifecycle & Retirement Criteria

Keep `depends_on: PROP-async-e2e-verification`. Start implementation after the prerequisite execution contract
and local usage land and pass required verification. Follow its identity through normal handoff rather than
removing the dependency to start early.

Before asset edits, load authoring context and the maintenance bundle's source instructions. Inspect the
then-current playbook and actual interfaces. Verify references and focused guidance checks; label recommendation
walkthroughs separately from runtime tests. Graduate through the normal proposal workflow.
