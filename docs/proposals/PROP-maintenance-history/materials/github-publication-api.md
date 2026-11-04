# GitHub publication API evidence for PROP-maintenance-history

- Read date: 2026-11-04 (all URLs below were read on this date; REST API version header shown in the docs: `2026-03-10`)
- Scope: answers Spike Question Q1 of `PROP-maintenance-history` (atomic multi-file publication and non-forced, retry-safe ref updates under concurrent writers) using official GitHub docs (docs.github.com REST/GraphQL reference, cli.github.com manual) and the Git book only. Nothing in this file touches the local checkout.

Citation convention: `[doc-short-name, section]` refers to the URL listed in the Sources block at the end. Quotes marked "(summary)" were extracted from a fetched page by a summarizing reader and must be re-checked against the live page before they become normative text.

## Short answer

- Atomic multi-file publication: only the Git Database path (blobs, then a tree with `base_tree`, then a commit, then one ref update) makes several files visible in one commit. The single `PATCH git/refs/heads/<name>` is the only publication point; earlier objects are unreferenced until then.
- Contents API `PUT` creates one commit per file, so it is not atomic across files.
- GraphQL `createCommitOnBranch` is the only API that carries an `expectedHeadOid`, but the official reference we could read documents neither its atomicity, its error for a stale head, nor branch/orphan creation. It stays unverified and is not recommended for the first implementation.
- Recommended: option (a), with `force` omitted or `false`, a re-read and rebuild loop on non-fast-forward rejection, and a verify-by-content step after a lost response. Details in the recommendation section.

## 1. Options for publishing one run's several files as one commit

| Option | Evidence | Cost (requests per run) | Risk | Open questions |
| --- | --- | --- | --- | --- |
| (a) Git Database: `POST git/blobs` per file, `POST git/trees` with `base_tree`, `POST git/commits` with `parents: [head]`, `PATCH git/refs/heads/<name>` with `force: false` | Blobs: `POST /repos/{o}/{r}/git/blobs`, `content` required, `encoding` `utf-8` or `base64`, 201 on create [rest-git-blobs, Create a blob]. Trees: `base_tree` is "The SHA1 of an existing Git tree object which will be used as the base for the new tree"; entries may use `content` or `sha`, not both: "Using both tree.sha and content will return an error"; deletion via `sha: null` [rest-git-trees, Create a tree]. Commits: `parents` "If omitted or empty, the commit will be written as a root commit" [rest-git-commits, Body parameters]. Ref update: `force` "Leaving this out or setting it to false will make sure you're not overwriting work" [rest-git-refs, Update a reference]. Docs also say "you will need to commit the tree and then update a branch to point to the commit" [rest-git-trees, Behavior notes]. | 1 request per file (blob) + 1 tree + 1 commit + 1 PATCH = N+3 per run (plus 1 GET ref to read the head, plus optional reads). Secondary limit: POST/PATCH counts 5 points each (see rate section). | Partial failure leaves unreferenced blob/tree/commit objects (harmless garbage, no visible change). Concurrent writer: a stale parent yields a non-fast-forward PATCH that must be rebuilt (see section 2). Tree/commit build cost grows if the history branch's tree grows. | Exact status/message for a rejected non-fast-forward PATCH is not in the docs (422 is listed generically). Whether a PAT/app needs extra permission on protected names is open (section 7). |
| (b) Contents API: `PUT repos/{o}/{r}/contents/{path}` per file with `branch` | `message`, base64 `content`, `sha` "Required if you are updating a file", `branch` "Default: the repository's default branch", 200/201/404/409/422 response codes [rest-repos-contents, Create or update file contents]. | 1 request per file; N requests produce N commits. Each PUT also needs the existing blob `sha` for updates (one GET per existing file, or a cached value). | Not atomic: the docs describe one file per call and no multi-file form. A failure after k of N files leaves a partial record on the branch. Each PUT moves the branch, so concurrent writers interleave commits; the `sha` check guards only the file itself, not the run. | Whether a 409 on PUT means "stale branch" or "stale file sha" is not distinguished in the docs (409 is listed as "Conflict" only). |
| (c) GraphQL `createCommitOnBranch` (`CreateCommitOnBranchInput`: `branch`, `expectedHeadOid`, `fileChanges`, `message`) | Description: "Appends a commit to the given branch as the authenticated user," it "creates a commit whose parent is the HEAD of the provided branch" and "updates that branch to point to the new commit" [graphql-commits, createCommitOnBranch] (summary). `expectedHeadOid`: "The git commit oid expected at the head of the branch prior to the commit" (summary). `branch`: "Must be a branch." (summary). | 1 GraphQL request per run (plus 1 read of the head). Mutation point cost 5 (vs 1 for a query) [rate-limits-graphql, Secondary rate limits]. | Atomicity: not stated in the page read. Stale-head behavior: not documented on the page read; no documented error list. Branch creation and orphan commit: not stated ("This must refer to a git branch"). Base64 contents and size limits for `FileAddition`/`FileChanges` were not in the page read. | Needs the GraphQL reference sections for `FileChanges`/`FileAddition`, the mutation error list, and whether an absent branch can be created. Until read, this option is unverified. It is also a GraphQL-only dependency for `gh api graphql`. |

