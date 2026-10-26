---
id: UC-reconcile-living-spec-drift
title: Reconcile Living Spec Drift
summary: "A developer has an AI coding agent review a bounded batch of Living Spec contracts, code and guidance for semantic drift, record evidence and coverage gaps, and apply only the corrections, deferrals and waivers the developer decides."
area: governance
primary_actor: Developer
supporting_actors:
  - AI coding agent running the drift-reconciliation playbook
status: active
capabilities:
  - CAP-DIST-context-and-playbooks
  - CAP-DLV-drift-reconciliation
created_at: 2026-10-22
---

# [UC-reconcile-living-spec-drift] Reconcile Living Spec Drift

## 1. Goal

- **Goal**: have every mismatch between the Living Spec, the implementation and its consumer guidance in a bounded
  batch exposed with precise evidence and resolved only by the developer's explicit decision, so that drift that
  structural checks cannot show is corrected, deferred or waived on record instead of silently accumulating
- **Scope**: the `drift-reconciliation` playbook of the opt-in `maintenance` catalog bundle, run by an AI coding agent
  with the repository's existing lookup, reference, entrypoint and governance tools and its development workflow
- **Trigger**: the developer suspects drift that structure cannot show and explicitly invokes the playbook, or confirms
  it when `spec` intake offers it
- **Preconditions**: the `maintenance` bundle is installed; structural consistency is kept separately under
  `UC-keep-the-living-spec-consistent`

---

## 2. Main Success Scenario

1. The developer explicitly invokes the drift-reconciliation playbook through `devkit-playbook`, or confirms the
   one-line offer `spec` intake makes for a request to reconcile Living Spec drift, which loads its procedure on demand (`CAP-DIST-context-and-playbooks`, `CAP-DLV-drift-reconciliation`).
2. The agent records the intake (repository identity, HEAD and dirty paths, the selected contract IDs or area, the
   permitted implementation and guidance roots, prior reports and the report destination) and lists the candidates
   of one bounded batch (`CAP-DLV-drift-reconciliation`).
3. The agent compares the selected contracts with the implementation, tests and consumer guidance at the recorded
   revision, and records each confirmed mismatch as a finding with precise citations on both sides, expected and
   observed behavior, its evidence, its `deterministic` or `semantic-assessment` classification and a proposed
   disposition (`CAP-DLV-drift-reconciliation`).
4. The agent presents all findings together in one decision round; the developer decides each one (update
   documentation or guidance, or fix code), and the agent records each decision with its reason and provenance
   (`CAP-DLV-drift-reconciliation`).
5. The agent applies each decided correction through the repository's development workflow within its write-scope
   and approval boundaries (`CAP-DLV-drift-reconciliation`).
6. The agent verifies each correction: a code fix with regression evidence, a documentation correction by rechecking
   the disputed claims, references and applicable checks (`CAP-DLV-drift-reconciliation`).
7. The agent rechecks HEAD and the dirty paths and completes the report for the batch with its coverage, findings,
   decisions, corrections, counts, verification and follow-ups; with no decision pending, the batch is reconciled
   (`CAP-DLV-drift-reconciliation`).

---

## 3. Extensions

- **2a.** The selected contracts, area or permitted roots are missing: the agent clarifies the scope with the
  developer before any broad inspection; resumes at step 2.
- **2b.** The selected area is too large for one review: the agent splits it into explicit batches and records the
  reviewed and excluded candidates; resumes at step 3 with one batch.
- **3a.** A tool, document, entrypoint, check or evidence is missing, malformed or unavailable, or a suspicion lacks
  supporting evidence: the agent records a coverage gap or an investigation gap with its reason, never a finding, and
  installs nothing without asking; resumes at step 3.
- **3b.** The comparison confirms no mismatch: the report still names the reviewed coverage and its gaps; resumes at
  step 7.
- **4a.** The developer defers or waives a finding: a deferral records its reason, an existing or newly authorized
  feedback or proposal destination found after searching open ones, and its restart condition; a waiver records the
  intentional gap and its rationale; the finding receives no correction; resumes at step 5 for the decided
  corrections.
- **4b.** The developer leaves a finding unanswered: it stays pending and receives no correction, and the batch is
  never claimed fully reconciled; resumes at step 5 for the decided corrections.
- **4c.** A prior report covers the batch: the agent links each finding to the earlier report keys and rechecks the
  earlier dispositions; resumes at step 4.
