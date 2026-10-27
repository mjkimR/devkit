---
id: FB-support-role-diff-check-on-dirty-tree
title: Support-role diff check misses writes to already-modified files
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/SKILL.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-support-role-diff-check-on-dirty-tree] Support-role diff check misses writes to already-modified files

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `spec-delegate` step 4 verifies a support role by checking that `git status --short` is
  unchanged after the run, except a Scout's agreed `materials/` path.
- **Proposed Procedure**: Before delegating, require a clean tree, or snapshot `git status --porcelain` together with a
  hash of `git diff` and of untracked files, and compare the snapshot after the run.
- **Expected Benefit**: A role that edits a file which was already modified before the call is detected; today the
  status code stays ` M` and the check passes.
- **Cost & Risk**: One extra command per delegation; a clean-tree requirement could force a stash-free worktree for
  callers that delegate mid-edit.
- **Attempted**: Hypothesis, raised by challenger-01 finding 3 while planning the Backlog roles; that proposal adopts a
  clean-tree requirement for its own roles only.

## Diagnostic Details

- **Reproduction**: not reproduced; follows from `git status --short` reporting a status code per path, not content.
- **Expected / Actual**: Expected: any role write is detected. Actual: a write to a path already listed as modified
  leaves the output identical.
- **Versions**: spec bundle at `<worktree>` head `ec2e0b68`.
- **Conditions**: a delegation from a checkout with uncommitted changes, which the Unit path and Backlog both allow.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `spec-delegate` SKILL step 4, `bundle/subagents/scout.md`, `CAP-DLV-delivery-workflows`
  section 4.6.

## Evidence

```text
spec-delegate SKILL.md step 4: "a support role leaves `git status --short` unchanged, except a Scout's agreed
`materials/` path."
challenger-01 finding 3 (PROP-backlog-subagent-roles envelopes): status-code comparison misses a role editing a file
that is already modified; Backlog commits in the current checkout with no clean-tree requirement.
```

- **Disposition**: SPEC-backlog-subagent-roles: resolved; `spec-delegate` steps 2 and 4 compare working-tree snapshots (a tree written from a temporary index) taken before and after a support role instead of `git status --short`, so a write to an already-modified or untracked file is detected; verified by `test_the_support_role_snapshot_sees_a_write_to_an_already_modified_file` (AC-05).
