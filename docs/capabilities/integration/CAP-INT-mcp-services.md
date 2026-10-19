---
id: CAP-INT-mcp-services
title: "Scoped MCP Services"
summary: "Four scoped local integration MCP tools with one native approval in the Codex and Claude Code terminal CLIs, concise default results, detailed inspection and resumable cleanup."
area: integration
status: active
entrypoints:
  - packages/devkit/src/devkit/integration/
created_at: 2026-10-17
---

# [CAP-INT-mcp-services] Scoped Local Integration

`devkit.integration` prepares an immutable request, obtains a native confirmation through `devkit.host`, and
executes a local fast-forward and its exact cleanup scope. `host` owns MCP transport and native UI adaptation;
integration owns authorization binding, policy, readiness and execution. It imports no SDD models. Command and
code quick reference: [reference.md](../../development/reference/integration.md).

## 1. Supported path

The supported paths are interactive MCP tool calls under `dev-integration=ask` from two terminal hosts: the Codex
CLI and the Claude Code terminal CLI (verified in `MAT-claude-terminal-mcp-approval-evidence`). The server checks the
client's advertised form capability, not a host name. `integration_integrate`
prepares the request, awaits form elicitation, and continues into execution in the same call. After reporting verified work, call it directly; no separate conversational approval or preceding integration_prepare call is required. The native affirmative form supplies local dev-integration ask approval and exact execution authority together. A workflow waiting on that gate permits the approval-requesting call; --given dev-integration is asserted only after native acceptance. Only native
`action=accept` with a boolean `approve=true` grants authority. The field defaults to false. Submission without
approval, decline, cancellation, unavailable form capability and transport failure perform no integration changes.
Tool arguments cannot supply `approved`, authority tokens or serialized execution requests.

The form displays the repository, task, source/target branches and full SHAs, worktree removal and local branch
retention/deletion, and each cleanup extension's target kinds and identities. It states fast-forward execution and
network exclusion. Text values are quoted and control characters escaped so caller text cannot introduce misleading
extra scope lines. Filesystem identities, policy hashes, provider/guard registrations, cleanup revisions and full
readiness evidence remain in the immutable internal request and digest; they are not printed in the form.

The four tools have distinct roles:

- `integration_prepare`: optional read-only readiness and effect-scope inspection; no authority is granted. Integrate
  prepares a fresh request, so callers do not pass a prepared request ID as execution authority.
- `integration_integrate`: the normal entry point; prepares, requests one native approval, executes and returns progress.
- `integration_status`: read-only retained progress and observed state, concise by default. Optional boolean `detail`
  defaults false; true returns the complete retained request, evidence, revisions and underlying finish result.
- `integration_resume`: continues remaining steps of an already approved process-local request, with no second form.
  It accepts only request_id and cannot grant authority, change scope or request arbitrary execution.

Task tools accept branch, task_kind, task_id, optional unit and claims. All four default result views include the
request ID/digest and effect scope, status, authority, steps, errors and notices. UI action, per-extension steps,
failing operation and observed state appear when present. Internal validation fields and duplicate FinishResult
are omitted. Detailed status preserves the existing full representation. CLI preparation and the library's full
serialization remain unchanged. MCP text JSON and structuredContent encode the same compact object for clients
using either transport representation.

The executor runs from the retained base checkout on its target branch, using an installed interpreter outside
the worktree being removed. It supports normal linked worktrees and marked `--no-worktree` activity branches.
It excludes PR operations, fetch, push, remote branch deletion, squash/rebase integration and automatic policy
dispatch. Required-PR policy refuses the local path. Worktree/PR `auto` does not authorize integration.

