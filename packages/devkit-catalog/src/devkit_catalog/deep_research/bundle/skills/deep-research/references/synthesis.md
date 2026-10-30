# Retain the investigation as one indexed material

1. Review the compared directions and evidence before drafting; retain user decisions separately from recommendations and assumptions.
2. For a new investigation, choose a slug and check that `uv run devkit docs resolve MAT-<slug>` finds no document and that `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` is absent; otherwise choose another slug. Never overwrite an existing material.
3. Create that directory with the index `<YYYYMMDD>-<slug>.md`: frontmatter `id: MAT-<slug>` and `created_at`, H1 `# [MAT-<slug>] <title>`. Put the run's other retained notes beside it and link them from the index by relative path; a note carries its own `MAT-` ID only when a consumer cites it alone.
4. Ask discovery-planner for drafts when separate synthesis is useful; validate its claims against the actual sources, role returns and user decisions before saving.
5. Cover the logical contents below proportionately in the index or its linked notes; label proposed behavior and conditional work as planned, not current capability or an accepted delivery commitment.
6. End the index with a `Status:` line (`complete` or `partial`), its open questions and the next investigation.
7. When the user names a `partial` material to resume the same investigation, update that index in place. Never rewrite a `complete` material: later research creates a new material that cites it.
8. Before returning, inspect the written files and report actual paths, evidence coverage and unverified decisions; verify that the next action grants no authority absent from the user's request. Retain selected supporting evidence and important rejected alternatives, and resolve required references without transient-only files.
9. Leave the files uncommitted and tell the user to commit them through the project's Git policy; a proposal can cite the material only once it is on the base.

## Logical contents

| Content | What makes it useful |
| --- | --- |
| Research brief | Question, intended users, problem, representative usage, value hypothesis, constraints and scope of the investigation |
| Research and alternatives | Supported claims and sources, what was inspected, contradictions, unknowns and materially different candidate directions |
| Direction and architecture | Provisional recommendation, actual user decisions, assumptions, consequences, checks to run or defer, and conditions to reopen an alternative |
| Initial roadmap | Outcomes/questions by horizon, ordering/dependencies, validation signals and conditional implementation slices |

Do not require a fixed file count; a small investigation fits in the index alone. A roadmap distinguishes learning
work from build work and omits unsupported dates or ownership promises. Link each consequential choice to its
evidence or the missing check. A vendor feature claim is not observed usability; a working technical experiment is
not proof of demand.

## Citing the material

Consumers cite the index ID in a code span (`` `MAT-<slug>` ``) and never copy or move the material into their own
directories: a proposal, spec or decision cites it in prose, and an iteration's current-context note links the same
ID. A material is not a capability, decision, milestone, proposal or work unit; a research recommendation creates no
current capability, user approval or delivery commitment.

Keep current facts and useful alternatives, not an immutable transcript or hidden reasoning log. Retain brief
decision rationale and source references. Report unavailable evidence as unknown, and budget exhaustion as a
bounded partial result.

Example roadmap item: "Determine whether shared edits overlap; depends on observing the current workflow.
Choose conflict handling only after that evidence. Implementation remains conditional on the product decision."
