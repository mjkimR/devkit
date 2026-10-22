---
name: drift-reconciliation
description: Manually review a bounded Living Spec, code and guidance scope for spec-code drift and consistency, then reconcile evidenced findings through explicit user decisions.
---

# Drift reconciliation

Run only on explicit manual invocation through `devkit-playbook`; selecting the maintenance bundle does not run
this procedure. It reviews accumulated drift in one bounded batch and complements per-work-unit reconciliation.

- Neither code nor documentation decides intended behavior; the user decides each mismatch.
- Changed paths, document age, entrypoints and passing checks locate evidence; they establish neither semantic
  drift nor consistency. A deterministic failure proves only that check's condition, not which side is intended.
- Preserve unrelated changes throughout.

## 1. Bound the review

1. Record repository identity, current HEAD and dirty paths (for Git repositories, `git rev-parse HEAD` and
   `git status --short`), selected contract IDs or one selected area, permitted implementation and guidance roots,
   report destination and prior reports.
2. If scope is missing, clarify it before broad inspection.
3. Store an ordinary Markdown report under the owning work unit's materials; when no unit exists, use the
   repository's existing materials location.
4. Before review, enumerate candidate contracts, implementation interfaces and consumer guidance. Mark each
   reviewed, excluded (with reason), or a coverage gap.
5. Split a large area into explicit batches before inspecting it; completion applies only to the declared batch.

## 2. Collect evidence

Use existing tools; build no new detector, and install no tool or expand permissions without asking.

- In a devkit-spec repository, navigate with `devkit spec resolve <ID>`, `devkit spec refs <ID> --direction out`
  and declared entrypoints.
- Run applicable governance checks (for example `devkit rules check <path>` when the harness is installed),
  relevant tests, and inspect implementation and guidance.
- In other repositories, use their existing lookup and validation tools.
- Record the actual commands and results.

Compare documented commands and options, interfaces, terminology and behavior with implementation, tests and the
guidance that restates the contract. Record missing tools, malformed documents, absent entrypoints, unavailable
checks and insufficient evidence as coverage gaps with reasons, never as a clean verdict.

For every evidenced mismatch record:

- A stable report-local key, contract ID and exact section/line citation.
- Code or guidance path and section/line citation at the recorded revision, including relevant dirty content.
- Expected and observed behavior, affected user outcome and supporting command/test where applicable.
- Classification: `deterministic` or `semantic-assessment`, with reasoning and uncertainty.
- Proposed disposition.

Record an unsupported suspicion as an investigation gap, not a mismatch. Keep detailed evidence in the report, and
present narrative review as assessment, not as a check result.

## 3. Obtain dispositions together

Present all findings in one decision round with both sides of the evidence and recommended dispositions. Record
an explicit user decision and reason for each key, with its decision provenance:

| Disposition | Required record and next action |
| --- | --- |
| Update documentation/guidance | User confirms implemented behavior is intended; name the document correction and delivery destination. |
| Fix code | User confirms documented intent; route the regression through the applicable development workflow with regression evidence. |
| Defer | Record reason, existing or newly authorized feedback/proposal destination, and restart condition. |
| Waive | Record the intentional gap and rationale. |

- Before creating a follow-up, search open feedback and proposals by contract and mismatch. Reuse a matching
  record and link prior report keys.
- On a repeat run, recheck the earlier disposition instead of duplicating work.
- Leave an unanswered finding pending. Invocation, clean checks and integration policy never substitute for the
  user's decision, and the report alone authorizes no source correction.
- If only an exercise is requested, label simulated decisions and apply no repository change.

## 4. Apply decided corrections

1. Follow the repository's development workflow, write scope and approval policy for each decided correction.
   - Track corrections outside the selected scope as separate work.
   - Leave broad structural cleanup to its own authorized review or refactoring task.
   - Keep undecided findings unchanged.
2. Before correcting, compare HEAD and relevant dirty paths with intake. If they changed, revalidate the cited
   evidence and decision applicability; obtain a new disposition when the intended correction changes.
3. Verify code fixes with regression evidence. For documentation corrections, recheck disputed claims, references
   and applicable checks.
4. Record the correction revision, commands, actual results and remaining limitations per finding.

## 5. Finish the bounded report

1. Before final verification, recheck HEAD and relevant dirty paths and revalidate changed evidence.
2. Complete the report with these sections:
   - Intake: repository, HEAD, dirty paths, batch, permitted roots, destination, prior reports.
   - Coverage: candidate / reviewed, excluded or gap / evidence or reason.
   - Findings: key / both citations / expected and observed / outcome / classification / evidence / proposal.
   - Decisions: key / disposition and reason / provenance / destination and restart condition when deferred.
   - Corrections: key / workflow destination / revision / verification and limits.
   - Completion: detected, resolved, deferred, waived and pending counts; unresolved gaps; reused follow-ups;
     revalidation evidence.

The review is complete when the report names its coverage and gaps, even with zero findings. It may retain
deferrals, waivers and coverage gaps when it states them. Claim the batch fully reconciled only with no pending
decision, and never claim whole-repository consistency.
