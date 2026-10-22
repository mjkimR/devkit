---
name: drift-reconciliation
description: Manually review a bounded Living Spec, code and guidance scope for spec-code drift and consistency, then reconcile evidenced findings through explicit user decisions.
---

# Drift reconciliation

Run only on explicit invocation through `devkit-playbook`. Review one bounded batch. The user, not code or
documentation, decides each mismatch. Changed paths, age, entrypoints and passing checks locate evidence but prove
neither drift nor consistency; a failing check proves only its own condition.

## 1. Bound the review

1. Record repository, HEAD, dirty paths, selected contract IDs or area, permitted implementation and guidance
   roots, prior reports and the report destination: the owning work unit's materials, else the repository's
   materials location. Clarify missing scope before inspecting.
2. List candidate contracts, interfaces and consumer guidance; split a large area into explicit batches.

## 2. Collect evidence

Use existing tools only: in a devkit-spec repository `devkit spec resolve <ID>`, `devkit spec refs <ID> --direction
out` and entrypoints; `devkit rules check <path>` where installed; tests. Install nothing without asking. Compare
documented commands, options, interfaces, terminology and behavior with implementation, tests and guidance.

Per mismatch, record a report-local key; contract ID and citation; code or guidance citation at the recorded
revision, dirty content included; expected and observed behavior and the user outcome; the evidence command or
test; `deterministic` or `semantic-assessment` with its uncertainty; a proposed disposition. Record an unsupported
suspicion as an investigation gap, and a missing tool, document, entrypoint, check or evidence as a coverage gap
with its reason.

## 3. Obtain dispositions together

Present all findings in one decision round with both sides and a recommendation. Record each user decision with
its reason and provenance:

| Disposition | Required record and next action |
| --- | --- |
| Update documentation/guidance | User confirms implemented behavior is intended; name the correction and delivery destination. |
| Fix code | User confirms documented intent; route the fix through the development workflow with regression evidence. |
| Defer | Record reason, existing or newly authorized feedback/proposal destination, and restart condition. |
| Waive | Record the intentional gap and rationale. |

- Search open feedback and proposals before creating a follow-up; reuse a match and link earlier report keys. On a
  repeat run, recheck earlier dispositions.
- Leave unanswered findings pending; neither invocation, clean checks nor the report authorizes a correction.
- In an exercise, label decisions as simulated and change nothing.

## 4. Apply decided corrections

1. If HEAD or relevant dirty paths changed since intake, revalidate the evidence and get a new decision when the
   correction changes.
2. Apply each decided correction through the repository's development workflow; track out-of-scope corrections and
   structural cleanup as separate work.
3. Verify code fixes with regression evidence and documentation fixes by rechecking the disputed claims and
   references. Record revision, commands, results and limits per finding.

## 5. Finish the report

Recheck HEAD and dirty paths, then record coverage (reviewed, excluded with reason, gaps), findings, decisions,
corrections and counts (detected, resolved, deferred, waived, pending). A zero-finding review still names its
coverage and gaps. Claim the batch fully reconciled only with no pending decision, and never claim
whole-repository consistency.
