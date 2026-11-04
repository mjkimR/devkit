# Planning options for PROP-maintenance-history

Scope: the option sets Planning compared on 2026-11-04 at `plan-maintenance-history`, with the evidence files
`github-publication-api.md` (official GitHub and `gh` documentation) and `internal-constraints.md` (repository
contracts). Each table names the option, its evidence, its cost, its risk and what stays open. The recommendation
closes each set; the proposal's Planning decisions record what the user settled.

## Set 1: publication mechanism (Spike Q1)

| Option | Evidence | Cost | Risk | Open |
| --- | --- | --- | --- | --- |
| 1a. Git Database API: `POST git/blobs`, `POST git/trees` (`base_tree`), `POST git/commits`, `PATCH git/refs/heads/<branch>` with `force` omitted | `github-publication-api.md` §1-2: the only documented route to several files in one commit; a non-fast-forward update is refused | N blobs + 3 mutating requests per run, one head read | Exact error texts undocumented; retry logic must re-read the head and compare content | API-level idempotency of repeated POSTs; same-sha PATCH |
| 1b. Contents API: `PUT repos/{o}/{r}/contents/{path}` per file | §1: one commit per file, `sha` required for updates | N PUTs and up to N GETs | Not atomic: a failure after k files leaves a partial record; N branch moves race with other writers | 409 meaning |
| 1c. GraphQL `createCommitOnBranch` with `expectedHeadOid` | §1: one mutation per run; atomicity, stale-head error, branch creation and orphan commits undocumented in the pages read | 1 mutation + 1 read | Cannot create the branch or a root commit; undocumented failure contract | All of the above until a live reference confirms them |

Recommendation: 1a. Condition that changes it: an official reference documents 1c as atomic with a stable
stale-head error and branch creation; then 1c becomes the publish step and 1a stays for initialization.

## Set 2: where the procedure and code live

| Option | Evidence | Cost | Risk | Open |
| --- | --- | --- | --- | --- |
| 2a. A `devkit maintenance history` command family in `devkit-agt` beside `run_gh`; the playbooks call it | `internal-constraints.md` §3.1-3.2: the catalog is content-only; `run_gh` and the injectable `GitHub` runner exist; `ARCH-08-1-agent-output` binds command output | A new feature with CLI, use cases, services, repositories and tests; `boundaries.owns` and size grow (M to L) | A second GitHub operation family in `devkit-agt`; a feature edge to `worktree` for `run_gh` | Package name and feature edge |
| 2b. A content-only `gh api` procedure in a playbook reference file; the agent runs the calls | §3.4: precedent `review-refactor/references/applying.md`; lowest cost | Reference text only; size stays M | Retry, digest and concurrency rules are prose for an agent to follow; verification is manual scenario evidence only; token-heavy base64 handling in conversation | Whether a references directory is accepted under single-file playbooks |
| 2c. A `SharedArtifactAdapter` backend | §1.2, §6: the store forbids overwrite and deletion and expires in seven days; a production remote adapter is deferred (`ADR-mcp-runtime-and-shared-artifacts`) | Reuses the adapter protocol | Contradicts the store's contract; durable history is not a shared artifact | None; rejected |

Recommendation: 2a, because the proposal's verification list (duplicate retries, concurrent writers, lost
responses, unchanged local Git state) is mechanically testable only through an injected runner, and the command's
sentinels give the playbooks stable codes. 2b remains the fallback when the user prefers no new feature.

## Set 3: publication authority

| Option | Evidence | Cost | Risk | Open |
| --- | --- | --- | --- | --- |
| 3a. Per-run explicit authority: every publication names its destination and the authority the user gave in that run; the default outcome is `pending` | `CAP-DLV-weekly-report` §4 (invocation grants no external mutation), `ADR-mcp-runtime-and-shared-artifacts` (no standing publication permission), `ADR-delivery-approval-and-lifecycle-authority` | One confirmation per run | Unattended runs never publish | None |
| 3b. Standing opt-in in `.devkit/config.toml` (`[maintenance.history] publish = "auto"`) that authorizes every run's publication | None in the repository; contradicts the three documents above | A superseding ADR and a policy change | Policy would grant publication authority, which `CAP-DLV-project-policy` excludes | User decision |

Recommendation: 3a. The configured repository and branch are default inputs, never authority.

## Set 4: inspected-state identity (Spike Q2)

| Option | Evidence | Cost | Risk | Open |
| --- | --- | --- | --- | --- |
| 4a. Source SHA plus the dirty path list | `internal-constraints.md` §4.1: what every playbook records today | None | Two different dirty contents give the same record; a rerun cannot prove the same state | None |
| 4b. 4a plus a tree hash from a temporary index (`read-tree HEAD`, `add -A`, `write-tree`) | §4.3: `spec-delegate` step 2 and `run_git(index=...)` | One temporary index per run | Ignored files are not covered; a remote reader cannot rebuild the tree | Ignore handling |
| 4c. 4b plus a SHA-256 digest of the local diff (`git diff --binary HEAD` and untracked file bytes) with the diff retained locally | `CAP-DLV-weekly-report` §2 requires a preserved diff or artifact reference for selected uncommitted content | One diff file per dirty run | The diff may hold secrets; it stays local unless the run selects it | None |
| 4d. `git stash create` as a commit-shaped identity | Not in repository evidence | A dangling commit per run | Needs retention; tracked changes only; must not be used as `source_sha` | Unverified |

Recommendation: 4c, recorded as `ADR-inspected-state-identity`. `source_sha` stays a commit.

## Set 5: record layout and retrieval

| Option | Evidence | Cost | Risk | Open |
| --- | --- | --- | --- | --- |
| 5a. `runs/<playbook>/<run-id>/` holding `record.json`, `report.md` and `updates/`, plus `index/<playbook>/<YYYY>.jsonl` sharded by the run ID's year with one line per published run or amendment | `github-publication-api.md` §4: the contents GET reads one file up to 1 MB; no server-side filter by revision exists | One index line per run in the same commit | Concurrent writers both append to the index; the retry re-reads the shard from the new head before appending, so no line is lost (challenger-01 finding 3) | None |
| 5b. `runs/<playbook>/<source-sha>/<run-id>/` and a recursive tree walk | §4: recursive tree capped at 100,000 entries or 7 MB | No index | Listing by playbook walks every run; slow after thousands of runs | None |
| 5c. One record per run and a GitHub search | No endpoint searches file contents on a branch | None | Not available | Rejected |

Recommendation: 5a. Size-based rollover was dropped after challenger-01 finding 4: the year shard is fixed by the run ID, so concurrent writers never disagree on the file.
