---
id: FB-unselected-source-bundle-context
title: Clarify context loading for unselected source bundles
scope: repo
kind: friction
category: instruction-conflict
target: devkit get-context <bundle>
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-05
---

# [FB-unselected-source-bundle-context] Clarify context loading for unselected source bundles

## 1. Friction / Question

- **Context**: Editing the repository-owned design-explore bundle while it is not selected in the authoring checkout.
- **Expectation**: The agent guide requires `get-context` before work touching a bundle's assets.
- **Actual**: `uv run devkit get-context design-explore` returned `SELECTION_INVALID`, because it only loads synchronized bundles.
- **Workaround**: Read the source bundle manifest and skill directly, keep project selection unchanged, and verify deployment in isolated consumers.
- **Suggestion**: Document a source-bundle context route or explicitly permit source inspection when the named bundle is unselected. Installing the bundle into the authoring repository only to read its instructions changes unrelated selection.

## Diagnostic Details

- **Reproduction**: Run `uv run devkit get-context design-explore` with the authoring checkout's existing selection.
- **Expected / Actual**: Required source context versus a selection-only error naming `devkit add design-explore` as its fix.
- **Versions**: devkit 0.1.6; Development input 992799b38258dd4e2d504d1142d3a795f4de6573.
- **Conditions**: Source bundle exists under the catalog package; deep-research is selected, design-explore is not.
- **Workarounds Attempted**: Direct source inspection succeeded; initial sync check and built-wheel consumer tests passed. Selection was unchanged.
- **Related Assets**: Agent guide bundle-context prerequisite, `devkit get-context`, catalog design-explore source manifest and skill.

## Evidence

```text
uv run devkit get-context design-explore
exit=2 code=SELECTION_INVALID
message=bundle is not synchronized: design-explore
fix=uv run devkit add design-explore
uv run devkit sync --check: exit=0
```
