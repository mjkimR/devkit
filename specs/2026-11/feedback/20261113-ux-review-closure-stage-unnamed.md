---
id: FB-ux-review-closure-stage-unnamed
title: spec-ux-review names no stage for the implementer's closing envelope or for findings settled at specify
scope: repo
kind: question
category: spec-ambiguity
target: the spec-ux-review skill (Report section)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-ux-review-closure-stage-unnamed] spec-ux-review names no stage for the implementer's closing envelope or for findings settled at specify

## 1. Friction / Question (friction, question)

- **Context**: A consumer Unit ran `ux-review` round 1 at `specify`, folded most findings into `spec.md` before the
  plan, and closed the round during Development.
- **Expectation**: The skill says which `--stage` the implementer's closing `ux-review` envelope uses, and where a
  finding already settled in `spec.md` at `specify` is closed.
- **Actual**: The command template offers `--stage <specify|characterize|spike>` only. The text says "In Development
  the implementer closes the last round with a further `ux-review` envelope" without a stage. A finding folded into
  the spec at `specify` stays open until that Development envelope.
- **Workaround (or Interpretation Chosen)**: The implementer recorded `ux-review-02` with `--stage build-verify`,
  repeating each round-1 finding as `resolved` or `waived`.
- **Suggestion**: Name the closing stage (for example `build-verify`), and say whether a finding settled in the spec
  at `specify` may be closed there (a closing envelope at `specify`) or must wait for the implementation.

## Diagnostic Details

- **Reproduction**: Follow the `spec-ux-review` Report section for a Unit whose round-1 findings are folded at
  `specify`.
- **Expected / Actual**: Expected a named stage; actual a stage list without the Development stage.
- **Versions**: devkit `569379a06` (projected skill text checked).
- **Conditions**: `sdd-spec-feature` Unit with Screens drafts.
- **Workarounds Attempted**: `--stage build-verify`; the stage exit accepted it.
- **Related Assets**: `spec-ux-review` skill, `spec-specify` skill (`references/screens.md`).

## Evidence

```text
spec-ux-review: devkit workflow envelope new --unit <dir> --kind ux-review --stage <specify|characterize|spike> ...
spec-ux-review: "In Development the implementer closes the last round with a further `ux-review` envelope repeating
each finding with `resolution: resolved`, or `resolution: waived` and a `waiver` reason."
consumer ux-review-02.yaml: stage: build-verify
```