Project trust, hook trust, MCP tool approval, the business integration confirmation and host filesystem/network
permissions are distinct. This service never changes host permission settings. Native tool annotations describe
real write/destructive effects; they do not substitute for the integration form. Count actual prompts separately
when validating a host session. SDK transport tests do not establish interactive UI or permission behavior.
Unverified for Claude Code: its auto mode and other permission modes, the number of prompts per call, and the
Claude Desktop, VS Code extension and Agent SDK surfaces, where upstream reports describe elicitation declined
without a visible form (`MAT-native-approval-host-comparison`). Treat those surfaces like any client without
working form capability.

## 2. Request and state validation

Each request has a random process-local ID and a digest of its immutable contents:

- base repository, common Git directory and its filesystem identity;
- source branch and full commit SHA, target branch and expected full SHA;
- exact worktree path and filesystem identity, source upstream and devkit task markers;
- local branch deletion/marker policy, fixed FF method and network exclusion;
- Unit or session task reference, explicitly separate caller claims and provider evidence;
- effective configuration/receipt digest, expected post-merge configuration/receipt digest, provider and guard identities;
- each post-finish extension and its exact package-owned cleanup identities and revisions.

Claims are a provider-specific JSON object of at most 16 KiB; they are declarations, not automatically verified
facts or approval. A Unit task requires its canonical repository-relative directory. A session task has no Unit,
envelope or invented gate file. The provider decides how each kind establishes review, checks and other completion
conditions. Its evidence must bind the exact source and target SHAs and use stable `UPPER_SNAKE` codes.

Prepare checks clean base/source state, worktree identity/lock, fast-forward eligibility and safe local branch
deletion. It runs existing finish guards and plans scoped post-finish cleanup before showing confirmation.
Execution rechecks provider evidence before merge and revalidates Git identities, policy and cleanup scope at each
mutation boundary. Source/target changes, changed policy outside the expected merge, provider/guard changes or
changed cleanup revisions invalidate the request. A source commit's known configuration changes are included in
the expected post-merge digest. `delete_branch=false` in either applicable policy keeps the branch.

The Git common-directory lock serializes devkit integration executors. Stop workers that mutate the branch before
approval; arbitrary Git processes and filesystem editors do not take this lock. Git and filesystem identities are
rechecked immediately before operations, but this is not an exactly-once or general cross-process transaction.

## 3. Readiness providers

Configure the installed provider in the base project's `.devkit/config.toml`:

```toml
[integration]
provider = "my-methodology"
```

There is no permissive default provider. A missing, duplicate, unloadable or malformed provider fails closed. Its
package registers a module or object with `check(context)`:

```toml
[project.entry-points."devkit.integration.readiness"]
my-methodology = "my_package.integration"
```

`check(IntegrationContext) -> Readiness` verifies final committed work at `context.finish.source_sha`, compared with
`target_sha`. It returns immutable `Evidence(code, value)` entries and any blocking `reasons`. Empty evidence,
wrong SHAs and malformed results fail closed. Evidence must be deterministic across rechecks: use commit IDs and
verified facts rather than timestamps or mutable command logs. Read-only checks must not mutate Git, call network
services or treat claims as approval. Verification commands and any report/evidence interpretation belong to the
provider; the generic executor never executes model-supplied commands.

For SDD, devkit-spec owns the provider's Unit/session evidence, review, reconcile and blocked/question policy.
The existing workflow envelope finish guard remains active, but is not proof of all completion conditions. This
release supplies the public provider contract; installing devkit alone does not supply SDD readiness. The devkit
contract is released before the consuming package updates its dependency, provider and guidance.

## 4. Scoped post-finish cleanup

Reuse `devkit.post_finish` registration. Classic `worktree finish` keeps its existing callable contract. For
approval-bound integration, the registered object must additionally expose:

```python
integration_local_only = True

def integration_plan(context) -> tuple[CleanupTarget, ...]: ...
def integration_validate(context, targets: tuple[CleanupTarget, ...]) -> None: ...
def integration_run(context, result: FinishResult, targets: tuple[CleanupTarget, ...]) -> CleanupResult: ...
```

