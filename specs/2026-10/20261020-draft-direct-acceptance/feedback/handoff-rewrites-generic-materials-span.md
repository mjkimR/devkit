---
id: FB-handoff-rewrites-generic-materials-span
title: Handoff rewrites a generic materials/ code span in a PADR to the proposal's own materials path
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal handoff (code-span path rewrite, kind=path)
skill: spec-sync
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-20
---

# [FB-handoff-rewrites-generic-materials-span] Handoff rewrites a generic materials/ code span in a PADR to the proposal's own materials path

## 1. Friction / Question (friction, question)

- **Context**: Development of `SPEC-draft-direct-acceptance` checked the ADRs promoted by the handoff for wording
  the ID rewrite left.
- **Expectation**: a code span that names `materials/` as a generic part of any draft (here: what a session
  reclassification deletes) keeps its meaning after the promotion.
- **Actual**: the handoff's code-span path rewrite (`CAP-DLV-proposal-incubation` 4.7) turned `` `materials/` `` in
  `ADR-session-reclassification-of-a-queued-draft` into this proposal's own preserved materials directory, so the
  decision read as if every reclassification deleted that one directory.
- **Workaround (or Interpretation Chosen)**: restored the generic wording ("its `materials/`") by hand and listed the
  ADR as a reconcile target.
- **Suggestion**: limit the code-span path rewrite in promoted PADRs to spans that name a file of the bundle (a
  concrete path below `materials/`), or report directory-only rewrites in ADRs as `kind=path` lines the agent must
  reread, as `SPEC_PROPOSAL_REFS_REWRITTEN` already asks for IDs.

## Diagnostic Details

- **Reproduction**: a PADR whose body says "deletes the draft, its `materials/`, ..." as a general rule; hand the
  proposal off; read the promoted ADR.
- **Expected / Actual**: expected `` `materials/` ``; actual `` `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` ``.
- **Versions**: handoff commit b8c3a77 of this unit.
- **Conditions**: a proposal with a non-empty `materials/`.
- **Workarounds Attempted**: manual wording fix, recorded in `reconcile.md`.
- **Related Assets**: `CAP-DLV-proposal-incubation` 4.7, `packages/devkit-spec/src/devkit_spec/proposals/rewrite.py`.

## Evidence

```text
ADR line after handoff: "the draft and its gate records, `docs/materials/2026-10/<stamp>-draft-direct-acceptance/`
(kept in Git history only), the `milestone` membership ..."
```
