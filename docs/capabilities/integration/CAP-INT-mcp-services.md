---
id: CAP-INT-mcp-services
title: "Scoped MCP Services"
summary: "Four scoped integration MCP tools bind one native approval to local or GitHub pull request integration, with pinned source commits, landing evidence and resumable cleanup."
area: integration
status: active
entrypoints:
  - packages/devkit/src/devkit/integration/
created_at: 2026-10-17
---

# [CAP-INT-mcp-services] Scoped Integration

`devkit.integration` prepares an immutable request, obtains a native confirmation through the optional
`devkit-mcp` runtime using the dependency-free `devkit.core.mcp.Confirmation` contract, and
lands the task through the selected route: locally (a merge commit built outside the base checkout, or a fast-forward under
`[worktree] merge = "ff-only"`) or through a GitHub PR merge commit, with its exact cleanup scope. `devkit-mcp` owns MCP transport and native UI adaptation;
integration owns authorization binding, policy, readiness and execution. It imports no SDD models. Command and
code quick reference: [reference.md](../../development/reference/integration.md).

## 1. Supported path

The supported paths are interactive MCP tool calls under `dev-integration=ask` from two terminal hosts: the Codex
CLI and the Claude Code terminal CLI (verified in `MAT-claude-terminal-mcp-approval-evidence`). The server checks the
client's advertised form capability, not a host name. `integration_integrate`
prepares the request, awaits form elicitation, and continues into execution in the same call. After reporting verified work, call it directly; no separate conversational approval or preceding integration_prepare call is required. The native affirmative form supplies route-specific dev-integration ask approval and exact execution authority together. A workflow waiting on that gate permits the approval-requesting call; --given dev-integration is asserted only after native acceptance. Only native
`action=accept` with a boolean `approve=true` grants authority. The field defaults to false. Submission without
approval, decline, cancellation, unavailable form capability and transport failure perform no integration changes.
Tool arguments cannot supply `approved`, authority tokens or serialized execution requests.

The form leads with the action, `Approve local integration of "<branch>" into "<target>" with a merge commit?` (`by
fast-forward?` under `ff-only`; `Approve cleanup of "<branch>", already merged into "<target>"?` for a cleanup-only
request), and, when supplied by the readiness provider, the committed
task title, goal and final-report summary (`TASK_TITLE`, `TASK_SUMMARY`, `RESULT_SUMMARY` evidence). The SDD provider
reads these from the source commit; they are presentation evidence, not additional approval authority. Each displayed
summary is bounded to 1,500 characters with an explicit truncation marker; full evidence remains in the request.
The form then displays the repository, task, source/target branches and full SHAs, worktree removal and local branch
retention/deletion, and each cleanup extension's target kinds and identities. The target SHA is the confirmation
target, marked `(at confirmation)`. Under `no-ff` the form states that later commits on the target are merged in
without another confirmation only if the merge is clean, the integration policy is unchanged and the named readiness
provider passes again on the merged result, otherwise nothing changes on the target, followed by the provider's
result-check disclosure (`Result check: ...`); under `ff-only` that a moved target changes nothing; for a cleanup-only
request that nothing is merged. The local form states network exclusion. Text values are quoted and control characters escaped so caller text cannot introduce misleading
extra scope lines. Filesystem identities, policy hashes, provider/guard registrations, cleanup revisions and full
readiness evidence remain in the immutable internal request and digest; they are not printed in the form.

The four tools have distinct roles:

- `integration_prepare`: optional readiness and effect-scope inspection; PR prepare fetches the remote target but performs no remote write; no authority is granted. Integrate
  prepares a fresh request, so callers do not pass a prepared request ID as execution authority.
- `integration_integrate`: the normal entry point; prepares, requests one native approval, executes and returns progress.
- `integration_status`: read-only retained progress and observed state, concise by default. Optional boolean `detail`
  defaults false; true returns the complete retained request, evidence, revisions and underlying finish result.
- `integration_resume`: continues remaining steps of an already approved process-local request, with no second form.
  It accepts only request_id and cannot grant authority, change scope or request arbitrary execution.

