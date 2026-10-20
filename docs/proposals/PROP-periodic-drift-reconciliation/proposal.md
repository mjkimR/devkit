---
id: PROP-periodic-drift-reconciliation
title: Spec-code drift reconciliation maintenance playbook
summary: "Defines a manually invocable maintenance playbook that checks Living Spec, code, and guidance consistency using existing commands and evidence review, then resolves findings through user decisions: the Tier 2 reconciliation of ADR-dual-source-of-truth-and-periodic-reconciliation."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-14
milestone: MS-drift-reconciliation
target_area: capabilities/delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
    - capabilities/distribution/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
workflow_hash: sha256:90918c632715461d07f99f683b8381bdbe6381ad6689a7575a72c002c18c1399
---

# [PROP-periodic-drift-reconciliation] Spec-code drift reconciliation maintenance playbook

- **Parent decision**: `ADR-dual-source-of-truth-and-periodic-reconciliation`

## 1. Background & Hypothesis

### 1.1 Problem

- Per `ADR-dual-source-of-truth-and-periodic-reconciliation`, spec and code are complementary ledgers at different
  levels of abstraction.
- Even when `spec-sync` carries the core delta of each work unit, the interfaces, flags and terms the spec
  (`docs/capabilities/`, `docs/stories/`) names drift slightly from the code over time.
- Apart from reading by eye, nothing detects this, so drift is noticed only after it has piled up, and the large
  cleanup that follows is costly and tiring.

### 1.2 Hypothesis

- A manually invocable **maintenance playbook** combining existing commands and evidence-based review can expose
  accumulated drift without requiring a new detector or scheduler.
- A user-driven reconciliation sweep keeps spec and code aligned by deciding whether each finding calls for a
  documentation update, a code fix, or a documented deferral. Neither ledger is automatically authoritative.

## 2. Planning Questions

- **Q1. Scope and evidence.** Which documented commands, options, interfaces, terms, and behaviors should a bounded
  sweep examine, and which existing checks and source inspection support each finding?
- **Q2. Finding quality.** How should the playbook distinguish deterministic failures from suspected semantic drift,
  limit noise, and present enough evidence for a user decision? Section 4 records a rejected detection candidate.
- **Q3. Procedure and verification.** What inputs, review steps, disposition records, and verification make the
  playbook reusable, and how should its manual run demonstrate the complete reconciliation path? Catalog placement
  is the `maintenance` bundle described in section 3.4.

## 3. Proposed Design & Impact

### 3.1 Playbook Intake and Evidence Review

- **Invocation**: explicit manual invocation with a selected area or contract scope and repository revision.
  Scheduler integration and trigger design are outside this proposal.
- **Existing tools**: use document lookup, references, declared entrypoints, and governance checks where relevant
  (`CAP-DOCS-document-lookup`, `CAP-TRACE-code-entrypoints`, `CAP-GOV-evaluation-lifecycle`), then inspect the
  implementation and consumer-facing guidance for semantic consistency.
- **Review targets**:
  - Documented CLI commands and options, main interfaces, terminology, and behavior against implementation.
  - File paths and module references, reusing existing checks rather than duplicating them.
  - Consumer-facing guides and instructions that restate the reviewed contract.
- **Evidence limits**: changed paths or document age may help select review scope but do not establish drift.
  Entrypoint-based stale-document hints remain rejected under section 4.
- **Output**: findings cite both sides of the mismatch, distinguish deterministic failures from agent assessments,
  and explain the suspected discrepancy. Detailed evidence belongs in a report artifact; command output follows
  `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol`.

### 3.2 User-Driven Reconciliation

For each finding, obtain an explicit disposition:

1. **Update the spec or guidance**: the implemented behavior is intended; align the documentation with it.
2. **Fix the code**: the documented intent remains correct; handle the regression through the applicable delivery path.
3. **Defer or waive**: record the reason and a follow-up destination or the rationale for an intentional gap.

