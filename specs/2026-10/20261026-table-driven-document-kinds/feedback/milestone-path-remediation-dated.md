---
id: FB-milestone-path-remediation-dated
title: Misplaced milestones get the dated-partition remediation
scope: repo
kind: change-request
category: tool-error
target: packages/devkit-spec/src/devkit_spec/features/governance/usecases/id_convention.py
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-milestone-path-remediation-dated] Misplaced milestones get the dated-partition remediation

`RULE-id-convention` tells a misplaced milestone to move to a dated partition, while milestones live at
`docs/roadmap/MS-<slug>.md` without a date.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `IdConventionRule._target` gives every target outside the Living Spec kinds the remediation
  "Move the file to {YYYY-MM}/{YYYYMMDD}-{slug} with the decision or start date, then run ...", milestones included,
  although the milestone path issue itself says "Milestone must be stored at docs/roadmap/MS-{slug}.md".
- **Proposed Procedure**: Give milestones a remediation that names `docs/roadmap/MS-{slug}.md`, in a bugfix after
  `SPEC-table-driven-document-kinds`, which keeps the current text byte-for-byte (its Planning decision).
- **Expected Benefit**: An agent following the remediation no longer moves a milestone into a dated directory.
- **Cost & Risk**: One rule message changes; tests asserting it need updating.
- **Attempted**: Hypothesis; read in source, not reproduced with a misplaced milestone.

## Diagnostic Details

- **Reproduction**: unknown; read `id_convention.py:298-301` and `:476-485`.
- **Expected / Actual**: Expected a roadmap path remediation; actual is the dated-partition remediation.
- **Versions**: base `96df5d86`.
- **Conditions**: A milestone file outside `docs/roadmap/` or with an invalid stem.
- **Workarounds Attempted**: Not attempted.
- **Related Assets**: `RULE-id-convention`, historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/challenger-01.yaml` finding 7.

## Evidence

```text
id_convention.py:298-301  path_issue="Milestone must be stored at docs/roadmap/MS-{slug}.md"
id_convention.py:476-485  non-Living-Spec remediation: "Move the file to {YYYY-MM}/{YYYYMMDD}-{slug} with the decision or start date"
```