- **4d.** The review is an isolated seeded exercise: the agent labels the decisions as simulated and changes no
  source; resumes at step 7.
- **5a.** HEAD or a relevant dirty path changed since the intake: the agent revalidates the evidence; resumes at
  step 4 for a new decision when the correction changes, otherwise at step 5.
- **5b.** A decided correction falls outside the declared scope or is structural cleanup: the agent tracks it as
  separate work; resumes at step 6.

---

## 4. Postconditions

- **Success guarantee**: the report records the reviewed and excluded candidates, coverage gaps, every finding with
  its evidence, the developer's decision and provenance per finding, the applied corrections with their verification,
  and the detected, resolved, deferred, waived and pending counts; every deferral names its destination and restart
  condition and every waiver its rationale.
- **Minimal guarantee**: the report authorizes no correction by itself; no correction is applied without the
  developer's decision, and unrelated edits are preserved; a passing check is never claimed as semantic consistency,
  a batch never as whole-repository consistency, and a batch with a pending decision never as fully reconciled.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Exposes semantic drift in a bounded review
- **Covers**: main success scenario
- **Given**: the drift-reconciliation playbook is explicitly invoked for selected contracts, code and guidance at a
  recorded revision
- **When**: the agent compares both sides and runs the applicable checks
- **Then**: the report records the reviewed coverage, precise evidence for each finding and the coverage gaps, and
  structural checks alone do not establish semantic consistency

### Scenario 2: Clarifies a missing scope before inspecting
- **Covers**: 2a
- **Given**: an invocation that names neither contract IDs nor an area
- **When**: the agent records the intake
- **Then**: the agent asks the developer for the scope and inspects no candidate until the scope is recorded

### Scenario 3: Claims completion only for the declared batch
- **Covers**: 2b
- **Given**: a selected area split into explicit batches
- **When**: the agent completes the report of one batch
- **Then**: the report records the reviewed and excluded candidates, and claims no consistency beyond that batch

### Scenario 4: Records a missing check as a coverage gap
- **Covers**: 3a
- **Given**: a contract whose declared entrypoint is absent and a governance check that is not installed
- **When**: the agent collects evidence
- **Then**: both appear as coverage gaps with their reasons, neither is reported as a finding or as consistent, and
  nothing is installed without asking

### Scenario 5: Names the coverage of a zero-finding review
- **Covers**: 3b
- **Given**: a bounded batch in which the comparison confirms no mismatch
- **When**: the agent completes the report
- **Then**: the report states zero findings together with its reviewed coverage and its gaps

### Scenario 6: Applies only the corrections the developer decided
- **Covers**: 4a, 4b
- **Given**: evidenced findings in a bounded review
- **When**: the developer chooses a documentation update, a code fix, a deferral or a waiver for each finding
- **Then**: only decided corrections enter the applicable workflow and verification; deferrals keep their destinations
  and restart conditions, waivers keep their rationale, and unanswered findings remain pending

### Scenario 7: Reuses an open follow-up for a deferral
- **Covers**: 4a
- **Given**: an open proposal that already tracks the deferred mismatch
- **When**: the developer defers the finding
- **Then**: the deferral names that proposal and a restart condition, and no duplicate destination is created

### Scenario 8: Rechecks earlier dispositions on a repeat run
- **Covers**: 4c
- **Given**: a prior report with deferred and waived findings for the same batch
- **When**: the agent reviews the batch again
- **Then**: each finding links its earlier report key, and the earlier dispositions are rechecked

### Scenario 9: Changes nothing in a seeded exercise
- **Covers**: 4d
- **Given**: an isolated seeded exercise with evidenced findings
- **When**: the decisions are recorded
- **Then**: the decisions are labeled simulated, and no real source changes

### Scenario 10: Revalidates evidence after the revision moves
- **Covers**: 5a
- **Given**: decided corrections, and a HEAD that moved since the intake
- **When**: the agent prepares to apply the corrections
- **Then**: the evidence is revalidated, and a correction whose intent changes waits for a new decision

### Scenario 11: Tracks an out-of-scope correction separately
- **Covers**: 5b
- **Given**: a decided correction that needs a change outside the declared scope
- **When**: the agent applies the decided corrections
- **Then**: that correction is tracked as separate work, and only in-scope corrections are applied and verified
