---
id: FB-ux-writing-missing-style-file
title: ux-writing defers visual style to steering files but says nothing when the project has none
scope: repo
kind: question
category: spec-ambiguity
target: the ux-writing instruction (Visual style)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-13
---

# [FB-ux-writing-missing-style-file] ux-writing defers visual style to steering files but says nothing when the project has none

## 1. Friction / Question (friction, question)

- **Context**: A consumer spec for a color-system change had to describe color roles in Screens drafts and UX
  documents.
- **Expectation**: Guidance on where visual-style decisions live when the project has no steering style file.
- **Actual**: `ux-writing` says "cite the project's steering style files; never restate colors, type, spacing or
  tokens". The project had none, so a feature whose subject is visual style had no place for its decisions.
- **Workaround (or Interpretation Chosen)**: The Unit created `docs/steering/visual-style.md` and cited it from the
  UX documents.
- **Suggestion**: Say that when no steering style file exists and the change decides visual style, the Unit creates
  one under `docs/steering/` (with a summary for `get-context docs`), and name it in the docs skeleton preset if
  that fits.

## Diagnostic Details

- **Reproduction**: not applicable.
- **Expected / Actual**: Expected a home for style decisions; actual a citation rule with no target.
- **Versions**: devkit `569379a06` (instruction text checked).
- **Conditions**: consumer repository with UX documents but no style steering file.
- **Workarounds Attempted**: created a steering file; reconcile accepted it.
- **Related Assets**: `ux-writing` instruction, `living-spec-writing` (steering documents).

## Evidence

```text
ux-writing: "- **Visual style**: cite the project's steering style files; never restate colors, type, spacing or
tokens."
```

## Disposition

Resolved through `SPEC-feedback-guidance-clarifications`. UX authors use an existing project style/token source or an agreed-scope project-owned shared source; no filename, seeded file or additional write authority is required.

Verification: AC-05; test_style_source_guidance.py; spec bundle 685 passed, docs bundle 9 passed, affected all-tier 2664 passed
and independent code review with no findings at f356771f1224f847d459c39e339a0b8c31480030, retained in the Unit's
build-check-01 and review-01 envelopes. This resolves the authorized guidance scope; live consumer/model behavior
remains best effort and unverified.
