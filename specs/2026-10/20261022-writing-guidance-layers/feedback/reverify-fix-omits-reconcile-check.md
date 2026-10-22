---
id: FB-reverify-fix-omits-reconcile-check
title: The reverify refusal for a reconcile-check source does not name the reconcile path
scope: repo
kind: friction
category: docs-mismatch
target: devkit workflow envelope reverify
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-reverify-fix-omits-reconcile-check] The reverify refusal for a reconcile-check source does not name the reconcile path

## 1. Friction / Question (friction, question)

- **Context**: Closing a P3 finding of a `reconcile-check` envelope at `living-spec-draft` after fixing it.
- **Expectation**: The `spec-delegate` skill says findings are closed with `envelope reverify`, so the same command
  was tried with `--from envelopes/reconcile-check-01.yaml`.
- **Actual**: The command refused with `ENVELOPE_FROM_INVALID`; its `[FIX]` names only `--from latest` (review) and a
  challenger envelope, not the route for a reconcile finding.
- **Workaround (or Interpretation Chosen)**: The `spec` skill's `references/effort.md` says a fix may be closed by a
  new `reconcile-check`; a self-verified `reconcile-check-02` with no findings closed the stage.
- **Suggestion**: Make the `[FIX]` for a `reconcile-check` source say "record a new reconcile-check envelope (or call
  the reconcile-reviewer again)", and state the same in `spec-delegate` Step 6 next to the reverify sentence.

## Diagnostic Details

- **Reproduction**: `devkit workflow envelope reverify --unit <unit> --stage living-spec-draft --from
  envelopes/reconcile-check-01.yaml --resolve all ...`
- **Expected / Actual**: Expected a close or a FIX naming the reconcile route; actual: refusal whose FIX names only
  review and challenger rounds.
- **Versions**: devkit at base `542f4461`.
- **Conditions**: `sdd-spec-feature`, activity-effort `medium`.
- **Workarounds Attempted**: New `reconcile-check` envelope; the stage exit check passed.
- **Related Assets**: `spec-delegate` skill Step 6, the `spec` skill's `references/effort.md`.

## Evidence

```text
[ERROR]  (ENVELOPE_FROM_INVALID) --from must name a review, challenger or reverify envelope, not reconcile-check
[FIX]    Use --from latest for the review round, or --from envelopes/challenger-NN.yaml for a challenger round
```

## Disposition

- **Disposition (resolved)**: `SPEC-feedback-guidance-fixes` makes the `ENVELOPE_FROM_INVALID` `[FIX]` for a `reconcile-check` source name a
  new `reconcile-check` envelope (`envelope new --kind reconcile-check`) or another reconcile-reviewer call; the
  `spec` skill's `references/effort.md` already states the route, and the `spec-delegate` Step 6 sentence was left
  unchanged (outside that unit's write scope). Verified by
  `test_a_reconcile_check_source_names_the_reconcile_route` in `test_envelope_record_gaps.py`.
