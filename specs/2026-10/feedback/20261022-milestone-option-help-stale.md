---
id: FB-milestone-option-help-stale
title: The --milestone help of devkit spec proposal new says it is carried to spec.md
scope: repo
kind: friction
category: docs-mismatch
target: devkit spec proposal new --milestone (packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py)
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-milestone-option-help-stale] The --milestone help of devkit spec proposal new says it is carried to spec.md

## 1. Friction / Question (friction, question)

- **Context**: An ADR compaction run consolidated the roadmap and milestone ADRs.
- **Expectation**: The option help matches `ADR-roadmap-and-milestones`: only proposal anchors declare membership and handoff omits milestone metadata.
- **Actual**: The help reads "Existing global MS-<slug> milestone ID; carried to spec.md on handoff"; the handoff does not carry it.
- **Workaround (or Interpretation Chosen)**: None needed for compaction.
- **Suggestion**: Drop "carried to spec.md on handoff" from the help text.

## Diagnostic Details

- **Reproduction**: `uv run devkit spec proposal new --help`.
- **Expected / Actual**: No carry claim; a carry claim.
- **Versions**: main at dd008f2b.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `ADR-roadmap-and-milestones`, `CAP-DLV-proposal-planning`.

## Evidence

```text
proposals.py: help="Existing global MS-<slug> milestone ID; carried to spec.md on handoff"
```

- **Disposition**: resolved. Session change `packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py`: the `--milestone` help no longer claims a carry to spec.md; `just test-affected` (1353 passed), lint and Pyright pass.