### Option (a) details that matter for the design

- Blob content: `encoding` accepts `utf-8` or `base64` [rest-git-blobs, Create a blob]. Blob size limit for create is not stated; GET blob "supports blobs up to 100 megabytes in size" [rest-git-blobs, Get a blob].
- Blob SHA is deterministic: "Git concatenates the header and the original content and then calculates the SHA-1 checksum of that new content," with header `blob <size>\0` [git-book, Git Objects]. The REST blob page says "The file's SHA-1 hash is computed and stored in the blob object." [rest-git-blobs, Create a blob] (summary).
- Tree recursion: `GET git/trees/{sha}?recursive=1` is limited to "100,000 entries with a maximum size of 7 MB" [rest-git-trees, Note]. Building a tree from `base_tree` avoids re-sending unchanged entries.
- Token: classic `repo` scope is needed for the Contents PUT ("OAuth app tokens and personal access tokens (classic) need the repo scope") [rest-repos-contents, Permissions]. The fine-grained permissions table lists `POST git/blobs`, `POST git/trees`, `POST git/commits`, `POST git/refs`, `PATCH git/refs/{ref}` and `PUT contents` under Contents `write` [rest-fine-grained-permissions, Contents rows] (summary; the "Additional Permissions" column is marked for git/refs and PUT contents, its meaning was not explicit in the read).

## 2. Ref update and concurrency semantics

| Operation | Concurrency semantics (documented) | Non-forced behavior | Retry safety | Evidence |
| --- | --- | --- | --- | --- |
| `PATCH git/refs/heads/<name>` with `sha`, `force` omitted or `false` | "Indicates whether to force the update or to make sure the update is a fast-forward update. Default: false" [rest-git-refs, Update a reference]. | Non-fast-forward is refused. Only generic 422 "Validation failed, or the endpoint has been spammed" is documented; the message text is not documented. | Same target sha twice: not documented (see section 5). Retrying after a non-fast-forward requires re-reading the head and rebuilding. | rest-git-refs, Update a reference |
| `POST git/refs` (create `refs/heads/<name>`) | `ref` must be fully qualified (e.g. `refs/heads/master`), `sha` required [rest-git-refs, Create a reference]. | 422 for failure, generic text only. "You are unable to create new references for empty repositories, even if the commit SHA-1 hash used exists." [rest-git-refs, Create a reference] (summary). | Creating an already existing ref: the docs read did not mention "Reference already exists" (see section 3). | rest-git-refs |
| `GET git/ref/heads/<name>` | "If the :ref doesn't match an existing ref, a 404 is returned." [rest-git-refs, Get a reference] | Used to read the head before building. | Read-only, safe. | rest-git-refs |
| GraphQL `createCommitOnBranch` | `expectedHeadOid` is the head the commit is expected to be built on [graphql-commits] (summary). No documented stale-head error. | Not documented. | Not documented. | graphql-commits |
| Contents `PUT` | `sha` is the blob sha of the file being replaced; 409 "Conflict" [rest-repos-contents]. | Protects one file, not the branch as a whole. | Not documented for branch-level retries. | rest-repos-contents |

