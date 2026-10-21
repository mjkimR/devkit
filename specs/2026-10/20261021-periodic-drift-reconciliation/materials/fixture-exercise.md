# Isolated manual fixture exercise

This is a seeded paper fixture, independent of the real read-only sweep. All citations below refer to literal
fixture cells in this document at its first committed revision. All decisions are explicitly simulated; they
are not user authorization and change no repository contract or code. Repository identity: paper fixture v1;
HEAD: not a Git repository; dirty paths: not applicable. Permitted inspection/correction root: this document's
fixture cells only. Prior report: none. Candidate batch: F1-F5 plus G1; no excluded candidates.

## Fixture evidence and one batched disposition round

| Key | Contract cell / code or guidance cell | Evidence and affected outcome | Classification | Simulated explicit decision and reason | Destination |
| --- | --- | --- | --- | --- | --- |
| F1 | C1: default timeout 10; I1: default timeout 20 | Manual comparison 10 != 20; caller expectation differs | semantic-assessment | Update documentation: 20 is intended | Correction cell C1 below |
| F2 | C2: empty input returns []; I2: empty input returns null | Manual comparison [] != null; caller collection handling fails | semantic-assessment | Fix code: collection return is intended | Fixture bugfix B2 with regression assertion below |
| F3 | C3: guide names --output; G3: guide example uses --out | Manual comparison option spelling differs; copied invocation is uncertain | semantic-assessment | Defer: need owner to choose canonical spelling | Existing simulated feedback Q3; restart when CLI owner resolves spelling |
| F4 | C4: all hosts show button; I4: terminal host has no button | Manual comparison host exception; universal statement differs | semantic-assessment | Waive: terminal-only interaction intentionally uses text | Intentional gap W4 in this row |
| F5 | C5: retry count 3; I5: retry count 4 | Manual comparison 3 != 4; retry load differs | semantic-assessment | Unanswered; pending | No correction authorized |
| G1 | C6: external server latency bound; implementation unavailable | No server or measurement available | investigation gap, not finding | No clean verdict | Need measured server access |

## Corrections and verification

C1 corrected fixture value: default timeout 20. Re-reading C1=20 and I1=20 confirms the disputed claim matches.
Fixture bugfix B2 replaces I2 null with []; regression assertion `empty_result == []` evaluates true for the
corrected literal cell. These are manual literal comparisons, not an executed production test or delivery approval.
No real development workflow is opened: B2 is a simulated destination only. For a live run both corrections must
enter the repository's applicable workflow and permissions, with an actual regression test for F2.

## Repeat and changed evidence

Repeat batch v2 searches the fixture destination table by C3 and --out/--output before proposing a follow-up:
Q3 already matches F3, so link F3/Q3 and create zero new destinations. Recheck Q3: owner decision remains absent.
For changed-evidence exercise, change the I1 cell to 30 in fixture v2. Revalidation compares C1=20 with I1=30,
invalidates F1's earlier verification, reopens F1 pending a fresh explicit decision, and applies no correction.
The earlier simulated decision for 20 cannot authorize 30. No unrelated fixture cells change.

## Completion

v1: detected 5, resolved 2, deferred 1, waived 1, pending 1, coverage gaps 1. Reviewed all six candidates.
v2: detected 5, resolved 1, deferred 1, waived 1, pending 2, coverage gaps 1; Q3 reused once, no duplicate created.
Decision provenance: simulated exercise only. Review complete for the declared batch, not fully reconciled:
F5 (and reopened F1 in v2) need decisions and G1 lacks evidence. This exercise verifies the procedure's records
and arithmetic by manual inspection; it makes no claim about autonomous agent reliability.