Task tools accept branch, task_kind, task_id, optional unit, claims and route (`local` by default, or `pull-request`). All four default result views include the
request ID/digest and effect scope, status, authority, steps, errors and notices. UI action, per-extension steps,
failing operation and observed state appear when present. Internal validation fields and duplicate FinishResult
are omitted. Detailed status preserves the existing full representation. CLI preparation and the library's full
serialization remain unchanged. MCP text JSON and structuredContent encode the same compact object for clients
using either transport representation.

The executor runs from the retained base checkout on its target branch, using an installed interpreter outside
the worktree being removed. It supports normal linked worktrees and marked `--no-worktree` activity branches.
The default local route excludes PR operations, fetch, push and remote branch deletion. Both routes exclude squash/rebase integration and automatic policy dispatch. Required-PR policy refuses the local path. Worktree/PR `auto` does not authorize integration.

Project trust, hook trust, MCP tool approval, the business integration confirmation and host filesystem/network
permissions are distinct. This service never changes host permission settings. All four tools declare `openWorldHint=true`, since PR prepare/status also reach the network. Native tool annotations describe
real write/destructive effects; they do not substitute for the integration form. Count actual prompts separately
when validating a host session. SDK transport tests do not establish interactive UI or permission behavior.
Unverified for Claude Code: its auto mode and other permission modes, the number of prompts per call, and the
Claude Desktop, VS Code extension and Agent SDK surfaces, where upstream reports describe elicitation declined
without a visible form (`MAT-native-approval-host-comparison`). Treat those surfaces like any client without
working form capability.

## 2. Local request and state validation

Each request has a random process-local ID and a digest of its immutable contents:

- base repository, common Git directory and its filesystem identity;
- source branch and full commit SHA, target branch and the confirmation target's full SHA;
- exact worktree path and filesystem identity, source upstream and devkit task markers;
- local branch deletion/marker policy, the merge method (`no-ff` or `ff-only`), whether the request is cleanup-only,
  and network exclusion;
- Unit or session task reference, explicitly separate caller claims and provider evidence;
- the effective policy digest of the base and the expected one of the result, provider and guard identities;
- the provider's readiness, including its declared target-bound evidence codes and result-check disclosure;
- each post-finish extension and its exact package-owned cleanup identities and revisions.

Claims are a provider-specific JSON object of at most 16 KiB; they are declarations, not automatically verified
facts or approval. A Unit task requires its canonical repository-relative directory. A session task has no Unit,
envelope or invented gate file. The provider decides how each kind establishes review, checks and other completion
conditions. Its evidence binds the context's source, target and result commits and uses stable `UPPER_SNAKE` codes.

Prepare checks clean base/source state, worktree identity/lock and safe local branch deletion. The source must
contain the target, or the target must already contain the source, which prepares a cleanup-only request; any other
pair is `WORKTREE_MERGE_NOT_FF`, whose fix merges the target into the branch (never a rebase). Under `no-ff` a
missing committer identity is refused before the confirmation (`WORKTREE_COMMIT_FAILED`). Prepare runs the existing
finish guards (with the merge base: the target, or the source for a cleanup-only request), plans scoped post-finish
cleanup and builds nothing before showing confirmation.

**Effective policy** (`ADR-effective-policy-digest`): the digest covers the parsed values devkit owns,
`[workflow.approvals] dev-integration`, `[worktree] pull_request`, `delete_branch` and `merge`, and
`[integration] provider`, with their defaults. Raw configuration and receipt bytes and asset hashes are not bound, so
a bundle sync on the target leaves an open confirmation valid. The base's digest must be unchanged at every
validation before the merge (a change is `INTEGRATION_REQUEST_STALE` whatever the new value); the result commit's
must equal the one prospected from the source commit; after the merge the base's must equal it. A cleanup-only
request expects the target's policy at prepare. `delete_branch=false` or `merge="ff-only"` in either the base's or the
source's policy wins.