Each `CleanupTarget(kind, identity, revision)` names one exact package-owned target. Planning and validation are
read-only. Validation refuses replaced/revised targets; the runner consumes only the approved tuple and is safe to
rerun after partial completion. It must not discover additional targets to delete at execution time.
`CleanupResult(done, notices)` reports completion and normal advisory notices. `done=false` leaves cleanup partial
with `INTEGRATION_CLEANUP_INCOMPLETE` and an explicit resume directive. Earlier Git progress is preserved.
Completed cleanup extensions are skipped on subsequent attempts.

An installed legacy callback without this scoped contract is `INTEGRATION_CLEANUP_UNSCOPED` before approval; it is
never silently skipped or invoked with broader authority. devkit-spec must adapt its existing scope/proposal
cleanup before its installed pair can use this path. This avoids a second host adapter or duplicated Git executor.

The executor itself invokes no network operation. Installed providers, guards, Git hooks/filters and cleanup code
are trusted code and must obey the local-only contract; OS/host network restrictions enforce the process boundary.
The application does not claim to sandbox arbitrary extension code.

## 5. Partial results and main-agent recovery

Compact results report status, authority, concise request scope, steps, errors and notices, plus native UI action,
per-extension cleanup steps, observed state and failing operation when present. Detailed status additionally reports
the complete request and underlying FinishResult. Steps
are `not_run`, `running`, `completed`, `skipped`, `failed` or `unknown`. A timeout can leave an unknown operation;
the observed state is included rather than asserting that it never happened.

After affirmative confirmation, `integration_resume(request_id)` can finish the retained request without asking
the business approval again solely for execution-permission failure. It inspects state and preserves completed
merge/removal steps. It does not merge again after a confirmed merge. Changed scope requires a new request and
approval; dirty, locked, replaced or unrelated worktrees are preserved. Permission remedies stay host-owned.

The service retains at most 128 requests in memory. Pending/partial requests are not evicted to make room; completed
or non-approved ones can be retired. There is no approval file, durable execution journal, automatic background
retry or cross-session restart recovery. After process termination or an unknown request ID, inspect Git first.
Use the existing guarded `worktree finish --local-only` cleanup path only after confirming the remaining targets
and existing authority, or obtain a new request for the remaining scope. Never infer approval from a digest or
replay a serialized result as authority.

## 6. Setup and verification

Follow the optional MCP onboarding route linked from installation. Install `devkit-agt[mcp]` in a retained base
runtime, then run `devkit host mcp setup --host codex` there for explicit user-scoped Codex registration.
`devkit host mcp status --host codex` checks registration against that runtime/base and SDK availability; it leaves
connection and approval UI unknown. Matching entries are unchanged; different registrations require explicit
`--replace`. Setup refuses linked-worktree/submodule workspace or runtime paths. Sync does not register MCP.
The read-only `devkit host mcp config --format json -w <base>` still prints exact add/get/remove commands and TOML.
Claude Code has no devkit setup adapter: register server `devkit` with Claude Code's own writer,
`claude mcp add --scope user devkit -- <command> <args...>`, using the `command` and `args` that config prints for
the retained base and runtime; `claude mcp get devkit` inspects it and `claude mcp remove devkit -s user` removes it.
`devkit host mcp status` does not inspect that registration. Reconnect the client and verify tool discovery and
visible confirmation separately. See `CAP-HOST-lifecycle-observation` and
[Host MCP](../../development/reference/host.md#mcp-services).

Development checks exercise an installed SDK client/server over stdio and real disposable Git fixtures: approval,
non-approval, decline/cancel, absent form capability, caller approval-flag rejection, stale scope, PR policy,
branch retention, scoped cleanup and merge-then-cleanup failure recovery. No external API call is needed.
Consumer smoke installs the wheel extra and checks the installed transport. Native host UI, actual host permission
prompts and the installed devkit-spec provider remain separate validation evidence, not consequences of SDK tests.
