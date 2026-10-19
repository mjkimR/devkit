---
id: FB-reconcile-self-check-cross-component
title: The medium reconcile self-check exception leaves "cross-component impact" undefined for bundle wording changes
scope: repo
kind: question
category: spec-ambiguity
target: devkit-spec bundle skills/spec/references/effort.md (Medium initial reconcile exception)
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-reconcile-self-check-cross-component] The medium reconcile self-check exception leaves "cross-component impact" undefined for bundle wording changes

## 1. Friction / Question (friction, question)

- **Context**: At `living-spec-draft` of a medium-effort spec, the change touched repository tooling plus two
  sentences of the devkit-spec bundle skills `spec-review` and `spec-plan`. The only Living Spec targets were three
  `docs/development/` files.
- **Expectation**: The exception lets the implementer skip the first `reconcile-reviewer` call when there is "no
  unresolved contract interpretation or cross-component impact".
- **Actual**: It does not say whether a wording change in another package's shipped skill counts as cross-component
  impact when no capability document describes that wording.
- **Workaround (or Interpretation Chosen)**: Treated it as cross-component (two packages touched) and called the
  reviewer, following "If any condition is uncertain, call the reviewer". The reviewer found four documentation gaps,
  so the call was worth it here.
- **Suggestion**: State whether "cross-component" means more than one package or component touched by the diff, or
  only an impact on contracts owned by another component, ideally with one example of each.

## Diagnostic Details

- **Reproduction**: Read the medium exception in effort.md while deciding on the first reconcile check for a change
  that spans `scripts/`, `docs/development/` and `packages/devkit-spec/src/devkit_spec/bundle/skills/`.
- **Expected / Actual**: Expected a deterministic rule; the text leaves the call to judgment.
- **Versions**: devkit and devkit-spec at the workspace head of this branch.
- **Conditions**: activity-effort medium, workflow `sdd-spec-feature`.
- **Workarounds Attempted**: Called the reconcile reviewer (completed, four low findings, fixed in docs).
- **Related Assets**: `SPEC-targeted-tests`, effort.md, the `spec-sync` skill Principle 5.

## Evidence

```text
effort.md, Medium initial reconcile exception:
"The implementer MAY omit the first reconcile-reviewer call only when all affected contracts and documents can be
identified, their agreement with the actual diff can be directly demonstrated, and there is no unresolved contract
interpretation or cross-component impact. ... If any condition is uncertain, call the reviewer."
```

- **Disposition**: skills/spec/references/effort.md: the medium reconcile exception defines cross-component impact with one example each way
