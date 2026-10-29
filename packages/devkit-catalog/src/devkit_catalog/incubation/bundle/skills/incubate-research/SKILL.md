---
name: incubate-research
description: Start an explicitly requested incubation research team to investigate an ambiguous idea, compare product or architecture directions, and draft initial documents and a roadmap before development.
---

# Incubation research

Use this entry when the user explicitly invokes it or selects a proposed research-team investigation.
If broad discovery merely seems useful during other work, suggest this entry and wait for that selection.

## Constraints

- Before product actions, read `uv run devkit config show` and require `configuration.development.approach` to be `incubation`.
- If policy is unreadable or the approach is SDD, stop product actions and report the actual error or the shared `.devkit/config.toml` setting `[development] approach = "incubation"`; change it only on the user's direction.
- Treat the invocation as authority for bounded research and local planning notes inside the agreed goal; it does not authorize implementation, publication or approach switching.
- Keep the invoking agent as coordinator (master); roles return evidence or drafts, and only the coordinator saves retained synthesis and `.devkit/incubation.md`.

## Procedure

1. Read `uv run devkit get-context incubation` once per context, existing `.devkit/incubation.md` and the supplied idea, roadmap or product documents.
2. Recover the user goal, constraints, actual decisions and open questions; ask only missing decisions that change the research target.
3. Read `references/orchestration.md` before allocating an investigation or comparing candidate directions.
4. Choose a bounded next investigation from the missing evidence; use optional roles only where separate context adds useful coverage. Read `references/workspace.md` before allocating scratch work or promoting its results.
5. Validate actual role returns and source support, then revise, combine or stop assignments as findings change the decision.
6. Read `references/synthesis.md` before drafting retained documents, a roadmap, or resume facts; follow `get-context docs` and its relevant writing instructions before document work.
7. Save proportionate current evidence and planning notes, update changed resume facts and report the result and next decision.
8. End with the research outcome; start implementation or another product action only within the user's authorization.

## Completion

Return compared directions, supporting sources and coverage limits, recommendations versus user decisions,
retained document paths, conditional roadmap and unresolved questions. A bounded partial result is valid when
its missing evidence is explicit; do not report an unexecuted role, unavailable check or speculative choice as verified.

Example: `/incubate-research Compare ways to organize technical reading for a solo-maintained product; research alternatives and propose initial documents and a roadmap.`
