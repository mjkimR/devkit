---
id: FB-refs-rewritten-notice-docstring
title: The refs-rewritten notice docstring still names only proposal and PADR rewrites
scope: repo
kind: friction
category: other
target: packages/devkit-spec/src/devkit_spec/base/errors.py
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-17
---

# [FB-refs-rewritten-notice-docstring] The refs-rewritten notice docstring still names only proposal and PADR rewrites

Documentation drift in a code docstring.

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-handoff-sibling-alias-rewrite` made the handoff rewrite stale alias references in the carried
  documents and widened the `SPEC_PROPOSAL_REFS_REWRITTEN` message and its `CAP-DLV-proposal-lifecycle` §4.8 row.
- **Expectation**: The `ProposalReferencesRewrittenNotice` docstring describes the same trigger as the message and
  the §4.8 row.
- **Actual**: The docstring still reads "ID references to the proposal or its PADRs now name the spec or the ADRs";
  `errors.py` was outside the Unit's declared boundary, so the reconcile review waived it.
- **Workaround (or Interpretation Chosen)**: The message and §4.8 row are authoritative; the docstring was left.
- **Suggestion**: Widen the docstring to "ID references now name the spec, the ADRs or the current ID of a stale
  reference" in the next change that touches `base/errors.py`.

## Evidence

```text
packages/devkit-spec/src/devkit_spec/base/errors.py: class ProposalReferencesRewrittenNotice docstring
reconcile-check-01 of SPEC-handoff-sibling-alias-rewrite: P3 waived as out of boundary
```
