---
id: FB-bundle-asset-edits-miss-authoring-instruction
title: Editing another bundle's assets does not lead the agent to the agent-asset-writing instruction
scope: repo
kind: suggestion
category: other
target: AGENTS.md
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-bundle-asset-edits-miss-authoring-instruction] Editing another bundle's assets does not lead the agent to the agent-asset-writing instruction

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The repository guide tells agents to run `uv run devkit get-context <bundle>` for the bundle
  whose assets they touch. A worker editing `spec` bundle skills loads `spec` and `docs`, whose instructions do not
  include `agent-asset-writing`; that instruction lives in the `authoring` bundle and already held the
  self-containment rule. `FB-bundle-text-document-id-citations` was filed because the worker searched only
  `living-spec-writing` and `document-writing`.
- **Proposed Procedure**: In the repository-owned part of `AGENTS.md`, say that editing any bundle's skill, playbook,
  instruction or guide also needs `uv run devkit get-context authoring` and its `agent-asset-writing` instruction.
- **Expected Benefit**: Bundle authors find the writing and self-containment rules before writing, not in review.
- **Cost & Risk**: One line in the repository guide; no behavior change.
- **Attempted**: Hypothesis from the source feedback's evidence; `AGENTS.md` outside the managed block was outside
  this unit's write scope.

## Evidence

```text
uv run devkit get-context authoring -> instructions: agent-asset-writing ("... bundle self-containment")
FB-bundle-text-document-id-citations: "Neither living-spec-writing, document-writing nor the bundle guidance tests state it"
```
