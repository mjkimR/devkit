---
id: SPEC-test-playbook-verification-policy
title: Align the Test Playbook with Verification Policy
summary: "Assess independent test groups and asynchronous verification without weakening consumer checks; provide optional local and cloud scheduling examples through the existing decision round."
status: planned
created: 2026-11-06
depends_on:
  - SPEC-async-e2e-verification
related_capabilities: [CAP-DLV-test-management]
related_usecases: [UC-assess-test-management]
workflow: sdd-spec-feature
---

# [SPEC-test-playbook-verification-policy] Align the Test Playbook with Verification Policy

## 1. Problem Statement & Motivation

The test-management playbook preserves coverage and safe resources but lacks guidance for independently runnable
verification and asynchronous result collection. The prerequisite SPEC-async-e2e-verification is delivered on the
current base. This change teaches assessment and recommendation; it does not run an assessment on devkit.

## 2. User Stories

- **US-1**: As an AI coding agent, I want to assess actual consumer test commands and coverage so that asynchronous
  scheduling preserves the consumer's required verification.
- **US-2**: As a consumer maintainer, I want local and cloud examples with explicit evidence and repair ownership
  so that I can decide scoped changes in the existing decision round.

## 3. Non-Goals

1. **Scope Excluded**: Executor, test selector, scripts, CI, application runtime or local-orchestrator changes.
2. **Scope Excluded**: Policy selectors, test-profile maps, new feature edges or global completion requirements.
3. **Scope Excluded**: Running real consumer CI/services, tuning actual suites, mandatory pytest/devkit/verifier use
   or implicitly applying consumer configuration.
4. **Scope Excluded**: Changes to managed/projected assets, bundle selection or architecture metadata.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Native commands without configuration indirection
- **Given** the delivered fixed-commit executor and a consumer with native verification commands.
- **When** the playbook recommends execution.
- **Then** it uses actual commands or labelled generic examples with the consumer invocation prefix, preserves native checks and requires no test-profile map or local/cloud selector.

### [AC-02] Pending coverage and exact revision
- **Given** an asynchronous run at SHA A and later descendant C.
- **When** the agent reports verification.
- **Then** it records tested SHA, native command, selection baseline and outstanding coverage with a collection action; launch success or A passing cannot establish required C coverage.

### [AC-03] Failures and required gaps
- **Given** a failed required check, unavailable required prerequisite or unknown execution.
- **When** the agent assesses completion.
- **Then** it preserves failed, pending or not_run evidence and unmet gates, distinguishes optional omissions and routes proposed follow-up through the consumer workflow without weakening required coverage.

### [AC-04] Native ownership and independent cost
- **Given** a non-Python suite, costly integration tests or cheap browser tests.
- **When** the agent inventories tests.
- **Then** it inspects documents, scripts, runner configuration and CI triggers for coverage, exclusions, overlap, commands, cost and isolation separately; tier names and directories establish neither E2E existence nor cost or independent execution.

### [AC-05] Comparable tuning evidence
- **Given** a proposed runner or scheduling optimization.
- **When** the agent assesses its benefit.
- **Then** it distinguishes Host blocking, run count, native execution and setup/resource costs, retains pytest same-revision/selection/node-ID/outcome/skip/cleanup comparisons, and claims no speedup or default promotion without comparable measurements.

### [AC-06] Invocation and one decision round
- **Given** playbook retrieval without invocation or proposed edits without a decision.
- **When** the agent reaches the relevant boundary.
- **Then** retrieval starts no assessment, invocation authorizes only assessment, unanswered candidates stay pending, and approved exact-scope changes retain native workflow and integration approvals through one decision round.

### [AC-07] Cloud example accepts later detection
- **Given** a cloud PR workflow with required PR CI including E2E and no active Host.
- **When** the playbook gives an operating example.
- **Then** it describes worker checks, failed-CI rework, automatic merge on pass and nightly detection of a potentially broken combined main, without requiring latest-base prospective testing, base refresh, merge queues or immediate postmerge CI.

### [AC-08] Existing requirements and repair
- **Given** required PR CI fails, nightly finds broken combined main, or the consumer requires final integrated-result checks.
- **When** the agent recommends cloud scheduling.
- **Then** failed required PR CI blocks merge, nightly failures enter the existing consumer repair mechanism without an always-on Host assumption, intentionally absent checks are distinguished from unavailable required checks, and existing final checks remain unless changed through the same decision round.

### [AC-09] Conditional self-contained examples
- **Given** async execution or scheduling recommendations are in scope.
- **When** the main playbook routes the assessment.
- **Then** it conditionally loads a one-level execution reference with optional native-compatible runners and generic devkit examples, keeps every shared constraint in SKILL.md, and assumes neither spec/harness installation nor authoring-repository documents or a policy selector.

### [AC-10] Observation and cleanup are separate
- **Given** background waiting, timeout, interruption, cancellation or requested cleanup.
- **When** the agent recommends optional devkit execution.
- **Then** it explains tool-dependent result delivery or later collection, pending/unknown never passing, observation ending without cancellation, confirmed managed stop retaining checkout, guarded inactive cleanup, retained original outcome/logs and default artifact retention for diagnosis; optional verifiers and Git-only operators retain their boundaries.

### [AC-11] Independent groups before async separation
- **Given** an unseparated, unclear, overlapping, no-E2E or explicitly separated suite.
- **When** the agent chooses recommendations.
- **Then** it preserves complete required coverage, keeps existing required checks synchronous when no independent subset is established, preserves frequent existing unit/integration iteration and necessary selective E2E plus native checks/fallbacks, and routes any restructuring through the same decision round without fabricating E2E or empty coverage.

## 5. Implementation Assumptions

The direct acceptance settles the direction and skips Planning under user authority. The prerequisite interface
is present in this worktree; no premise breaks the agreed scope. Maintenance is unselected, so deployment tests
use isolated consumer fixtures and sync must leave selected assets unchanged. Execution examples are consumer
recommendations; concrete merge scheduling belongs to that consumer's orchestrator.

Keep scope/resource safety, explicit invocation, one decision round and existing required checks in the main file.
Use assessment.md for native inventory, execution.md for conditional scheduling and pytest.md for optional runner
comparison. This keeps bundle references one level deep and avoids duplicating a delivery implementation.
