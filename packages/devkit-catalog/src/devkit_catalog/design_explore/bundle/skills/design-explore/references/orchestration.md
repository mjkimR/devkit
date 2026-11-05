# Optional local assignments

1. Select only assignments that can change the useful directions; no role sequence or minimum cast applies.
   - `roles/solution-explorer.md`: reuse with distinct premises about ownership, timing, simplification or mechanisms.
   - `roles/reference-researcher.md`: resolve a bounded precedent or evidence question.
   - `roles/design-critic.md`: test a consequential assumption in a candidate after exploration.
2. Resolve each selected role from the directory containing the invoked `SKILL.md`, not the working directory or
   this reference's directory. If the skill location is missing, locate and verify it before delegation.
   Verify the selected role exists and pass its absolute installed path to a general child; load only that role.
3. Supply a self-contained assignment: role path to read first, problem and goal, premise, hard constraints versus
   preferences, relevant facts and source paths, permitted tools/actions, absolute read/write boundaries, stop
   condition and expected return. Include no product or retained-file writes in a role's write boundary.
4. Where supported, spawn a fresh context without parent conversation inheritance. Keep peer conclusions out of
   first-pass payloads so separate explorers can choose their own mechanisms. Pass relevant facts rather than the
   coordinator's complete narrative. Fresh contexts do not isolate files, credentials or ambient project guidance.
5. If fresh children are unavailable, perform selected passes inline and disclose that these were not independent
   contexts. Do not invent independent roles or returns. A failed or missing role is missing coverage, not agreement.
6. Wait for actual returns and check assigned scope, hard constraints, evidence and unknowns before synthesis.
   Keep plausible unconventional mechanisms visible with their tradeoffs. Resolve disagreements by their
   consequences for this problem rather than votes, averages or a consensus requirement.
7. If critique can change the choice, pass actual candidates to the critic and use the optional response exchange below.
   Stop when useful directions and material uncertainty are clear; no role must prove its benefit through an experiment.
8. Keep retained writes with the coordinator and only at an explicitly requested destination.

Example assignment: read the absolute installed solution-explorer role first; explore cross-process status sharing
with the premise that an existing store owns status. Keep the supplied latency and access constraints. Read only
the supplied schema and consumer code. Return ownership, stale/failure behavior, benefit, adoption cost and the
assumption that could reverse the recommendation. Stop after the mechanism is concrete and unknowns are named.

## Optional critique response

1. Select only supported objections that can change feasibility, a consequential tradeoff or the recommendation
   against the goal or hard constraints. Mere preference and zero supported findings require no author response.
2. After independent first passes, give the original explorer the actual candidate, selected objections, evidence,
   failure conditions, affected choice and preserved constraints. Assign a response using the existing
   `roles/solution-explorer.md`; normally allow one critic pass and at most one author response per affected candidate.
3. If the original explorer cannot return, disclose missing author coverage and label any inline analysis as the
   coordinator's own. Invent no author reply, agreement or independent finding.
4. Validate each actual response: accept and revise, rebut with inspected evidence or explicitly labeled inference,
   or identify a bounded unknown. Keep inaccessible support and uninspected claims visible; a role assertion alone
   does not prove an objection refuted.
5. For each selected objection, report the actual response or revision and the coordinator's reasoned disposition
   against the preserved constraints. Retain surviving alternatives, useful benefits and decision-changing unknowns;
   require no serialized schema, retained document, vote or consensus.
6. Synthesize after the normal exchange; the critic gets no automatic further reply. Before another pass, name a
   concrete unresolved question that can change the recommendation and a finite pass/time bound. If no such question
   exists or the bound is reached, return the unresolved assumption and stop without starting implementation.

Example: a critic shows that a cached status owner can return stale data after a worker crash. The explorer accepts
and revises the mechanism with lease expiry, or rebuts with inspected evidence that the existing store already
expires ownership. The coordinator checks that actual response against the latency constraint and explains whether
it addresses the failure. If expiry behavior is uninspected, retain that unknown instead of claiming the objection
was refuted. A missing explorer return stays missing coverage, even if the coordinator sketches lease expiry inline.