Design consequence: because the docs describe `force` only as "make sure the update is a fast-forward" and do not give the stale-head error text, the implementation must branch on the HTTP status class (422 or 409) and then re-read the ref (`GET git/ref/heads/<name>`) to decide, instead of parsing the message. Message text is not a stable code.

Concurrent writers, worked case (derived from the documented semantics, not from a GitHub statement about this exact race): writers A and B both read head H, both build commits with parent H. A's PATCH moves the ref to A'. B's PATCH with `force: false` is not a fast-forward from A' (its commit's parent is H, not A'), so it is refused. B re-reads A', rebuilds its tree with `base_tree` from A' and a commit with parent A', then PATCHes again. Every successful record survives because no writer uses `force: true`.

## 3. Orphan branch initialization

- Root commit: `parents` omitted or empty "will be written as a root commit" [rest-git-commits, Body parameters]. The tree object must exist first (`POST git/trees` without `base_tree` to build a tree from inline `content`), then `POST git/commits` with `tree` and empty `parents`, then `POST git/refs` with `ref: refs/heads/maintenance-history` and `sha` set to the root commit.
- Branch already exists: `POST git/refs` for an existing ref. The official page read lists 422 only as "Validation failed, or the endpoint has been spammed." and does not give the "Reference already exists" text or its behavior. The status and message in the proposal are **Unverified** against the live docs; treat them as expected behavior to be confirmed by a live test.
- Empty repository: "You are unable to create new references for empty repositories, even if the commit SHA-1 hash used exists" [rest-git-refs, Create a reference] (summary). The page read did not show a "Git Repository is empty" message. The 409 code is listed in several pages only as "Conflict". Treat the exact 409 text as **Unverified**. Practical consequence: an empty repository needs an initial commit made another way (e.g. the web UI, or `repos` creation with `auto_init`) before this path works. This is an inference from the documented statement, not a documented procedure.
- Existing branch with unrelated history: the docs do not describe a validation endpoint for ancestry. The implementation must detect it with reads: `GET git/ref/heads/<name>` for the head, then `GET repos/{o}/{r}/commits?sha=<name>&per_page=1` or `GET repos/{o}/{r}/compare/{base}...{head}` to check that the expected root is an ancestor. The compare endpoint is `GET /repos/{owner}/{repo}/compare/{basehead}` with `status` values `diverged`, `ahead`, `behind`, `identical` [rest-commits, Compare two commits] (the values are listed but not defined on the page read). The compare response caps changed files at "up to 300 changed files for the entire comparison" [rest-commits, Compare two commits]. The compare call should be used only as a root-ancestry test, not for diffs.
- Creating orphan history must not reuse code history: the root commit has an empty `parents` list by construction, so it cannot be merged into a code branch by a fast-forward. The protection against merging the branch is a repository/process decision, not an API property (see section 7).

## 4. Retrieval without fetching

