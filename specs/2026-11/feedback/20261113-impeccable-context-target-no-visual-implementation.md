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
status: promoted
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

## Disposition

Promoted to `SPEC-uiux-upstream-fallbacks` as completed local mitigation. The local skill treats negative visual detection as advisory, inspects actual target/code and the executable local branch build, and reports detector limits without claiming --target guarantees discovery.

Verification: focused UI/UX bundle integration 16 passed; installed-consumer E2E 1 passed; catalog lint/format and type checks passed; `just test-affected --base 5cab6156a60de1a2a2845e38fc19bda92961c90e --tier all` passed 182 tests. These checks verify shipped instructions and distribution, not upstream runtime or model obedience.

The upstream runtime was not fixed. Native upstream trials were not required or performed. The user selected local compensation and no external submission or retained upstream follow-up; this disposition records no upstream resolution.
