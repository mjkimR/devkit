---
id: FB-scout-materials-cite-full-ids
title: A scout's materials file used short ARCH IDs and the commit gate refused the Planning fold
scope: repo
kind: suggestion
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/scout.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-scout-materials-cite-full-ids] A scout's materials file used short ARCH IDs and the commit gate refused the Planning fold

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The scout contract asks for `path:line` citations internally and lets the scout write one
  file under the proposal's `materials/`. It says nothing about document IDs. A scout wrote two architecture
  documents by their number prefix alone (the first two segments of the ID, without the slug) in prose inside
  `materials/internal-constraints.md`; `RULE-id-convention` refused the fold commit with `GATE_RULES_FAILED`, and
  the Host edited the scout's file by hand before committing.
- **Proposed Procedure**: Add one line to the scout contract's write rule (and to the `spec-delegate` scout payload
  row): a written artifact cites documents by their full ID in backticks (`ARCH-08-1-agent-output`, never its
  number prefix alone), because `materials/` is committed and checked by `RULE-id-convention`.
- **Expected Benefit**: No hand edit of a support role's artifact by the Host, and no second commit attempt.
- **Cost & Risk**: One sentence in a contract and a payload reference; no behavior change.
- **Attempted**: Observed in this session; the one-line fix was applied to the materials file by hand.

## Diagnostic Details

- **Reproduction**: Delegate a `scout` with a `materials/` write path; the scout cites an ARCH document by its
  number prefix in prose; `git commit` in the Planning worktree.
- **Expected / Actual**: Expected the scout's artifact to pass the commit gate; actual `GATE_RULES_FAILED` with two
  `RULE-id-convention` violations at `materials/internal-constraints.md:115` and `:149`.
- **Versions**: worktree `plan-maintenance-history` at `c0d060b7`.
- **Conditions**: `RULE-id-convention` applies to `docs/proposals/**/materials/`.
- **Workarounds Attempted**: Edited the two lines to full IDs and recommitted; succeeded.
- **Related Assets**: `.devkit/managed/spec/subagents/scout.md`, `.claude/skills/spec-delegate/references/payload.md`,
  `RULE-id-convention`.

## Evidence

```text
[ERROR]  (GATE_RULES_FAILED) 2 rule violation(s) in the staged tree
[DETAIL] RULE-id-convention docs/proposals/PROP-maintenance-history/materials/internal-constraints.md:115: Date- or number-based identifier reference "<number prefix of ARCH-08-1-agent-output>"
[DETAIL] RULE-id-convention docs/proposals/PROP-maintenance-history/materials/internal-constraints.md:149: Date- or number-based identifier reference "<number prefix of ARCH-05-2-components>"
```
