---
name: operations-writing
description: Read before writing or editing operations/ under a docs root. Defines formal operations identity, symptoms, evidence and existing action-owner routing, supporting artifacts and ownership.
---

# Operations Writing

1. Start from `../templates/operations.md`; read `living-spec-writing.md` when responsibility crosses roles.
2. Write a canonical `docs/operations/OPS-<word-led-lowercase-kebab-slug>.md`, or the same flat path under a
   registered package docs root; reserve a repository-wide unique ID and use the stem as `id`.
3. Supply nonempty string `id`, `title`, `status` and double-quoted English `summary`; use draft, active or retired
   and the first H1 `# [ID] title` matching the metadata. Keep the summary within 300 characters by default.
4. Explain symptoms, evidence and existing action-owner routing; cite existing behavioral/permission owners instead of copying their normative statements.
5. Link only useful related_designs, related_domains, related_operations, related_capabilities or related_usecases
   IDs as lists; keep aliases as same-prefix identity, never relations. Require no reciprocal links or reading order.
6. Give independent Markdown detail its own formal peer ID; keep parent-owned support under
   `OPS-<slug>/artifacts/`, link it from the parent and name the parent in ID-free supporting Markdown.
7. On rename/root move, carry artifacts and repair ordinary links; on split/reclassification, assign each artifact
   one canonical parent. Keep a cross-kind predecessor retired, and use only same-prefix aliases for renames.
8. Omit area, proposal, decomposed_from, depends_on, milestone, supersedes and superseded_by; use conceptual prose
   and typed related_* fields for relationships. Retire with an explanation and optional successor reference.
9. Omit entrypoints; use ordinary source/artifact links and existing owner references where useful.
10. Run `devkit rules check` and fix identity, format, summary, reference and applicable entrypoint errors; review
    semantic ownership and ordinary artifact/source link destinations separately.
