---
name: deep-research
description: Coordinate a bounded research team that investigates a question, compares independent directions with sourced evidence and retains the result as one indexed material under docs/materials/.
---

# Deep research

Run only when the user explicitly invokes this entry; never suggest or start it otherwise.

## Constraints

- Treat the invocation as authority for bounded research inside the stated question: its transient run directory and one retained material. It authorizes no implementation, publication, project setting change, work unit, approval or envelope.
- Write only the run directory under `.devkit/transient/deep-research/` and the retained material under `docs/materials/`, and report both paths.
- Never stage, commit or push; the user commits the retained material through the project's Git policy.
- Keep the invoking agent as coordinator; roles return evidence or drafts, and only the coordinator writes the retained material.

## Procedure

1. Read the supplied question, sources and documents. Read an earlier run directory or retained material only when the user names it as an input source.
2. Recover the requested deliverable, intended use, known constraints, actual decisions and stop condition; ask only a missing decision that changes the research target.
3. Read `references/orchestration.md` before allocating an investigation or comparing candidate directions.
4. When delegating, select one role file under `roles/` through the orchestration reference; send its absolute path to a general subagent and instruct it to read that file first.
5. Choose a bounded next investigation from the missing evidence; use optional roles only where separate context adds useful coverage. Read `references/workspace.md` before allocating scratch work or promoting its results.
6. Review actual role returns and their inspected evidence; reopen sources only for consequential gaps, contradictions or suspect support, then revise, combine or stop assignments.
7. Read `references/synthesis.md` before creating or updating the retained material; read `uv run devkit get-context docs` and its relevant writing instructions before document work.
8. Check that the draft supplies the requested artifact and supports its intended use without unwanted prerequisites; repair a mismatch before retaining one indexed material, then inspect it and report the result and next decision.
9. End with the research outcome; any implementation or follow-up work starts separately under the user's own request.

## Completion

Return compared directions, supporting sources and coverage limits, recommendations versus user decisions, the
retained material's path and `MAT-<slug>` ID with its `Status`, the transient run path, the conditional roadmap and
unresolved questions. Tell the user that a proposal, spec, decision or current-context note can cite the material
only after it is committed to the base, and to commit it through the project's Git policy. A bounded partial result
is valid when its missing evidence is explicit; do not report an unexecuted role, unavailable check or speculative
choice as verified. Keep declined validation out of adoption prerequisites; state uncertain benefits without requiring a comparison experiment.

Example: `/deep-research Compare ways to organize technical reading for a solo-maintained product; research alternatives and propose initial documents and a roadmap.`
