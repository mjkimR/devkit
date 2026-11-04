---
id: FB-full-suite-host-capabilities
title: Full fallback does not identify loopback and wheel-build host requirements
scope: repo
kind: friction
category: missing-capability
target: scripts/affected_tests.py
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-full-suite-host-capabilities] Full fallback does not identify loopback and wheel-build host requirements

## 1. Friction / Question (friction, question)

- **Context**: The final local-orchestrated batch verification selected the full suite on a restricted execution
  host because the batch changed command registration.
- **Expectation**: The executor identifies the full selection's loopback and dependency-build requirements before
  treating its result as authoritative verification.
- **Actual**: The default restricted execution spent 155 seconds before reporting 9 failures and 77 setup errors.
  Viewer HTTP fixtures could not bind a socket, and three installed-wheel checks could not resolve a build
  dependency host. The selection line reports the full fallback but not those execution prerequisites.
- **Workaround (or Interpretation Chosen)**: Preserve the failed evidence and request the host permissions needed
  by the same verification command. No source rollback or weakened test is appropriate for these observed errors.
- **Suggestion**: Document or report the full selection's host requirements before execution so an agent can
  request the normal operation-specific permissions once. Keep required tests and the full fallback enabled;
  repository guidance does not grant host permission.

## Diagnostic Details

- **Reproduction**: At `d0d8bc7f`, run `just test-affected --base 2cf7879a74b50b687867e2184188dee6c29a2fbc`
  in the default restricted execution profile.
- **Expected / Actual**: Expected actionable prerequisites before the authoritative run; observed
  `mode=full changed=227`, then `9 failed, 6451 passed, 15 skipped, 77 errors` in 155.02 seconds.
- **Versions**: Repository head `d0d8bc7f`; Python 3.12.8; workspace-write execution with restricted network.
- **Conditions**: Viewer integration tests bind loopback HTTP sockets; installed-consumer e2e tests invoke wheel
  builds whose isolated dependencies may require registry access.
- **Workarounds Attempted**: Failure captured before the permission-enabled retry. Earlier permission-enabled
  full checks passed during integration preparation; this record does not claim a result for the final retry.
- **Related Assets**: `scripts/affected_tests.py`, `scripts/module.sh`,
  `packages/devkit-viewer/tests/integration/features/browse/test_server.py`,
  `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`,
  `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py`,
  `packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py`.

## Evidence

Sanitized failure log: `<log>/20261104-141946-uv-run-ckws9f5x.log`.

```text
[TEST_SELECTION: mode=full base=2cf7879a74b50b687867e2184188dee6c29a2fbc changed=227 paths=0 reason=packages/devkit-dist/src/devkit_dist/cli.py]
Viewer socket.bind: PermissionError: [Errno 1] Operation not permitted
Installed wheel builds: failed to lookup address information
9 failed, 6451 passed, 15 skipped, 77 errors in 155.02s
```
