---
id: FB-parallel-planning-feedback-id-collision
title: Parallel Planning branches record the same feedback ID unnoticed
scope: repo
kind: friction
category: missing-capability
target: spec-feedback references/sweep.md (deduplication step)
skill: spec-feedback
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-19
---

# [FB-parallel-planning-feedback-id-collision] Parallel Planning branches record the same feedback ID unnoticed

## 1. Friction / Question (friction, question)

- **Context**: Two proposals were planned in parallel on their own `plan-` branches; both Planning runs hit the same
  PADR title limit and each recorded it in its own `feedback/` directory.
- **Expectation**: The sweep's deduplication (`devkit spec list feedback --status open --all-namespaces`) and the
  `<name>` uniqueness check (`devkit spec resolve FB-<name>`) keep feedback IDs unique.
- **Actual**: Both checks only see the branch's own tree, so both branches chose `FB-padr-title-branch-length-limit`.
  After the first proposal was accepted on main, merging main into the second branch made `RULE-document-reference`
  report the ID as declared by two documents (two errors), which would have refused integration.
- **Workaround (or Interpretation Chosen)**: Merged main into the plan branch, deleted this branch's copy (the same
  observation) and recorded it as a duplicate in a new sweep envelope.
- **Suggestion**: Have the Planning sweep (or the Host before `plan-accept`) merge or diff against the current base
  and rerun `devkit rules check --ci --base <merge-base>` for document IDs, or name the duplicate case in
  `references/sweep.md` with the merge-then-delete recovery.

## Evidence

```text
devkit rules check --ci --base <merge-base>   (after merging main)
[VIOLATION: RULE-document-reference severity=error ... message="FB-padr-title-branch-length-limit is declared by 2 documents:
  docs/proposals/PROP-direct-planning-procedure/feedback/..., docs/proposals/PROP-envelope-record-gaps/feedback/..."]
[SUMMARY: errors=2 warnings=0 infos=0 fixed=0]
```

## Disposition

Dismissed: separate branches can independently record the same observation, but the existing integration procedure
incorporates the current base and runs cumulative rules before landing. `RULE-document-reference` detects duplicate
IDs in the combined tree, as the recorded incident demonstrates. Keep the existing recovery: retain one observation,
remove the duplicate and rerun verification. No additional cross-branch reservation or prevention mechanism is needed.
