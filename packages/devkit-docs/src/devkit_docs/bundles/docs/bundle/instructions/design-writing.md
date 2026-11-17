---
name: design-writing
description: Read before writing or editing designs/ under a docs root. Defines a formal design's path, lead, mechanism, example and datasheet sections, closing and support location.
---

# Design Writing

1. Read `living-spec-writing.md` "Responsibility and design navigation" for the steps all formal documents share,
   and start from `../templates/design.md`.
2. Write the bundle at `docs/designs/<area>/DESIGN-<slug>/design.md`, or the same path under a registered package
   docs root.
3. Open with a lead paragraph stating the problem the mechanism solves.
4. Explain implementation mechanisms and examples under topic headings named for what they explain; cite existing
   behavioral and permission owners instead of copying their normative statements.
   - When the mechanism writes data that a later run, another process or another tool reads back, add a datasheet:
     location pattern, encoding, fields or layout, identity derivation, ordering and one example.
   - Name public entry points, use cases, fields and codes; describe private helpers in words, because their names
     change without notice.
5. Close with `## Authority boundary`, naming the rules the design explains and their owners by full ID, also those
   the body cites inline, then `## Update triggers`, naming the source changes that make the design stale by public
   entry point, use case, field, code or capability section, and the command that rechecks a worked example.
6. Keep parent-owned support at any depth inside the bundle beside `design.md`; give independent Markdown detail its
   own peer bundle and never nest a bundle.
