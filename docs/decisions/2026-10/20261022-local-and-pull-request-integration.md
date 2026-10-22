---
id: ADR-local-and-pull-request-integration
title: Local and Pull Request Integration of Approved Sources
summary: "For integrating an approved source locally or through a GitHub pull request, we land a merge commit built outside the checkout or a head-pinned PR merge with readiness on the result and a policy digest, to land only checked trees, accepting disclosed unchecked landings."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-merge-commit-outside-checkout
  - ADR-target-advance-readiness
  - ADR-effective-policy-digest
  - ADR-pull-request-merge-with-pinned-source-and-verified-landing
  - ADR-github-pull-request-adapter-in-devkit-worktree
  - ADR-github-pull-request-repository-binding
---

# [ADR-local-and-pull-request-integration] Local and Pull Request Integration of Approved Sources

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: not recorded in the members (user decisions and Host approval are cited where the members record them)
- **Involved Components/Capabilities**: `CAP-INT-mcp-services`, `devkit.worktree`, `devkit worktree finish`

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

---

## 2. Decision Drivers

- The base checkout, which the user works in, must never be left mid-merge.
- Every SHA the unit's records cite stays reachable and an ancestor of the base.
- What lands is checked; a failure changes nothing on the target; what could not be checked is reported as such,
  never as success.
- History shape does not depend on timing; a project can still require linear history.
- One confirmation per change; never a broader authority than the form showed.
- The approved source SHA is what lands; a changed source needs a new approval.
- Bounded work per call; the approving call never waits for CI or review.
- The approval binds what changes the integration's authority and effects, nothing else.
- Fail closed when the merged result could be inconsistent.
- Required CI, review and branch protection stay conditions of the merge (the PR is the gate, not bypassed).
- No destructive cleanup on an unknown outcome, and none that could lose source commits.
- One platform is in use (GitHub); no second one is requested.
- Tests run without network through an injectable runner, as the stale report does.
- What cannot be verified locally is refused before the confirmation, never discovered after it.

---

## 3. Considered Options

### Merge method and where the merge is built (`ADR-merge-commit-outside-checkout`)
- **Merge method**: `ff-only` (the former behaviour; kept as the alternative); `ff` (merge commit only when needed;
  rejected); `no-ff` always (selected as default); squash or rebase (rejected).
