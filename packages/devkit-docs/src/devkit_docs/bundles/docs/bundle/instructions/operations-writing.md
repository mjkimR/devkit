---
name: operations-writing
description: Read before writing or editing operations/ under a docs root. Defines a formal operations document's path, lead, routing table, no-row fallback, normal-state observation, closing and support location.
---

# Operations Writing

1. Read `living-spec-writing.md` "Responsibility and design navigation" for the steps all formal documents share,
   and start from `../templates/operations.md`.
2. Write the document at `docs/operations/OPS-<slug>.md`, or the same flat path under a registered package docs
   root.
3. Open with a lead paragraph stating the observed symptom and why the obvious evidence is not enough.
4. Under `## Routing`, route each symptom or state to its existing action owner through a
   `Symptom or state | Discriminating evidence | Next useful owner` table; cite existing behavioral and permission
   owners instead of copying their normative statements or recovery steps.
5. Below the table, state where evidence that matches no row goes; if that fallback repeats a row, merge it into
   the row.
6. Under `## Normal-state observation`, state the observation that confirms the normal state after the owner's
   action, and its owner.
7. Close with `## Authority boundary` only when owners neither the table nor the body names, or limits of what the
   evidence can conclude, remain; then `## Update triggers`, naming the source changes that require reviewing the
   routing by capability section, field, code or source entry point.
8. Keep parent-owned support under `OPS-<slug>/artifacts/` beside the document.
