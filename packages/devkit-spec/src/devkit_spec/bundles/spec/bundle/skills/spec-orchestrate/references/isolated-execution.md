# Isolated verification in local-orchestrated work

Use this procedure when the project exposes a separate synchronous tier and required E2E tier; otherwise keep the project's required verification commands.

1. Save the landed baseline B before the first merge; keep the earliest still-uncovered baseline for each required tier.
2. After landing at A, synchronize the landed environment in fresh processes, restore bundles, repair stale generated artifacts and commit them before selecting tests.
3. Run required lint, types, rules, frontend checks and selected unit/integration tests synchronously against A; preserve selected-tier full fallback and explicit empty selections.
4. Check that the native command uses disposable data and isolated services or ephemeral ports; supply project setup through the existing worktree configuration or `--setup`.
5. Start the required selected E2E command with `devkit exec start --ref <A> -- <native argv>` and retain its run ID, tested SHA A, baseline B and selection.
6. Start one background `devkit exec wait <run-id> --clean --format json` through the execution tool, then continue independent work while verification is pending.
7. Collect the waiter's one final object through the tool's completion delivery; if the tool provides no completion delivery, inspect the returned run with `devkit exec list`, `status` or `wait` later.
8. At the next result check, hold further merges on a failed or unknown result and prioritize repair; inspect retained logs, retain the checkout when native artifacts are needed, and launch a new run for repaired content without merge replay or automatic rollback.
9. Before completion, collect required synchronous results and passing required E2E at current landed HEAD, or record an explicit empty E2E selection for the entire uncovered interval.

Example for a project with devkit's repository selector:

```sh
just test-affected --base <B> --tier unit-integration
devkit exec start --ref <A> -- just test-affected --base <B> --tier e2e
devkit exec wait <run-id> --clean --format json
```

Run the last command as a background tool call; CLI exit alone delivers no push event into an agent conversation.
Start with one outstanding E2E run to bound CPU and environment cost; allow more only when resources and independent service/data namespaces support them.
Keep this as a recommendation, without an executor concurrency restriction or mandatory verifier subagent.
If main advances to C while A runs, keep the added interval and generated repairs outstanding; a pass at A proves only A.
For accumulated changes, select from the earliest still-uncovered baseline to current landed SHA, retaining an older baseline when an intermediate run covered only part of it.
Before declaring C complete, run required selected E2E at C or record an explicit empty selection for the complete added interval; report every actual tested SHA without relabelling A as C.
If launch/setup, waiting or requested cleanup fails, keep execution, observer and cleanup outcomes separate; launch or cleanup success proves no test pass.
On wait timeout or interruption, retain the execution and environment; `wait` never implicitly cancels them.
Use `cancel` only to request confirmed managed-process shutdown, then use explicit `clean` for an eligible checkout; unknown ownership refuses cleanup.
Keep integration approval and delivery completion with the Host; git-operator remains a Git lifecycle executor.
The supervisor supports POSIX macOS/Linux; host descendant-kill policies, application exit and reboot have no survival guarantee.
