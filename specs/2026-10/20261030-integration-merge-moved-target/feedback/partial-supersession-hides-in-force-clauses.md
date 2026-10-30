---
id: FB-partial-supersession-hides-in-force-clauses
title: Partially superseded ADRs hide their in-force clauses and have no structured partial supersession
scope: repo
kind: friction
category: missing-capability
target: docs/decisions/ (decision kind in devkit-docs) and devkit spec proposal padr
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-partial-supersession-hides-in-force-clauses] Partially superseded ADRs hide their in-force clauses and have no structured partial supersession

## 1. Friction / Question (friction, question)

- **Context**: Planning a decision that replaces one clause (local containment before integration) of
  `ADR-local-and-pull-request-integration`, whose other clauses (merge construction, readiness, policy binding)
  remain the current contract.
- **Expectation**: The current integration contract is findable with `devkit docs search`, and a decision that
  replaces part of an ADR can say so in its metadata.
- **Actual**: That ADR is `status: superseded` (by `ADR-host-cli-lifecycle-authority`, which replaced only its native
  confirmation clauses), a terminal status, so search does not return it although `CAP-INT-mcp-services` names it as
  the current merge contract. `superseded_by` is a scalar that no code reads, `supersedes` is not parsed for ADRs, and
  the PADR scaffold has no `supersedes` key; a second partial superseder can be expressed only in prose.
- **Workaround (or Interpretation Chosen)**: The PADR adds `supersedes` by hand plus a "supersedes only ... remain in
  force" sentence, and Development will add a "Superseded in part by" line to the old ADR body, following existing
  precedents.
- **Suggestion**: Give decisions a structured partial supersession (for example a `status: amended` or a
  `superseded_in_part_by` list kept searchable), or a hygiene step that splits a partially superseded ADR's in-force
  clauses into an accepted ADR; let the PADR scaffold offer `supersedes`.

## Diagnostic Details

- **Reproduction**: `devkit docs search "Local and Pull Request Integration"` does not return the ADR;
  `devkit docs resolve ADR-local-and-pull-request-integration` shows `status=superseded`.
- **Expected / Actual**: Expected the in-force merge and readiness clauses to stay discoverable; actual: hidden as
  terminal history.
- **Versions**: plan base `fdba6646`.
- **Conditions**: Any ADR superseded in part.
- **Workarounds Attempted**: Prose annotation (above); not a structured fix.
- **Related Assets**: `ADR-local-and-pull-request-integration`, `ADR-host-cli-lifecycle-authority`,
  `CAP-INT-mcp-services`, `CAP-DOCS-document-model`, `devkit spec proposal padr`.

## Evidence

```text
docs/decisions/2026-10/20261022-local-and-pull-request-integration.md: status: superseded,
  superseded_by: ADR-host-cli-lifecycle-authority; body line 19: "The merge construction, readiness, policy binding,
  ... remain in force."
packages/devkit-docs/src/devkit_docs/features/documents/models/parse.py:68-69: supersedes skipped on non-unit anchors.
docs/decisions/README.md:25-28: superseded_by is a single value.
Scout envelope envelopes/scout-01.yaml (decision mechanics finding).
```

- **Disposition**: `SPEC-partial-adr-supersession`: an ADR is `superseded` only when wholly replaced; a partly replaced
  ADR stays `accepted` without `superseded_by` and carries a "Superseded in part by" line (`CAP-DOCS-document-model`,
  `decision-writing`, the decision template); the PADR scaffold offers a commented `supersedes` that handoff carries;
  `ADR-local-and-pull-request-integration` and three other misclassified ADRs are `accepted` again, and missing
  pointers were added. The suggested structured field was not adopted by the agreed scope. Verified:
  `devkit docs search "Local and Pull Request Integration"` returns the ADR first (`status=accepted`), the scaffold,
  handoff, rule and guidance tests pass, and `just test-affected` passed 2081.
