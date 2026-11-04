---
id: ADR-history-branch-publication
title: History publication on a parentless GitHub branch through the Git Database API
summary: "For durable maintenance run history, we publish each run's record as one commit on a dedicated parentless GitHub branch through the Git Database API with non-forced reference updates, to keep history atomic per run and apart from code history, accepting GitHub-only support and API rate limits."
proposal: SPEC-maintenance-history
status: accepted
created_at: 2026-11-04
---

# [ADR-history-branch-publication] History publication on a parentless GitHub branch through the Git Database API

- **Status**: Accepted
- **Date**: 2026-11-04
- **Deciders**: repository owner
- **Involved Components/Capabilities**: `capabilities/delivery/`, `packages/devkit/src/devkit_agt/features/`, the maintenance playbooks

---

## 1. Context & Problem Statement

Maintenance playbook runs end in a local report and a local companion record; nothing durable survives the
conversation (`MS-maintenance-run-history`). The shared artifact store expires content after seven days and forbids
overwrite and deletion (`CAP-COLL-shared-artifacts`), `CAP-DLV-weekly-report` excludes a history backend from its own
scope, and `ADR-mcp-runtime-and-shared-artifacts` keeps that backend independent and defers a production remote
artifact adapter. A history store therefore needs its own destination, its own write path and its own decision. The
store must publish one run's several files as one unit, survive concurrent writers without losing a record, retry
safely after a lost response and leave the local checkout untouched.

---

## 2. Decision Drivers

- Driver 1: one run's files become visible together or not at all.
- Driver 2: concurrent writers lose no successful record and never overwrite unrelated history.
- Driver 3: a retry after a lost response neither duplicates a run nor replaces different content.
- Driver 4: the local working tree, index, HEAD and refs stay unchanged (`MS-maintenance-run-history` exit condition).
- Driver 5: verification without network through an injectable runner (`ADR-local-and-pull-request-integration`).

---

## 3. Considered Options

### Option 1: Git Database API sequence on a parentless branch (Selected)
- **Overview**: `POST git/blobs`, `POST git/trees` with `base_tree`, `POST git/commits`, then one
  `PATCH git/refs/heads/<branch>` with `force` omitted; the branch starts from a root commit with no parents
  (`docs/materials/2026-11/20261104-maintenance-history/github-publication-api.md` §1-3).
- **Pros**:
  - The single ref update is the publication point, so several files land atomically (Driver 1).
  - A non-fast-forward update is refused, so a stale writer rebuilds on the new head instead of overwriting (Driver 2).
  - Blob, tree and commit SHAs are content-addressed; with pinned author, committer and dates a rebuilt commit has
    the same SHA, and the run ID in the record path serves as the idempotency key (Driver 3).
- **Cons**:
  - N blobs plus three mutating requests per run against the secondary limit of 80 content-generating requests per
    minute and 500 per hour.
  - Exact error texts and API-level dedupe are undocumented; the retry design branches on status classes and
    re-reads the head.

### Option 2: Contents API `PUT` per file
- **Overview**: one `PUT repos/{owner}/{repo}/contents/{path}` per file with the current blob `sha`.
- **Pros**: the simplest single call; no tree building.
- **Cons**: one commit per file, so a failure after k of N files leaves a partial record (fails Driver 1); N branch
  moves race with other writers; each update needs the existing file's `sha`.

### Option 3: GraphQL `createCommitOnBranch`
- **Overview**: one mutation with `fileChanges` and `expectedHeadOid`.
- **Pros**: one request per run with a server-side expected head.
- **Cons**: the official reference read on 2026-11-04 documents neither atomicity, the stale-head error, branch
  creation nor root commits; it cannot initialize the branch.

### Option 4: A `SharedArtifactAdapter` backend
- **Overview**: implement the history as a remote adapter of `devkit_dist.features.shared`.
- **Cons**: the store's contract expires content in seven days and forbids overwrite and deletion; the production
  remote adapter is deferred (`ADR-mcp-runtime-and-shared-artifacts`, `FB-remote-shared-adapter-follow-up`). Rejected.

---

## 4. Decision Outcome

We decided to adopt **Option 1**.

- Each maintenance run publishes its record, report and selected files as one commit on a dedicated branch that
  starts from a parentless root commit and is never merged into a code branch.
