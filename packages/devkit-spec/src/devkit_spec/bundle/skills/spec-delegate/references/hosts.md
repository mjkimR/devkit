# Spawning a role on each host

Read this in Step 3 when spawning an isolated subagent; skip it when the main session substitutes. `devkit sync`
renders role contracts into selected native directories. Use `devkit status` and normal `devkit sync` where
authorized to repair missing/stale projections; never edit managed/projected files or host trust settings by hand.

| Host | Mechanism | Projected file |
| :--- | :--- | :--- |
| Claude Code | The subagent named `<role>` (Agent tool or `@agent-<role>`) | `.claude/agents/<role>.md` |
| Codex CLI | `collaboration.spawn_agent` with `agent_type: <role>` when available | `.codex/agents/<role>.toml` |
| Antigravity | `invoke_subagent` with the role name | `.agents/agents/<role>.md` |

## Availability and trust

Prefer the projected named role and pass only the payload: the host loads its contract. A missing role can mean a
missing/stale projection or a session started above the project root; role absence alone does not prove the root
is untrusted. Diagnose availability separately from trust. A session unable to load the named role MAY spawn a
generic native subagent that reads and follows the effective managed/override contract by absolute path, only when
host project-instruction loading is permitted. Pass that path in the payload and explicitly report emulation.
Never replace an override with the upstream contract during fallback.

An explicit host trust restriction MUST stop this fallback. Do not use a generic role, another tool/process/path,
or host configuration edits to bypass it. If trust must change, the user controls that change. Do not diagnose or
promise trusted status from a successful unrelated operation.

Before starting a worker, establish that native spawning, required nested roles and the approval capability needed
for its actual operations are available. If one is unavailable, use existing delegation policy: the Host runs the
unit in `direct` when allowed; `required` isolation stops with `needs_input`. Do not start a worker that cannot meet
its required nested-role or approval obligations. Capability availability is not a promise that an approval will be
granted. No persistent-grant preflight or separate probe framework is needed.

## Codex worker access

Both workers are `emulated` with `sandbox_mode: workspace-write`. Native invocation supplies no native role/path
enforcement. Workers inherit model and reasoning effort; projected roles set no approval-policy override.
Normal devkit sibling worktrees and shared Git administration can lie outside active sandbox access.

Every command sets absolute worktree cwd, Git uses `git -C <worktree>`, and nested-role read/contract paths are
absolute. Request a separate narrowly scoped approval for each necessary out-of-sandbox operation with the exact
operation, target and justification: writes, shared Git, scope registry and verification/network access included.
Use no broad persistent prefix. A successful preflight or approved call grants no later access. Stop an operation
when approval is refused/unavailable; preserve and return its actual partial state under [worker](worker.md).
