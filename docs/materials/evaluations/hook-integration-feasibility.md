# Hook-Driven Integration & Cleanup Feasibility Evaluation

- **Evaluation Date**: 2026-10-16
- **Subject**: devkit-spec [SPEC-hook-driven-integration-cleanup](../../../specs/2026-10/20261017-hook-driven-integration-cleanup/spec.md)
- **Scope**: Official host documentation review, devkit `94085f4` source inspection, and lifecycle API experiments in a temporary Git repository.
- **Limits**: Real host hook installation, trust approvals, native confirmation buttons, and sandbox escalations were not executed. Local CLI environment was `codex-cli 0.163.0` and Git `2.43.0`; Claude Code and Antigravity binaries were evaluated from official interface specifications.
- **Outcome**: Adopted conditionally and implemented via `SPEC-hook-driven-integration-cleanup`, establishing `CAP-INT-mcp-services` and `IntegrationService`.

---

## 1. Assessment Summary

**The target capability is conditionally viable.** A deterministic executor performing merge, branch deletion, and worktree removal should be constructed, with host adapters relaying approvals or policy delegations to that executor.

**The concept of "a single shared hook intercepting a default approval button click to run the remaining integration sequence" was not confirmed across hosts.** Tool execution approval, SDD delivery integration approval, and hook trust are three distinct decisions. Binding all three into a single structured integration request avoids repetitive prompts. Both `ask` and `auto` policies assume host-granted execution permissions.

---

## 2. Host-Specific Evidence

| Host | Confirmed Contract | Assessment for Integration |
| :--- | :--- | :--- |
| **Codex** | `PermissionRequest` with `decision.behavior=allow` skips regular confirmation prompts. Deny takes precedence across multiple hooks. Modified unmanaged hooks require re-trusting. | Permission requests can be resolved through policy. Auto-review replacement is not guaranteed in all environments. |
| **Claude Code** | Command hooks run with user account permissions. `PermissionRequest` decides tool approval while explicit deny/ask rules remain intact. | Trusted command hooks can invoke an executor directly, distinct from general agent Bash tool calls. |
| **Antigravity** | `PreToolUse` with `auto_approve` skips default prompts while respecting explicit rules. No `PermissionRequest` event exists in the specification. | Requires a distinct adapter. Sandbox scope for the hook process itself requires isolated validation. |

Codex MCP hooks invoke connected servers without asking for separate tool approval. Providing a local executor with distinct permissions via MCP was identified as the primary path, provided the server validates requests.

Using native host buttons requires the **approved tool call itself to represent the entire integration command**. No shared contract was found where arbitrary conversation button clicks trigger a generic hook event.

---

## 3. Observed devkit Behavior

- Source inspection: `devkit.worktree.lifecycle`, `devkit.worktree.cli`.
- `finish --merge` executes fast-forward merge -> base push -> worktree removal -> local branch deletion per configuration.
- Successful executions run `post_finish` extensions. PR merging and remote task branch deletion remain separate responsibilities. Push failures are recorded as warnings while local cleanup proceeds.

Experiments in isolated Git fixtures:

| Experiment | Result | Design Implication |
| :--- | :--- | :--- |
| Work commit followed by `finish(merge=True)` | `merged=true`, `push=no-upstream`, `removed=true`, `branch_deleted=true` | Core local sequence is directly reusable. |
| Repeating the same call after completion | `WORKTREE_NOT_FOUND` | Idempotent duplicate event handling requires completion receipts. |
| Squashing two separate commits before `finish()` | `WORKTREE_UNMERGED`, worktree preserved despite identical trees | PR merge evidence requires a dedicated cleanup contract. |
| Untracked files in worktree during `finish(merge=True)` | Merge succeeds, removal refused with `WORKTREE_DIRTY` | Steps are not inherently atomic; pre-checks and resumable cleanup are essential. |

---

## 4. Implementation Direction

1. **Preparation**: Bind repository, base, branch, head SHA, PR, merge strategy, cleanup targets, and completion evidence into an immutable integration request.
2. **Authority Binding**: `ask` requires a single explicit approval for the entire request; `auto` validates effective policy and completion evidence. Initial host trust is treated as an installation prerequisite.
3. **Execution**: A single installed command validates the request and executes merge, push, and cleanup in sequence. Hooks act as adapters for this command without duplicating execution.
4. **Resumption**: Store per-request locks and step receipts. Duplicate events return cached results; failures resume from the remaining steps. Head changes invalidate pre-merge approval, but post-merge cleanup retries reuse existing evidence.
