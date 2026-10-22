---
name: drift-reconciliation
description: Manually review a bounded Living Spec, code and guidance scope for spec-code drift and consistency, then reconcile evidenced findings through explicit user decisions.
---

# Drift reconciliation

Use only on explicit manual invocation through `devkit-playbook`; selecting the maintenance bundle does not run
this procedure.

- It complements per-work-unit reconciliation; it is not a detector or scheduler.
- Neither code nor documentation automatically determines intended behavior.
- This playbook adds no standalone skill or report store.

## 1. Bound the review

1. Record repository identity, current HEAD and dirty paths (for Git repositories, `git rev-parse HEAD` and
   `git status --short`), selected contract IDs or one selected area, permitted implementation and guidance roots,
   report destination and prior reports.
2. If scope is missing, clarify it before broad inspection.
3. Follow repository instructions and read permissions; preserve unrelated changes.
4. Store an ordinary Markdown report under the owning work unit's materials; when no unit exists, use the
   repository's existing materials location.
5. Before review, enumerate candidate contracts, implementation interfaces and consumer guidance. Mark each
   reviewed, excluded (with reason), or a coverage gap.
6. Split a large area into explicit batches before inspecting it; completion applies only to the declared batch.

Changed paths and document age may help select scope but prove no drift.

## 2. Collect evidence

Use available existing tools, not a new detector:

- In a devkit-spec repository, navigate with `devkit spec resolve <ID>`, `devkit spec refs <ID> --direction out`
  and declared entrypoints.
- Use applicable existing governance checks (for example `devkit rules check <path>` when the harness is
  installed), relevant tests, and implementation and guidance inspection.
- In other repositories, use their existing lookup and validation tools.
- Record the actual commands and results.
- Do not install tools or expand permissions silently.

Compare documented commands/options, interfaces, terminology and behavior to implementation/tests and guidance
that restates the contract. Reuse path and reference checks.

- Name missing tools, malformed documents, absent entrypoints, unavailable checks or insufficient evidence as
  coverage gaps with reasons; do not omit them or claim a clean verdict.
- Entrypoints locate evidence only: changed paths, age and passing checks establish neither semantic drift nor
  consistency.
- A deterministic failure proves only that check's condition, not which ledger is intended.

For every evidenced mismatch record:

- A stable report-local key, contract ID and exact section/line citation.
- Code or guidance path and section/line citation at the recorded revision, including relevant dirty content.
- Expected and observed behavior, affected user outcome and supporting command/test where applicable.
- Classification: `deterministic` or `semantic-assessment`, with reasoning and uncertainty.
- Proposed disposition. Unsupported suspicions stay investigation gaps, not confirmed mismatches.

Keep detailed evidence in the report. Preserve each existing command's output contract; do not invent machine
sentinels or treat narrative review as a deterministic checker result.

## 3. Obtain dispositions together

Present all findings in one decision round with both sides of the evidence and recommended dispositions. Record
an explicit user decision and reason for each key, with its decision provenance:

| Disposition | Required record and next action |
| --- | --- |
| Update documentation/guidance | User confirms implemented behavior is intended; name the document correction and delivery destination. |
| Fix code | User confirms documented intent; route the regression through the applicable development workflow with regression evidence. |
| Defer | Record reason, existing or newly authorized feedback/proposal destination, and restart condition. |
| Waive | Record the intentional gap and rationale. |

- Before creating a follow-up, search existing open feedback/proposals by contract and mismatch. Reuse matching
  records and link prior report keys.
- On a repeat run, recheck the earlier disposition instead of duplicating work.
- Unanswered findings remain pending; do not call the run fully reconciled.
- Invocation, clean checks, or automatic integration policy never substitutes for explicit human arbitration of
  each mismatch. A report alone authorizes no source correction.
- If only an exercise is requested, label simulated decisions and apply no repository change.

## 4. Apply decided corrections

1. Follow the repository's development workflow, write scope and approval policy for each decided correction.
   - Track corrections outside the selected scope as separate work.
   - Leave broad structural cleanup to its own authorized review/refactoring task, not this sweep.
   - Keep undecided findings unchanged.
2. Before correction, compare HEAD and relevant dirty paths with intake. If they changed, revalidate the cited
   evidence and decision applicability; obtain a new disposition when the intended correction changes.
3. Preserve unrelated edits.
4. Verify code fixes with regression evidence. For documentation corrections, recheck disputed claims, references
   and applicable checks.
5. Record the correction revision, commands, actual results and remaining limitations per finding.

## 5. Finish the bounded report

1. Before final verification, recheck HEAD and relevant dirty paths and revalidate changed evidence.
2. Record reviewed and excluded candidates, coverage gaps, detected/resolved/deferred/waived/pending counts,
   decision provenance, verification evidence and follow-up destinations.

- A zero-finding review still names its coverage and gaps.
- A completed review may retain deferrals, waivers and coverage gaps, but must state them; pending decisions
  prevent a fully reconciled claim.
- Do not assert whole-repository consistency or equate a passing check with semantic truth.

## Report outline

- Intake: repository, HEAD, dirty paths, batch, permitted roots, destination, prior reports.
- Coverage: candidate / reviewed, excluded or gap / evidence or reason.
- Findings: key / both citations / expected and observed / outcome / classification / evidence / proposal.
- Decisions: key / explicit disposition and reason / provenance / destination and restart condition when deferred.
- Corrections: key / workflow destination / revision / verification and limits.
- Completion: counts, unresolved gaps, pending decisions, reused follow-ups and revalidation evidence.
