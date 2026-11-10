---
id: FB-split-depends-on-undecided-option
title: Planning step 1 does not say what to do when the split depends on an option the user has not chosen
scope: repo
kind: question
category: spec-ambiguity
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-split-depends-on-undecided-option] Planning step 1 does not say what to do when the split depends on an option the user has not chosen

## 1. Friction / Question (friction, question)

- **Context**: First Planning turn of an investigation-first proposal. The investigation compared five delivery
  options. Two of them are one spec, two are two specs, and one delivers nothing. Which one is carried forward is a
  question for the user in the same turn.
- **Expectation**: Step 1 of the Planning reference says when a proposal is returned to Backlog for decomposition:
  "If the proposal must be split (or has `needs_decompose: true`, or a `size` other than absent or exactly `S`, `M`
  or `L`), return it".
- **Actual**: The step treats "must be split" as a fact of the proposal. Here it is a consequence of an answer that
  does not exist yet. Returning in the same turn would decompose work the investigation recommends not starting and
  would close the turn's questions with `choice: null`, so the user would never be asked which option to carry
  forward. Not returning leaves a proposal in review whose draft design, read literally, is more than one spec.
- **Workaround (or Interpretation Chosen)**: Kept `status: reviewing` and the single size, stated in the proposal
  which options are one spec and which are two, named the children the split would produce, and asked the option as
  a question. The return for decomposition is left to the turn that folds the answer. Three `challenger` rounds
  judged that reading defensible.
- **Suggestion**: Add one sentence to step 1 for this case, for example: "When the split depends on an option the
  user has not chosen, ask the option first; return the proposal in the turn that folds an answer selecting a split."

## Diagnostic Details

- **Reproduction**: Run a first Planning turn on a proposal whose spike questions include a decomposition question
  and whose options differ in the number of specs.
- **Expected / Actual**: Expected a rule for a conditional split. The step names only the unconditional case.
- **Versions**: The `spec` bundle at commit `79156358` of this repository.
- **Conditions**: `planning_effort: high`, a `planning-worker` run with a payload that asked both for the questions
  and for step 1 to be followed if the delivery is more than one spec.
- **Workarounds Attempted**: The interpretation above; no other.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`
  step 1; `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`, "Return
  from Planning for decomposition"; the proposal template's `size` comment.

## Evidence

```text
planning.md, step 1:
  If the proposal must be split (or has `needs_decompose: true`, or a `size` other than absent or exactly `S`, `M`
  or `L`), return it: set `status: draft` and `needs_decompose: true`, keep what you learned in `materials/`, close
  open questions with an `answer` envelope (`choice: null`, "Planning ended: returned to Backlog for
  decomposition"), commit and end.

proposal.md of the unit, section 3.7 (options): (a) 1 spec, (b) 2 specs, (c) 1 or 2 specs, (d) 0, (e) 0 now.
```
