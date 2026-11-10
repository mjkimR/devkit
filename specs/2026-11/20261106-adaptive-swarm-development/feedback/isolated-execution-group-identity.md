---
id: FB-isolated-execution-group-identity
title: Isolated execution loses established group leader identity before tests
scope: repo
kind: friction
category: tool-error
target: packages/devkit/src/devkit_agt/features/isolated_execution/
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-11-06
---

# [FB-isolated-execution-group-identity] Isolated execution loses established group leader identity before tests

## 1. Friction / Question

- **Context**: Required selected E2E launched through the established isolated executor at a fixed full commit SHA.
- **Expectation**: Execution reaches setup/tests and wait returns a final result with guarded cleanup.
- **Actual**: The run stopped before setup/tests with group-leader identity failure; wait and supported cancel returned unknown, and no result file appeared.
- **Workaround**: Host authorized the identical native E2E command synchronously; all four selected tests passed. Unknown execution state and checkout were preserved.
- **Suggestion**: Investigate process identity capture during checkout creation and provide supported recovery when managed identities disappear; keep cleanup guards intact.

## Diagnostic Details

- **Reproduction**: One observed run via `devkit exec start --ref <full-sha> -- just test-affected --base <saved-sha> --tier e2e`; no repeat launched after unknown result.
- **Expected / Actual**: Expected supervised test outcome; actual unknown before tests, no cleanup proof.
- **Versions**: Source c1996ba434b8988612f5bc9aba707115ce8ff46d; POSIX managed host, Python 3.12.
- **Conditions**: Linked development worktree; separately escalated launch/wait; exact underlying identity mismatch cause unknown.
- **Workarounds Attempted**: Supported wait and cancel both returned unknown. Host-selected synchronous scheduling passed required selected E2E at corrected source de3e9af5634125e9ab16ebbcfb69fbc35a7e1ad0.
- **Related Assets**: Isolated execution runtime and local-orchestrated isolated-verification procedure. Existing feedback search found no matching observation.

## Evidence

```text
run=9c1f721c93e6402fb1a5cebd278cfad2
output.log: established group leader identity changed
wait --clean: exit=2 phase=unknown outcome=unknown observer=unknown
result.json: absent; executor checkout and records preserved
native selected E2E at corrected source: 4 passed in 9.79s
```

- **Disposition**: Dismissed: retire the historical incident without claiming a fix; its underlying cause remains unverified. Investigate only if Linux use produces a new occurrence with fresh execution and identity evidence; retain the existing cleanup guards.
