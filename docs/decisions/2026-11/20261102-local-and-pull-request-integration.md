---
id: ADR-local-and-pull-request-integration
title: Local and Pull Request Integration of Approved Sources
summary: "For integrating an approved source locally or by GitHub PR, we land a merge built outside the checkout, checked at prepare even onto a moved target, seeding generated-only conflicts, or a head-pinned PR merge, to land only checked trees, accepting disclosed unchecked or stale landings."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-merge-commit-outside-checkout
  - ADR-target-advance-readiness
  - ADR-effective-policy-digest
  - ADR-pull-request-merge-with-pinned-source-and-verified-landing
  - ADR-github-pull-request-adapter-in-devkit-worktree
  - ADR-github-pull-request-repository-binding
  - ADR-reject-persistent-pr-merge-journal
  - ADR-moved-target-merge
  - ADR-generated-conflicts-in-prepared-merge
  - ADR-retire-stale-integration-approval-clauses
supersedes:
  - ADR-configuration-language-and-rendering
---

# [ADR-local-and-pull-request-integration] Local and Pull Request Integration of Approved Sources

Superseded in part by `ADR-post-merge-verification`: the requirements for target-runtime readiness, content finish guards and receipt consistency before landing, readiness evidence equality and disclosure, and mandatory provider binding in the integration digest. Git identity, conflict, route, approval and unknown-outcome clauses remain.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: user, agent (user decisions are cited where the members record them)
- **Involved Components/Capabilities**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `CAP-DLV-delivery-workflows`,
  `CAP-GEN-tracked-artifacts`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-content-packages`, `devkit.worktree`,
  `devkit worktree finish`

---

## 1. Context & Problem Statement

Integration ran `git merge --ff-only` in the base checkout (`worktree/lifecycle.py` `finish`), and the request fixed
`merge_method: ff-only` (`integration/models.py`). Any commit landing on the target during a confirmation made the
approved integration impossible (`WORKTREE_MERGE_NOT_FF`, `INTEGRATION_REQUEST_STALE`). A unit lands 10 to 13
commits, most of them records, which its envelopes cite by SHA.

`_validate` required the provider's evidence to equal the approved evidence before the merge, and evidence bound the
exact source and target SHAs; `validate_finish` required the target to still point at the approved SHA. The
devkit-spec provider ran CI rules on the source tree, so when the target moved the tree that lands was never checked.
Repeated confirmations can be overtaken again on a busy base.

Local preparation (`devkit integration prepare --route local`, `devkit spec proposal accept --mode
accept_only|accept_and_handoff`) refused a source that does not contain the target's HEAD (`WORKTREE_MERGE_NOT_FF` in
`plan_finish`). The Host then merged the base into the task branch, reran checks (and `devkit rules fix` when the merge
brought reference drift) and retried, even when the merge was conflict-free and touched unrelated files; only target
commits landing after an integrate call's own preparation were absorbed. Any conflict of the in-memory merge refused
with `WORKTREE_MERGE_CONFLICT`, including a conflict only in `.devkit/installation.json`, the built-in generated
artifact `devkit-receipt`. The generated registry (`CAP-GEN-tracked-artifacts`) already states how such a file is
settled: keep the artifact's `seed` side, then regenerate it; regenerating needs a checkout and runs the artifact's
command, which an in-memory build has neither of.

The request bound a digest of the raw bytes of `.devkit/config.toml` and `.devkit/installation.json`
(`integration/providers.py` `policy`, `service.py` `_post_policy`). The receipt lists every managed asset hash, so any
activity that edits a bundled skill invalidated every open confirmation though no integration policy changed
(`FB-integration-stale-on-base-advance`: target `fa6aa90` changed the receipt and four bundle files).

A pull request merge is performed by the platform: the head can be pinned (`gh pr merge --match-head-commit`, REST
`sha`), but nothing pins the base, and the platform builds its own merge commit onto whatever the target is at that
moment. The integration service and `devkit worktree finish` performed no remote write; `gh` was used only read-only by
the stale-branch report (`worktree/stale.py`, an injectable `GhRunner` with a 60-second bound). The pull request route
needs remote identity, merge-method permissions, PR lookup, creation and state, a merge with the head pinned and a
conditional remote branch deletion. `integration` may import `worktree`, never the reverse, and `worktree` uses only
`core` and `advisory`. Installed gh 2.96.0 help and the official manuals show that `gh repo view` takes a repository
operand, `gh api` takes an endpoint and hostname, and `gh ruleset check` does not offer JSON output; `gh pr merge` can
enqueue implicitly when target queue policy is enabled, even without `--auto`.

`FB-integration-reissues-merge-after-unknown-outcome` records a fake provider receiving a second merge request. That
observation does not establish duplicate GitHub merge effects; a persistent attempt journal would add persistence,
crash windows and refusal of existing untracked OPEN PRs without demonstrating proportionate benefit.

Integration approval is the Host's conversation followed by a CLI call (`ADR-delivery-approval-and-lifecycle-authority`); the
MCP-native approval paths and the MCP confirmation channel are removed (commits `2a491881`, `8f570521`). Clauses only
that channel could carry out remained: a refusal before the confirmation of "any path that would need `--auto` or
`--admin`", which the PR route reaches only after approval (pending checks return `INTEGRATION_CHECKS_PENDING`, a merge
only an admin could make ends as `INTEGRATION_MERGE_REFUSED` at the merge call, unreadable classic protection is
disclosed, not refused), and the confirmation-form rules and "native approval routes" of
`ADR-configuration-language-and-rendering`.

---

## 2. Decision Drivers

- The base checkout, which the user works in, must never be left mid-merge.
- Every SHA the unit's records cite stays reachable and an ancestor of the base.
- What lands is checked; a failure changes nothing on the target; what could not be checked is reported as such,
  never as success.
- History shape does not depend on timing; a project can still require linear history.
- One confirmation per change; never a broader authority than the form showed.
- The approved source SHA is what lands; a changed source needs a new approval; no rebase, force operation or rewrite
  of the task's cited SHAs.
- Bounded work per call; the approving call never waits for CI or review.
- The approval binds what changes the integration's authority and effects, nothing else.
- Fail closed when the merged result could be inconsistent.
- Required CI, review and branch protection stay conditions of the merge (the PR is the gate, not bypassed).
- No destructive cleanup on an unknown outcome, and none that could lose source commits.
- One platform is in use (GitHub); no second one is requested.
- Tests run without network through an injectable runner, as the stale report does.
- What cannot be verified locally (or can be checked locally) is refused before the confirmation, never discovered
  after it.
- Lifecycle branch checks stay light; tests verify behavior (user direction).
- A real textual conflict or failing readiness still refuses with nothing changed on the target.
- A semantic conflict may surface later in CI, nightly CI or hygiene; a hidden one may not, so every integration result
  states what was checked on the merged result and which target it merged.
- One request digest per scope: two preparations of the same source and target yield the same digest.
- No manual base merge for a conflict the generated registry already settles.
- A stale generated file may land, but never unnoticed.
- The checks on the merged result (`receipts.check_merge`, the policy digest, the CI rules) stay as they are.
- Prepare and integrate of one source and target build one tree, so the checked result is the landed result.
- `devkit_agt.features.worktree` stays independent of the generated registry (`ARCH-05-2-components`).
- Keep recovery cost proportionate to observed failure effects.
- Preserve current identity, source, readiness, authority and error checks.
- Avoid introducing persistent state and new restrictions on existing PRs.
- Accepted ADRs agree with the shipped integration route.
- Unsafe merges stay impossible: devkit never enqueues, auto-merges or admin-merges.
- No new code is written to honor a clause whose channel is gone.

---

## 3. Considered Options

### Merge method and where the merge is built (ADR-merge-commit-outside-checkout)
- **Merge method**: `ff-only` (the former behaviour; kept as the alternative); `ff` (merge commit only when needed;
  rejected); `no-ff` always (selected as default); squash or rebase (rejected).
- **Where**: `git merge --no-ff` in the base checkout (rejected: a conflict leaves it mid-merge); merge the base into
  the source worktree, then fast-forward (rejected: the source gains a commit after approval and the base's first
  parent becomes the source side); build the merge in the object store with `git merge-tree --write-tree` and
  `git commit-tree`, check it, then fast-forward the base onto it (selected); a scratch detached worktree running
  `git merge --no-ff` (hooks run, older Git works, could host tests; rejected on checkout cost, a temporary worktree
  to clean up and the executor's no-commands rule).

### Target advances during approval (ADR-target-advance-readiness)
- Keep exact target binding, a new confirmation per advance (rejected).
- Bind the target at confirmation and accept any later target without re-checks (rejected).
- Show and record the target at confirmation, accept later targets only when the merge is clean, the effective policy
  is unchanged and readiness passes again on the result commit (selected).

### Policy binding (ADR-effective-policy-digest)
- Keep the raw-byte digest; every asset edit is stale (rejected).
- Tolerate only base commits outside `.devkit/`; still stale on every sync (rejected).
- Digest parsed devkit-owned policy values, and refuse a receipt-recorded path both sides changed (rejected: 33 of 366
  recent commits on `main` changed the receipt, so concurrent bundle-editing units are common).
- Digest parsed devkit-owned policy values, and refuse only a tracked receipt record the merge makes inconsistent
  (selected).

### Source that does not contain a moved target at prepare (ADR-moved-target-merge)
- **Keep containment** (rejected in ADR-moved-target-merge): every unrelated base commit costs a merge commit on the
  branch, a rerun of checks and a retry; observed twice in one local-orchestrated run.
- **A: drop the refusal and check only at integrate** (rejected in ADR-moved-target-merge): smallest change, but the
  prospective policy digest is read from the source, so a target that changed an effective integration policy key or
  `[tool.spec]` refuses after the user's OK on every retry until the base is merged; conflicts and CI-rule drift also
  surface only after the confirmation.
- **B: build the prospective merge at prepare** (selected): prepare builds the merge in the object store, runs the
  guards on the real merge base, the readiness provider on the result, the policy digest from the result and the
  receipt check before the scope is presented; integrate rebuilds on the current target. Costs a `merge-tree` and CI
  rules over the result at prepare. A deterministic prospective commit keeps the request digest contract unchanged;
  excluding result-bound readiness from the digest instead would change it for every route and provider.
- **B including the pull-request route** (rejected by the user in ADR-moved-target-merge): its prepare would build and
  check the prospective merge the same way, but the platform already builds the merge and runs required checks on its
  merge ref, and the change would widen the decision into a published remote-route behavior change.
- **C: merge the target into the task branch automatically** (rejected in ADR-moved-target-merge): rewrites the
  approved source, needs a checkout mid-merge and leaves conflicts in the worktree.

### Conflicts confined to generated files (ADR-generated-conflicts-in-prepared-merge)
- **Keep refusing** (rejected in ADR-generated-conflicts-in-prepared-merge): every concurrent receipt change costs a
  base merge, a rerun and a retry.
- **Regenerate during the build** (rejected in ADR-generated-conflicts-in-prepared-merge): needs a temporary checkout
  and runs project commands inside integration, before the user's confirmation, with the merged tree's commands.
- **Seed and disclose** (selected): keep each owned conflict at its artifact's seed side, refuse when any conflict is
  unowned or read by an artifact to regenerate, and disclose the seeded artifacts with the command that regenerates
  them on the target after landing.

### Pull request merge (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- **A** (selected): fetch the target, build the prospective merge locally, run the policy digest and readiness on it,
  recheck the remote target immediately before the call, merge with the head pinned, then verify the landed merge
  commit (second parent the source, first parent the checked target, tree equal to the checked tree).
- **B** (not required): require the platform's "branch must be up to date" rule, so any target advance refuses the
  merge; every advance then changes the source and needs a new approval.
- **C** (rejected for this route): push the locally built merge commit to the remote target with a lease; GitHub marks
  the PR merged. Exact compare-and-swap, but it bypasses the PR merge and its protections (or silently uses an admin
  bypass), removing the PR gate the route exists for.

### Recovery state for uncertain PR merge replies (ADR-reject-persistent-pr-merge-journal)
- Persist an issued marker before merge (rejected in ADR-reject-persistent-pr-merge-journal): preserves a never-resend
  condition but adds durable state and conservative refusals.
- Retain existing guarded invocations and error reporting (selected): adds no state or runtime change; no universal
  retry-idempotency guarantee is claimed.

### Platform adapter (ADR-github-pull-request-adapter-in-devkit-worktree, ADR-github-pull-request-repository-binding)
- A provider entry-point group (`devkit.pull_request_provider`) with a GitHub implementation (rejected).
- GitHub only, through `gh`, behind a narrow protocol in `devkit.worktree` beside `run_gh` (selected).
- Direct REST calls with a token devkit reads itself (rejected).
- Repository binding: `-R` on every gh invocation (superseded by `ADR-github-pull-request-repository-binding`); the
  syntax each gh command supports (selected).
- Merge call: `gh pr merge --merge --match-head-commit` (superseded: it can enqueue implicitly); the synchronous
  `gh api` merge endpoint (selected by `ADR-github-pull-request-repository-binding`); the asynchronous endpoint or
  queue/admin bypass (rejected).

### Approval clauses of the removed confirmation channel (ADR-retire-stale-integration-approval-clauses)
- **Retire the clauses** (selected): replace the stale clauses; the current behavior, already stated in
  `CAP-INT-mcp-services`, stands. No code change; ADRs match the route; an admin-only merge costs one approval before
  it is refused.
- **Move the `--auto`/`--admin` refusal into `prepare`** (rejected in ADR-retire-stale-integration-approval-clauses):
  detect admin-only and auto-merge paths before the approval. Matches the original wording, but classic branch
  protection is not always readable, so `prepare` cannot decide every case, and the approval it would save is cheap.

---

## 4. Decision Outcome

The local route builds the merge commit outside the checkout and checks the merged result at prepare and at
integrate, settling conflicts confined to generated files; the pull-request route merges with the head pinned and
verifies the landing. Together they remove the manual base merge while conflicts, CI-rule failures and policy changes
still refuse before the confirmation, and every landing that was not checked is disclosed.
(ADR-moved-target-merge; ADR-generated-conflicts-in-prepared-merge)

### Local merge commit

- `[worktree] merge = "no-ff" | "ff-only"`, default `"no-ff"` (user decision), applies to the integration service and
  `devkit worktree finish --merge`. `ff-only` in either policy wins. `ff`, squash and rebase are not offered locally.
  (ADR-merge-commit-outside-checkout)
- Under `no-ff` the result commit is built in the object store with the target as first parent and the approved source
  tip as second, under a devkit-composed message, and the base only fast-forwards to it. Without an advance the tree is
  the source tree (`commit-tree <source>^{tree}`); with one the service builds it with `git merge-tree --write-tree`
  (Git 2.38 or later, probed only then, `WORKTREE_GIT_UNSUPPORTED` below; a conflict is `WORKTREE_MERGE_CONFLICT` with
  nothing changed, except a conflict settled under Generated-file conflicts below). (ADR-merge-commit-outside-checkout)
- A source already contained in the target builds nothing: a rerun is a no-op, and a fresh prepare yields a
  cleanup-only request (guards and readiness on `merge-base(target, source)`, the source as its result, the target's
  policy as expected). (ADR-merge-commit-outside-checkout)
- The message uses validated branch names only (`chore(merge): integrate <branch> into <target>`); the build lives in
  `devkit.worktree`, honours identity and signing configuration, runs with a 30-second bound and no terminal prompt
  and refuses with `WORKTREE_COMMIT_FAILED` and nothing changed on failure. (ADR-merge-commit-outside-checkout)
- Conflict fixes are package-neutral and SHA-preserving: merge the target into the branch, re-verify, prepare again.
  (ADR-merge-commit-outside-checkout)
- Under `ff-only` the result commit is the source tip and an advanced target is refused.
  (ADR-merge-commit-outside-checkout)
- The CLI `finish --merge`, which runs no readiness provider, builds a merge commit only when the target did not
  advance and keeps `WORKTREE_MERGE_NOT_FF` otherwise; it takes the integration lock in its command entry.
  (ADR-merge-commit-outside-checkout)

### Moved target at prepare

- Under `[worktree] merge = "no-ff"`, local preparation accepts a source that neither contains nor is contained by the
  target, through an opt-in `plan_finish` keyword (`advance`, default off) that only the local integration service
  sets; other callers keep today's refusal and error precedence. It builds a prospective merge commit with
  `build_result(advance=True)`: unsigned, referenced by no ref, UTF-8, with author and committer lines (name, email,
  raw date and offset) copied from the committer of whichever parent has the later committer date. The commit thus
  does not depend on Git identity, `TZ` or commit encoding, and the request digest stays as defined; the merged tree
  follows the repository's Git merge configuration, as the integrate build does. (ADR-moved-target-merge)
- Preparation passes a prospective context (the approved context plus that commit as `result_sha`) to the finish
  guards (with `merge-base(target, source)`), the readiness provider, `receipts.check_merge` and the prospective policy
  digest. A provider can thus receive at prepare a result that never lands; the `IntegrationContext` and the
  devkit-spec provider docstrings and `CAP-DLV-delivery-workflows` state it. Cleanup scopes are planned from the
  approved context (`result_sha` `None`); the prospective commit never enters `IntegrationResult.build_target` or
  `result_sha`, which keep naming only real builds for recovery. (ADR-moved-target-merge)
- Composed acceptance passes the same prospective context to its preview, which runs the delivery provider's
  result-dependent checks (the CI rules on the prospective result and the unit-advance check: the target changed the
  proposal directory since the merge base) before the acceptance commit and refuses with
  `SPEC_PROPOSAL_APPROVAL_NOT_READY` and their reasons. Reference drift from main (a cited proposal handed off
  meanwhile) and a target edit to the proposal directory, the only way the acceptance delta can conflict, refuse
  before anything is committed. (ADR-moved-target-merge)
- A conflict refuses at prepare with `WORKTREE_MERGE_CONFLICT` and nothing changed, except a conflict settled under
  Generated-file conflicts. (ADR-moved-target-merge)
- Failing readiness refuses with `INTEGRATION_NOT_READY` and the provider's reasons; core keeps that code's fix. The
  devkit-spec provider (and the acceptance preview's refusal) words each CI-rule reason found on a prospective or
  built result (`result_sha` set) with the conditional base merge: merge the target into the task branch, fix what the
  rules report (`devkit rules fix`), re-verify what the merge changed, prepare again. Other readiness reasons keep
  their wording. `INTEGRATION_RECEIPT_CONFLICT` names the same conditional base merge for its own cause. After
  `INTEGRATION_TARGET_MOVED`, or any target change between prepare and integrate, a fresh preparation rebuilds on the
  current target; no base merge is required. (ADR-moved-target-merge)
- Integrate keeps its build: it rebuilds on the current target (which must descend from the confirmation target),
  signs as configured, reruns the guards, readiness, policy digest and receipt check, and fast-forwards the base onto
  the result. Under `ask`, a target that moved after the presented prepare still changes the digest
  (`INTEGRATION_REQUEST_STALE`): the Host presents a fresh prepare for a new decision, with no base merge.
  (ADR-moved-target-merge)
- Every prepare, integrate and composed acceptance result that carries a request shows the readiness disclosure and
  the merged target SHA: prepare the confirmation target, integrate the build target and the landed result, composed
  acceptance the delivery provider's disclosure and its landed result. A cleanup-only or `ff-only` result shows the
  target it was prepared against. A refusal before a request exists shows neither. (ADR-moved-target-merge)
- `merge = "ff-only"` keeps refusing a moved target with `WORKTREE_MERGE_NOT_FF`, because a fast-forward cannot absorb
  it; its fix names merging the target into the branch or the `no-ff` policy. (ADR-moved-target-merge)
- `devkit worktree finish --merge` keeps refusing a moved target: it runs no readiness provider, so a merge it built
  would land an unchecked tree. (ADR-moved-target-merge)
- The pull-request route keeps its containment refusal (`WORKTREE_MERGE_NOT_FF`, unchanged precedence; it does not
  set `advance`): the platform builds its own merge, and its required checks run on the platform's merge ref.
  (ADR-moved-target-merge)

### Generated-file conflicts

- When every conflict of a local prepare or integrate build is owned by an enabled artifact of the registry committed
  at the build target, the build keeps each owned path from the artifact's `seed` side (`ours` = the target,
  `theirs` = the source) and removes it where that side deleted it. Nothing is regenerated during the build.
  (ADR-generated-conflicts-in-prepared-merge)
- A conflict no artifact owns refuses with `WORKTREE_MERGE_CONFLICT`, nothing changed, one detail per such path; the
  detail names the artifacts to regenerate that read or update it (`inputs`, `updates`, or any path when an artifact
  declares no `inputs`), the `GENERATED_INPUTS_CONFLICTED` condition of `resolve`.
  (ADR-generated-conflicts-in-prepared-merge)
- The worktree feature takes the settler as an injected callable (`ConflictSettler`); the integration feature
  composes it from the generated registry. Without a settler, a build refuses every conflict as before: the
  pull-request route, `finish --merge` and composed proposal acceptance pass none.
  (ADR-generated-conflicts-in-prepared-merge)
- The prepare and integrate results disclose the seeded artifacts in `generated` (ids, paths, seed, side kept and the
  `devkit generated regen <ids>` command) and with an `INTEGRATION_GENERATED_SEEDED` warning, beside the readiness
  disclosure. (ADR-generated-conflicts-in-prepared-merge)
- A local-orchestrated run regenerates stale artifacts on the base branch and commits them before its batch test run
  (`ADR-test-selection-and-ci`); a direct-mode integration does so after landing.
  (ADR-generated-conflicts-in-prepared-merge)

### Target advances and readiness on the result

- The approval shows and records the confirmation target; the request stays immutable with it. An execution context
  (approved context plus build target and result SHA) goes to the provider, guards and cleanup, and the latest build is
  kept outside the digest. (ADR-target-advance-readiness)
- Every build target must descend from the confirmation target, and the base must still point at the build target
  immediately before the fast-forward (else `INTEGRATION_TARGET_MOVED`). (ADR-target-advance-readiness)
- The provider must return no reasons and evidence equal to the approved evidence except the codes it declared
  target-bound at confirmation (the declared set is digested). The provider also declares a required result-check
  disclosure (one line, at most 200 characters; missing or malformed fails closed at `prepare`), shown in the form and
  digested. (ADR-target-advance-readiness)
- devkit-spec declares `TARGET_SHA` and `RESULT_SHA`, evaluates the unit from the source tree, binds its `[tool.spec]`
  policy through a source-bound `SPEC_POLICY` item and runs its CI rules on the result tree. Tests are not re-run on
  the result: only the CI rules run on it, and the form and the integration report say that tests and review ran on
  the source only (user decision). (ADR-target-advance-readiness)
- One build per call (no in-call retry). (ADR-target-advance-readiness)
- The integrating call waits for the integration lock up to a bound (30 seconds, checked together with the commit-tree
  bound and readiness on the result) instead of failing at once, then `LOCK_HELD` with nothing changed.
  (ADR-target-advance-readiness)
- Recovery: the base containing the latest result means merged, equal to the last build target means not merged,
  anything else is stale or ambiguous. `validate_finish(merged=True)` and the service's merge recovery check that HEAD
  contains the latest result commit. (ADR-target-advance-readiness, ADR-merge-commit-outside-checkout)

### Effective policy digest

- The digest covers `[workflow.approvals]` `dev-integration`, `[worktree]` `pull_request`, `delete_branch` and
  `merge`, and `[integration] provider`, normalized after parsing. Provider, guard and cleanup extension identities
  stay separate request fields. (ADR-effective-policy-digest)
- The base's digest must be equal at confirmation and execution; the result commit's digest must equal the one
  prospected at confirmation; a cleanup-only request (a source the target already contains) builds nothing, checks no
  result digest and expects the target's policy at `prepare`. (ADR-effective-policy-digest)
- Each build checks the receipt records the merge makes inconsistent: a record whose path is tracked in the result and
  whose blob or recorded hash differs from both parents must match there, else `INTEGRATION_RECEIPT_CONFLICT` before
  anything lands. Untracked projections and inconsistencies already on a parent are skipped; the receipt is read
  through `devkit.core`. (ADR-effective-policy-digest)

### Pull request route

- `prepare` fetches the target's remote ref; the fetched remote SHA is the confirmation target, the source must contain
  it and the target policy is read from it. The approval binds the source SHA (enforced server-side by the head pin)
  and that confirmation target. (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- Before the merge call the fetched target must descend from the confirmation target, the prospective merge must be
  clean, the effective policy unchanged and readiness must pass on it.
  (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- After the call, devkit fetches and reads the PR's merge commit `M`: `M^2` equals the source and `M` is contained in
  the fetched target. When `M^1` is the checked target and `M`'s tree equals the checked tree, the landing is checked;
  any other landing is never reported as checked. (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- Checks and review (user decision, q-checks-wait a): the merge call is made only when the PR is mergeable with required
  checks and reviews satisfied, which happens in the approving call when the agent already pushed a ready PR whose
  checks passed. Otherwise the approving call publishes and returns `INTEGRATION_CHECKS_PENDING`.
  (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
  → `CAP-INT-mcp-services` §Authority and route limits (MUST)
- Unchecked landing (user decision, q-unchecked-landing): once the merge is confirmed (PR `MERGED`, `M^2` the source)
  and the source is an ancestor of the fetched target, cleanup runs whether or not the landing was checked. Every
  landing other than the checked one (an advance in the window, a tree mismatch, a first parent outside the
  confirmation target's history, `M` not in the fetched target) is reported as the notice
  `INTEGRATION_LANDED_UNCHECKED` with its reason and a directive naming the landed-target check the readiness provider
  declares, runnable after cleanup. devkit does not re-run guards, readiness or the policy digest on `M`; cleanup uses
  the scope bound in the approved request. Cleanup stops only when the fetched target does not contain the source
  (`INTEGRATION_SOURCE_NOT_CONTAINED`). (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- A merge call whose outcome is unknown is resolved only from the PR state; while it stays unknown no cleanup runs.
  (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- The persistent PR merge journal (~~`PROP-pr-merge-recovery`~~, rejected at Git
  `2092282ab6a30059243e26ee4cc148e865e91107`) is not adopted: "Repeated merge requests alone do not establish duplicate
  merge effects. The journal and refusal of untracked existing PRs add unjustified complexity; preserve existing
  validation, retry and error reporting without new persistent recovery state." (ADR-reject-persistent-pr-merge-journal)
- That rejection changes no production code or integration lifecycle contract. It does not authorize unchecked
  replays, automatic retry loops, replacement PR creation or cleanup after an unconfirmed merge.
  (ADR-reject-persistent-pr-merge-journal)

### GitHub adapter

- GitHub only, through `gh`, behind an injectable pull request port in `devkit.worktree`: remote and repository
  identity, merge-method permissions and applicable rules, PR find/create/update by head and base, PR state with
  `headRefOid`, `baseRefOid`, `mergeCommit`, `state`, `isDraft` and the check, review and mergeability state that tells
  pending from failed and from mergeable, the pinned-source merge, and remote branch deletion leased on the expected
  SHA. Calls run with no terminal prompt and a bound per call, returning exit status, stdout and stderr.
  Authentication is `gh`'s; devkit stores no token. No token reader, direct HTTP client, additional hosting
  platform or protection bypass is introduced. (ADR-github-pull-request-repository-binding)
  → `CAP-INT-mcp-services` §Authority and route limits (MUST NOT)
- Every repository operation binds the resolved host and owner/repository using the syntax its gh command supports:
  `-R` where supported, a repository operand for `repo view`, and an explicit hostname and repository endpoint or
  GraphQL variables for `gh api`. Applicable rules are read from structured API responses through gh, not by parsing
  ruleset display text. Repository discovery binds the selected Git remote, including SSH aliases gh resolves; it never
  silently chooses an unrelated default remote or omits the Enterprise hostname.
  (ADR-github-pull-request-repository-binding)
- The merge is the synchronous `gh api --method PUT repos/<owner>/<repo>/pulls/<number>/merge`, with the explicit
  hostname, the approved `sha`, `merge_method=merge` and a composed commit title and body; the asynchronous endpoint and
  queue or admin bypass are not used. HTTP refusal statuses are reported separately from unknown transport outcomes,
  which remain observational recovery. (ADR-github-pull-request-repository-binding)
  → `CAP-INT-mcp-services` §Authority and route limits (MUST)
- Remote branch deletion is `git push --force-with-lease=refs/heads/<branch>:<sha> <remote> --delete <branch>`, the only
  leased form. `gh pr merge --delete-branch` is not used (it deletes the local branch outside devkit's guards).
  (ADR-github-pull-request-adapter-in-devkit-worktree, preserved by ADR-github-pull-request-repository-binding)
  → `CAP-INT-mcp-services` §Authority and route limits (MUST NOT)
- Refused before the confirmation with stable codes: a remote `gh` cannot resolve, `gh` missing or not authenticated, a
  cross-repository (fork) PR and a merge queue on the target. A nonzero exit that is not a recognised refusal is an
  unknown outcome, resolved from the remote. (ADR-github-pull-request-adapter-in-devkit-worktree, preserved by
  ADR-github-pull-request-repository-binding, kept by ADR-retire-stale-integration-approval-clauses)
  → `CAP-INT-mcp-services` §Authority and route limits (MUST)
- The PR route does not enqueue, auto-merge or admin-merge. A merge that needs admin rights ends as
  `INTEGRATION_MERGE_REFUSED`. (ADR-retire-stale-integration-approval-clauses)
  → `CAP-INT-mcp-services` §Authority and route limits (MUST NOT)

### Retired confirmation-form clauses of a kept ADR

- From `ADR-configuration-language-and-rendering`, the confirmation-form rules are retired: messages explain every
  choice when a host omits schema metadata, source and provider prose is displayed verbatim, and language is sampled
  once per form. "Native approval routes" is also retired from its local-text clause; local text keeps MCP-first
  discovery and connection. Every other clause of that ADR stays in force, and it stays `accepted`.
  (ADR-retire-stale-integration-approval-clauses)
- Domain-owned static English and Korean copy and the preserved canonical keys, action values, identifiers and
  evidence stay in force. `CAP-DIST-sync-and-transactions` and `CAP-DLV-proposal-planning` state them.
  (ADR-retire-stale-integration-approval-clauses)

---

- Supersedes in part `ADR-configuration-language-and-rendering`: the confirmation-form rules requiring explanations when schema metadata is omitted, verbatim source and provider prose, and language sampled once per form; and native approval routes in the local-text clause. Its other clauses remain in force.

## 5. Consequences

- **Positive**:
  - One `--first-parent` line per task; stage commits stay bisectable; ancestry checks keep working.
    (ADR-merge-commit-outside-checkout)
  - Bundle syncs and asset edits on the target no longer invalidate confirmations. (ADR-effective-policy-digest)
  - Provider-owned policy (such as `[tool.spec]`) is bound through source-bound provider evidence: devkit-spec adds a
    `SPEC_POLICY` digest that evidence equality enforces. (ADR-effective-policy-digest)
  - Unrelated base commits no longer require a branch merge, rerun and retry before integration or acceptance.
    (ADR-moved-target-merge)
  - Policy changes, `[tool.spec]` changes, reference drift and receipt inconsistencies on the merged result refuse
    before the confirmation instead of after it, and before the acceptance commit in composed acceptance.
    (ADR-moved-target-merge)
  - A receipt-only conflict no longer requires a base merge into the task branch; the disclosure and the batch
    completion step make the stale artifact visible and fixed on the base branch.
    (ADR-generated-conflicts-in-prepared-merge)
  - A second platform later becomes an entry-point group over the same port; no consumer exists yet.
    (ADR-github-pull-request-adapter-in-devkit-worktree)
  - No accepted ADR describes a refusal point or form that the code does not have.
    (ADR-retire-stale-integration-approval-clauses)
- **Negative / Risks**:
  - `commit-tree` runs no commit hooks: the result's tree is checked by the readiness provider, not by the commit
    gates. Commit-msg hook trailers (DCO, Change-Id) are not added to the merge commit. One extra commit per
    integration even when the target did not move. (ADR-merge-commit-outside-checkout)
  - Readiness runs twice per integration (prepare and the build); CI rules cost is bounded by the diff. A semantic
    break that no CI rule catches can land after a clean merge of a later target; main's own CI finds it.
    (ADR-target-advance-readiness)
  - A semantic conflict no CI rule catches can land after a conflict-free merge; tests and review ran on the source
    only, as the disclosure states. `ADR-test-selection-and-ci` adds the batch run that surfaces it.
    (ADR-moved-target-merge)
  - Preparation of a moved target needs Git 2.38 or later (`WORKTREE_GIT_UNSUPPORTED` otherwise) and costs a
    `merge-tree` and CI rules over the result. (ADR-moved-target-merge)
  - A provider outside devkit-spec that assumed `result_sha` is `None` at prepare now sees a prospective commit; the
    changed docstrings state it. (ADR-moved-target-merge)
  - The landed generated artifact is the seed side's file until regenerated; a consumer reading it in between sees the
    seed side's content. `receipts.check_merge` still refuses a merged receipt record that matches neither parent.
    (ADR-generated-conflicts-in-prepared-merge)
  - The integration feature depends on the generated feature, a new edge in the declared feature graph.
    (ADR-generated-conflicts-in-prepared-merge)
  - A source and a target whose re-syncs leave an inconsistent merged receipt must integrate the target into the
    source and re-sync first. (ADR-effective-policy-digest)
  - A residual race remains on the pull request route and is disclosed in the form and the result; a commit landing in
    the window is merged without devkit's checks and only reported, since cleanup does not wait for it.
    (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
  - On a repository with required checks or reviews the usual flow is two integration calls
    unless the agent opened the PR and let its checks pass before `prepare`. A target commit landing while checks run
    costs a target merge into the source, re-verification, a new confirmation and a new check run; on a target that
    moves faster than its checks the route may never merge, which is disclosed.
    (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
  - The PR merge commit is GitHub's: its committer, signature and message handling are the platform's; no local commit
    hooks or trailers apply. GitHub-specific behaviour (merge commit identity and signature, rules readable only by
    admins) is disclosed, not hidden. (ADR-pull-request-merge-with-pinned-source-and-verified-landing,
    ADR-github-pull-request-adapter-in-devkit-worktree)
  - The merge API does not support stacked PRs or merging with a merge queue; a platform refusal leaves the PR
    unmerged. (ADR-github-pull-request-repository-binding)
  - The proposed PR merge journal and its capacity, corruption and adoption rules are not implemented; existing
    guarded retries and error reporting are accepted, with no universal retry-idempotency guarantee.
    (ADR-reject-persistent-pr-merge-journal)
  - A user can approve an integration that then ends as `INTEGRATION_MERGE_REFUSED`.
    (ADR-retire-stale-integration-approval-clauses)
- **Follow-ups / scope**:
  - The `WORKTREE_PUSH_REJECTED` fix stops recommending `git pull --rebase`: `git pull --rebase=merges` if a fixture
    shows it keeps the unit's SHAs, else `git fetch <remote> <ref>` then `git merge --no-ff -m "chore(merge): integrate
    <remote>/<ref> into <target>" FETCH_HEAD` (`git pull` has no message option), with its first-parent cost
    documented. (ADR-merge-commit-outside-checkout)
  - The provider contract changes (released before devkit-spec updates). The approval's meaning changes from "this
    target" to "this source onto the target as it will be, under these conditions, within one call";
    `CAP-INT-mcp-services` section 2 is rewritten accordingly, and Development updates the exit condition of the
    then-existing multi-host native integration milestone to "bound to the verified source commit and the
    confirmation target and its descendants" (user decision). (ADR-target-advance-readiness)
  - Cleanup verifies PR state `MERGED`, `M^2` the source and the source contained in the fetched target; later target
    commits and an unchecked landing do not block cleanup.
    (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
  - `devkit worktree finish` itself stays local-merge only; the port is used by the integration service's pull request
    route and by its cleanup. (ADR-github-pull-request-adapter-in-devkit-worktree)
  - Development adds a "Superseded in part by" line to `ADR-local-and-pull-request-integration` naming
    `ADR-moved-target-merge`, without changing its status or `superseded_by`. (ADR-moved-target-merge)
  - `ADR-moved-target-merge` gets a "Superseded in part by" line naming `ADR-generated-conflicts-in-prepared-merge`,
    without a status change. (ADR-generated-conflicts-in-prepared-merge)
  - The source feedback of the rejected PR merge journal retains its promoted history with the rejection as its final
    destination. Reconsider recovery changes only when a concrete harmful failure is reproduced against the actual API
    semantics. (ADR-reject-persistent-pr-merge-journal)

---

## 6. Confirmation

- Tests verify each gh command's repository binding (ADR-github-pull-request-repository-binding).
- Tests: a conflict-free moved target integrates and accepts without a base merge; a conflict refuses at prepare with
  nothing changed; a moved target that changed `dev-integration`, `delete_branch` or `[tool.spec]` integrates;
  CI-rule drift on the result refuses at prepare and, in composed acceptance, before the acceptance commit, as does
  a target change to the proposal directory; two preparations in environments with different Git identity and `TZ`
  yield one digest; `ff-only`, `finish --merge` and the pull-request route still refuse
  (`packages/devkit/tests/e2e/features/integration/test_base_advance.py`,
  `packages/devkit/tests/integration/features/worktree/test_merging.py`,
  `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`, the plan-accept CLI tests).
  (ADR-moved-target-merge)
- Tests: `packages/devkit/tests/e2e/features/integration/test_base_advance.py` (a receipt-only conflict prepares,
  discloses and lands the prepared tree; mixed and input conflicts refuse with nothing changed; the receipt check
  still refuses) and `packages/devkit/tests/integration/features/worktree/test_merging.py` (seeding sides, removal,
  no settler). (ADR-generated-conflicts-in-prepared-merge)
- `RULE-architecture` checks the declared `integration -> generated` feature dependency.
  (ADR-generated-conflicts-in-prepared-merge)
- `CAP-INT-mcp-services` §Authority and route limits; `rg "ctx.elicit|elicit\(" packages/` finds no confirmation form.
  (ADR-retire-stale-integration-approval-clauses)
- Review: `CAP-WT-task-worktrees`, `CAP-INT-mcp-services` and `CAP-DLV-delivery-workflows` state the moved-target
  contract (ADR-moved-target-merge); the PR merge journal rejection introduces no integration runtime change, preserves
  the Planning history in Git and leaves no live dependency on the removed proposal
  (ADR-reject-persistent-pr-merge-journal). The other clauses are review only.
