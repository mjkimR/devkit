---
id: FB-bundle-text-document-id-citations
title: No rule says whether shipped bundle text may cite this repository's document IDs
scope: repo
kind: question
category: spec-ambiguity
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-bundle-text-document-id-citations] No rule says whether shipped bundle text may cite this repository's document IDs

## 1. Friction / Question (friction, question)

- **Context**: A Development worker added a rule sentence to `spec-delegate/references/worker.md` that comes from an
  accepted ADR of this repository.
- **Expectation**: The writing instructions or the bundle tests say whether shipped bundle text may cite a
  repository ADR ID, given that consuming projects lack this repository's `docs/`.
- **Actual**: Neither `living-spec-writing`, `document-writing` nor the bundle guidance tests state it; the plan
  first said the sentence would cite the ADR, and the code review flagged the mismatch with the uncited text.
- **Workaround (or Interpretation Chosen)**: Followed the observed convention: the bundle's skills cite no `ADR-` ID
  (only a placeholder `` `ADR-<slug>` `` in `spec-next`), so the sentence states the rule without a citation and the
  capability carries the ADR reference.
- **Suggestion**: State the convention once (writing instruction or a bundle test asserting no repository document ID
  in shipped skill text), or confirm that citing is allowed.

## Evidence

```text
rg "`ADR-" packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills -> only spec-next/references/post-handoff.md
  (the placeholder `ADR-<slug>`)
review-01.yaml finding (P3): plan.md said "citing the ADR"; worker.md cites none
```
