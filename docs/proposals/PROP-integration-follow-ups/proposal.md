---
id: PROP-integration-follow-ups
title: "Integration base advances: merge commits, effective policy digest and readiness on the result"
summary: "Lets an approved local integration absorb target commits that land during its confirmation: tasks land as merge commits built outside the base checkout, the approval binds the effective integration policy instead of raw file bytes, and readiness runs again on the merged result."
status: accepted                      # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: integration/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - integration/
    - worktree/
    - delivery/
    - packages/devkit/src/devkit/integration/
    - packages/devkit/src/devkit/worktree/
    - packages/devkit-spec/src/devkit_spec/
    - docs/roadmap/MS-multi-host-native-integration.md
  excludes: []                       # docs/decisions/ is written only by the handoff's PADR promotion
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-integration-follow-ups] Integration base advances: merge commits, effective policy digest and readiness on the result

- **Merged draft**: this draft also carries the former `integration-base-advance` draft (Backlog merge), whose
  questions are E1 to E6 below.
- **Split (Planning, `answer-01.yaml` q1-split)**: this proposal keeps the base advances (E1 to E6). Pull request
  cleanup (Q3) is `PROP-integration-pull-request-cleanup` and host confirmation (Q4) is
  `PROP-integration-host-confirmation`, both drafts; auto dispatch (Q2) stays as the open feedback it came from.
- **Related**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `ADR-integration-approval-asserted`.

## 1. Background & Hypothesis

### 1.1 Problem

`SPEC-hook-driven-integration-cleanup` shipped approval-bound local integration under `dev-integration = ask` and
deferred three extensions (its Non-Goal 3); daily use since then added a fourth problem. Each is recorded as feedback;
this proposal now addresses the first, and 3.1 says where the other three went:

- **Base advances** (`FB-integration-stale-on-base-advance`): an accepted `integration_integrate` confirmation was
  refused with `INTEGRATION_REQUEST_STALE` because another activity's commit landed on `main` during the confirmation.
  - *Raw receipt digest*: the request binds a digest of the base's `.devkit/config.toml` and
    `.devkit/installation.json` (`integration/service.py` `_validate`). The receipt lists bundle asset hashes, so any
    activity that edits a bundled skill invalidates every open confirmation, though no policy changed.
  - *Fast-forward only*: the request fixes `merge_method: ff-only` (`integration/models.py`), and
    `devkit worktree finish --merge` runs `git merge --ff-only` (`worktree/lifecycle.py`). Any base advance makes the
    merge impossible (`WORKTREE_MERGE_NOT_FF`) until the branch integrates the base again.
  - *Repeated confirmations*: with several activities landing on one base, each retry can be overtaken again; every
    retry is a new native confirmation for the same change. Fast-forward only was a default, not a requirement, and
    the policy check should compare the effective policy, not raw file bytes.
- **Auto dispatch** (`FB-auto-integration-dispatch`): no integration runs without an interactive confirmation under
  `dev-integration = auto`.
- **Remote and pull request** (`FB-pr-remote-and-squash-integration`): no remote push or pull request merge, and
  `WORKTREE_UNMERGED` after a squash or rebase merge, because the merge test is commit ancestry.
- **Host adapters** (`FB-multi-host-integration-ergonomics`): native confirmation only through Codex MCP elicitation;
  other hosts get `INTEGRATION_CONFIRMATION_UNAVAILABLE` and the CLI fallback.

The deferral of the last three waited for ask-mode integration to be used in real workflows. Several sessions have
since completed local integrations through `integration_integrate` with `authority="mcp-elicitation"`.

### 1.2 Hypothesis

The four extensions share the integration service, its confirmation binding and the scoped cleanup, so one Planning
could settle their common contract and decide whether they are delivered together or split. Planning split them
(3.1): base advances affect every integration today and auto dispatch would depend on them, so they are delivered
first, here. An approval can then bind the approved source, the confirmation target and its descendants within one
call, and land a clean merge with readiness checked again on the result, without a second confirmation.

## 2. Technical Spike Questions

- **Q1 (Split and order)**: One spec or several? Which extension comes first, and which depends on another?
  Decided in 3.1.

Base advances:

- **E1 (Merge method)**: fast-forward when possible, else a merge commit (`git merge --ff`), always a merge commit
  (`--no-ff`), or a policy key (`[worktree] merge = "ff" | "no-ff" | "ff-only"`) with a default.
  **Backlog leaning (user, 2026-10-19)**: consider an always-merge-commit default (`--no-ff`) first. Every stage
  boundary commits, so a unit lands about 10 to 13 commits, most of them records only; a merge commit gives one line
  per unit under `git log --first-parent` while keeping the stage commits that review, reconcile-check, final-report
  and worker envelopes cite by SHA, and keeps `git bisect` inside a unit.
- **E2 (Where the merge runs)**: in the base checkout (a conflict leaves the user's base checkout mid-merge and needs
  `git merge --abort`), or first merging the base into the source worktree and then fast-forwarding the base (the
  base checkout never sees a conflict; the source gains a merge commit).
- **E3 (Effective policy)**: the fields the digest covers: `[workflow.approvals]`, `[worktree]` (`pull_request`,
  `delete_branch`, merge policy), `[integration] provider`, and the identities of the readiness provider, finish
  guards and post-finish extensions; not asset hashes. Whether a base change to a managed asset the source also
  changed is a conflict to refuse.
- **E4 (Readiness after the base advanced)**: provider evidence binds exact source and target SHAs. Whether the
  executor re-runs `check` against the new target and proceeds when it passes, and what devkit-spec's provider must
  change so its evidence stays valid for a later target.
- **E5 (Confirmation text)**: how the form states that later base commits are merged in without another
  confirmation, and which target SHA it shows (the one at confirmation time).
- **E6 (Bounds)**: whether the executor retries when the base advances again during its own run (under the existing
  Git common-directory lock, other devkit executors are already serialized), and how many times.

The deferred extensions, kept here as asked at the start of Planning; 3.1 moved each out of this proposal:

- **Q2 (Auto dispatch)**: which readiness evidence must hold before an `authority="policy-auto"` integration runs
  without a prompt, and how is that authority recorded?
- **Q3 (Remote and pull request)**: how is remote push or pull request merge authority separated from local-only
  integration, and how is a no-ff PR merge verified against recorded PR state and source ancestry in the fetched
  target before the worktree and branch are removed? PR integration preserves the source SHAs, as local no-ff
  integration does; squash and rebase are excluded.
- **Q4 (Host adapters)**: which confirmation surfaces do Claude Code, Antigravity and other hosts offer that keep the
  binding to `request.id` and the approved scope and never let the agent approve itself?

## 3. Proposed Design & Impact

Spike evidence: `envelopes/scout-01.yaml`, the option comparison in
[materials/20261019-base-advance-options.md](materials/20261019-base-advance-options.md) and the PADRs under
`decisions/`. Challenger rounds are in `envelopes/challenger-NN.yaml`.

### 3.1 Split and order (Q1)

Decided (`answer-01.yaml` q1-split): this proposal keeps the base advances (E1 to E6), is retitled to that scope and
goes to `plan-accept`. The other extensions are handled as follows; their order is a preference, not a dependency,
except where named:

1. **Base advances** (this proposal): every integration is affected today; Q2 depends on it (an unattended run
   would otherwise be refused on the first base advance).
2. **Pull request no-ff merge and cleanup** (Q3): the draft `PROP-integration-pull-request-cleanup`. It uses merge
   commits to preserve source SHAs, verifies PR merge state and source ancestry in the fetched target before cleanup,
   needs remote authority in the form, and must weigh `ADR-branch-guards-and-close-discard` (which supersedes
   `ADR-worktree-and-pull-request-levels`). Squash and rebase are excluded.
3. **Auto dispatch** (Q2): an `authority="policy-auto"` integration contradicts accepted texts verbatim
   (`ADR-integration-approval-asserted`: "no policy value grants commit, merge, publication or deletion authority";
   also `CAP-DLV-project-policy`, `CAP-DLV-delivery-workflows`, `CAP-INT-mcp-services`). No draft is created: it
   stays as the open feedback it came from (`FB-auto-integration-dispatch`) until the user decides whether a policy
   may ever grant merge and deletion authority; a draft created then ends its Planning in a superseding ADR.