**One build per approving call** (`ADR-merge-commit-outside-checkout`, `ADR-target-advance-readiness`): after the
native acceptance the call reads the current target (the build target), which must descend from the confirmation
target (a reset or rewritten target is `INTEGRATION_REQUEST_STALE`). `devkit.worktree.build_result` builds the result
commit in the object store: under `no-ff` a commit with the build target as first parent, the approved source tip as
second and the message `chore(merge): integrate <branch> into <target>`, whose tree is the source tree when the target
did not advance and the `git merge-tree --write-tree` result when it did (Git 2.38 or later,
`WORKTREE_GIT_UNSUPPORTED`; a conflict is `WORKTREE_MERGE_CONFLICT`); under `ff-only` the source tip itself (an advanced
target is `WORKTREE_MERGE_NOT_FF`). `git commit-tree` uses the identity configuration, signs when `commit.gpgSign` is
on, never prompts and is bounded to 30 seconds (`WORKTREE_COMMIT_FAILED`). The build then runs the finish guards with
`merge-base(build target, source)` and the source tip, the readiness provider with the execution context, the result
policy check and the receipt check: a merged `.devkit/installation.json` record whose path is tracked in the result
and whose `(recorded hash, blob)` pair equals neither parent's must match its blob (`INTEGRATION_RECEIPT_CONFLICT`,
also for a merged receipt that does not parse; untracked projections and inconsistencies already on a parent are
skipped). Immediately before the fast-forward the base must still point at the build target
(`INTEGRATION_TARGET_MOVED`, merge step `not_run`, no in-call retry). The base checkout only fast-forwards onto the
result, so it never stops mid-merge; every refusal of the build changes nothing on the target. The result reports
`build` (confirmation target, build target, result commit), kept in the process outside the request digest.

After the merge every step checks that the base contains the result (later commits on the base are allowed) and
revalidates Git identities, policy and cleanup scope at each mutation boundary. Changed source, provider/guard
registrations or cleanup revisions invalidate the request.

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
`target_sha`. At prepare `context.result_sha` is `None`; at a build the execution context carries the build target as
`finish.target_sha` and the result commit as `result_sha`. It returns immutable `Evidence(code, value)` entries, any
blocking `reasons`, the bound `result_sha`, the `target_bound` evidence codes whose values may change with the target,
and a required `disclosure`: one printable line of at most 200 characters saying what it checks on the merged result,
shown in the form. Empty evidence, wrong SHAs, undeclared codes, a missing or malformed disclosure and malformed
results fail closed (`INTEGRATION_PROVIDER_FAILED`). At a build the result must carry no reasons
(`INTEGRATION_NOT_READY`) and equal the approved readiness except the target-bound evidence
(`INTEGRATION_REQUEST_STALE`); the generic executor runs no tests on the result. Evidence must be deterministic across rechecks: use commit IDs and
verified facts rather than timestamps or mutable command logs. Read-only checks must not mutate Git, call network
services or treat claims as approval. Verification commands and any report/evidence interpretation belong to the
provider; the generic executor never executes model-supplied commands.

PR readiness additionally declares a nonempty `landed_check`, bound in the request and shown before approval; devkit-spec declares `devkit rules check` in the retained base checkout. The executor reports this directive and does not execute it.

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

Validation and the runner receive the execution context: after a build `finish.target_sha` is the build target and
`result_sha` the landed result commit; a cleanup-only request passes the source as `result_sha`; before a build it is
the approved context. Cleanup revisions bind to the source and package-owned state, never to a target SHA. Each
`CleanupTarget(kind, identity, revision)` names one exact package-owned target. Planning and validation are
read-only. Validation refuses replaced/revised targets; the runner consumes only the approved tuple and is safe to
rerun after partial completion. It must not discover additional targets to delete at execution time.
`CleanupResult(done, notices)` reports completion and normal advisory notices. `done=false` leaves cleanup partial
with `INTEGRATION_CLEANUP_INCOMPLETE` and an explicit resume directive. Earlier Git progress is preserved.
Completed cleanup extensions are skipped on subsequent attempts.

An installed legacy callback without this scoped contract is `INTEGRATION_CLEANUP_UNSCOPED` before approval; it is
never silently skipped or invoked with broader authority. devkit-spec must adapt its existing scope/proposal
cleanup before its installed pair can use this path. This avoids a second host adapter or duplicated Git executor.

The local executor invokes no network operation; only the PR executor invokes remote operations. Installed providers, guards, Git hooks/filters and cleanup code
are trusted code and must obey the local-only contract; OS/host network restrictions enforce the process boundary.
The application does not claim to sandbox arbitrary extension code.

## 5. Partial results and main-agent recovery

The following local recovery rules are supplemented by the PR route contract below.

