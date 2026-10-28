---
id: FB-review-refactor-cited-sections-embed-the-route
title: review-refactor application sections embed the overall-refactor route
scope: repo
kind: suggestion
category: other
target: packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/references/applying.md
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-10-28
---

# [FB-review-refactor-cited-sections-embed-the-route] review-refactor application sections embed the overall-refactor route

Coupling between two playbooks: route-specific text sits in sections another playbook cites as route-neutral.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `applying.md` "Branch and edit tasks" names the overall-refactor workflow's Git policy, and
  "Integration" names the session integration path with task kind `overall-refactor`. `performance-pass` cites both
  sections but routes every work item through the feature workflow, so it needs an override that disables that text.
- **Proposed Procedure**: Keep the branch policy and integration path choice in "Work items and route" only, and
  have "Branch and edit tasks" and "Integration" say "the branch and integration path of the route chosen in §1".
- **Expected Benefit**: The cited sections become route-neutral; a citing playbook needs no override, and the two
  playbooks cannot drift on this point.
- **Cost & Risk**: A small edit of `review-refactor` and its capability; `performance-pass`'s third override then
  becomes redundant and can be removed in the same change.
- **Attempted**: Hypothesis; the code review of `SPEC-performance-pass` found the conflict and the override was added.

## Diagnostic Details

- **Reproduction**: not applicable.
- **Expected / Actual**: not applicable.
- **Versions**: `maintenance` bundle 0.1.4 sources at head of `dev-performance-pass`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: `performance-pass` `references/changes.md` override 3.
- **Related Assets**: `CAP-DLV-review-refactor`, `CAP-DLV-performance-pass`.

## Evidence

```text
review-refactor applying.md "Branch and edit tasks": "With the `spec` bundle, use the branch the overall-refactor
workflow's Git policy allows."
review-refactor applying.md "Integration": "With the `spec` bundle, use the session integration path with task kind
`overall-refactor`; a single-module work item uses its feature workflow's path."
```

## Disposition

- **Disposition**: Dismissed by the user's decision: `CAP-DLV-performance-pass` already selects its feature route
  through an explicit override of the cited text. Current routing is defined; removing that documentation
  duplication alone does not justify separate work. Keep the existing override and behavior.
