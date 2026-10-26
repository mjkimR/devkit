---
id: FB-plan-branch-depends-on-not-relocated
title: A dependency's handoff misses depends_on edges on plan branches
scope: repo
kind: friction
category: missing-capability
target: devkit spec proposal handoff
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-plan-branch-depends-on-not-relocated] A dependency's handoff misses depends_on edges on plan branches

## 1. Friction / Question (friction, question)

- **Context**: Planning `SPEC-ux-documentation` added `SPEC-foundation-documents` to its `depends_on` on its own
  Planning branch while that prerequisite was still in Planning.
- **Expectation**: When the prerequisite is handed off, the dependent's edge follows the PROP-to-SPEC relocation.
- **Actual**: Handoff rewrites incoming references on the branch it runs on; an edge that exists only on another
  Planning branch keeps the deleted PROP ID, and after merging `main` the dependent's handoff would refuse with
  `SPEC_PROPOSAL_INVALID` (`challenger-04` finding 1).
- **Workaround (or Interpretation Chosen)**: The proposal tells the Host to rewrite every handed-off `depends_on`
  entry to its SPEC ID after each merge of `main`, before `plan-accept`.
- **Suggestion**: Resolve a `depends_on` PROP ID to the spec that carries it as an alias after handoff, or have
  `devkit spec proposal check` report the stale edge with the replacement ID and a `devkit rules fix` repair.

## Diagnostic Details

- **Reproduction**: unknown; derived from `CAP-DLV-proposal-incubation` section 4.5 and the branch layout, not run.
- **Expected / Actual**: Expected the edge to resolve after the prerequisite's handoff; actual stale PROP ID.
- **Versions**: plan branch based on `main` at `96df5d86`.
- **Conditions**: A dependent proposal in Planning on its own branch while a prerequisite is handed off from `main`.
- **Workarounds Attempted**: The Host rewrite note in the proposal.
- **Related Assets**: `CAP-DLV-proposal-incubation`, `CAP-DOCS-document-model`.

## Evidence

```text
proposal.md frontmatter: depends_on: [PROP-table-driven-document-kinds, PROP-foundation-documents]
envelopes/challenger-04.yaml finding 1: the foundation handoff from main cannot rewrite this branch's edge.
```

## Disposition

Resolved by existing behavior. `RULE-document-reference` already reports a `depends_on` entry whose proposal was
handed off as fixable (`` <ID> was handed off; reference `SPEC-<slug>` ``), and `devkit rules fix` rewrites it. After
merging `main` into this branch, `devkit rules fix` rewrote the table-driven edge to
`SPEC-table-driven-document-kinds`; the `SPEC-foundation-documents` edge is repaired the same way after its handoff
lands on `main`. The Host procedure is: merge `main`, run `devkit rules fix` on the proposal.