Compact results report status, authority, concise request scope, steps, errors and notices, plus native UI action,
per-extension cleanup steps, observed state and failing operation when present. Detailed status additionally reports
the complete request and underlying FinishResult. Steps
are `not_run`, `running`, `completed`, `skipped`, `failed` or `unknown`. A timeout can leave an unknown operation;
the observed state is included rather than asserting that it never happened.

After affirmative confirmation, `integration_resume(request_id)` can finish the retained request without asking
the business approval again solely for execution-permission failure. It inspects state and preserves completed
merge/removal steps. It does not merge again after a confirmed merge. The approval tolerates target advances only
within the approving call: resume continues only onto the last build target, or onto the confirmation target when the
approving call ran no build, and a later target is `INTEGRATION_REQUEST_STALE` (a new `integration_integrate`); a
cleanup-only request resumes only its remaining cleanup. After a failed or unknown merge step, a base containing the
latest result (the source under `ff-only`) means merged, a base equal to the last build target means not merged, and
anything else is stale.

The approving call waits up to 20 seconds for the Git common-directory integration lock another devkit executor holds
(`devkit worktree finish --merge` takes it too), then reports `LOCK_HELD` with nothing changed and a `[FIX]` naming
`integration_resume` while the target still equals the confirmation target, else a new `integration_integrate`.
`integration_resume` never waits (`LOCK_HELD` at once). The 20-second wait, within the 30-second upper bound of
`ADR-target-advance-readiness`, plus the 30-second `commit-tree` bound stays below Codex's default 60-second MCP tool
timeout; a host that cuts a call leaves the request inspectable with
`integration_status`. Changed scope requires a new request and
approval; dirty, locked, replaced or unrelated worktrees are preserved. Permission remedies stay host-owned.

The service retains at most 128 requests in memory. Pending/partial requests are not evicted to make room; completed
or non-approved ones can be retired. There is no approval file, durable execution journal, automatic background
retry or cross-session restart recovery. After process termination or an unknown request ID, inspect Git first.
Use the existing guarded `worktree finish --local-only` cleanup path only after confirming the remaining targets
and existing authority, or obtain a new request for the remaining scope. Never infer approval from a digest or
replay a serialized result as authority.

## 5a. GitHub pull request route

`route="pull-request"` implements `ADR-github-pull-request-repository-binding` and
`ADR-pull-request-merge-with-pinned-source-and-verified-landing`. The gh-backed injectable port lives in
`devkit.worktree`; provider/cleanup extensions remain local-only. Every repository operation binds the resolved host
and owner/repository, using supported gh syntax, including Enterprise hosts and aliases resolved by gh. Credentials
remain owned by gh. No caller-authored PR title or body is accepted; devkit composes them from validated names/task ID.

PR preparation requires a 1–256 character task ID matching `[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}`. The selected
remote must have exactly one effective push destination, and fetch/push destinations must resolve to the same
GitHub repository. Credential-bearing HTTP(S) remote URLs are refused; authentication stays with gh.
Prepare fetches the same-named upstream of the checked-out target branch. That fetched commit supplies the
confirmation target and target policy. A local target ahead of or divergent from upstream, divergent remote source,
missing authenticated gh, unsupported/fork/draft/wrong-base PR, merge queue, or readable merge-commit prohibition
refuses before confirmation. `ff-only` on either side refuses this route. Unreadable classic protection is disclosed
as unverified. Source commits must contain the confirmation target, except confirmed cleanup-only requests.

The immutable request additionally binds route, remote name/URLs and resolved host/repository, source/target refs,
PR number or create, the source SHA, confirmation target, no-ff merge and selected local/remote cleanup. Raw remote
URLs are not emitted in result/form serializers. The form lists push, PR create/use, merge, fetch, local fast-forward,
worktree removal and selected branch/scope deletion. It discloses GitHub automatic branch deletion, which can remove
the remote branch independently of devkit retention policy, unverified protection, the target race and landed check.

Publication pushes an explicit source-SHA refspec without force or `-u`, preserving the source upstream. PR identity
changes after prepare refuse new publication. Under the common-directory lock, execution fetches the target,
requires descendant history and unchanged effective policy, constructs and checks the prospective merge with the
existing guards, readiness and receipt validation, then rechecks the remote ref. Required checks and reviews must
pass. The synchronous GitHub merge API receives `sha=<approved source>` and `merge_method=merge`; it cannot enqueue,
including when queue policy changes after preflight. No auto-merge or admin bypass is requested.

