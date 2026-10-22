---
id: FB-instruction-wrap-style-mixed
title: The ADR's 120-character line bound does not match the living-spec-writing style, so the instruction now mixes wrapped and unwrapped bullets
scope: repo
kind: question
category: spec-ambiguity
target: packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-instruction-wrap-style-mixed] The ADR's 120-character line bound does not match the living-spec-writing style, so the instruction now mixes wrapped and unwrapped bullets

## 1. Friction / Question (friction, question)

- **Context**: Writing the terminology rules into the Glossary section of `living-spec-writing` under the 30-line bound
  of `ADR-writing-and-terminology-guidance`.
- **Expectation**: The ADR counts lines "of at most 120 characters, the instruction's current style".
- **Actual**: The instruction's existing bullets are one unwrapped line each (most well over 120 characters), and its
  `description` frontmatter line was already over 120 characters. Only the new Glossary text is wrapped at 120.
- **Workaround (or Interpretation Chosen)**: Wrapped only the added body lines at 120 characters, kept the description
  on one frontmatter line and did not rewrap the existing bullets (recorded as an assumption in the spec). The file now
  has two wrapping styles.
- **Suggestion**: Decide one wrapping convention for bundle instructions (and whether a line bound counts wrapped or
  logical lines) and state it in the authoring guidance or apply it to the whole file in a follow-up.

## Diagnostic Details

- **Reproduction**: `awk 'length > 120' <the instruction>` lists the pre-existing bullets; the Glossary rules are not listed.
- **Expected / Actual**: Expected one style per the ADR wording; actual two styles in one file.
- **Versions**: devkit-spec at the handoff base of this spec.
- **Conditions**: not applicable.
- **Workarounds Attempted**: The interpretation above; the bound holds at 25 added lines.
- **Related Assets**: `ADR-writing-and-terminology-guidance`, `SPEC-terminology-authoring-guidance`.

## Evidence

```text
git diff --numstat <base> -- .../living-spec-writing.md  ->  25 added, 1 deleted
added body lines over 120 characters: 0; the only added line over 120 is the frontmatter description
```

- **Disposition**: `session` task `dev-feedback-resolutions`: unwrapped the Glossary section bullets in `packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md` to match the consistent single-line bullet style of the rest of the instruction. Synced to managed files via `devkit sync`.

