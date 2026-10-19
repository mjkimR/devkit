---
id: PROP-integration-follow-ups
title: "Integration follow-ups: base advances, auto dispatch, pull request cleanup and host confirmation adapters"
summary: "Plans four integration extensions: tolerating base advances during approval, policy-driven dispatch under dev-integration auto, pull request and squash or rebase cleanup, and confirmation adapters for hosts beyond Codex."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: integration/
priority: high                        # critical | high | medium | low
size: XL                              # S | M | L | XL
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
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-integration-follow-ups] Integration follow-ups: base advances, auto dispatch, pull request cleanup and host confirmation adapters

- **Merged draft**: this draft also carries the former `integration-base-advance` draft (Backlog merge), whose
  questions are E1 to E6 below.
- **Related**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `ADR-integration-approval-asserted`.

## 1. Background & Hypothesis

### 1.1 Problem

`SPEC-hook-driven-integration-cleanup` shipped approval-bound local integration under `dev-integration = ask` and
deferred three extensions (its Non-Goal 3); daily use since then added a fourth problem. Each is recorded as feedback:

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
can settle their common contract (what an approval binds, how execution may adapt, which authority runs it) and
decide whether they are delivered together or split. Base advances affect every integration today, so they are the
first candidate.

## 2. Technical Spike Questions

- **Q1 (Split and order)**: One spec or several? Which extension comes first, and which depends on another?

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

The deferred extensions:

- **Q2 (Auto dispatch)**: which readiness evidence must hold before an `authority="policy-auto"` integration runs
  without a prompt, and how is that authority recorded?
- **Q3 (Remote and pull request)**: how is remote push or pull request merge authority separated from local-only
  integration, and how is a squash or rebase merge verified (recorded pull request state, tree or patch equivalence)
  before the worktree and branch are removed? A squash with branch deletion leaves the envelope SHAs unreachable
  (see the E1 leaning), so a squash path either keeps the source under another ref or is not offered for units.
- **Q4 (Host adapters)**: which confirmation surfaces do Claude Code, Antigravity and other hosts offer that keep the
  binding to `request.id` and the approved scope and never let the agent approve itself?

## 3. Proposed Design & Impact

Spike evidence: `envelopes/scout-01.yaml`, the option comparison in
[materials/20261019-base-advance-options.md](materials/20261019-base-advance-options.md) and the PADRs under
`decisions/`. Challenger rounds are in `envelopes/challenger-NN.yaml`.

### 3.1 Split and order (Q1)

Recommended (pending the user's answer): this proposal keeps the base advances (E1 to E6) and goes to `plan-accept`;
Q2, Q3 and Q4 become child drafts created with `--decomposed-from PROP-integration-follow-ups`, in this order:

1. **Base advances** (this proposal): every integration is affected today, and Q2 and Q3 build on its contract (the
   result commit, the effective-policy digest, readiness on the result).
2. **Pull request and squash or rebase cleanup** (Q3): needs the `[worktree] merge` key and the result-commit
   verification of 3.2; adds remote authority to the form and must weigh `ADR-worktree-and-pull-request-levels`.
3. **Auto dispatch** (Q2): an `authority="policy-auto"` integration contradicts accepted texts verbatim
   (`ADR-integration-approval-asserted`: "no policy value grants commit, merge, publication or deletion authority";
   also `ADR-approval-gates-intent-direction-integration`, `CAP-DLV-project-policy`, `CAP-DLV-delivery-workflows`,
   `CAP-INT-mcp-services`). Its Planning starts with the user's decision whether a policy may ever grant merge and
   deletion authority, and ends in a superseding ADR if so. Without 1, every unattended run would be refused on the
   first base advance.
4. **Host confirmation** (Q4): independent of 1 to 3. The Claude Code terminal CLI is already a verified native path
   (`SPEC-claude-terminal-mcp-approval`, docs only); the `Confirmation` callable in `devkit.host.mcp` is host-agnostic
   form elicitation. What is left is research-led: a `devkit host mcp setup --host claude` adapter and verification of
   Claude Desktop, the VS Code extension, the Agent SDK, Antigravity and OpenCode surfaces, in step with
   `MS-multi-host-native-integration`.

### 3.2 Base advances

- **Merge method (E1)**: a new `[worktree] merge = "no-ff" | "ff-only"` key, default `"no-ff"`, read by both the
  integration service and `devkit worktree finish --merge`. `no-ff` always lands a merge commit whose first parent is
  the target and second the approved source tip: one `--first-parent` line per task, every stage commit and every
  SHA cited by the unit's records stays reachable and an ancestor of the base (`git branch -d`, `is_ancestor` and the
  `WORKTREE_UNMERGED` test keep working; `main` already holds 18 merge commits). `ff-only` keeps today's behaviour
  for projects that require linear history and refuses an advanced base. `ff` (a merge commit only when needed) is not
  offered: the history shape would depend on timing. Squash and rebase are not local options (they rewrite the SHAs
  the records cite).
