---
name: domain-writing
description: Read before writing or editing domain/ under a docs root. Defines a formal domain document's path, lead, relationship table, worked example, closing and support location.
---

# Domain Writing

1. Read `living-spec-writing.md` "Responsibility and design navigation" for the steps all formal documents share,
   and start from `../templates/domain.md`.
2. Write the document at `docs/domain/<area>/DOMAIN-<slug>.md`, or the same path under a registered package docs
   root.
3. Open with a lead paragraph stating the concepts readers confuse.
4. Under `## Relationship overview`, explain concepts, identities, relationships and lifecycles around a
   `Concept or relationship | Distinction | Authoritative owner` table; cite existing behavioral and permission
   owners instead of copying their normative statements, and point to the glossary instead of defining terms.
5. Include a worked example that separates the confused concepts, in the overview or in its own section.
6. Close with `## Authority boundary` only when owners neither the table nor the body names, or limits of what the
   document can conclude, remain; then `## Update triggers`, naming the source changes that make the document stale
   by capability section, field, code or use case.
7. Keep parent-owned support under `DOMAIN-<slug>/artifacts/` beside the document.