4. **Host confirmation** (Q4): the draft `PROP-integration-host-confirmation` (milestone
   `MS-multi-host-native-integration`), independent of 1 to 3. The Claude Code terminal CLI is already a
   verified native path (`SPEC-claude-terminal-mcp-approval`, docs only); the `Confirmation` callable in
   `devkit.host.mcp` is host-agnostic form elicitation. What is left is research-led: a
   `devkit host mcp setup --host claude` adapter and verification of Claude Desktop, the VS Code extension, the Agent
   SDK, Antigravity and OpenCode surfaces, in step with `MS-multi-host-native-integration`.

### 3.2 Base advances

Terms: the **confirmation target** is the target SHA shown in the form; a **build** is one attempt that reads the
current target (the **build target**), builds the **result commit** and fast-forwards the base onto it.

- **Merge method (E1)**, decided (`answer-01.yaml` e1-merge-method): a new `[worktree] merge = "no-ff" | "ff-only"` key, default `"no-ff"`, read by the
  integration service and `devkit worktree finish --merge`; `ff-only` in either the base's or the source's policy
  wins (like `delete_branch = false`). `no-ff` lands a merge commit whose first parent is the target and second the
  approved source tip: one `--first-parent` line per task, and every SHA the unit's records cite stays reachable and
  an ancestor of the base (`git branch -d`, `is_ancestor` and `WORKTREE_UNMERGED` keep working; ancestry checks in
  devkit never walk first parents). `ff-only` keeps today's behaviour and refuses an advanced target. `ff` (a merge
  commit only when needed) is not offered: the history shape would depend on timing. Squash and rebase are not local
  options (they rewrite the SHAs the records cite).
