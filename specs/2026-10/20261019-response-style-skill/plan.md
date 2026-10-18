---
id: PLAN-response-style-skill
spec: SPEC-response-style-skill
---

# Templated skill deployment plan

## Invariant review

Preserve module layering, scalar-only sandboxing, manifest-owned invocation settings, and transaction planning
before writes. Extend the skill source contract in `CAP-DIST-manifest-spec`, projection behavior in
`CAP-DIST-agent-projections`, and template/override semantics in `CAP-DIST-sync-and-transactions`.

## Components

- Resolve exactly one plain or templated skill entry during manifest validation and override reporting.
- Render skill Markdown using the existing renderer; validate final entry frontmatter and invocation keys before
  context insertion. Project rendered filenames and then apply native invocation settings.
- Keep raw override sources/digests and managed rendered consumer paths. Preserve ordinary skills unchanged.
- Move response-style language selection back into the skill template and restore a static guidance reminder.

## Verification

Exercise all native projections, context and user invocation, ordinary Markdown literals, duplicate/collision
rejection, rendered-header and override failures without writes, raw overrides, locked restoration and variable
changes. Run distribution/catalog tests, lint, Pyright, layering, bundle validation and synchronized-state checks.
