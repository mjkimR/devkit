---
id: FB-automatic-review-managed-sync
title: Automatic review treats sanctioned sync as forbidden direct edits
scope: unknown
kind: friction
category: instruction-conflict
target: Codex exec_command automatic approval review for devkit sync
origin: agent
severity: blocked
recurring: false
status: dismissed
created_at: 2026-10-18
---

# [FB-automatic-review-managed-sync] Automatic review treats sanctioned sync as forbidden direct edits

## Friction

- **Context**: Restoring missing generated context before development.
- **Expectation**: Repository instructions require get-context and direct generated-file changes through source bundles
  or devkit sync. The tool's recovery directive explicitly names sync.
- **Actual**: Automatic approval rejected escalated sync because it writes protected projected agent files, citing the
  prohibition on direct edits as a reason to disallow the prescribed generator.
- **Workaround**: Obtained explicit permission for the dry-run's 205 create operations; the subsequent sync succeeded.
- **Suggestion**: Distinguish generator-mediated restoration from direct asset editing, while reviewing the actual
  deployment plan and the authority to change persistent agent instructions. Do not globally exempt sync operations.

## Diagnostic Details

- **Reproduction**: Missing context caused NOT_SYNCHRONIZED; sync in the sandbox failed on the protected projection
  directory. Escalated sync was rejected, and read-only dry-run showed create=205 update=0 remove=0.
- **Expected / Actual**: Authorized recovery should be assessed using the generator's plan; the rejection instead
  interpreted a direct-edit prohibition as forbidding the recovery tool itself.
- **Versions**: devkit-agt 0.1.1; automatic reviewer version unknown.
- **Conditions**: Codex workspace-write environment; managed and projected context absent in a fresh checkout.
- **Workarounds Attempted**: Read-only preview followed by explicit approval succeeded; no rejected operation was bypassed.
- **Related Assets**: AGENTS.md managed-file policy, devkit get-context, devkit sync and Codex automatic approval review.

## Evidence

```text
get-context: NOT_SYNCHRONIZED, fix devkit sync.
sync dry-run: create=205 update=0 remove=0.
automatic review: protected .agents/.codex mutations rejected under direct-edit prohibition and missing explicit authority.
after explicit authorization: sync succeeded with create=205 update=0 remove=0.
```

- **Disposition**: dismissed. The observation concerns host-level automatic permission review prompt/policy in OpenAI Codex, which mistakenly interpreted the direct-edit prohibition as forbidding the sanctioned recovery generator (`devkit sync`). devkit repository code does not own or configure the host's automatic review model behavior.