- **Already merged**: when the source is already an ancestor of the current target, nothing is built and the merge
  step is a no-op (a rerun of `finish --merge` after a completed merge only continues the cleanup), for the CLI and
  the service. A fresh `prepare` of such a branch (after a no-ff merge the target is the merge commit, which the
  source does not contain; after a server restart this is the only native route) prepares a cleanup-only request:
  the form says the branch is already merged and lists only the cleanup, the merge step is `skipped`, and `WORKTREE_MERGE_NOT_FF` stays for a target the source neither contains nor is
  contained in. The cleanup-only request runs guards and readiness with `merge-base(target, source)`, which is the
  source (an empty guard diff, so later envelopes in other units are not read as the branch's), its result commit is
  the source (so "contains the result" means "contains the source"), and its expected policy is the target's at
  prepare.
- **Where the merge runs (E2)**: never in a checkout. When the target is an ancestor of the source (no advance), the
  result is `git commit-tree <source>^{tree} -p <target> -p <source>`: its tree is exactly the gated source tree and
  no new Git version is needed. When the target advanced, the service builds the tree with
  `git merge-tree --write-tree <target> <source>` (Git 2.38 or later, probed only on this path,
  `WORKTREE_GIT_UNSUPPORTED` below it; exit 1 is `WORKTREE_MERGE_CONFLICT` with nothing changed, whose package-neutral `[ACTION]` is to merge the target
  into the branch in its worktree with a message the commit-msg gate accepts, re-verify and prepare again (the
  `spec-integrate` skill maps it to its Step 1); `WORKTREE_MERGE_NOT_FF`'s fix gets the same SHA-preserving text
  instead of "rebase or merge it in the worktree"; any other status is a failure) and commits it the same way. The message is devkit-composed from validated names only, in the form the repository's commit-msg gate
  already accepts for merges: `chore(merge): integrate <branch> into <target>` (no task ID or other caller text;
  tested against the configured gate). The base checkout only fast-forwards
  to the result (`git merge --ff-only <result>`), so it never stops mid-merge; the source branch and its worktree are
  untouched. The build lives in `devkit.worktree` (shared by the CLI and the service) and honours the Git identity
  and signing configuration: a missing committer identity is refused before the confirmation (service) or before
  any change (CLI); `commit-tree` runs with no terminal prompt (`GIT_TERMINAL_PROMPT=0`) and a 30-second bound, and a
  failed or timed-out signature is `WORKTREE_COMMIT_FAILED` with nothing changed on the target; the service passes these `WORKTREE_*` codes through as the cause of a
  refusal, never as `INTEGRATION_REQUEST_STALE` (the unreferenced object is left to `git gc`). Trailers that commit-msg hooks would add (DCO, Change-Id) are not added; this is
  documented. Under `ff-only` the result is the source tip.
- **CLI `devkit worktree finish --merge`**: runs no readiness provider, so under `no-ff` it builds a merge commit only
  when the target is an ancestor of the source (the landed tree is the gated source tree) and keeps
  `WORKTREE_MERGE_NOT_FF` for an advanced target, as today; the `spec-integrate` Steps 1 to 4 (merge the base into the
  branch, re-verify) stay the CLI's route. It takes the same Git common-directory lock as the service, in the `--merge` command entry
  (`worktree/cli.py`), not inside `finish()`, which the service calls while holding it. The
  `WORKTREE_PUSH_REJECTED` fix stops recommending `git pull --rebase` (it drops the merge commit and rewrites the
  unit's SHAs): Development verifies with a fixture that `git pull --rebase=merges` keeps the unit's commit SHAs and
  recreates only the merge commit on the fetched upstream, and uses it; if it does not, the fix is
  `git fetch <remote> <ref>` then
  `git merge --no-ff -m "chore(merge): integrate <remote>/<ref> into <target>" FETCH_HEAD` (`git pull` has no
  message option; this message passes the commit-msg gate), covered by the same fixture, and CAP-WT states its cost (the upstream's commits become a
  second parent) and that a conflict leaves the base checkout mid-merge (`git merge --abort`).
- **Target descent and compare-and-swap (E2, E6)**: every build target must descend from the confirmation target
  (a target that was reset or rewritten is stale, `INTEGRATION_REQUEST_STALE`); immediately before the fast-forward
  the base must still point at that build's target, else `INTEGRATION_TARGET_MOVED`.
- **Request and execution state**: `IntegrationRequest` stays immutable and digested, with the confirmation target.
  A separate execution context (the approved context plus the build target and the result SHA) is what the provider,
  the guards and the cleanup extensions receive at execution; the latest build target and result SHA are kept in the
  process-local result, outside the digest, and reported. Cleanup revisions bind to the source and to package-owned
  state, never to a target SHA.
- **Prepare scope**: apart from the cleanup-only request above, `prepare` keeps today's requirement that the source
  contains the target (an activity branch cut
  before later target commits integrates them first through `spec-integrate` Step 1 and re-verifies). Only advances
  after `prepare` are tolerated, so the gap the tests disclosure covers is limited to commits landed during the
  confirmation and execution.
- **Recovery after a failed or unknown merge step**: the base containing the latest result (the source under
  `ff-only`) means merged; the base equal to the last build target means not merged; anything else is stale or
  ambiguous (inspect Git). `INTEGRATION_TARGET_MOVED` leaves the merge step `not_run`. After the merge, every step checks that the base
  contains the result (later commits on the base are allowed), not that it equals it; `validate_finish(merged=True)`,
  the service's recovery and devkit-spec's cleanup `_is_post_git` change from "HEAD equals the source" to "HEAD
  contains the result (the source under `ff-only`) and the worktree is gone".
- **Guards**: unchanged at `prepare` (the source contains the target, so `plan.target_sha` is the merge base), except
  the cleanup-only request ("Already merged": `merge-base(target, source)`, the source, is the guard base); before
  each fast-forward of a build on an advanced target the guards run again with `merge-base(build target, source)`
  and the source tip.
- **Effective policy (E3)**: the request binds a digest of parsed values devkit owns: `[workflow.approvals]`
  `dev-integration`, `[worktree]` `pull_request`, `delete_branch` and `merge`, and `[integration] provider`, for the
  base at confirmation (must equal at each build, and at execution of a cleanup-only request) and for the result commit (must equal what the confirmation
  prospected; a cleanup-only request builds nothing, checks no result digest and expects the target's policy at
  `prepare`). Provider, guard and cleanup extension identities stay separate fields as today. Raw config and receipt
  bytes and asset hashes are no longer bound. Instead of refusing every managed path changed on both sides, each
  build checks the receipt records the merge itself makes inconsistent: a record whose path is tracked in the result
  and whose blob or recorded hash differs from both parents must match there, else `INTEGRATION_RECEIPT_CONFLICT`.
  Untracked projections (gitignored `.agents/`, `.claude/`, `.codex/`) and inconsistencies already on a parent are
  not this integration's and are skipped. It parses the receipt blobs of the result and both parents
  (`git cat-file blob <commit>:.devkit/installation.json`) with `devkit.core`'s `parse_receipt`, not
  `devkit.distribution`; a merged receipt that does not parse is `INTEGRATION_RECEIPT_CONFLICT` with nothing changed. A commit without a
  receipt has no records: the check is skipped when the result has none, and a parent without one contributes no
  records. In this repository 33 of the 366 commits on `main` since 2026-10-12 changed the receipt, so
  two concurrent bundle-editing units are common.
- **Readiness after the target advanced (E4)**: each build runs the provider with the execution context; `Readiness`
  binds source, build target and result. It must return no reasons, and its evidence must equal the approved evidence
  except the codes the provider declared target-bound at confirmation; that declared set is part of the request
  digest. devkit-spec declares `TARGET_SHA` and `RESULT_SHA` (absent at `prepare`, which builds nothing, and present at each
  build), evaluates the unit from the source tree (a target change
  inside the unit directory since the merge base is a reason), adds a `SPEC_POLICY` evidence item (a digest of the
  parsed `[tool.spec]` of the base and the result) that it does not declare target-bound, so evidence equality refuses
  a policy change, and runs its CI rules on the result tree with the diff from the build target.
- **Tests on the landed tree**, decided (`answer-01.yaml` t-tests-on-result): tests are not run on the result (the
  executor never runs commands); only the CI rules run on it, and the form and the integration report say that tests
  and review ran on the source only. The SDD-agnostic form (devkit-agt) does not say what a provider checks: the
  readiness provider declares a short result-check disclosure at confirmation, which the form shows and the request
  digest binds with the declared target-bound codes. The disclosure is required, one line of plain text of at most
  200 characters; a missing or malformed disclosure fails closed at `prepare` like a malformed `Readiness`.
  devkit-spec declares "CI rules only on the merged result; tests and review ran on the source only", and
  `spec-integrate`'s integration report states the same.
- **Confirmation text (E5)**: the form says "Approve local integration of <branch> into <target> with a merge
  commit?", shows the confirmation target SHA, and states that later commits on the target are merged in without
  another confirmation only if the merge is clean, the integration policy is unchanged and readiness provider
  <provider> passes again on the merged result (followed by the provider's disclosure), otherwise nothing changes on
  the target. The result reports the confirmation
  target, the build target and the result commit. `approval_scope()` and `to_dict()` carry the configured
  `merge_method`.
- **Bounds (E6) and approval lifetime**: one build per call. Advances during the confirmation are absorbed by that
  build; with the CLI taking the lock every devkit executor is serialized, so only a non-devkit ref write can move the
  target between the build and its fast-forward, which is `INTEGRATION_TARGET_MOVED` with nothing changed (no
  in-call retry). Decided (`answer-01.yaml` a-approval-lifetime): the approval tolerates target advances only within
  that call; `integration_resume` continues an approved request only onto the last build target (its CAP-INT section
  5 use, permission failures and cleanup after the merge), and a later target needs a new confirmation. A request
  whose approving call ran no build resumes only onto the confirmation target (the base must still equal it, else a
  new confirmation); a cleanup-only request, which never builds, resumes only its remaining cleanup steps. `LOCK_HELD`
  from the approving call carries an `[ACTION]` naming `integration_resume` while the target still equals the
  confirmation target, else a new `integration_integrate`. So that a
  concurrent devkit executor does not void an approval, the approving call waits for the Git common-directory
  integration lock up to a bound (a module constant, 30 seconds, which Development checks, together with the 30 s
  commit-tree bound and readiness on the result, against the hosts' MCP tool-call timeouts after the user's reply,
  such as Codex `tool_timeout_sec`, and lowers if a host would cut the call), instead of today's `timeout=0`; past the
  bound it is `LOCK_HELD` with nothing changed. `integration_resume` keeps `timeout=0`. Tests cover the lock freed
  within the bound (the build runs), the bound exceeded (`LOCK_HELD`, nothing changed) and `integration_resume`
  refusing a held lock at once.
- **Prepare builds nothing**: `integration_prepare` and `plan_finish` stay read-only; the prospective result tree is
  the source tree, and the prospective policy is read from the source commit as today, except the cleanup-only
  request, whose expected policy is the target's at `prepare` ("Already merged").
- **Skills**: `spec-integrate` Step 1 (merge the base into the activity branch before integration) stays required
  before `prepare` when the branch does not contain the target, and after a refusal on a later target (conflict,
  receipt conflict, readiness on the result); the worktree reference and `CAP-WT-task-worktrees` describe the merge
  key.

Every extension keeps the existing invariants: fail closed, exact scope binding (repository, task, source branch and
SHA, confirmation target and its descendants, worktree and branch cleanup, cleanup extensions and targets, effective
policy, target-bound evidence codes and the provider's result-check disclosure), no network operation without explicit authority, and no deletion of unmerged
work.

### 3.3 Impact and coordination

- **Impact**: `packages/devkit/src/devkit/integration/` (request and execution context, policy
  digest, builds, recovery, confirmation text, new codes `INTEGRATION_TARGET_MOVED`, `INTEGRATION_RECEIPT_CONFLICT`, the cleanup-only request), `packages/devkit/src/devkit/worktree/` (`config.py`
  merge key, `planning.py`, `lifecycle.py` `finish`, the merge-commit build, the `WORKTREE_MERGE_NOT_FF` fix text and `WORKTREE_MERGE_CONFLICT`, `WORKTREE_GIT_UNSUPPORTED` and `WORKTREE_COMMIT_FAILED`, lock, push fix, CLI help for `--merge`, module docstring),
  devkit-spec's readiness provider (`devkit_spec/integration.py`) and scoped cleanup (`devkit_spec/cleanup.py`), its
  `spec-integrate` skill, its integration report text and the confirmation binding sentence (`spec/references/completion.md`, which still
  says the native confirmation is bound to the exact `(source_sha, target_sha)` pair) and worktree reference,
  the confirmation lock wait, `CAP-INT-mcp-services` (sections 1, 2, 3 and 5), `CAP-WT-task-worktrees`
  (section 3 rerun and fix text), `CAP-DLV-delivery-workflows` 4.8 (readiness binding), `CAP-DLV-project-policy` (the
  new key), the project config template, `guides/` (Git 2.38 for advanced targets),
  `docs/development/reference/integration.md` and `worktree.md`, and the exit condition of
  `docs/roadmap/MS-multi-host-native-integration.md` (below). No change to `devkit.host` (packages/devkit-dist).
  Accepted ADRs are not changed; the handoff promotes this proposal's PADRs.
- **Milestone**: `MS-multi-host-native-integration`'s exit condition says the approval is "bound to the verified
  source and target commits"; with 3.2 it binds the confirmation target and its descendants within one call.
  Decided (`answer-01.yaml` m-milestone-wording): Development updates the exit condition during reconcile, in the
  same change, to "bound to the verified source commit and the confirmation target and its descendants"; Planning
  does not edit the milestone.
- **Coordination**: none. The devkit-dist package separation is complete (`SPEC-devkit-dist-package-separation`
  completed, its branch gone); `integration/` and `worktree/` are in `packages/devkit` (devkit-agt) and `host/` in
  `packages/devkit-dist`.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-follow-ups "<title>"`.
- Split done in Planning (3.1): the child drafts were created with `devkit spec proposal new` and name this proposal
  in their body; `--decomposed-from` refuses a source in Planning (`SPEC_PROPOSAL_IN_PLANNING`).
- Source feedback after the split (owner: the Host, outside this Planning's write scope, after the plan branch merges
  and before the handoff): `FB-auto-integration-dispatch` goes back to `status: open`, its disposition replaced by a
  note that the user keeps it open until deciding whether a policy may grant merge and deletion authority
  (`answer-01.yaml` q1-split); `FB-pr-remote-and-squash-integration`'s disposition becomes
  `PROP-integration-pull-request-cleanup`, and `FB-multi-host-integration-ergonomics`'s
  `PROP-integration-host-confirmation`. Left undone, the handoff rewrites all three to this proposal's spec and auto
  dispatch later reads as delivered.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-follow-ups`.
- On rejection: `status: rejected` with the user's reason in the commit message.
