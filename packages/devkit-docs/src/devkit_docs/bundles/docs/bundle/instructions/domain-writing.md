---
name: domain-writing
description: Read before writing or editing domain/ under a docs root. Defines formal domain identity, concepts, identities, relationships and lifecycles, supporting artifacts and ownership.
---

# Domain Writing

1. Start from `../templates/domain.md`; read `living-spec-writing.md` when responsibility crosses roles.
2. Before writing, settle the one reader question the document answers; if the content answers none, drop it, and if
   it answers several, split it into documents that each answer one.
3. Write a canonical `docs/domain/<area>/DOMAIN-<word-led-lowercase-kebab-slug>.md`, or the same path under a
   registered package docs root; reserve a repository-wide unique ID, use the stem as `id` and the area directory name
   as `area`. Choose the area name; on an area move, move the file and update `area`, never the ID.
4. Supply nonempty string `id`, double-quoted `title`, `status` and double-quoted English `summary`; use draft, active
   or retired and the first H1 `# [ID] title` matching the metadata. Keep the summary within 300 characters by
   default.
5. Open with an unheaded lead paragraph under the H1 stating the concepts readers confuse, with at most one sentence
   phrased as a question; add no question section or label.
6. Under `## Relationship overview`, explain concepts, identities, relationships and lifecycles around a
   `Concept or relationship | Distinction | Authoritative owner` table; cite existing behavioral/permission owners
   instead of copying their normative statements.
7. Include an example that distinguishes the confused concepts, in the overview or a worked-example section; keep
   concise term definitions in the glossary and point to it instead of defining terms here.
8. Close with `## Authority boundary`, naming what the document does not settle and the owner that does by full ID,
   then `## Maintenance and next action`, naming the change that requires an update and the next useful reader action.
9. Link only useful related_designs, related_domains, related_operations, related_capabilities or related_usecases IDs
   as lists; keep aliases as same-prefix identity, never relations. Require no reciprocal links or reading order.
10. Give independent Markdown detail its own formal peer ID; keep parent-owned support under
    `DOMAIN-<slug>/artifacts/` beside the document in its area directory, link it from the parent and name the parent
    in ID-free supporting Markdown.
11. On rename/root move, carry artifacts and repair ordinary links; on split/reclassification, assign each artifact
    one canonical parent. Keep a cross-kind predecessor retired, and use only same-prefix aliases for renames.
12. Omit proposal, decomposed_from, depends_on, milestone, supersedes and superseded_by; use conceptual prose and
    typed related_* fields for relationships. Retire with an explanation and optional successor reference.
13. Omit entrypoints; use ordinary source/artifact links and existing owner references where useful.
14. Delete every template HTML comment before `devkit rules check`; agents read the raw Markdown, where comments stay
    visible.
15. Run `devkit rules check` and fix identity, format, summary, reference and applicable entrypoint errors; review
    semantic ownership and ordinary artifact/source link destinations separately.
