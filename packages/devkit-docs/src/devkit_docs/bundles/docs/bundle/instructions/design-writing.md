---
name: design-writing
description: Read before writing or editing designs/ under a docs root. Defines formal design identity, implementation mechanisms, examples and datasheets, supporting artifacts and ownership.
---

# Design Writing

1. Start from `../templates/design.md`; read `living-spec-writing.md` when responsibility crosses roles.
2. Before writing, settle the one reader question the document answers; if the content answers none, drop it, and if
   it answers several, split it into documents that each answer one.
3. Write a canonical bundle `docs/designs/<area>/DESIGN-<word-led-lowercase-kebab-slug>/design.md`, or the same path
   under a registered package docs root; reserve a repository-wide unique ID, use the bundle directory name as `id`
   and the area directory name as `area`. Choose the area name; on an area move, move the bundle and update `area`,
   never the ID.
4. Supply nonempty string `id`, double-quoted `title`, `status` and double-quoted English `summary`; use draft, active
   or retired and the first H1 `# [ID] title` matching the metadata. Keep the summary within 300 characters by
   default.
5. Open with an unheaded lead paragraph under the H1 stating the problem the mechanism solves, with at most one
   sentence phrased as a question; add no question section or label.
6. Explain implementation mechanisms, examples and datasheets under topic headings named for what they explain; cite
   existing behavioral/permission owners instead of copying their normative statements.
7. Close with `## Authority boundary`, naming what the document does not settle and the owner that does by full ID,
   then `## Maintenance and next action`, naming the change that requires an update and the next useful reader action.
8. Link only useful related_designs, related_domains, related_operations, related_capabilities or related_usecases IDs
   as lists; keep aliases as same-prefix identity, never relations. Require no reciprocal links or reading order.
9. Give independent Markdown detail its own peer bundle; keep parent-owned support at any depth inside the bundle
   beside `design.md`, link it from the parent and name the parent in ID-free supporting Markdown. Never nest a bundle
   or give Markdown inside a bundle an ID.
10. On rename/root move, move the whole bundle and repair ordinary links; on split/reclassification, assign each
    artifact one canonical parent. Keep a cross-kind predecessor retired, and use only same-prefix aliases for
    renames.
11. Omit proposal, decomposed_from, depends_on, milestone, supersedes and superseded_by; use conceptual prose and
    typed related_* fields for relationships. Retire with an explanation and optional successor reference.
12. Use optional existing workspace-relative entrypoint paths for source reading/reverse lookup; on source deletion
    remove or replace obsolete declarations even when retired.
13. Delete every template HTML comment before `devkit rules check`; agents read the raw Markdown, where comments stay
    visible.
14. Run `devkit rules check` and fix identity, format, summary, reference and applicable entrypoint errors; review
    semantic ownership and ordinary artifact/source link destinations separately.