| Need | Endpoint and documented limit | Evidence |
| --- | --- | --- |
| Read a file | `GET repos/{o}/{r}/contents/{path}?ref=<branch>`. "1 MB or smaller: All features of this endpoint are supported." "Between 1-100 MB: Only the raw or object custom media types are supported." "Greater than 100 MB: This endpoint is not supported." Raw body: `Accept: application/vnd.github.raw+json`. | rest-repos-contents, Get repository content |
| List a directory | Upper limit: "This API has an upper limit of 1,000 files for a directory." | rest-repos-contents, Get repository content |
| Whole tree | `GET git/trees/{sha}?recursive=1`: "truncated is true ... the number of items in the tree array exceeded our maximum limit"; limit "100,000 entries with a maximum size of 7 MB when using the recursive parameter." Non-recursive fetch one subtree at a time when truncated. | rest-git-trees, Get a tree |
| History per path | `GET repos/{o}/{r}/commits?sha=<branch>&path=<path>`: `path` "Only commits containing this file path will be returned"; `per_page` default 30, max 100; `page` default 1. | rest-commits, List commits |
| Ref head | `GET git/ref/heads/<name>`: 404 when absent. | rest-git-refs, Get a reference |
| Blob by sha | `GET git/blobs/{sha}`: up to 100 MB; content always base64. | rest-git-blobs, Get a blob |
| `gh api` flags | `--paginate` (fetch all pages), `--slurp` (array of pages with `--paginate`), `-q/--jq`, `-F/--field` (typed; `@<path>` or `@-` reads from file or stdin), `-f/--raw-field`, `-H/--header`, `-X/--method` (default GET), `--input <file>` (`-` for stdin), `-i/--include`, `--cache` [cli-gh-api, Flags]. | cli-gh-api |

Notes:
- The contents GET is the cheapest way to read one file at the history branch's head, and it avoids the 1,000-entry directory limit when the path is a file. The raw media type avoids base64 decoding for files up to 100 MB.
- For "latest completed run for revision X", list commits filtered by `path` (or read a per-run index file), then read the record. The docs do not show a combined search; the proposal's filter by revision must live in the stored record path or a small index file.
- `gh api --paginate` follows pagination for list endpoints; it is not needed for the single-file GET.

## 5. Rate limits and idempotency

### Rate limits (documented)

- Primary: "All of these requests count towards your personal rate limit of 5,000 requests per hour." GitHub App requests on behalf of an Enterprise Cloud organization get "a higher rate limit of 15,000 requests per hour" [rest-rate-limits, Primary rate limit for authenticated users].
- Secondary, content-generating: "In general, no more than 80 content-generating requests per minute" and "no more than 500 content-generating requests per hour are allowed"; "Some endpoints have lower content creation limits" [rest-rate-limits, Secondary rate limits for content-creating requests]. Content creation limits include web UI and API actions [graphql-rate-limits] (summary).
- Secondary, point-based: "Most REST API POST, PATCH, PUT, or DELETE requests" score 5 points, versus 1 for most GET [rest-rate-limits, Secondary rate limit for POST, PATCH, PUT, and DELETE requests]. The GraphQL endpoint: "No more than 2,000 points per minute"; GraphQL requests with mutations score 5 [graphql-rate-limits] (summary).
- Headers: `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-used`, `x-ratelimit-reset` (UTC epoch seconds), `x-ratelimit-resource`, `retry-after` [rest-rate-limits, Rate limit headers].
- Handling: primary limit gives 403 or 429, "You should not retry your request until after the time specified by the `x-ratelimit-reset` header." Secondary: if `retry-after` is present, wait that many seconds; if `x-ratelimit-remaining` is `0`, wait until `x-ratelimit-reset`; otherwise "wait at least one minute before retrying"; on repeated failures "wait for an exponentially increasing amount of time between retries" and fail after a set number of retries. "Continuing to make requests while you are rate limited may result in the banning of your integration." [rest-rate-limits, Handling 403 and 429 responses].
- Budget per run (option a): about N+3 POST/PATCH-class requests (N blobs, 1 tree, 1 commit, 1 PATCH), each scoring 5 points against the secondary point budget. A run of 5 files is 8 mutating requests. At 80 content-generating requests per minute and 500 per hour, many concurrent runs would hit the hourly ceiling first only if they publish dozens of runs an hour; the docs do not say which limit is binding for a given burst.
- `gh api` on rate-limit errors: the manual does not document how `gh api` reports or retries these errors. **Unverified** (see Unverified list).

