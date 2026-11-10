# Verification ownership in client repositories

Use this guide when adopting or upgrading agent guidance for delegated development. Keep the repository's native
commands, invocation prefixes, required coverage, affected-selection fallback and CI requirements unchanged.

## Assign the responsibility

- Workers run the project's required native checks synchronously in their assigned worktree and wait for results.
  Include necessary selective E2E; the responsibility split removes no required check.
- The local-orchestrated Host owns post-integration asynchronous verification, result collection, outstanding
  coverage and final acceptance. Directory location does not choose the role: a Host can work in a worktree.
- Direct/session work keeps the project's existing native verification procedure.
- Use asynchronous separation only where supported independent groups preserve complete required coverage.
  Combined commands stay combined; a project without E2E needs no new E2E tier or empty coverage claim.

For project-owned `AGENTS.md`, adapt this example without changing the existing command list:

```text
Workers run required project-native checks synchronously in their assigned worktree,
including necessary selective E2E, and return the command, source identity and result.
The local-orchestrated Host owns post-integration asynchronous verification and final
integrated-result acceptance. Workers do not inherit the Host's launch/wait/cleanup steps.
Direct/session work retains the project's existing native verification procedure.
```

A worker payload names the existing native command, its coverage and expected evidence. For example, where
`npm test` is the required combined command, pass `npm test` and wait for its result. Do not replace it with an
invented split or wrap it in the Host's execution lifecycle. This pattern requires neither devkit nor a harness.

If the Host uses devkit for supported post-integration asynchronous coverage, it owns `devkit exec start`,
`wait`, result collection and guarded cleanup. The CLI remains general purpose for separately requested uses;
no role or current-directory restriction is installed.

## Apply an upgrade

1. Inventory existing required commands and their CI coverage before editing guidance.
2. If devkit is not installed, keep the native tooling and skip this step. Otherwise upgrade the installed devkit packages through the project's documented dependency procedure, then run its
   documented `devkit sync` invocation to refresh selected managed assets. No fixed package manager is required
   by the responsibility split; use the consumer's existing prefix.
3. Inspect project-owned instructions outside the managed block. Sync updates managed assets and its own block;
   it does not rewrite manually owned `AGENTS.md` verification instructions.
4. Find generic instructions such as "in local-orchestrated work, run exec" and qualify them by owner and phase.
   Route changes through the consumer's normal development workflow; preserve explicit user instructions and
   obtain any authority that workflow requires. Do not auto-migrate another repository.
5. Check worker and Host payloads separately. Worker payloads contain native check commands and returned evidence;
   Host payloads retain baseline SHA, tested SHA, run identity, collection, repair and completion responsibilities.
6. Run the project's existing required verification. Confirm managed guidance and project-owned instructions agree,
   all required coverage remains, and no new E2E, tooling dependency or CI redesign was introduced.

The ownership split is complete when a worker can follow its task without launching a second execution checkout,
and the Host still accounts for every required integrated-result check. Instruction and rendered-asset tests
verify this routing; live agent compliance remains a review responsibility.
