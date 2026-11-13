---
id: FB-impeccable-context-target-no-visual-implementation
title: impeccable context reports hasVisualImplementation=false for a monorepo UI even with --target
scope: upstream
kind: friction
category: tool-error
target: impeccable context --target
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-impeccable-context-target-no-visual-implementation] impeccable context reports hasVisualImplementation=false for a monorepo UI even with --target

## 1. Friction / Question (friction, question)

- **Context**: A consumer monorepo keeps a SvelteKit SPA in a subdirectory. The Impeccable session ran
  `impeccable context` to frame its work.
- **Expectation**: With `--target <ui path>`, the command detects the visual implementation in that subdirectory.
- **Actual**: At the repository root it reported `hasVisualImplementation=false`; with `--target <ui path>` it still
  reported `false`.
- **Workaround (or Interpretation Chosen)**: The brief named `--target`, and the framing came from the consumer's OOUX
  documents instead.
- **Suggestion**: Report upstream to Impeccable with the monorepo layout. In devkit, do not present `--target` as a
  fix in the brief template until upstream behavior changes.

## Diagnostic Details

- **Reproduction**: In a monorepo with the UI under a subdirectory, run `impeccable context` at the root, then with
  `--target <ui path>`.
- **Expected / Actual**: Expected `true` with `--target`; actual `false` both times.
- **Versions**: Impeccable 4.8.x (exact version unknown).
- **Conditions**: SvelteKit SPA in a monorepo subdirectory.
- **Workarounds Attempted**: framing from OOUX documents (worked).
- **Related Assets**: `MAT-uiux-improve-pilot` finding A2c.

## Evidence

```text
Pilot finding A2c: impeccable context at the repository root reports hasVisualImplementation=false for a UI under
a monorepo subdirectory; with --target <ui path> it still reported false.
```
