---
id: FB-reverify-reopens-earlier-resolutions
title: A second reverify of a challenger round reopens findings an earlier reverify resolved
scope: repo
kind: friction
category: tool-error
target: devkit workflow envelope reverify
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-reverify-reopens-earlier-resolutions] A second reverify of a challenger round reopens findings an earlier reverify resolved

## 1. Friction / Question (friction, question)

- **Context**: Planning turn 2 closed challenger findings that the user's answers decided, after turn 1 had already
  resolved the other findings of the same challenger round in `reverify-01.yaml`.
- **Expectation**: `planning.md` step 3 says to close a round with `--resolve <N>` per folded finding; a later
  reverify for the remaining findings should keep the earlier resolutions.
- **Actual**: `reverify --from envelopes/challenger-01.yaml --resolve 4 --resolve 5 --resolve 10` wrote a new
  envelope that copied the findings from the challenger envelope and marked every finding except 4, 5 and 10 as
  `open` again (`open_findings=8`).
- **Workaround (or Interpretation Chosen)**: Deleted the uncommitted envelope and reran with `--resolve` for every
  finding the turn-1 reverify had resolved, as well as the new ones.
- **Suggestion**: Seed a reverify from the latest reverify of the same review, or document in `planning.md` and the
  command help that each reverify must restate every resolution.

## Diagnostic Details

- **Reproduction**: Run `devkit workflow envelope reverify --unit <proposal> --stage spike --from envelopes/challenger-01.yaml --resolve 4`
  on a unit whose `reverify-01.yaml` already resolved other findings of `challenger-01.yaml`.
- **Expected / Actual**: earlier resolutions preserved / reset to `open`.
- **Versions**: the worktree at the Planning base of PROP-release-handbook.
- **Conditions**: a challenger round closed across two Planning turns.
- **Workarounds Attempted**: restating all resolutions; it produced `open_findings=0`.
- **Related Assets**: `devkit workflow envelope reverify`, the `spec` skill's `references/planning.md` step 3.

## Evidence

```text
[ENVELOPE: .../envelopes/reverify-02.yaml kind=reverify seq=02 status=completed open_findings=8]
reverify-02.yaml: findings 1, 2, 3, 6, 7, 8, 9, 11 resolution: open (resolved in reverify-01.yaml)
```
