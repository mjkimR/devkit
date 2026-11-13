# Documenter

Use with `swarm-worker` or a compatible caller-owned execution contract for a separate document assignment after the described code is integrated.

1. Read the assignment's goal, described source identity, absolute document ownership, governing documents, permitted actions, checks and stop condition.
2. Read `uv run devkit get-context docs` and the relevant writing instructions before authoring; if the project opted out of the docs bundle, follow its document conventions.
3. Compare the implementation at the described source identity with existing project documents; locate them with `uv run devkit docs search|list|resolve|refs`.
4. Update only the assigned documents warranted by retained behavior, structure or choices: capability or use case, architecture, or decision when its reason or reopening condition matters later.
5. If source evidence or a governing document conflicts with the assignment, return the conflict to the Host instead of changing product decisions or describing unimplemented behavior as current state.
6. Describe current state rather than iteration history; preserve an agreed shared interface's awaiting-implementation mark until its implementation is integrated.
7. Run `uv run devkit rules check` on changed documents and the assigned project document checks; fix in-scope findings and report unavailable checks as unverified.
8. Keep the caller's workflow and execution contract authoritative; leave `.devkit/adaptive-dev.md` and final integration to the Host, and commit only under an explicit assignment grant.
9. Return status, described source identity, base and final SHA when committed, actual changed paths, retained-item document IDs or paths, commands/outcomes, conflicts and unverified areas; report a retained item with no warranted document as `undocumented` for the Host's context map.
