# Completed and unintegrated work evidence

Captured local integration main SHA: 56d64bd79b2874a94f64707077df786917ffaa6f. These are current snapshot observations on 2026-10-21,
not assertions about the March fixture interval or remote freshness. Integration event time is unknown.

## Completed and verified reachable work

SPEC-periodic-drift-reconciliation is completed at the captured integration SHA. Executed git show at that SHA
for each path under specs/2026-10/20261021-periodic-drift-reconciliation:

- spec.md: status completed.
- tasks.md: both tasks checked.
- reconcile.md: status resolved with named Living Spec targets.
- envelopes/final-report-01.yaml: tests PASS (4019 passed/14 skipped), build PASS consumer smoke,
  lint PASS and independent review/reconcile PASS, with limitations retained.

Executed git merge-base --is-ancestor 9d616c8a6182ffe128196d07824d734c4472d6ec 56d64bd79b2874a94f64707077df786917ffaa6f: exit 0. This corroborates completed, verified work
reachable from the selected integration snapshot. It does not establish integration during a particular week,
remote release or deployment. Evidence uses the recorded check revision/scope, not a claim about today's checks.
Changed decision evidence remains the committed ADR citation in fixture-1-report.md.

## Unintegrated or unverified work

The same reporting exercise retains fixture-1-report.md's weekly-report work as unverified: at its captured
revision it had unchecked tasks and lacked a final report/reconcile. A task commit alone does not establish
completed delivery. This pair exercises the success and qualification paths without changing immutable artifacts.

## Rerun outcome repair verification

fixture-2-outcome.json now resolves from fixture-2-report.md and names that artifact's existing run ID and
SHA-256 2fc97d83a389ba7cc8f3ab4e85f90140407fbf6bfea742474cbffb4cde9cdcb9. Readback and digest comparison passed. Generation is completed; publication pending,
destination and authority absent; no send occurred. Neither fixture report nor fixture-1 receipt was modified.
The reports' phrase about predating the interval is illustrative only: the actual October committed snapshot is
outside the March interval, and cannot be represented as a March event.