- **Where the merge runs (E2)**: never in a checkout. The executor builds the result in the object store:
  `git merge-tree --write-tree <target> <source>` (Git 2.38 or later; a conflict refuses with nothing changed), then
  `git commit-tree <tree> -p <target> -p <source>` with a devkit-composed message
  (`merge: integrate <branch> into <target>` and the task ID; no caller text). The base checkout then only
  fast-forwards to that commit (`git merge --ff-only <result>`), so it never stops mid-merge; the source branch and
  its worktree are untouched. Under `ff-only` the result commit is the source tip. `commit-tree` runs no commit hooks,
  so the commit gates do not see the result: readiness on the result (E4) is what checks the tree that lands. A
  missing committer identity in the base is refused before the confirmation.
- **Fast-forward assumptions replaced**: `plan_finish` (`WORKTREE_MERGE_NOT_FF` when the base is not an ancestor of
  the source) checks only under `ff-only`; `validate_finish(merged=True)` and the service's merge recovery test
  "base HEAD equals the recorded result commit and contains the source" instead of `HEAD == source_sha`; the
  post-merge policy is read from the result commit, not the source commit.
- **Effective policy (E3)**: the request binds a digest of parsed values devkit owns: `[workflow.approvals]`
  `dev-integration`, `[worktree]` `pull_request`, `delete_branch` and `merge`, and `[integration] provider`, for the
  base at confirmation (must equal at execution) and for the result commit (must equal what the confirmation
  prospected). Provider, guard and cleanup extension identities stay separate fields as today. Raw config and receipt
  bytes and asset hashes are no longer bound. A path the receipt records (or `.devkit/installation.json` itself)
  changed on both sides since the merge base is refused (`fail closed`), since the merged bytes would match neither
  side's receipt record.
- **Readiness after the base advanced (E4)**: at execution the provider runs again with the current target and the
  result commit (`IntegrationContext` gains `result_sha`; `Readiness` binds source, target and result). It must
  return no reasons, and its evidence must equal the approved evidence except the items the provider declares
  target-bound. devkit-spec declares `TARGET_SHA` and `RESULT_SHA` target-bound, evaluates the unit from the source
  tree as today (a base change inside the unit directory since the merge base is a reason) and runs its CI rules on
  the result tree with the diff from the current target, so a semantic conflict the rules catch refuses before
  anything lands. Tests are not run by the provider (unchanged).
- **Confirmation text (E5)**: the form says "Approve local integration of <branch> into <target> with a merge
  commit?", shows the target SHA at confirmation time, and states that later commits on the target are merged in
  without another confirmation only if the merge is clean, the integration policy is unchanged and readiness passes
  again; otherwise nothing changes on the target. The result reports the target at confirmation, the target merged
  and the result commit. `approval_scope()` and `to_dict()` carry the configured `merge_method`.
- **Bounds (E6)**: devkit executors are serialized by the Git common-directory lock, but other commits (a person, a
  session in the base checkout) are not. If the target moves between building the result and the fast-forward, the
  executor rebuilds and re-checks, at most three builds per call, then refuses with a new
  `INTEGRATION_TARGET_MOVED` code and nothing changed on the target; `integration_resume` may try again under the
  same approval, since the approval never bound the target SHA.
- **Skills**: `spec-integrate` Step 1 (merge the base into the activity branch before integration) is needed only for
  a conflict the executor refused; the worktree reference and `CAP-WT-task-worktrees` describe the merge key.

Every extension keeps the existing invariants: fail closed, exact scope binding (repository, task, source branch and
SHA, target branch, worktree and branch cleanup, cleanup extensions and targets, effective policy), no network
operation without explicit authority, and no deletion of unmerged work.

### 3.3 Impact and coordination

- **Impact (base advances)**: `packages/devkit/src/devkit/integration/` (request model, policy digest, executor,
  confirmation text, new code), `packages/devkit/src/devkit/worktree/` (`config.py` merge key, `planning.py`,
  `lifecycle.py` `finish`), devkit-spec's readiness provider (`devkit_spec/integration.py`) and its
  `spec-integrate` skill and worktree reference, `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`,
  `CAP-DLV-project-policy` (the new key), `docs/development/reference/integration.md` and `worktree.md`. No change to
  `devkit.host` (packages/devkit-dist) or to `docs/decisions/`.
- **Coordination**: none. The devkit-dist package separation is complete (`SPEC-devkit-dist-package-separation`
  completed, its branch gone); `integration/` and `worktree/` are in `packages/devkit` (devkit-agt) and `host/` in
  `packages/devkit-dist`.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-follow-ups "<title>"`.
- If Planning splits the work: decompose into child drafts with `--decomposed-from PROP-integration-follow-ups`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-follow-ups`.
- On rejection: `status: rejected` with the user's reason in the commit message.
