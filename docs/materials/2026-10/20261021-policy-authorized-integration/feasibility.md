# Policy-authorized integration feasibility

## Recommendation and alternatives

Extend the existing MCP `integration_integrate` entry point: `IntegrationService` derives policy authority for auto
local requests, skips its confirmation callback and executes the same validated request. Keep ask elicitation,
retained status/resume and local-only execution. No new tool, runtime profile or executing CLI is necessary.

| Route | Existing evidence | Additional work and limitation |
| --- | --- | --- |
| MCP/service dispatch (recommended) | `service.py:199` prepares/confirms, `service.py:329` executes, `mcp.py:65` exposes the service | Admit local auto, derive/report internal authority, preserve scope and policy validation; requires connected/permitted runtime |
| New execution CLI on shared service | `cli.py:16` currently prepares only | Add explicit owning-workspace/environment binding and restart semantics; `core/mcp_context.py:89` has no binding guard for an ordinary CLI invocation |
| Gate-only or finish command guidance | Workflow already supports policy gate passage | Cannot establish checked policy authority or reuse the service's retained partial progress |

All relative source references below are under the repository: integration files under
`packages/devkit/src/devkit/integration/`, core context under `packages/devkit-dist/src/devkit/core/`.

## Internal evidence

- `providers.py:78–99`: base shared policy is read directly and ask is the only accepted policy today.
- `service.py:199–239`: only native affirmative confirmation currently authorizes `_run`; no caller-supplied
  boolean or serialized authority is accepted. Auto must derive authority internally, not fabricate a reply.
- `service.py:144–181,276–317`: interpreter retention, required PR policy, readiness, exact cleanup scopes,
  provider/guard identities and effective-policy digests are already checked.
- `service.py:329–550`: the common engine locks execution, records progress, inspects uncertain outcomes,
  revalidates before effects and distinguishes the initial build from retained resume.
- `core/mcp_context.py:38–98`: owning workspace identity and local environment are checked; no binding means an
  ordinary explicit CLI uses its existing authorization contract. Do not weaken this guard for auto.
- `packages/devkit-mcp/src/devkit_mcp/server.py:47–83`: elicitation capability is checked inside the confirmation
  callback, not unconditionally before tool dispatch. Avoiding that callback can support auto without form capability.
  The non-read-only binding guard and read-only profile remain effective.
- `packages/devkit-spec/src/devkit_spec/integration.py:10,225,433`: source completion and committed evidence remain
  checked; CI rules run on the built result. Tests and code review do not rerun on that result.
- `ADR-integration-approval-asserted`, `CAP-DLV-project-policy` and `CAP-DLV-delivery-workflows` deny execution authority
  to existing gate policies. A successor ADR and consistent contract/instruction edits are required.

## Official host documentation

Read by the isolated Scout on 2026-10-20. These describe permission boundaries, not proof of this feature's runtime
behavior. Repository policy does not override any of them.

- [OpenAI sandboxing](https://learn.chatgpt.com/docs/sandboxing), “What the sandbox does”: command execution is subject
  to filesystem and network restrictions.
- [OpenAI agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security): approval policy and
  review govern host permission independently of the repository's business approval.
- [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference): sandbox and MCP
  tool approval configuration are separate host controls.
- [Claude Code permissions](https://code.claude.com/docs/en/permissions), tool-specific permission rules: MCP tools
  have permission rules independently of Bash commands.
- [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing), “What runs outside the sandbox”: local MCP
  servers run outside the Bash sandbox with user access. Choosing MCP after a refused shell write would evade a
  host boundary; this design never uses route switching as a remedy for refusal.

## Observed host coverage and gaps

`MAT-claude-terminal-mcp-approval-evidence` records Claude Code 2.1.303 on macOS completing real ask-mode merge,
worktree removal, branch deletion and scoped extension cleanup without push. It explicitly excludes auto-mode and
separate prompt counts. The Codex CLI 0.163.0 spike in
`docs/materials/2026-10/20261017-hook-driven-integration-cleanup/codex-spike-evidence.md` demonstrates form behavior
with simulated integration results, excluding real mutations and auto execution.

Neither source establishes live auto behavior. No live Codex CLI or Claude Code auto session was run in this
Planning turn. Development must exercise the implemented tool on both hosts in disposable repositories with the
selected MCP tool and server access permitted, recording versions, tool prompts, absence of devkit elicitation,
actual refs/cleanup and no remote effects. If unavailable or denied, leave that acceptance evidence unverified;
report the exact boundary rather than promise zero host prompts.

## Engine reuse verification

Planning ran the existing tests with:

```bash
uv run --no-sync pytest packages/devkit/tests/integration/test_service.py -q -k 'native_approval_integrates or delete_branch_false or merge_then_permission_failure or scoped_cleanup_receives or public_local_only_finish or unknown_merge_outcome'
```

Result: **6 passed, 45 deselected**. Coverage: no-network real merge/cleanup in test Git repositories, retained
branch policy, post-merge permission failure and resume, exact extension cleanup after Git finish, explicit
local-only finish, and uncertain merge outcome inspection. These tests use the current ask confirmation callback;
they prove reusable mechanics only. They are not auto-mode tests, live host smoke or a full-suite claim.

## Recovery and revocation choice

Keep requests and step progress in the existing server process. Auto requests bind their initial policy and exact
scope, require effective auto before remaining effects and refuse a prospective auto-to-ask result before merge.
Retained resume cannot absorb a later target. A new call may prepare current state under current policy, never an
old approval file. After server loss, missing branch/worktree evidence may prevent exact extension cleanup from
being reconstructed: report incomplete scope and use deliberate recovery, without guessing targets or adding a
journal to this feature.

No code implementation or repository ask-policy change occurs in Planning. `ADR-policy-authorized-local-integration`
proposes the contract change; the proposal acceptance criteria define the implementation evidence still required.
