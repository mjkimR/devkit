---
id: FB-handoff-leaves-stale-sibling-proposal-aliases
title: Handoff commit is refused when the carried proposal cites a sibling proposal handed off earlier
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal handoff
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-17
---

# [FB-handoff-leaves-stale-sibling-proposal-aliases] Handoff commit is refused when the carried proposal cites a sibling proposal handed off earlier

## 1. Friction / Question (friction, question)

- **Context**: The Host handed off `SPEC-adr-body-metadata-removal` (then PROP-adr-body-metadata-removal). Its
  `proposal.md` cited the sibling proposal PROP-formal-doc-padding-trim three times. That sibling was handed off, and
  its spec integrated, after this proposal's Planning had merged into the base, so the base `proposal.md` already
  held three alias references to `SPEC-formal-doc-padding-trim`.
- **Expectation**: The handoff transaction carries the proposal into a spec whose references resolve, and its commit
  passes the commit gate like any other handoff.
- **Actual**: The handoff rewrote references to its own proposal ID, but not references to the other, already
  handed-off proposal. The carried `spec.md` kept the three PROP-formal-doc-padding-trim references, and the
  transaction's commit was refused (`SPEC_HANDOFF_COMMIT_REFUSED` with `GATE_RULES_FAILED`, alias references in the
  staged spec).
- **Workaround (or Interpretation Chosen)**: The Host ran `devkit rules fix` on the carried spec, which rewrote the
  three references to `SPEC-formal-doc-padding-trim`, and committed the staged handoff by hand.
- **Suggestion**: Before the handoff commit, rewrite every alias reference in the carried and promoted files to its
  current ID, as `devkit rules fix` does, or run that fix as part of the transaction; alternatively make
  `devkit spec proposal accept` (plan acceptance) or the sibling's handoff rewrite references in proposals already
  merged on the base. Related, not the same symptom: `FB-handoff-rewrite-edits-sibling-draft` (resolved), which
  covers a sibling draft still in Planning.

## Diagnostic Details

- **Reproduction**: Merge the Planning of proposal A, which cites proposal B; hand off and integrate B; then hand off
  A. The handoff commit is refused on A's carried spec.
- **Expected / Actual**: A committed handoff / `SPEC_HANDOFF_COMMIT_REFUSED`, `GATE_RULES_FAILED` on three alias
  references, with the transaction left staged.
- **Versions**: base `main` at `8c86857bb`; handoff commit `dd9850334`.
- **Conditions**: local-orchestrated delivery, two sibling proposals planned in parallel and handed off in sequence.
- **Workarounds Attempted**: `devkit rules fix` on the carried spec, then a manual commit of the staged handoff;
  succeeded. The same three stale references in the base `proposal.md` were removed with the proposal by the handoff.
- **Related Assets**: `devkit spec proposal handoff`, `devkit spec proposal accept`, `RULE-document-reference`,
  `CAP-DLV-proposal-lifecycle` §4.1.

## Evidence

```text
handoff commit: SPEC_HANDOFF_COMMIT_REFUSED (GATE_RULES_FAILED)
staged <worktree>/specs/2026-11/20261117-adr-body-metadata-removal/spec.md: 3 alias references to the sibling
proposal ID PROP-formal-doc-padding-trim (now SPEC-formal-doc-padding-trim)
fix: devkit rules fix <spec.md>, then a manual commit of the staged handoff (dd9850334)
```

## Resolution

- **Disposition**: `SPEC-handoff-sibling-alias-rewrite` resolved it: after its existing rewrite passes, the handoff
  runs `rewrite_aliases` on the carried spec bundle files and the promoted ADRs, rewriting a handed-off sibling's
  `PROP-<slug>` to its `SPEC-<slug>` and another document's alias to its ID with the resolution
  `RULE-document-reference` fixes, reported as `[REWRITTEN ... kind=id]`, so the composed commit passes the gate.
  `CAP-DLV-proposal-lifecycle` §4.1 and §4.3 state the guarantee. Verified by the regression tests in
  `test_proposal_aliases.py` and `just test-affected --base main` (1789 passed).