Apply agreed changes through the applicable delivery and approval boundaries, verify the affected behavior and
references, and record detected, resolved, and deferred findings separately. Repeated sweeps reuse existing feedback
or proposals instead of duplicating follow-ups.

### 3.3 Delivery and Verification

- Deliver a playbook with defined inputs, scope selection, evidence collection, user decisions, cleanup, verification,
  and completion evidence; demonstrate it with a manual run that records findings and their dispositions.
- Complement per-work-unit `spec-sync`; broad structural cleanup belongs to the review/refactoring playbook unless
  needed to resolve an agreed drift finding.
- A dedicated detection command, a new standalone skill, automated scheduling, and automatic contract rewriting are
  excluded. A future detector requires a separately evidenced gap and scope decision.

### 3.4 Catalog Bundle and Presets

- Ship `drift-reconciliation` as a playbook asset of the opt-in, content-only `maintenance` bundle in
  `devkit-catalog`. The same bundle contains the independent `weekly-report` and `review-refactor` playbooks;
  do not create separate bundles or packages for these three procedures.
- Presets: `reporting` selects `weekly-report`; `upkeep` selects `drift-reconciliation` and `review-refactor`;
  the reserved `all` preset selects all three and is the bundle default. Keep `auto_select` disabled, following
  `CAP-DIST-content-packages` and `CAP-DIST-manifest-spec`.
- Each playbook is invoked independently and its body is read on demand. A reconciliation run does not require
  reporting or review/refactoring to run first; installing all three does not imply running all three.
- This proposal delivers and verifies the reconciliation asset and its preset membership, reusing or establishing
  the shared bundle as needed. It does not implement the other two playbooks or wait for their delivery.
- Verify bundle discovery, preset selection, package validation, and a manual reconciliation run. Update package
  documentation, installation recommendations, and the affected Living Spec distribution contract.

## 4. Rejected Candidate: Entrypoint-Based Stale-Document Hints

- **Source**: code-entrypoints work, implemented as `CAP-TRACE-code-entrypoints` (entrypoint metadata and
  reverse lookup by path).
- **Examined**: join a change's Git paths with entrypoints and show the documents whose code changed but which were
  not updated, as non-blocking candidates and as input to the periodic check.
- **Conclusion: rejected.** `MAT-drift-candidate-retrospective` looked up the code paths of 47 completed specs
  (45 evaluation units) against the entrypoints of the time and compared them with the reconcile targets. Excluding
  self-derived declarations (leave-one-out), precision is 0.48 and recall 0.54. No noise filter (hub paths excluded,
  file granularity only, at least two code paths per document) raises precision above 0.5 while keeping recall at
  0.5, so the data gives no threshold. Of ten false-positive pairs (not random: the first unit for each top
  entrypoint), eight were changes to what the document does not describe (file moves and splits, internal helper
  swaps, generated files, details delegated to other documents) and two were real updates fixed later in another
  commit.
- **What remains**: both late updates were places where a document restated a cross-cutting convention in prose
  (where the integration approval is recorded, the spec path format). Prose drift at that semantic level is caught
  neither by path lookup, nor by the path validity check of 3.1, nor by devkit's `RULE-cli-contract`, which checks
  only command citations. The main cause of lost recall is documents with narrow declarations, which no threshold
  fixes.
- **Reopen condition**: the same measurement on another repository gives leave-one-out precision of at least 0.6
  together with recall of at least 0.5. Integration into the `spec-review` skill is then designed separately.

## 5. Lifecycle & Retirement Criteria

- **Milestone**: `MS-drift-reconciliation`; manual playbook delivery is independent of scheduling.
- **Priority**: medium. Evidence from other repositories can refine the playbook but is not a prerequisite for its
  initial delivery and manual verification.
- The parent decision remains `ADR-dual-source-of-truth-and-periodic-reconciliation`. Existing rejected-detector
  evidence and its reopen condition remain in force; this proposal does not introduce a new detector threshold.
- Acceptance follows the proposal approval workflow; Development handoff follows acceptance.
- On rejection, preserve the decision and relevant evidence through the proposal retirement workflow.