### Idempotency under lost responses

- Blob: content addressing is documented: the blob SHA-1 is computed from the content header plus content [git-book, Git Objects]; `POST git/blobs` returns the blob and its sha. Re-POSTing identical content yields the same sha by construction of Git hashing. The REST page does not state dedupe behavior for repeated POSTs. Result: a retry of a blob POST is safe in effect (same object id), but it is not documented as idempotent at the API level. Status on repeat: **Unverified**.
- Tree: a tree sha is a hash of its entries. Same entries and same `base_tree` give the same tree sha. Not explicitly documented by GitHub; follows from Git object hashing (git-book). Treat as derived.
- Commit: the commit object format includes "the author/committer information ... and a timestamp" and a message [git-book, Git Objects]. With fixed `author.name`, `author.email`, `author.date`, `committer` fields, the same tree, parents and message produce the same commit bytes and sha. The REST commit page says "By default, the author will be the authenticated user and the current date" and `date` is optional [rest-git-commits, author] (summary). It does not say whether GitHub dedupes identical commit creations. Status: **Unverified** whether a repeated POST returns the existing commit or a new one. Deterministic sha is derived, not documented by GitHub.
- Ref PATCH with the same target sha twice: not documented. Derived behavior: after the first success, the ref already equals the target, so the second PATCH is a no-op update to the same sha, which Git treats as "already up to date" (not a non-fast-forward). **Unverified** against the live API; must be tested.
- Contents PUT retry: a retry after a lost response will fail with 409 or 422 if the `sha` is now stale (the file was already replaced). Result: the retry must GET the file first and compare content before deciding "already published".

### Implications for the retry design (derived)

