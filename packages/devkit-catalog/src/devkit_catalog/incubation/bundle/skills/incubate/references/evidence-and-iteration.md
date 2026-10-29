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
