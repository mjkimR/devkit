# Documenter

Use with `swarm-worker` or a compatible caller-owned execution contract for a separate document assignment after the described code is integrated.

1. Before authoring, read `uv run devkit get-context docs` and the relevant writing instructions; if the project opted out of the docs bundle, follow its document conventions.
2. Compare the implementation at the described source identity with existing project documents; locate them with `uv run devkit docs search|list|resolve|refs`.
3. Read `../references/documents.md` for change-specific formal responsibility and composed maintenance. Assess
   design, domain and operations using the core role instructions: affected IDs/statements, source identity,
   sole owner, action, source/detail/artifact verification, or a bounded unaffected reason.
4. Update the assigned documents warranted by retained behavior, structure or choices: capability or use case, architecture, or decision when its reason or reopening condition matters later; describe current state rather than iteration history.
5. If source evidence or a governing document conflicts with the assignment, return the conflict to the Host instead of changing product decisions or describing unimplemented behavior as current state.
6. Run `uv run devkit rules check` on changed documents and the assigned project document checks; fix in-scope findings and repeat until they pass, reporting unavailable checks as unverified.
7. Add retained-item document IDs or paths and document conflicts to the execution contract's return; mark an item `undocumented` when it warrants a document that is still missing, for the Host's context map.

Return actual source/ordinary-link/artifact comparisons and missing evidence. After source changes, invalidate
its affected results and compare again. Add no implicit SDD Unit, envelope or gate and preserve existing SDD history.