1. Compute every object sha locally and pin all identity fields (author/committer name, email, date) so the commit sha is reproducible.
2. Before a publication attempt, read the head. After a lost PATCH, re-read the head: if it equals the commit you built, the publish succeeded; if the head is a descendant of your commit (verify via compare), it also succeeded; otherwise rebuild on the new head and retry.
3. Idempotency key: the run ID in the record path. A retry checks whether the record path already exists with identical content (GET contents) before writing. This is the key defence against duplicate logical records, since a git-level commit dedupe is not documented.
4. Never use `force: true`. Never overwrite a path with different content silently (the proposal's requirement).

## 6. `gh` specifics

- Repository: `gh api` documents placeholder substitution for `{owner}`, `{repo}` and `{branch}`: "Placeholder values {owner}, {repo}, and {branch} in the endpoint argument will get replaced ... with values from the repository of the current directory or the repository specified in the GH_REPO environment variable" [cli-gh-api, Placeholder substitution] (summary). No `-R/--repo` flag is listed on the `gh api` page read.
- `GH_REPO`: "specify the GitHub repository in the `[HOST/]OWNER/REPO` format for commands that otherwise operate on a local repository" [cli-gh-help-environment, GH_REPO] (summary). Using `GH_REPO=owner/repo` is the documented way to target a repository without depending on the current directory's remote. Preferred for the procedure: explicit `owner/repo` from `config` rather than placeholders, so that no local Git state is read.
- Local state: the docs do not say how the current repository is resolved (which remote). **Unverified**: that `{owner}`/`{repo}` read the git remote without changing HEAD, index or refs. The page says it uses the current directory's repository; the mechanism is not documented.
- Token: `GH_TOKEN` "takes precedence over previously stored credentials"; `GITHUB_TOKEN` is lower precedence [cli-gh-help-environment, GH_TOKEN and GITHUB_TOKEN] (summary).
- Auth status: `gh auth status` "Display active account and authentication state on each known GitHub host"; "the authentication state of each known account is tested" [cli-gh-auth-status] (summary). The page read does not show token scopes. Flags `-t/--show-token`, `-a/--active`, `-h/--hostname` [cli-gh-auth-status, Flags]. Scope listing is therefore **Unverified** from the manual; check the live `gh auth status` output on a machine.
- Scopes meaning (classic): `repo` "Grants full access to public and private repositories"; `workflow` needed to add or update `.github/workflows` files [oauth-scopes, repo; workflow]. Not needed for history paths under a normal directory.
- Failure behavior: `gh api` exit code and printing on HTTP errors are not in the manual read. **Unverified**.

## 7. Branch protection and rulesets on a non-default branch

- Rulesets target "selected branches and tags in a repository"; "You can use `fnmatch` syntax to define a pattern to target specific branches and tags" [rulesets-about, What rulesets can target] (summary).
- Restrict creations: "If selected, only users with bypass permissions can create branches or tags whose name matches the pattern you specify." [rulesets-rules, Restrict creations]. A ruleset matching `maintenance-history` with this rule would block the initializing `POST git/refs` for non-bypass actors (the token's user or app).
- Restrict updates: "If selected, only users with bypass permissions can push to branches or tags whose name matches the pattern you specify." [rulesets-rules, Restrict updates]. This would block the ref PATCH.
- Restrict deletions: "This rule is selected by default" [rulesets-rules, Restrict deletions].
- Block force pushes: "You can prevent users from force pushing to the targeted branches or tags. This rule is enabled by default." [rulesets-rules, Block force pushes]. A forced PATCH would be blocked, which matches the non-forced design.
- Bypass: "When you create a ruleset, you can allow certain users to bypass the rules in the ruleset", including repository administrators, teams or GitHub Apps [rulesets-about, Bypass actors] (summary). Whether bypass applies specifically to API actions is not stated.
- Classic branch protection was not read in this pass. **Unverified**: its interaction with API ref creation.

## Recommendation

Option (a), the Git Database sequence, with these rules:

1. Build: blobs (one per file) → tree with `base_tree` set to the current head's tree (or no `base_tree` for the root) → commit with pinned author, committer and date, and `parents` equal to the observed head → `PATCH git/refs/heads/<name>` with `force` omitted (or `false`). Request cost is N blobs + 1 tree + 1 commit + 1 PATCH, plus one GET of the head.
2. Retry: on a rejected PATCH (422 or 409, with the message not parsed), re-read the head, check whether the record already exists by content, then rebuild on the new head. Bound the retries and report a publication failure with an explicit outcome, separate from the run's own result.
3. Lost response: re-read the head and check whether it is the built commit or a descendant of it (compare endpoint) before any retry.
4. Initialization: follow section 3, with the existing-branch ancestry check; never call `POST git/refs` or `PATCH` with `force: true`.
5. Auth: a fine-grained token with Contents write on the repository (or a GitHub App with Contents write); classic tokens need `repo`. A `GH_REPO` environment setting selects the repository explicitly.

Why not (b): one commit per file, not atomic across files, more requests (N PUTs, N GETs for shas) and more branch moves to race with.
Why not (c) now: the docs read does not give the atomicity, stale-head error, branch creation or orphan behavior. It may be a simpler single request if those are confirmed on the live GraphQL reference.

Condition that would change the recommendation:
- If the GraphQL reference for `createCommitOnBranch` documents atomic application of all `fileChanges`, a documented stale-head error with a stable code, and creation of an orphan or missing branch, then (c) would become the simpler choice (1 mutation per run, server-side expected-head check), and the Git Database path would become the fallback.
- If a live test shows that a repeated ref PATCH with the same sha or a repeated commit POST with identical fields returns an error, the retry design must change to "treat that error as success after a GET confirms the sha".
- If rulesets on `maintenance-history` restrict creation or updates for the publishing identity, the publishing identity needs bypass or the design needs an approval step.
- If the per-run count of blobs grows (large run output), the 100,000-entry tree limit or the secondary content-creation limit (80/min, 500/hour) becomes binding; then batching records into fewer runs or a per-run single blob would be needed.

## Unverified

- Exact status and message for a non-fast-forward `PATCH git/refs/heads/<name>` with `force: false` (docs say only 422 generic).
- The `POST git/refs` 422 "Reference already exists" text and behavior when the ref exists (not on the page read).
- The 409 "Git Repository is empty" text (only the "unable to create new references for empty repositories" sentence was seen).
- Whether POST git/blobs, POST git/trees, POST git/commits dedupe or are idempotent at the API level; whether identical commit creations return the same sha.
- Whether a repeated PATCH with the same target sha succeeds.
- `createCommitOnBranch`: atomicity, stale-`expectedHeadOid` error, branch creation, orphan commits, base64 and size limits of `FileAddition`/`FileChanges` (the reference section could not be read; index and commits pages gave only the summary above).
- Contents PUT: how a 409 distinguishes stale branch from stale file sha.
- Meaning of the "Additional Permissions" column for `git/refs` and `PUT contents` in the fine-grained table; whether protected-branch or ruleset rules add permissions.
- Whether `gh api` resolves `{owner}`/`{repo}` via the git remote and whether it changes local Git state (the manual says only "the repository of the current directory").
- Whether `gh api` exits non-zero on HTTP 4xx/5xx and how it prints rate-limit responses; whether it retries.
- `gh auth status` token scope listing (the manual page read had no scopes).
- Whether classic branch protection rules affect API ref creation or update on non-default branches.
- The exact meaning of the compare `status` values (`diverged`, `ahead`, `behind`, `identical`) beyond their names.
- Rate-limit point cost of the Git Database calls specifically (only "Most REST API POST, PATCH, PUT, or DELETE requests" scores 5).
- Live behavior for all the above: none of this was tested against GitHub in this pass; no API call was made.

## Sources

- [rest-git-blobs] https://docs.github.com/en/rest/git/blobs — read 2026-11-04 (Create a blob; Get a blob)
- [rest-git-trees] https://docs.github.com/en/rest/git/trees — read 2026-11-04 (Create a tree; Get a tree; Note)
- [rest-git-commits] https://docs.github.com/en/rest/git/commits — read 2026-11-04 (Create a commit; Body parameters; HTTP response status codes)
- [rest-git-refs] https://docs.github.com/en/rest/git/refs — read 2026-11-04 (Create a reference; Update a reference; Get a reference)
- [rest-repos-contents] https://docs.github.com/en/rest/repos/contents — read 2026-11-04 (Create or update file contents; Get repository content; Permissions)
- [graphql-commits] https://docs.github.com/en/graphql/reference/commits — read 2026-11-04 (createCommitOnBranch, summary only). The mutations index https://docs.github.com/en/graphql/reference/mutations did not contain the section.
- [rest-rate-limits] https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api — read 2026-11-04
- [graphql-rate-limits] https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api — read 2026-11-04
- [rest-commits] https://docs.github.com/en/rest/commits/commits — read 2026-11-04 (List commits; Compare two commits; Compare anchor section)
- [rest-fine-grained-permissions] https://docs.github.com/en/rest/overview/permissions-required-for-fine-grained-personal-access-tokens — read 2026-11-04 (summary of table rows)
- [rulesets-about] https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets — read 2026-11-04
- [rulesets-rules] https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets — read 2026-11-04
- [cli-gh-api] https://cli.github.com/manual/gh_api — read 2026-11-04
- [cli-gh-auth-status] https://cli.github.com/manual/gh_auth_status — read 2026-11-04
- [cli-gh-help-environment] https://cli.github.com/manual/gh_help_environment — read 2026-11-04
- [oauth-scopes] https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps — read 2026-11-04
- [git-book] https://git-scm.com/book/en/v2/Git-Internals-Git-Objects — read 2026-11-04 (Pro Git, Git Objects; a secondary/primary-for-Git-format source)
- Not read (404 or not reached): `https://docs.github.com/en/rest/commits/commits` section anchors for the 409 text returned the Commits page without the "Git Repository is empty" message; `https://docs.github.com/en/rest/git/commits` returned no permission table.
