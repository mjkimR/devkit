---
id: PROP-periodic-drift-reconciliation
title: Spec-code drift reconciliation maintenance playbook
summary: "Defines a manually invocable maintenance playbook that checks Living Spec, code, and guidance consistency using existing commands and evidence review, then resolves findings through user decisions: the Tier 2 reconciliation of ADR-dual-source-of-truth-and-periodic-reconciliation."
status: accepted                     # draft | reviewing | accepted | rejected
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
    - capabilities/traceability/
    - packages/devkit-catalog/
    - guides/
    - docs/stories/governance/
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

## 2. Planning Outcome

The selected direction is a bounded, manually invoked evidence review using existing lookup and governance
commands. A new detector, scheduler, standalone skill, report database, or MCP tool is unnecessary. The report is
an ordinary Markdown material in the owning work unit, or the repository's existing materials location when no
unit exists. Creating that report authorizes no source corrections. Preset membership is delivered incrementally
while the two independent companion playbooks do not yet exist (section 3.4).

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
  `devkit-catalog`; use its existing entry-point, package resource, and preset machinery. No engine extension or
  additional runtime dependency is required. Set `default_preset = "all"`, leave `auto_select` disabled, and never
  declare the reserved `[presets.all]` table.
- The final bundle organization remains `reporting` for `weekly-report`, `upkeep` for `drift-reconciliation` and
  `review-refactor`, and implicit `all` for all delivered assets. Each playbook is independently invoked and read
  on demand. Selection never implies execution.
- **Selected staged delivery:** initially publish only `drift-reconciliation`, with `upkeep` containing that asset and
  implicit `all` containing the same asset. Add `reporting` only with its weekly-report asset, and extend `upkeep`
  only with review-refactor. Do not create missing asset references, empty placeholder procedures, or advertise
  undelivered presets. If companion assets are already present when Development starts, preserve them and verify
  the combined selection. This proposal does not wait for or implement the companion playbooks.
- Verify bundle discovery, selected asset membership, opt-in behavior, package validation, and independent
  playbook lookup. Update catalog package documentation and existing installation recommendations. The existing
  manifest contract is reused; the content-packages contract describes the new available bundle.

### 3.5 Bounded Run and Report Contract

1. Intake records repository identity, HEAD, dirty-path status, selected contract IDs or one selected area, the
   implementation and guidance roots permitted for inspection, report destination, and any prior report. Missing
   scope is clarified before broad inspection. Enumerate an explicit candidate list and record reviewed versus
   excluded items; a large area is split into batches before review. Completion applies only to the declared batch.
2. Resolve IDs, inspect references and entrypoints to navigate, run only applicable existing checks, and read the
   relevant implementation/tests and guidance. Missing tools, malformed documents, missing entrypoints, or checks
   that cannot run become coverage gaps with their reason; no silent omission or clean verdict is permitted.
   Neither stale age, a changed path, nor passing governance checks proves semantic drift or consistency.
3. Each finding records a report-local stable key, contract ID and precise citation, code/guidance path and
   citation at the recorded revision, expected and observed behavior, evidence command/test when applicable,
   classification (`deterministic` or `semantic-assessment`), affected outcome, and proposed disposition. A
   deterministic checker failure proves that check's condition only; choosing intended behavior still belongs to
   the user. An unsupported suspicion remains an investigation gap rather than a confirmed mismatch.
4. Present all findings in one disposition round with enough evidence to choose documentation update, code fix,
   deferral, or waiver. Record the explicit decision and reason per key; unanswered findings remain pending.
   Deferral names an existing or newly authorized feedback/proposal destination and restart condition; waiver
   names the intentional gap and rationale. Search existing open feedback/proposals by affected contract and
   mismatch before creating another destination. No run is called fully reconciled while decisions remain pending.
5. Apply only user-decided changes through the repository's applicable development workflow and gate policy.
   Code fixes get regression evidence; documentation changes recheck the disputed claims, references, and affected
   checks. Invocation, a clean check, or an automatic integration policy never substitutes for the parent's
   human arbitration of each mismatch. Corrections outside the selected scope become separately tracked work.
6. Revalidate evidence when HEAD or relevant dirty paths change before correction or final verification. Preserve
   unrelated changes; a repeat run links the earlier finding and rechecks its disposition instead of duplicating
   it. A completed review can contain deferred/waived findings and coverage gaps, but the report names each and
   does not assert whole-repository consistency. Completion lists reviewed items, gaps, pending, resolved,
   deferred and waived counts, decision provenance, verification evidence and follow-up destinations.

### 3.6 Development Acceptance Evidence

- Given only this asset is delivered, selecting `maintenance:upkeep` or
  default `maintenance` deploys precisely drift-reconciliation; an unselected catalog deploys none. Existing
  companion assets, when present, retain their membership. No missing source or asset ID passes validation.
- Given a bounded manual sweep, the retained report names its input revision, candidate coverage and evidence
  on both sides of every finding; a zero-finding run still records what was inspected and any coverage gaps.
- Given unavailable checks or uncertain semantic evidence, the report records gaps or assessments and never
  turns them into a clean or automatically authoritative verdict.
- Given one example of each disposition, a manual exercise records the explicit decisions, delivery destination,
  correction verification or deferral/waiver rationale. Use an isolated seeded fixture for cases absent from a
  real bounded sweep; fixture decisions are explicitly simulated and authorize no repository change. Keep a
  real repository read-only sweep separate from the fixture exercise. Development need not manufacture live
  defects or fix unrelated findings to demonstrate the playbook.
- Given repeated findings, changed evidence, or an unanswered decision, a manual exercise shows deduplication,
  revalidation or pending status respectively. No scheduler or rejected path-based detector is introduced.

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
