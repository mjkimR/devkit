---
name: deep-research
description: Coordinate a bounded research team that investigates a question, compares independent directions with sourced evidence and retains the result as one indexed material under docs/materials/.
---

# Deep research

Run only when the user explicitly invokes this entry; never suggest or start it otherwise.

## Constraints

- The invocation authorizes bounded research inside the stated question, its transient run directory and one retained material; it authorizes no implementation, publication, project setting change, work unit, approval or envelope.
- Write only the run directory under `.devkit/transient/deep-research/` and the retained material under `docs/materials/`; report both paths.
- Never stage, commit or push; the user commits the retained material through the project's Git policy.
- Stay the coordinator: roles return evidence or drafts, and only the coordinator writes the retained material.

## Procedure

1. Read the supplied question, sources and documents; read an earlier run directory or retained material only when the user names it as an input source.
2. Recover the requested deliverable, intended use, known constraints, actual decisions and stop condition; ask only for a missing decision that changes the research target.
3. Read `references/orchestration.md` before allocating an investigation or comparing candidate directions. To delegate, select one role file under `roles/` through it, send its absolute path to a `role-worker` subagent and instruct it to read that file first.
4. Choose a bounded next investigation from the missing evidence; add optional roles only where separate context adds coverage. Read `references/workspace.md` before allocating scratch work or promoting its results.
5. If a bounded missing question benefits from user-mediated cloud research or the user requests it, read `references/cloud-handoff.md` before preparing a request or incorporating a returned report; cloud work stays optional.
6. Review actual role returns and their inspected evidence; reopen sources only for consequential gaps, contradictions or suspect support, then revise, combine or stop assignments.
7. Read `references/synthesis.md` before creating or updating the retained material, and run `uv run devkit get-context docs` and apply its relevant writing instructions before document work.
8. Check that the draft supplies the requested artifact and supports its intended use without unwanted prerequisites; repair a mismatch, then retain one indexed material, inspect it and report the result and next decision.
9. End with the research outcome; implementation or follow-up work starts only under a separate user request.

## Completion

Return compared directions, supporting sources and coverage limits, recommendations versus user decisions, the
retained material's path, `MAT-<slug>` ID and `Status`, the transient run path, the conditional roadmap and
unresolved questions.

- Tell the user that a proposal, spec, decision or current-context note can cite the material only after it is committed to the base, and to commit it through the project's Git policy.
- A bounded partial result is valid when its missing evidence is explicit; never report an unexecuted role, unavailable check or speculative choice as verified.
- Keep declined validation out of adoption prerequisites; state uncertain benefits without requiring a comparison experiment.

Example: `/deep-research Compare ways to organize technical reading for a solo-maintained product; research alternatives and propose initial documents and a roadmap.`