Pending checks/reviews or undetermined mergeability return successful incomplete `status="pending"`, with
`INTEGRATION_CHECKS_PENDING` under notices, publication completed and merge not run. The directive names bounded
`gh pr checks <number> -R <host/owner/repo> --watch`, then `integration_resume`; report required checks that never
start. No lock is held while waiting. Resume acquires the lock without waiting, re-reads PR identity/head/state,
and merges only onto the last checked target, reusing that checked build. A moved target returns
`INTEGRATION_TARGET_MOVED`: merge it into the source, re-verify and obtain new approval. Report repeated movement;
a target advancing faster than checks finish may prevent this route from ever merging.

PR `MERGED` plus merge commit `M` with exactly two parents and `M^2` equal to source confirms the merge. A checked
landing also requires `M^1` equal to the checked build target, equal checked tree and `M` contained in fetched target.
Other confirmed landings carry `INTEGRATION_LANDED_UNCHECKED` at WARNING with reason `advanced`, `tree-mismatch`,
`rewritten-base`, `merge-not-contained` or `not-recorded`, plus merge/parent/fetched-target evidence and the provider's
landed-check directive. Never describe these as checked integration. Guards/readiness/policy are not rerun on M.
Source ancestry in the fetched target is mandatory; its loss is `INTEGRATION_SOURCE_NOT_CONTAINED` and deletes nothing.

Checked and unchecked confirmed landings both proceed with the approved cleanup scope: fast-forward a clean local
target, remove the worktree/local branch through guarded finish, delete the selected remote branch with the exact
source-SHA lease after checking dependent PRs, then invoke scoped cleanup extensions. Dirty/divergent local target
stops before deletion. An already-absent remote branch counts as done; a moved branch or open dependent PR is
`INTEGRATION_REMOTE_DELETE_BLOCKED` and remains intact. Later target configuration changes do not broaden or block
approved cleanup. A fresh prepare can confirm a still-present merged task for cleanup after restart, reporting
`not-recorded`; process-local approval is never restored from a file.

Mutation outcomes remain unknown until remote observations confirm them. HTTP 403/405/409/422 merge refusals are
`INTEGRATION_MERGE_REFUSED`; unresolved transport failures are `INTEGRATION_STEP_UNKNOWN`. Unknown merge never retries
or deletes destructively. Results distinguish publication, merge, fetch, local fast-forward, local/remote deletion
and extension progress. `integration_status` observes remote state without authorizing work.

Each network subprocess is capped at 5 seconds, further limited by a 20-second phase budget. Prepare and approved
execution each start a phase; resume/status start one phase. These network budgets do not bound provider, local Git,
lock or interactive confirmation time. SDK/offline timings do not establish live-host latency. A host timeout may
leave the executor thread running; inspect `integration_status` before recovery. Default host timeout evidence and
measurement limits are recorded in the unit's platform evidence material.

## 6. Setup and verification

Install `devkit-agt[mcp]` intentionally in a retained base/tool runtime, then run ordinary `devkit sync` for selected
Codex/Claude project registrations. `devkit mcp status` distinguishes local registration facts from unknown
connection, effective enablement, forms, trust and permissions. See `CAP-MCP-runtime-registration`.

The Host validates the final committed scope and checks before calling `integration_integrate`; its native form
is the business approval. Workers return scope to their Host and do not request business approval. No extra chat
approval or `integration_prepare` call is required when native forms work. Missing runtime, disconnected transport,
unavailable form or unsupported cloud connectivity requires intentional installation/connection or an independently
authorized CLI/PR route. Missing UI never grants authority.

The calling Host's explicit configuration workspace controls execution, independently of source-branch provenance
or executor cwd. Integration status is read_only; prepare is preflight; integrate is interactive; resume is
approved_resume. Cloud rejects all but read-only invocation, including stale/direct registrations, before forms,
after replies/lock waits and before subsequent effects. A transition after effects returns partial progress.
Missing/malformed/replaced workspace identity fails closed. Only terminal cleanup of the exact configuration
workspace in the approving call can use its captured context after intentional self-removal; later calls, new
merge/push and resume cannot. Read-only retained diagnostics remain available.
