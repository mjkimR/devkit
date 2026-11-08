# Evidence and iteration

1. State the concrete decision or intended flow and its current source/artifact identity.
2. For research, use evidence that addresses that decision; verify time-sensitive facts against current primary sources and record links, limits and the recommendation.
3. When documentation cannot settle feasibility, bound an experiment by question, absolute write boundary, execution method and stop condition.
4. Separate observed evidence from inference; an unavailable check or inconclusive experiment stays a gap.
5. Implement a representative flow end to end with commands to set it up, run it and verify it; add structure and tooling only as the implementation needs them.
6. Inside the agreed product goal, replace features, technologies, data models, tests and documents when the retained result warrants it; discarded choices are not immutable history.
7. Run applicable build, lint and tests, then exercise actual usage against the expected flow; a unit test alone does not establish usable interaction.
8. Record the exact command or interaction, relevant environment, source/artifact identity, observed outcome and coverage limitation.
9. When source or retained behavior changes, rerun the affected verification; keep unaffected evidence with its original identity and applicability.

Example evidence: `python app.py --add milk` then `python app.py --list`, with the actual output and tested revision. A mocked transcript is scenario input, not an observed product run.

## Failure probes and repair

1. Select the normal path and failure and integration probes from the changed behavior and consequence of failure. For stateful work, assess malformed input, duplicate execution, cancellation/resume, stale state and partial failure when relevant; omit inapplicable cases.
2. Keep probes bounded by existing authority; do not require production writes. Record each expected signal, actual command or interaction, source/artifact identity, outcome and limitation. Mark unavailable probes unverified.
3. If a probe fails before valid product execution, classify a harness or environment failure only when evidence supports it; otherwise retain an unknown cause. Leave product behavior unverified until a valid product probe passes, including after a harness fix.
4. Compare the symptom, causal hypothesis, attempted change and new evidence before another repair. Keep an assignment's own repair bound. Without one, after two consecutive attempts produce the same symptom without materially new diagnostic evidence, change strategy before another equivalent attempt.
5. Treat evidence as material when it changes or tests a causal hypothesis, isolates a dependency or identifies a distinct failure. Repeating the same output alone is not progress.
6. Continue safe, useful diagnosis within authority; report the unresolved blocker and next action when the necessary action is unavailable. The trigger is not a cap on authorized work or a completion condition. Rerun affected checks before claiming the original behavior passed.

Example: if a fixture twice fails to start with the same import error, inspect its environment or import path before another equivalent run. Preserve the failure and leave the product probe unverified until it executes.
