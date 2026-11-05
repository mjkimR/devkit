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
7. If critique can change the choice, pass actual candidates to the critic and normally refine once.
   Stop when useful directions and material uncertainty are clear; no role must prove its benefit through an experiment.
8. Keep retained writes with the coordinator and only at an explicitly requested destination.

Example assignment: read the absolute installed solution-explorer role first; explore cross-process status sharing
with the premise that an existing store owns status. Keep the supplied latency and access constraints. Read only
the supplied schema and consumer code. Return ownership, stale/failure behavior, benefit, adoption cost and the
assumption that could reverse the recommendation. Stop after the mechanism is concrete and unknowns are named.