- The root commit is deterministic (fixed `README.md` bytes, a fixed `devkit maintenance history` identity and a
  fixed date), so its SHA is a constant the capability records; an existing branch is used only when one compare
  request against that root answers 200 with `identical` or `ahead`. A 200 with another status or a 404 on the
  compare is a foreign branch, refused without any update. Every request is tested for a rate limit (a 429, or a
  403 with `retry-after` or `x-ratelimit-remaining: 0`) before any status mapping; a rate limit, a 5xx or a timeout
  on a read or on a content-creating request before the reference update is deferred with a retry time, never
  foreign and never failed; unavailable means only a missing or logged-out `gh`.
- The publication updates the branch reference without force. A rejected update re-reads the head, repeats the
  inspection, re-reads the index shard from that head and rebuilds on it, at most three times; exhaustion is a
  deferred publication whose outcome stays `pending`, never a confirmed failure.
- The run ID in the record path is the idempotency key: before an attempt and after a lost response the publisher
  reads the repository (after the rate-limit test, a 401, 403 or 404 there is a failed publication), then the branch reference (a 404 there
  is a missing branch that leaves the publication pending and names initialization), then the record at the head,
  resolves an identical canonical blob as published, refuses a different blob as a collision and never overwrites.
- The published record is canonical JSON (sorted keys, compact separators, UTF-8, newline-terminated), so a retry
  from another machine produces the same blob.
- Integration state that arrives after `finish` is an append-only amendment under the run's `updates/` directory
  with a file name fixed at the first attempt, the same read-before-write as the record and its own index line;
  a published record's bytes never change, and listings take the amendment with the greatest update time.
- Initialization, publication and amendment each need an explicit `--authority`; configuration supplies the
  repository and branch only, publication never initializes a branch implicitly, and initialization writes no
  local file.
- The `secret_leak` builtin runs at `finish` over the report and the record before the report digest is computed,
  and at publication over added files only, called directly with a rule context rooted at the run directory and an
  empty exclude list; a hit is an input error that names the path and line.
- Before sending, the publisher recomputes the digests of the report and the selected files and refuses a
  mismatch with the digests frozen at `finish` as an input error; changed content is a new run, and later
  integration state is an amendment, never an edit of the report file.
- The publisher reads the local repository only (`git rev-parse`, `git status --porcelain`, a temporary index) and
  never writes the index, HEAD, refs or working tree outside the run directory.
- Every history commit, the root included, carries the fixed devkit identity as author and committer with dates
  pinned from the record, so the same content rebuilds to the same commit SHA on every machine; the person who
  authorized the publication is named in the record's `authority` field, not in the commit.
- GitHub is the only provider, reached through `gh api` behind an injectable runner that names the repository in
  every endpoint path and sets its own timeout per request class; `gh` owns authentication.
- Option 3 replaces the publish step only when an official reference documents atomic `fileChanges`, a stable
  stale-head error and branch creation; Option 1 then remains for initialization.
- Option 1 satisfies Drivers 1 to 4 with documented semantics and Driver 5 through the existing runner pattern.

---

## 5. Consequences

- **Positive**: durable, revision-linked history outside code history; every successful record survives concurrent
  publication; retries are safe by construction of the record path.
- **Negative / Risks**: GitHub-only; the secondary rate limit binds bursts of runs; undocumented error texts need a
  labelled live exercise before the capability states them; a ruleset that restricts creation or updates of the
  branch name blocks the publishing identity; history commits are not attributed to a person on GitHub, so a
  reader finds the person in the record's `authority` field.
- **Follow-ups**: a non-GitHub provider starts a new proposal when a repository on another host needs history;
  the live exercise runs once in Development before the new `maintenance-history` capability states the error contract.
- **Frozen root**: the root `README.md` bytes, the fixed identity, the fixed date and the resulting constant are
  frozen for good, because any change turns every existing history branch into a foreign branch. Changing them
  needs a superseding ADR and a capability that accepts the set of known root constants.

---

## 6. Confirmation

Integration tests of the `devkit maintenance history` commands with an injected runner (multi-file publication,
interleaved writers with both index lines at the final head, lost response, collision, foreign branch, 404 on a
private repository, amendment, unchanged local Git state) and the restating clauses of
`CAP-DLV-maintenance-history` rules 1–12.
