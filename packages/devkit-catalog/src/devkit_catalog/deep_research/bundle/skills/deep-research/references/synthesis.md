# Retain the investigation as one indexed material

1. Review the requested deliverable, compared directions and evidence before drafting; keep user decisions separate from recommendations and assumptions.
2. For a new investigation, choose a slug for which `uv run devkit docs resolve MAT-<slug>` finds no document and `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` is absent; otherwise choose another. Never overwrite an existing material.
3. Create that directory with the index `<YYYYMMDD>-<slug>.md`: frontmatter `id: MAT-<slug>` and `created_at`, H1 `# [MAT-<slug>] <title>`. Put other retained notes beside it, linked from the index by relative path; a note carries its own `MAT-` ID only when a consumer cites it alone.
4. When separate synthesis is useful, ask discovery-planner for drafts with the requested artifact, intended use and constraints; validate its claims against actual sources, role returns and user decisions.
5. Cover the logical contents below proportionately in the index or linked notes; label proposed behavior and conditional work as planned, not current capability or an accepted delivery commitment.
6. End the index with a `Status:` line (`complete` or `partial`), its open questions and the next investigation.
   For pending cloud work, keep the exact safe prompt, request label/revision, selected attachments, truthful disposition, remaining question and next action in this same partial material, with any report evidence used and its inspection limits, and no transient-only required reference.
7. When the user names a `partial` material to resume the same investigation, update that index in place. Never rewrite a `complete` material; later research creates a new material that cites it.
8. Before retention, check that the draft contains the requested artifact, supports the intended next action and imposes no unwanted prerequisite; repair a mismatch inline or use optional criticism.
   Retain selected supporting evidence and important rejected alternatives, and resolve required references without transient-only files.
   Inspect the written files, report actual paths, evidence coverage and unverified decisions, and verify that the next action grants no authority absent from the user's request.
9. Leave the files uncommitted and tell the user to commit them through the project's Git policy; a proposal can cite the material only once it is on the base.

## Logical contents

| Content | What makes it useful |
| --- | --- |
| Research brief | Requested deliverable, intended use, question, constraints and stop condition; add user/problem framing when it serves the inquiry |
| Research and alternatives | Supported claims and sources, what was inspected, contradictions, unknowns and materially different candidate directions |
| Direction and architecture | Provisional recommendation, actual user decisions, assumptions, consequences, checks to run or defer, and conditions to reopen an alternative |
| Initial roadmap | Relevant next action, outcome dependencies and conditional work; separate optional investigation from prerequisites |

- No fixed file count, output template, repository list or extra form applies; a small investigation fits in the index alone,
  and a factual inquiry uses its requested factual result.
- A roadmap separates learning work from build work and omits unsupported dates or ownership promises.
- Link each consequential choice to its evidence or the missing check. A vendor feature claim is not observed
  usability; a working technical experiment is not proof of demand.
- Name a further check only when its unknown can change a consequential choice; do not turn every uncertainty into
  another research task.
- If the user declines comparative validation, state uncertain benefits and offer a usable starting point without a
  same-task comparison or proof of superiority as a prerequisite.
- Keep current facts, useful alternatives, brief decision rationale and source references, not an immutable
  transcript or hidden reasoning log. Report unavailable evidence as unknown and budget exhaustion as a bounded
  partial result.

Example practical output: for reusable agent configurations, retain repository/file references, what to borrow,
what to omit and a starting composition.

Example roadmap item: "Determine whether shared edits overlap; depends on observing the current workflow.
Choose conflict handling only after that evidence. Implementation remains conditional on the product decision."

## Citing the material

Consumers cite the index ID in a code span (`` `MAT-<slug>` ``) and never copy or move the material into their own
directories: a proposal, spec or decision cites it in prose, and an iteration's current-context note links the same
ID. A material is not a capability, decision, milestone, proposal or work unit; a research recommendation creates no
current capability, user approval or delivery commitment.
