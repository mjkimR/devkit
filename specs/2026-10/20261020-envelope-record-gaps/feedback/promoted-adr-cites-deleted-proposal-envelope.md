---
id: FB-promoted-adr-cites-deleted-proposal-envelope
title: Promoted ADRs cite proposal envelopes the handoff deleted
scope: repo
kind: friction
category: docs-mismatch
target: devkit spec proposal handoff (PADR promotion and reference rewrite)
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-promoted-adr-cites-deleted-proposal-envelope] Promoted ADRs cite proposal envelopes the handoff deleted

## 1. Friction / Question (friction, question)

- **Context**: Development of `SPEC-envelope-record-gaps` read the three ADRs its handoff promoted from PADRs.
- **Expectation**: References in a promoted ADR resolve after handoff, as the handoff rewrites `PROP-`/`PADR-` IDs
  and moves `materials/` to `docs/materials/` (the ADRs' material links were rewritten).
- **Actual**: `ADR-review-and-reconcile-verification` and `ADR-proposal-acceptance` cite the
  user's answers as `envelopes/answer-01.yaml`, a file of the proposal bundle the handoff deleted. The path names
  nothing in the current tree and nothing says it is historical; the spike evidence, by contrast, carries a
  `Historical proposal source: Git <sha>:...` line for its deleted sources.
- **Workaround (or Interpretation Chosen)**: Left the accepted ADRs unchanged (the delegated boundary allows only
  wording fixes of the ID rewrite); the answers are recoverable from Git at the handoff's parent commit.
- **Suggestion**: Have the handoff rewrite unit-relative envelope paths in promoted decisions to a Git-pinned
  historical source (as the feedback and materials retirement does), or have the PADR template cite answers by
  question id and decision only.

## Evidence

```text
docs/decisions/2026-10/20261020-reverify-closes-challenger-rounds.md, section 4:
  "(the user's answer `answer-fold-round`, `envelopes/answer-01.yaml`)"
docs/decisions/2026-10/20261020-proposal-boundaries-name-existing-paths.md, section 4:
  "(the user's answer `new-boundary-paths`, `envelopes/answer-01.yaml`)"
git show --stat 03eef3f: docs/proposals/PROP-envelope-record-gaps/envelopes/answer-01.yaml deleted
```

## Disposition

Directly resolved by `SPEC-feedback-handoff-references`. Dropped-record references now identify verified full-commit Git evidence; unavailable history is reported unresolved. Both identified ADR citations were repaired without decision changes.

Verification: five regression cases failed before the fix and pass after it; 1,115 affected tests passed,
with 21 record tests rerun after the final refinement. Lint, type checks and independent code review passed.
The historical source was verified with `git show`. Integration remains a separate Host step.