- **Where**: `git merge --no-ff` in the base checkout (rejected: a conflict leaves it mid-merge); merge the base into
  the source worktree, then fast-forward (rejected: the source gains a commit after approval and the base's first
  parent becomes the source side); build the merge in the object store with `git merge-tree --write-tree` and
  `git commit-tree`, check it, then fast-forward the base onto it (selected); a scratch detached worktree running
  `git merge --no-ff` (hooks run, older Git works, could host tests; rejected on checkout cost, a temporary worktree
  to clean up and the executor's no-commands rule).

### Target advances during approval (`ADR-target-advance-readiness`)
- Keep exact target binding, a new confirmation per advance (rejected).
- Bind the target at confirmation and accept any later target without re-checks (rejected).
- Show and record the target at confirmation, accept later targets only when the merge is clean, the effective policy
  is unchanged and readiness passes again on the result commit (selected).

### Policy binding (`ADR-effective-policy-digest`)
- Keep the raw-byte digest; every asset edit is stale (rejected).
- Tolerate only base commits outside `.devkit/`; still stale on every sync (rejected).
- Digest parsed devkit-owned policy values, and refuse a receipt-recorded path both sides changed (rejected: 33 of 366
  recent commits on `main` changed the receipt, so concurrent bundle-editing units are common).
- Digest parsed devkit-owned policy values, and refuse only a tracked receipt record the merge makes inconsistent
  (selected).

### Pull request merge (`ADR-pull-request-merge-with-pinned-source-and-verified-landing`)
- **A** (selected): fetch the target, build the prospective merge locally, run the policy digest and readiness on it,
  recheck the remote target immediately before the call, merge with the head pinned, then verify the landed merge
  commit (second parent the source, first parent the checked target, tree equal to the checked tree).
- **B** (not required): require the platform's "branch must be up to date" rule, so any target advance refuses the
  merge; every advance then changes the source and needs a new approval.
- **C** (rejected for this route): push the locally built merge commit to the remote target with a lease; GitHub marks
  the PR merged. Exact compare-and-swap, but it bypasses the PR merge and its protections (or silently uses an admin
  bypass), removing the PR gate the route exists for.

### Platform adapter (`ADR-github-pull-request-adapter-in-devkit-worktree`, `ADR-github-pull-request-repository-binding`)
- A provider entry-point group (`devkit.pull_request_provider`) with a GitHub implementation (rejected).
- GitHub only, through `gh`, behind a narrow protocol in `devkit.worktree` beside `run_gh` (selected).
- Direct REST calls with a token devkit reads itself (rejected).
- Repository binding: `-R` on every gh invocation (superseded by `ADR-github-pull-request-repository-binding`); the
  syntax each gh command supports (selected).
- Merge call: `gh pr merge --merge --match-head-commit` (superseded: it can enqueue implicitly); the synchronous
  `gh api` merge endpoint (selected by `ADR-github-pull-request-repository-binding`); the asynchronous endpoint or
  queue/admin bypass (rejected).

---

## 4. Decision Outcome

### Local merge commit

- `[worktree] merge = "no-ff" | "ff-only"`, default `"no-ff"` (user decision), applies to the integration service and
  `devkit worktree finish --merge`. `ff-only` in either policy wins. `ff`, squash and rebase are not offered locally.
  (ADR-merge-commit-outside-checkout)
- Under `no-ff` the result commit is built in the object store with the target as first parent and the approved source
  tip as second, under a devkit-composed message, and the base only fast-forwards to it. Without an advance the tree is
  the source tree (`commit-tree <source>^{tree}`); with one the service builds it with `git merge-tree --write-tree`
  (Git 2.38 or later, probed only then, `WORKTREE_GIT_UNSUPPORTED` below; a conflict is `WORKTREE_MERGE_CONFLICT` with
  nothing changed). (ADR-merge-commit-outside-checkout)
- A source already contained in the target builds nothing: a rerun is a no-op, and a fresh prepare yields a
  cleanup-only request. (ADR-merge-commit-outside-checkout)
- The message uses validated branch names only (`chore(merge): integrate <branch> into <target>`); the build lives in
  `devkit.worktree`, honours identity and signing configuration, runs with a 30-second bound and no terminal prompt
  and refuses with `WORKTREE_COMMIT_FAILED` and nothing changed on failure. (ADR-merge-commit-outside-checkout)
- `prepare` still requires the source to contain the target, except for a source the target already contains, which
  yields a cleanup-only request (guards and readiness on `merge-base(target, source)`, the source as its result, the
  target's policy as expected); only later advances are merged in. (ADR-merge-commit-outside-checkout)
- Conflict and not-fast-forward fixes are package-neutral and SHA-preserving: merge the target into the branch,
  re-verify, prepare again. (ADR-merge-commit-outside-checkout)
- Under `ff-only` the result commit is the source tip and an advanced target is refused. (ADR-merge-commit-outside-checkout)
- The CLI `finish --merge`, which runs no readiness provider, builds a merge commit only when the target did not
  advance and keeps `WORKTREE_MERGE_NOT_FF` otherwise; it takes the integration lock in its command entry.
  (ADR-merge-commit-outside-checkout)

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
- One build per call (no in-call retry); the approval tolerates target advances only within the integrate call that
  asked for it (user decision): `integration_resume` continues only onto the last build target, and a later target
  needs a new confirmation. A request whose approving call ran no build resumes only onto the confirmation target (the
  base must still equal it, else a new confirmation); a cleanup-only request resumes only its remaining cleanup steps.
  (ADR-target-advance-readiness)
- `LOCK_HELD` from the approving call names `integration_resume` while the target still equals the confirmation
  target, else a new `integration_integrate`. The approving call waits for the integration lock up to a bound (30
  seconds, checked together with the commit-tree bound and readiness on the result against host MCP tool-call timeouts
  after the user's reply) instead of failing at once, then `LOCK_HELD` with nothing changed.
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
  clean, the effective policy unchanged and readiness must pass on it. (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- After the call, devkit fetches and reads the PR's merge commit `M`: `M^2` equals the source and `M` is contained in
  the fetched target. When `M^1` is the checked target and `M`'s tree equals the checked tree, the landing is checked;
  any other landing is never reported as checked. (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
- Checks and review (user decision, q-checks-wait a): the merge call is made only when the PR is mergeable with
  required checks and reviews satisfied, which happens in the approving call when the agent already pushed a ready PR
  whose checks passed. Otherwise the approving call publishes and returns `INTEGRATION_CHECKS_PENDING`, and
  `integration_resume` merges later only while the remote target still equals the last build target (else a new
  confirmation). (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
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

### GitHub adapter

- GitHub only, through `gh`, behind an injectable pull request port in `devkit.worktree`: remote and repository
  identity, merge-method permissions and applicable rules, PR find/create/update by head and base, PR state with
  `headRefOid`, `baseRefOid`, `mergeCommit`, `state`, `isDraft` and the check, review and mergeability state that tells
  pending from failed and from mergeable, the pinned-source merge, and remote branch deletion leased on the expected
  SHA. Calls run with no terminal prompt and a bound per call, returning exit status, stdout and stderr.
  Authentication is `gh`'s; devkit stores no token. No token reader, direct HTTP client, additional hosting platform or
  protection bypass is introduced. (ADR-github-pull-request-repository-binding)
- Every repository operation binds the resolved host and owner/repository using the syntax its gh command supports:
  `-R` where supported, a repository operand for `repo view`, and an explicit hostname and repository endpoint or
  GraphQL variables for `gh api`. Applicable rules are read from structured API responses through gh, not by parsing
  ruleset display text. Repository discovery binds the selected Git remote, including SSH aliases gh resolves; it never
  silently chooses an unrelated default remote or omits the Enterprise hostname. (ADR-github-pull-request-repository-binding)
- The merge is the synchronous `gh api --method PUT repos/<owner>/<repo>/pulls/<number>/merge`, with the explicit
  hostname, the approved `sha`, `merge_method=merge` and a composed commit title and body; the asynchronous endpoint
  and queue or admin bypass are not used. HTTP refusal statuses are reported separately from unknown transport
  outcomes, which remain observational recovery. (ADR-github-pull-request-repository-binding)
- Remote branch deletion is `git push --force-with-lease=refs/heads/<branch>:<sha> <remote> --delete <branch>`, the
  only leased form. `gh pr merge --delete-branch` is not used (it deletes the local branch outside devkit's guards).
  (ADR-github-pull-request-adapter-in-devkit-worktree, preserved by ADR-github-pull-request-repository-binding)
- Refused before the confirmation with stable codes: a remote `gh` cannot resolve, `gh` missing or not authenticated, a
  cross-repository (fork) PR, a merge queue on the target, and any path that would need `--auto` or `--admin`. A
  nonzero exit that is not a recognised refusal is an unknown outcome, resolved from the remote.
  (ADR-github-pull-request-adapter-in-devkit-worktree, preserved by ADR-github-pull-request-repository-binding)

---

## 5. Consequences

- **Positive**:
  - One `--first-parent` line per task; stage commits stay bisectable; ancestry checks keep working.
    (ADR-merge-commit-outside-checkout)
  - Bundle syncs and asset edits on the target no longer invalidate confirmations. (ADR-effective-policy-digest)
  - Provider-owned policy (such as `[tool.spec]`) is bound through source-bound provider evidence: devkit-spec adds a
    `SPEC_POLICY` digest that evidence equality enforces. (ADR-effective-policy-digest)
  - A second platform later becomes an entry-point group over the same port; no consumer exists yet.
    (ADR-github-pull-request-adapter-in-devkit-worktree)
- **Negative / Risks**:
  - `commit-tree` runs no commit hooks: the result's tree is checked by the readiness provider, not by the commit
    gates. Commit-msg hook trailers (DCO, Change-Id) are not added to the merge commit. One extra commit per
    integration even when the target did not move. (ADR-merge-commit-outside-checkout)
  - Readiness runs twice per integration (prepare and the build); CI rules cost is bounded by the diff. A semantic
    break that no CI rule catches can land after a clean merge of a later target; main's own CI finds it.
    (ADR-target-advance-readiness)
  - A source and a target whose re-syncs leave an inconsistent merged receipt must integrate the target into the
    source and re-sync first. (ADR-effective-policy-digest)
  - A residual race remains on the pull request route and is disclosed in the form and the result; a commit landing in
    the window is merged without devkit's checks and only reported, since cleanup does not wait for it.
    (ADR-pull-request-merge-with-pinned-source-and-verified-landing)
  - On a repository with required checks or reviews the usual flow is two calls (approve, then `integration_resume`)
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

---

## 6. Confirmation

Tests verify each gh command's repository binding (ADR-github-pull-request-repository-binding). Otherwise review only;
the members name no rule ID or test path.
