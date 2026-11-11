# Evidence and iteration

1. State the concrete decision or intended flow and its current source/artifact identity.
2. For research, use evidence that addresses that decision; verify time-sensitive facts against current primary sources and record links, limits and the recommendation.
3. When documentation cannot settle feasibility, bound an experiment by question, absolute write boundary, execution method and stop condition.
4. Separate observed evidence from inference; an unavailable check or inconclusive experiment stays a gap.
5. Implement a representative flow end to end with commands to set up, run and verify it; add structure and tooling only as the implementation needs them.
6. Inside the agreed goal, replace features, technologies, data models, tests and documents when the retained result warrants it; discarded choices are not immutable history.
7. Run applicable build, lint and tests, then exercise actual usage against the expected flow; a unit test alone does not establish usable interaction.
8. Record the exact command or interaction, relevant environment, source/artifact identity, observed outcome and coverage limitation.
9. When source or retained behavior changes, rerun the affected verification; keep unaffected evidence with its original identity and applicability.

Example evidence: `python app.py --add milk` then `python app.py --list`, with the actual output and tested revision. A mocked transcript is scenario input, not an observed product run.

## Failure probes and repair

1. Select normal-path, failure and integration probes from the changed behavior and the consequence of failure; for stateful work, assess malformed input, duplicate execution, cancellation/resume, stale state and partial failure where relevant.
2. Keep probes within existing authority, with no production writes. Record each expected signal with the step 8 evidence; mark unavailable probes unverified.
3. If a probe fails before valid product execution, call it a harness or environment failure only when evidence supports that, else keep the cause unknown. Product behavior stays unverified until a valid product probe passes, including after a harness fix.
4. Before another repair, compare the symptom, causal hypothesis, attempted change and new evidence. Keep an assignment's own repair bound; without one, after two consecutive attempts show the same symptom without materially new diagnostic evidence, change strategy before another equivalent attempt.
5. Evidence is material when it changes or tests a causal hypothesis, isolates a dependency or identifies a distinct failure; the same output repeated is not progress.
6. Continue safe, useful diagnosis within authority; when the necessary action is unavailable, report the blocker and next action. The strategy-change trigger neither caps authorized work nor marks completion. Rerun affected checks before claiming the original behavior passed.

Example: a fixture fails twice to start with the same import error; inspect its environment or import path before another equivalent run, preserve the failure and keep the product probe unverified until it executes.
