---
id: FB-agent-guidance-asset-list-drifts
title: Hand-kept spec asset lists drift outside a unit's boundary
scope: repo
kind: friction
category: docs-mismatch
target: CAP-HARN-agent-guidance
origin: agent
severity: workaround
recurring: true
status: open
created_at: 2026-10-26
---

# [FB-agent-guidance-asset-list-drifts] Hand-kept spec asset lists drift outside a unit's boundary

## 1. Friction / Question (friction, question)

- **Context**: Development of `SPEC-ux-documentation` added the `ux-writing` instruction, the `ux-links` and
  `ux-coverage` rules, the `spec-ux-review` skill and the `ux-reviewer` subagent to the `spec` bundle, and a `ux/`
  directory to the `docs-skeleton` seed.
- **Expectation**: The Living Spec lists of the bundle's assets and the repository's directory map follow the bundle.
- **Actual**: `CAP-HARN-agent-guidance` section 4.1 lists the instructions, rules and subagents by name, and
  `docs/README.md` maps the `docs/` directories by hand. Neither is in the unit's write scope, so both stay stale; the
  rule list already omitted `steering-documents` from an earlier unit.
- **Workaround (or Interpretation Chosen)**: Recorded under Deferred work in `REC-ux-documentation`; left for the
  Host.
- **Suggestion**: Replace the hand-kept asset lists with a pointer to `bundle.toml` (or a test that compares them),
  and name `CAP-HARN-agent-guidance` and `docs/README.md` in the boundaries of any proposal that adds a bundle asset
  or a seeded directory.

## Evidence

```text
CAP-HARN-agent-guidance 4.1, rule row: document-reference ... document-summary, code-entrypoints, proposal-boundaries
  (no steering-documents, ux-links, ux-coverage)
CAP-HARN-agent-guidance 4.1, subagent row: challenger, reconcile-reviewer, code-reviewer, scout, planning-worker,
  development-worker (no ux-reviewer)
docs/README.md directory map: capabilities/, usecases/, ... (no ux/)
```
