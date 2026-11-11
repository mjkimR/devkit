---
sources:
  CAP-HARN-isolated-execution: 7b36ba1e9522527ede0d5a91189ee2ec1efcf6ff
  UC-execute-an-isolated-command: 97ce16cbc581039df913892de074d7cc65263803
title: Execute an isolated command
---

# Execute an isolated command

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `f115e96c8059`, generated 2026-11-11. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

Use `devkit exec` when a native command can run at a fixed local commit while you continue independent work. Provide disposable data, isolated services and ephemeral ports; the checkout is not an OS sandbox.

```sh
uv run devkit exec start --ref HEAD -- just lint-check
uv run devkit exec list
uv run devkit exec wait <run-id> --clean
```

Start returns a pending run identity. The captured supervisor prepares a detached checkout, performs setup and locked sync where applicable, then runs the command. Use `status <run-id>` and `logs <run-id>` to inspect it; full logs and results remain in the common Git directory.

A wait timeout or interrupted observer leaves execution running. `cancel <run-id>` confirms managed shutdown and retains the checkout. Explicit `clean <run-id>` removes only an eligible terminal checkout with proven process quiescence, matching ownership and clean content. Unknown ownership or unexpected files retain it. Cleanup outcomes stay separate from the command result.

Apply passing evidence only to the recorded commit and scope. `devkit run` remains the synchronous compact-output command.

## Sources

- [UC-execute-an-isolated-command](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/harness/UC-execute-an-isolated-command.md)
- [CAP-HARN-isolated-execution](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-isolated-execution.md)
