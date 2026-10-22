---
id: FB-spec-sync-reconcile-check-command
title: spec-sync names the reconcile-check envelope but not its command
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/SKILL.md
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-spec-sync-reconcile-check-command] spec-sync names the reconcile-check envelope but not its command

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `spec-sync` step 5 says "run the reconcile check for the effort (a `reconcile-check`
  envelope)" without a command. At `low` the implementer records it alone; the command
  (`devkit workflow envelope new --kind reconcile-check`) is named only in `spec-delegate` and the `spec` skill's
  `references/envelope.md`.
- **Proposed Procedure**: add the exact command with `--stage living-spec-draft`, `--effort` and `--base`/`--head` to
  `spec-sync` step 5, as `spec-review` does for the review envelope.
- **Expected Benefit**: one fewer failed guess (`devkit workflow envelope reconcile-check` does not exist) and one
  fewer lookup per low-effort Unit.
- **Cost & Risk**: one line in a skill; a bundle budget test may need its limit checked.
- **Attempted**: observed in this session; the proposed line was not written (outside the write scope).

## Diagnostic Details

- **Reproduction**: `devkit workflow envelope reconcile-check --help` exits with "No such command".
- **Expected / Actual**: a named command in the skill / a generic `envelope new --kind` command found elsewhere.
- **Versions**: base commit 3b854eae.
- **Conditions**: development worker at `activity-effort` low.
- **Workarounds Attempted**: read `spec-delegate`; `envelope new --kind reconcile-check` worked.
- **Related Assets**: `spec-sync`, `spec-delegate`, `references/envelope.md`.

## Evidence

```text
Error: No such command 'reconcile-check'.
[ENVELOPE: .../envelopes/reconcile-check-01.yaml kind=reconcile-check seq=01 status=completed open_findings=0]
```
