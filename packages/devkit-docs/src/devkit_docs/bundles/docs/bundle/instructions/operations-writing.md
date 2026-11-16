---
name: operations-writing
description: Read before writing or editing operations/ under a docs root. Defines formal operations identity, symptoms, evidence and existing action-owner routing, supporting artifacts and ownership.
---

# Operations Writing

1. Start from `../templates/operations.md`; read `living-spec-writing.md` when responsibility crosses roles.
2. Before writing, settle the one reader question the document answers; if the content answers none, drop it, and if
   it answers several, split it into documents that each answer one.
3. Write a canonical `docs/operations/OPS-<word-led-lowercase-kebab-slug>.md`, or the same flat path under a
   registered package docs root; reserve a repository-wide unique ID and use the stem as `id`.
4. Supply nonempty string `id`, double-quoted `title`, `status` and double-quoted English `summary`; use draft, active
   or retired and the first H1 `# [ID] title` matching the metadata. Keep the summary within 300 characters by
   default.
5. Open with an unheaded lead paragraph under the H1 stating the observed symptom, with at most one sentence phrased
   as a question; add no question section or label.
6. Under `## Routing`, route each symptom or state to its existing action owner through a
   `Symptom or state | Discriminating evidence | Next useful owner` table; cite existing behavioral/permission owners
   instead of copying their normative statements or recovery steps.
7. Under `## Normal-state observation`, state the observation that confirms the normal state after the owner's action,
   and its owner.
8. Close with `## Authority boundary`, stating that the document routes and owns no recovery, naming the action,
   permission and readiness owners by full ID and what the evidence cannot conclude, then
   `## Maintenance and next action`, naming the change that requires reviewing the routing and the next useful action
   for evidence matching no row.
9. Link only useful related_designs, related_domains, related_operations, related_capabilities or related_usecases IDs
   as lists; keep aliases as same-prefix identity, never relations. Require no reciprocal links or reading order.
10. Give independent Markdown detail its own formal peer ID; keep parent-owned support under `OPS-<slug>/artifacts/`,
    link it from the parent and name the parent in ID-free supporting Markdown.
11. On rename/root move, carry artifacts and repair ordinary links; on split/reclassification, assign each artifact
    one canonical parent. Keep a cross-kind predecessor retired, and use only same-prefix aliases for renames.
12. Omit area, proposal, decomposed_from, depends_on, milestone, supersedes and superseded_by; use conceptual prose
    and typed related_* fields for relationships. Retire with an explanation and optional successor reference.
13. Omit entrypoints; use ordinary source/artifact links and existing owner references where useful.
14. Delete every template HTML comment before `devkit rules check`; agents read the raw Markdown, where comments stay
    visible.
15. Run `devkit rules check` and fix identity, format, summary, reference and applicable entrypoint errors; review
    semantic ownership and ordinary artifact/source link destinations separately.
