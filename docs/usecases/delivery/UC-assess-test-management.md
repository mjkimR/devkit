---
id: UC-assess-test-management
title: Assess a selected test suite
summary: "An AI coding agent combines selected-suite evidence and user aims into a concrete test recommendation, then routes decided changes without weakening native verification."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Human approver]
status: active
capabilities:
  - CAP-DLV-test-management
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/SKILL.md
created_at: 2026-11-05
---

# [UC-assess-test-management] Assess a selected test suite

## 1. Goal

- **Goal**: recommend a test arrangement grounded in repository evidence and user priorities, then decide bounded follow-up work.
- **Scope**: the opt-in maintenance playbook.
- **Trigger**: the human explicitly invokes or confirms a selected-suite consultation.
- **Preconditions**: the agent can read the consumer repository.

## 2. Main Success Scenario

1. The agent records selected roots and reads current code, tests, fixtures, scripts and CI to establish native
   verification facts (CAP-DLV-test-management).
2. The agent clarifies only missing goals, preferences and tradeoffs relevant to the recommendation
   (CAP-DLV-test-management).
3. The agent inspects collection and resource prerequisites before executing safe bounded checks
   (CAP-DLV-test-management).
4. The agent assesses coverage, cost, resource isolation, independent groups and applicable runner evidence
   against native requirements (CAP-DLV-test-management).
5. The agent synthesizes a concrete recommendation with prioritized aims, reasons, meaningful alternatives and
   coverage, latency, resource and failure-detection tradeoffs (CAP-DLV-test-management).
6. The agent presents the recommendation and exact candidate scope/validation for the single change-decision
   round (CAP-DLV-test-management).
7. The human decides dispositions and the agent routes approved work through the native workflow
   (CAP-DLV-test-management).
8. The agent reports actual results, retained settings, destinations and outstanding verification/collection
   (CAP-DLV-test-management).

## 3. Extensions

- **1a.** Selection or retrieval without invocation: the agent performs no assessment; the use case does not start.
- **2a.** Repository already answers a question: the agent uses that evidence instead of asking the human; resumes at step 3.
- **2b.** Relevant preferences remain missing: the agent bundles concise questions without a mode choice or edit
  approval; resumes at step 3 when enough context exists. Unknown resource safety still holds affected execution.
- **3a.** Required prerequisite unavailable or unknown: leave the affected check not_run with an unmet gate;
  continue assessment of safe available evidence at step 4.
- **4a.** Groups unseparated, unclear or overlapping: keep existing required commands synchronous and present any
  supported restructuring as a candidate; resumes at step 5 without fabricating E2E or empty coverage.
- **4b.** Comparable tuning evidence incomplete or mismatched: retain settings and claim no speedup/default
  promotion; resumes at step 5.
- **5a.** Evidence favors current setup: recommend keep with reasons and remaining constraints; resumes at step 6.
- **5b.** Active local Host with independent groups: recommend bounded overlap with pending exact-revision
  coverage, Host collection and repair ownership; resumes at step 6.
- **5c.** Cloud PR without active Host: explain required PR failure blocks/rework, accepted nightly detection of
  broken combined main and existing repair routing; preserve consumer-required final checks; resumes at step 6.
- **6a.** Unattended or unanswered change decision: report pending candidates with nothing applied; the assessment ends.
- **8a.** Run pending/unknown, waiter interrupted or cleanup failed: retain original outcome, tested revision,
  outstanding coverage and next collection/repair action; assessment can end with gaps visible, native delivery
  remains subject to its required checks.

## 4. Postconditions

- **Success guarantee**: the recommendation explains evidence, aims and tradeoffs; every approved candidate has
  a native-workflow destination and missing required checks remain visible.
- **Minimal guarantee**: invocation/preference answers infer no configuration edits, product-data modifications
  or integration-policy changes; no launch, ancestor result or cleanup success is relabelled a required test pass.

## 5. Acceptance Criteria (Given / When / Then)

### Evidence and user aims
- **Covers**: main success scenario, 2a, 2b, 5a
- **Given** readable repository facts and a missing responsiveness or delayed-detection preference.
- **When** the agent develops its recommendation.
- **Then** it reads current facts first, asks only relevant missing aims, and explains a concrete arrangement with
  reasons/tradeoffs and a viable alternative when meaningful; current settings remain when evidence favors them.

### Native groups and resources
- **Covers**: 3a, 4a
- **Given** an unseparated non-Python command that includes browser coverage or a costly integration suite.
- **When** the agent assesses coverage and prerequisites.
- **Then** names establish neither cost nor independent groups; required commands stay synchronous until a complete
  supported split exists, and unknown resource safety leaves the affected execution unrun.

### Inconclusive comparison
- **Covers**: 4b
- **Given** a parallel candidate with different identities/skips or only reduced Host waiting.
- **When** the agent compares evidence.
- **Then** it retains settings and distinguishes blocking from duration, run count, setup and resource cost without
  a speedup claim or default promotion.

### Local pending verification
- **Covers**: 5b, 8a
- **Given** a run at A while main advances to C, or an interrupted observer/failed cleanup.
- **When** the agent reports verification.
- **Then** tested A and the outstanding interval remain explicit with collection/repair ownership; observation and
  cleanup do not alter the original native outcome or establish C's required pass.

### Cloud accepted risk and required checks
- **Covers**: 5c
- **Given** passing PRs can break combined main and nightly repair is the chosen detection arrangement.
- **When** the agent explains the example.
- **Then** it preserves failed-required-PR merge blocks, describes later repair and adds no immediate-postmerge or
  latest-base prerequisite; any change to an existing required final check uses the single change-decision round.

### Invocation and change decision
- **Covers**: 1a, 6a
- **Given** retrieval without invocation or proposed edits without human decisions.
- **When** the agent reaches the relevant boundary.
- **Then** no assessment starts from retrieval and no edits follow unanswered candidates or preference answers;
  approved changes retain native routing and integration approvals.
