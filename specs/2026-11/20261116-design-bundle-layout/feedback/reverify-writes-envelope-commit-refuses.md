---
id: FB-reverify-writes-envelope-commit-refuses
title: envelope reverify writes an envelope without a summary that envelope commit then refuses
scope: repo
kind: friction
category: tool-error
target: devkit workflow envelope reverify
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-reverify-writes-envelope-commit-refuses] envelope reverify writes an envelope without a summary that envelope commit then refuses

## 1. Friction / Question (friction, question)

- **Context**: Closing two code-review rounds with `devkit workflow envelope reverify --from latest --resolve ...`
  and committing each result with `devkit workflow envelope commit --file envelopes/reverify-NN.yaml`.
- **Expectation**: An envelope the writer command accepts is committable by the commit command, or the writer
  refuses the missing field up front.
- **Actual**: `reverify` without `--summary` wrote `summary: ''` and reported success; `envelope commit` then refused
  it with `ENVELOPE_COMMIT_INVALID` ("envelope needs a nonempty summary ..."). The FIX line suggested finishing the
  envelope or committing manually, without naming the empty summary as the cause.
- **Workaround (or Interpretation Chosen)**: Edited the `summary` field in the written YAML, then committed it.
- **Suggestion**: Make `--summary` required on `envelope reverify` (as the commit gate already requires it), or have
  the commit error name the empty field and the flag that fills it.

## Diagnostic Details

- **Reproduction**: `uv run devkit workflow envelope reverify --unit <spec> --stage review-refine --from latest
  --resolve all`, then `uv run devkit workflow envelope commit --unit <spec> --file envelopes/reverify-01.yaml`.
- **Expected / Actual**: committed / `ENVELOPE_COMMIT_INVALID`.
- **Versions**: devkit main after the formal document lifecycle integration.
- **Conditions**: Clean worktree apart from the new envelope.
- **Workarounds Attempted**: Hand edit of the summary; succeeded.
- **Related Assets**: `devkit workflow envelope reverify`, `devkit workflow envelope commit`, the `spec-review` skill.

## Evidence

```text
[ENVELOPE: envelopes/reverify-01.yaml kind=reverify seq=01 status=completed open_findings=0]
summary: ''
[ERROR]  (ENVELOPE_COMMIT_INVALID) envelope needs a nonempty summary, a declared stage and the current workflow/segment
```

## Disposition

- **Outcome**: resolved by `SPEC-reverify-summary-required`.
- **Change**: `devkit workflow envelope reverify` refuses an authored envelope without a nonempty `--summary`
  (`ENVELOPE_FLAG_INVALID`, `[TARGET] --summary`) before writing; `devkit workflow envelope commit` names each failing
  field (`summary is empty`, an undeclared stage, a stale workflow/segment) and its `[FIX]` names the writer command
  with `--summary`/`--stage`.
- **Verification**: regression tests in `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py`
  (red before the fix, green after), `just test-affected` and an isolated code review of the range.
