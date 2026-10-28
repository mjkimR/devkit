---
id: FB-proposal-new-accepts-a-done-milestone
title: proposal new places a draft in a done milestone without a notice
scope: repo
kind: friction
category: missing-capability
target: devkit spec proposal new --milestone (devkit_spec.features.proposals.usecases.roadmap.milestone_id)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-27
---

# [FB-proposal-new-accepts-a-done-milestone] proposal new places a draft in a done milestone without a notice

## 1. Friction / Question (friction, question)

- **Context**: Planning of a draft whose frontmatter names `MS-maintenance-operations`, whose status is `done`.
- **Expectation**: The milestone rules make every milestone status change a user decision: extending a `done`
  milestone needs the user's decision to reopen it with both completion assertions reset, or another milestone.
  Placing a new draft in a `done` milestone is such an extension, so the intake that writes it should surface the
  choice.
- **Actual**: `devkit spec proposal new --milestone MS-<done>` validates only that the ID names a global milestone,
  writes the membership and reports no notice. The conflict appears later as `SPEC_MILESTONE_DONE_UNSETTLED` in the
  hygiene check, or when Planning reads the milestone.
- **Workaround (or Interpretation Chosen)**: Planning asks the user in its question round whether to reopen the
  milestone, move the proposal or clear its milestone.
- **Suggestion**: Have `proposal new` (and the Backlog reassignment path) return a notice with a stable code when the
  named milestone is `done` or `dropped`, naming the reopen-or-reassign decision, so intake asks before the draft
  lands.

## Diagnostic Details

- **Reproduction**: Create a proposal with `--milestone` naming a `done` milestone; the command succeeds without a
  notice.
- **Expected / Actual**: A notice naming the milestone status / none.
- **Versions**: worktree base `ebe984d3`.
- **Conditions**: Any `done` or `dropped` global milestone.
- **Workarounds Attempted**: A Planning question to the user.
- **Related Assets**: `devkit_spec.features.proposals.usecases.roadmap.milestone_id`;
  `devkit_spec.features.governance.usecases.hygiene` (`SPEC_MILESTONE_DONE_UNSETTLED`); the `spec` skill's milestone
  completion reference ("Later changes").

## Evidence

```text
docs/roadmap/MS-maintenance-operations.md: status: done, both completion assertions confirmed
docs/proposals/PROP-performance-pass/proposal.md: milestone: MS-maintenance-operations (status draft at intake)
roadmap.milestone_id: checks prefix, existence, kind and global path only; no status check
hygiene.py: warns SPEC_MILESTONE_DONE_UNSETTLED for done milestones with unsettled members
```

## Disposition

`SPEC-input-recovery-notices` resolves the authorized notice-only scope. Creation in done/dropped milestones
succeeds with `SPEC_PROPOSAL_MILESTONE_INACTIVE` at NOTICE level, identifying canonical ID and state and advising
membership review. No milestone reopening, assertion reset or approval gate is performed. Regression tests verify
aliases, canonical membership, unchanged milestone bytes and text/JSON `--strict` success. All 8 originally failing
notice cases pass; planned/active cases remain passing. The affected suite passed 2157 tests and independent code
review found no issues.
