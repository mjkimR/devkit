---
id: FB-reconcile-reviewer-no-diff-list
title: The reconcile-reviewer payload carries no changed-file list, and the role cannot list the diff itself
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/payload.md (reconcile-reviewer row)
skill: spec-delegate
agent: claude-code
origin: agent
severity: noise
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-reconcile-reviewer-no-diff-list] The reconcile-reviewer payload carries no changed-file list, and the role cannot list the diff itself

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the `reconcile-reviewer` contract grants only `Read`, `Grep` and `Glob` (no shell), while
  its payload row requires a `diff_scope` (base and head) and names `spec.md`, `reconcile.md`, the deciding review
  envelope and the affected docs. The role cannot run `git diff --name-only` on that range or confirm that HEAD
  still equals the head it was given, so it infers the change set from the files it is pointed at.
- **Proposed Procedure**: add to the `reconcile-reviewer` row of the payload table "the output of
  `git diff --name-only <base> <head>`" (and the head it was taken at), so the verifier checks target completeness
  against the actual file list rather than against the caller's selection.
- **Expected Benefit**: target completeness, the reconcile reviewer's main check, rests on the real diff; the
  verification no longer lists "exact file list of the diff" as unverified.
- **Cost & Risk**: one more line per call; the list is the caller's output, so the caller still could omit a path,
  but a mismatch with the committed range becomes visible to the Host's range validation.
- **Attempted**: in this run the reviewer returned zero findings and named the missing file list and HEAD
  freshness as unverified areas; the implementer confirmed HEAD unchanged afterwards and recorded that as an
  assumption in `reconcile-check-01.yaml`.

## Diagnostic Details

- **Reproduction**: delegate a `living-spec-draft` verification to the projected `reconcile-reviewer` with the
  payload the table prescribes; read its `unverified_areas`.
- **Expected / Actual**: expected a check against the diff range; actual is a check against the files named in the
  payload, with the range listed as unverified.
- **Versions**: devkit 0.1.1, branch dev-role-reasoning-effort-presets.
- **Conditions**: activity-effort medium, Claude Code, nested subagent under a development worker.
- **Workarounds Attempted**: confirmed HEAD in the caller after the return; it worked for freshness, not for the
  file list.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/bundle/subagents/reconcile-reviewer.md`,
  the `spec-delegate` skill's payload reference, `CAP-DLV-delivery-workflows` §4.6.

## Evidence

```text
reconcile-reviewer.md hosts.claude-code.tools: [Read, Grep, Glob]
payload.md row: | `reconcile-reviewer` | `spec.md`, `reconcile.md`, the deciding review envelope, ... | required | ...
reviewer return, unverified_areas: "Exact file list of the diff from <base> to <head>, and whether the worktree
HEAD still equals <head> (no shell ...)"
```

- **Disposition**: `SPEC-worker-range-validation`: compared heads and changed-path information for read-only
  reviewer payloads, generated with the existing worker-result checks.
