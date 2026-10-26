---
id: FB-viewer-review-probes-outside-vitest-include
title: Viewer review probes fall outside the vitest include
scope: repo
kind: friction
category: docs-mismatch
target: .devkit/managed/spec/subagents/code-reviewer.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-viewer-review-probes-outside-vitest-include] Viewer review probes fall outside the vitest include

## 1. Friction / Question (friction, question)

- **Context**: A nested `code-reviewer` wrote executable probes for a viewer frontend change under the round's
  ignored probe path (`<worktree>/scratch/review-01/`).
- **Expectation**: The role contract says to write probes under that path "and run the package's test command on
  them".
- **Actual**: The viewer's `just viewer test` runs `vitest run`, whose config includes only `src/**/*.test.ts`, so a
  probe under `scratch/` is never collected; the reviewer had to write its own `vitest.config.mts` beside the probe
  and pass `--config`.
- **Workaround (or Interpretation Chosen)**: The caller warned the reviewer in the brief; the reviewer added a probe
  config and ran `npx vitest run --config ../../../scratch/review-01/vitest.config.mts`.
- **Suggestion**: Either name in the code-reviewer contract (or the viewer reference) how to run a frontend probe
  outside `src/`, or give `scripts/viewer.sh` a probe entry that runs vitest with an explicit include for a given
  directory.

## Diagnostic Details

- **Reproduction**: write `scratch/review-01/x.test.ts` and run `just viewer test`; the file is not collected.
- **Expected / Actual**: probe collected by the package test command / not collected.
- **Versions**: vitest 5.0.5, worktree of `SPEC-viewer-handbook-first-knowledge`.
- **Conditions**: viewer frontend changes reviewed with probes; Python packages are unaffected (pytest takes paths).
- **Workarounds Attempted**: a probe-local vitest config, which worked.
- **Related Assets**: `packages/devkit-viewer/frontend/vite.config.ts` (`test.include`), `scripts/viewer.sh`.

## Evidence

```text
vite.config.ts: test: { environment: 'jsdom', include: ['src/**/*.test.ts'] }
reviewer probe: npx vitest run --config ../../../scratch/review-01/vitest.config.mts (3 probes run)
```
