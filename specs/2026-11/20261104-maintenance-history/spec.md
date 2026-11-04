---
id: SPEC-maintenance-history
title: Maintenance execution history on a GitHub orphan branch
summary: "Persists maintenance playbook execution records on a dedicated GitHub orphan branch through gh api, linked to the inspected source revision, without touching the local checkout or code history."
status: in-progress
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-maintenance-history] Maintenance execution history on a GitHub orphan branch

## 1. Problem Statement & Motivation

Handed off from proposal PROP-maintenance-history on 2026-11-04.
- **Preserved Materials**: `docs/materials/2026-11/20261104-maintenance-history`

### 1. Background & Hypothesis

Maintenance playbooks (`weekly-report`, `drift-reconciliation`, `review-refactor`, `performance-pass`) produce
findings and decisions that later runs and reports need, but nothing keeps them beyond the run. Recording each run
on a dedicated GitHub orphan branch through `gh api` keeps durable, revision-linked history apart from code history,
without switching branches, staging files, creating local commits or pushing. Manual playbook delivery does not
depend on it. This draft is the direct member of `MS-maintenance-run-history`, which took this scope over from
`MS-maintenance-operations`.

## 2. User Stories

- **US-1**: As a maintenance agent, I want a frozen run record identifying inspected content and evidence.
- **US-2**: As a maintenance agent, I want authorized atomic publication and retry-safe amendments on an independent history branch.
- **US-3**: As a maintenance agent, I want to find and read prior runs without fetching or changing my checkout.

## 3. Non-Goals

1. **Scope Excluded**: schedulers, automatic code integration, history on or merged into a code branch, non-GitHub providers, retention cleanup and a web viewer.
2. **Scope Excluded**: publishing retained dirty diffs without explicit file selection and granting publication authority through configuration.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Initialize and validate the history branch
- **Given** an explicitly authorized repository and absent, matching, foreign or empty destination.
- **When** `init` runs.
- **Then** it creates one deterministic parentless root or validates its ancestry; foreign and empty destinations are refused without updating a ref, and no local file is written.

### [AC-02] Identify inspected content without changing local Git state
- **Given** a clean or dirty repository and run/report paths inside or outside it.
- **When** `start` snapshots the comparison set fixed at intake.
- **Then** source SHA, dirty paths, temporary-index tree and retained diff digest identify that content; run/report output is excluded and the real index, HEAD and refs stay unchanged.

### [AC-03] Freeze evidence and detect drift
- **Given** a started run and a report.
- **When** `finish` records completed, failed or interrupted outcome.
- **Then** it secret-checks report and record, freezes canonical record/report digests, refuses a different report path, and warns with `HISTORY_RUN_DRIFTED` if inspected content changed.

### [AC-04] Publish atomically and retry by inspection
- **Given** a finished run and explicit authority.
- **When** `publish` targets a valid history branch.
- **Then** record, report, selected files and one year-shard index line become visible through one non-forced ref update; identical retries resolve without resending and different content at the same path is refused.

### [AC-05] Preserve concurrent writers and classify uncertain outcomes
- **Given** races, rate limits, unavailable gh, permission failures, read/object-creation timeouts or a lost ref-update response.
- **When** publication is attempted.
- **Then** races rebuild on the latest head at most three times, successful writers survive; deferred operations remain pending, permission/collision failures are failed, and only a lost ref-update response is unknown until inspection.

### [AC-06] Append immutable amendments
- **Given** a published run whose work integrates or stops after finish.
- **When** authorized `update` runs or retries.
- **Then** it publishes an append-only amendment with a fixed retry filename and its own index line without changing the published record or report.

### [AC-07] Retrieve latest runs and published files
- **Given** year-sharded indexes, amendments, superseded runs or an absent branch.
- **When** `list` or `get` runs.
- **Then** list merges amendments by update time, filters source/outcome/supersession and limits newest-first; an absent branch lists zero with a notice and get refuses a missing run.

### [AC-08] Keep publication separate from local evidence and authority
- **Given** missing authority, a secret, changed evidence, config defaults or selected extra files.
- **When** a history command runs.
- **Then** missing authority, secrets and changed evidence are refused with the stated stable codes; configuration grants no authority and commands write local state only within the run directory.

### [AC-09] Mount an agent-first command family and integrate four playbooks
- **Given** devkit-agt is installed with or without the maintenance catalog.
- **When** commands or any of the four playbooks run.
- **Then** commands expose text sentinels or one JSON result with advisories on stderr; playbooks conditionally start/finish records, request separate publication authority and amend later integration state; manual paths remain available.

### [AC-10] Confirm undocumented GitHub behavior through a labelled live exercise
- **Given** a user-selected throwaway repository and explicit external mutation authority.
- **When** the recorded live exercise runs.
- **Then** it confirms repeated object POSTs, same-SHA ref updates, rejected stale ref updates and 404 distinctions with retained sanitized evidence before the capability claims live verification.

## Assumptions

- Host clarification: repeatable `finish --file` registers added evidence and freezes its digest; `publish --file` selects only that frozen set, with no added files selected by default. This preserves the accepted immutable record contract despite late publication selection.

- The accepted command table and failure table carried below remain the detailed interface contract; implementation choices do not parse GitHub error messages.
- The live exercise requires a concrete destination and authority from the Host; local fakes are supplementary evidence, not live confirmation.
- `start` may operate before publication initialization; local operation still resolves a credential-free repository identity from configuration or origin.


## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Which GitHub Contents or Git Database endpoints give atomic multi-file publication and non-forced,
  retry-safe branch updates under concurrent writers?
  Answer (`docs/materials/2026-11/20261104-maintenance-history/github-publication-api.md`): only the Git Database sequence (blobs, a tree with `base_tree`,
  a commit, one `PATCH git/refs/heads/<branch>` with `force` omitted) publishes several files in one commit and
  refuses a non-fast-forward update. The Contents API writes one commit per file. GraphQL `createCommitOnBranch`
  carries an expected head but its atomicity, branch creation and orphan behavior are undocumented. API-level
  idempotency and exact error texts are unverified; Development confirms them in a labelled live exercise.
- **Q2**: How does a run that inspected uncommitted changes identify that state, given a commit SHA alone does not?
  Answer (`docs/materials/2026-11/20261104-maintenance-history/internal-constraints.md` §4): by the source SHA, the dirty path list, a tree hash from a
  temporary index and a SHA-256 digest of the retained local diff (`ADR-inspected-state-identity`).

### 3. Proposed Design & Impact

The comparison behind each choice is `docs/materials/2026-11/20261104-maintenance-history/planning-options.md`; the decisions are
`ADR-history-branch-publication` and `ADR-inspected-state-identity`. The challenger findings of
historical Git `2cf7879a74b50b687867e2184188dee6c29a2fbc:docs/proposals/PROP-maintenance-history/envelopes/challenger-01.yaml` are folded into this section.

#### 3.1 Command family

`devkit maintenance history` is a new feature of `devkit-agt` (`packages/devkit/src/devkit_agt/features/
maintenance_history/`) with `cli`, `usecases`, `services` and `repositories` layers, mounted through the
`devkit.commands` entry point of `packages/devkit/pyproject.toml`. It calls GitHub only through `gh api` behind an
injectable runner of its own beside `run_gh`; `gh` owns authentication. The runner names the repository in every
endpoint path, never through `GH_REPO`, and sets its own timeout per request class (a blob upload is sized by its
content) instead of the pull-request runner's network budget. The catalog playbooks stay content and call the
commands where `devkit maintenance` is installed. Every command follows `ARCH-08-1-agent-output`,
`CAP-CLI-agent-cli-toolkit` and `CAP-ADV-agent-advisory-protocol`: one `[KIND: ...]` line per fact on stdout,
advisories on stderr with a stable `UPPER_SNAKE` code and an `[ACTION]`, one JSON object under `--format json`.

| Command | Effect |
| --- | --- |
| `init --authority "<text>" [--repository <owner/repo>] [--branch <name>]` | Creates the deterministic root commit and the branch, or validates an existing branch against the constant root (§3.2); refuses a foreign branch without updating it; prints the root SHA, the head SHA and the authority text on its result line and writes no local file |
| `start --playbook <id> --scope "<text>" --into <dir> --report <path> [--timezone <IANA name>] [--supersedes <run-id>]... [--prior-run <run-id>]...` | Captures the inspected state (§3.3) and writes the local run directory `<dir>/<run-id>/` with `record.json` and, for a dirty run, `inspected.diff`; `--report` is the report path the playbook recorded at intake and fixes the comparison set |
| `finish --file <path>... --run <dir> --outcome completed\|failed\|interrupted [--result "<text>"] [--report <file>] [--applied-commit <sha>]... [--follow-up <ID>]...` | Recaptures the inspected state with the set fixed at `start`, warns on drift, runs the secret check over the report and the record, computes the report SHA-256, closes the record; `--report` is optional and must equal the path given at `start`, otherwise `finish` refuses with an input error |
| `publish --run <dir> --authority "<text>" [--repository] [--branch] [--file <path>]...` | Publishes the record, the report and the named files as one commit on the history branch; writes the publication fields into the local record |
| `update --run <dir> --authority "<text>" --integration-state "<text>" [--applied-commit <sha>]...` | Publishes an append-only amendment `updates/<UTC time>-<8 hex>.json` for a run whose work items integrated or stopped after `finish`; the name is fixed at the first attempt and kept in the local record so a retry reuses it |
| `list --playbook <id> [--source-sha <sha>] [--outcome <value>] [--include-superseded] [--limit <n>]` | Reads the index shards newest year first until `--limit` is met and prints one `[HISTORY_RUN: ...]` line per run; an absent branch is an empty result with a notice, never a refusal |
| `get --run-id <id> [--file record.json\|report.md\|<path>]` | Prints one published file of a run; the run ID carries the playbook, so no second flag is needed |

`--repository` defaults to `[maintenance.history] repository` in `.devkit/config.toml`, else to the `origin` remote
read with `git remote get-url origin`; `--branch` defaults to `[maintenance.history] branch`, else
`maintenance-history`. The configuration supplies inputs only; it grants no authority. `init`, `publish` and
`update` are the only commands that mutate GitHub; each refuses without `--authority`, and `publish` never
initializes a branch.

#### 3.2 History branch layout

```
README.md                                           # fixed bytes: history marker, layout, "never merge into a code branch"
runs/<playbook>/<run-id>/record.json                # canonical JSON (sorted keys, compact separators, UTF-8, newline-terminated)
runs/<playbook>/<run-id>/report.md
runs/<playbook>/<run-id>/<file>                     # files the run selected with --file
runs/<playbook>/<run-id>/updates/<YYYYMMDDTHHMMSSZ>-<8 hex>.json   # append-only amendments, canonical JSON
index/<playbook>/<YYYY>.jsonl                       # one line per published run or update, sharded by the run ID's year
```

- The run ID is `<playbook>-<UTC start time as YYYYMMDDTHHMMSSZ>-<8 hex random>`, generated by `start`; listings
  sort by time, two runs never share a path and `get` derives the playbook from the ID.
- The root commit is deterministic: fixed `README.md` bytes, a fixed `devkit maintenance history` identity and a
  fixed date give one constant root commit SHA, computed once in Development and recorded in the capability. The
  bytes, identity, date and constant are frozen for good (`ADR-history-branch-publication` §5). `init`, `publish`
  and `update` validate an existing branch with one `GET compare/<root>...<head>?per_page=1` request after the
  reference read succeeded: a 200 with status `identical` or `ahead` passes; a 200 with any other status, or a 404
  on the compare, is `HISTORY_BRANCH_FOREIGN` and the branch is never updated. Every request is tested for a rate
  limit before any status mapping: a 429, or a 403 with `retry-after` or `x-ratelimit-remaining: 0`, is
  `HISTORY_DEFERRED` with `retry_after` taken from `retry-after` or `x-ratelimit-reset`; a 5xx or a timeout on any
  read is `HISTORY_DEFERRED` with a default `retry_after`.
- An index line is `{"kind":"run"|"update","run_id","source_sha","inspected_tree","outcome","result",
  "finished_at","supersedes","path"}`; an `update` line repeats the run line's fields and adds
  `integration_state`, `updated_at` and the amendment `path`. `list` merges lines by `run_id`, taking the line with
  the greatest `updated_at` (a run line counts as its `finished_at`; ties go to file order), and skips superseded
  runs unless `--include-superseded`.
- Every published commit's message is `history: <playbook> <run-id>` (or `history: update <run-id>`); its author
  and committer are the fixed devkit identity (name `devkit maintenance history`, a no-reply address) and its dates
  are pinned from the record, so a rebuilt commit for the same content has the same SHA on every machine; the
  record's `authority` field names the person. Source SHAs and history commit SHAs stay distinct fields.

#### 3.3 Run record

One record type serves the four playbooks and is the companion record that `CAP-DLV-weekly-report` §4 defines:

- Identity: `run_id`, `playbook`, `repository` (credential-free `owner/repo`), `scope`, `timezone` (the IANA name
  from `--timezone`, else the system zone marked `source: system`), `started_at` and `finished_at` as UTC and local
  time with offset, `supersedes` (run IDs this run replaces) and `prior_runs` (earlier run IDs the playbook compared).
- Inspected state (`ADR-inspected-state-identity`): `source_sha` (HEAD at intake), `dirty`, `dirty_paths`,
  `inspected_tree`, `diff_digest` and `diff_path`. The comparison set is fixed at `start` and reused by `finish`: it
  excludes the run directory and the report path given with `--report`, which are left out of `dirty_paths`, of the
  temporary index and of the retained diff, so a run's own output never counts as drift. The exclusion is a
  pathspec (`-- . ':!<path>'`) on both `git add -A` and `git diff`, added only for a path inside the worktree; a
  run directory outside the worktree needs no exclusion. Each command uses its own temporary index file in the Git
  directory and deletes it after `write-tree`; growth of the object store is accepted and is not a checkout change.
  A failing clean filter is `HISTORY_SNAPSHOT_FAILED`, and no record is written.
  `inspected_tree` is the content identity: the same content under the same ignore rules and clean filters gives
  the same tree, and its consumer is the start-versus-finish comparison in one checkout. `diff_digest`
  binds the record to the retained diff file and is reproducible from that file alone, not across machines. The
  file holds `git -c diff.noprefix=false -c core.quotepath=false diff --no-ext-diff --no-textconv --no-renames
  --no-color --binary HEAD` with the exclusion pathspec, followed by one entry per untracked path in byte order:
  an 8-byte big-endian length and the path bytes, then an 8-byte big-endian length and the file bytes;
  `diff_digest` is the SHA-256 of the whole file, which lives in the run directory as `inspected.diff`. A clean run records `inspected_tree` equal to `HEAD^{tree}` and
  null diff fields. `finish` adds `drifted_at_finish` when HEAD or the inspected tree changed and prints
  `HISTORY_RUN_DRIFTED` as a warning.
- Outcome: `outcome` (`completed`, `failed` or `interrupted`, the same for every playbook) and `result` (the
  playbook's own vocabulary, such as the performance pass's `stopped at decision round`). `counts` holds the
  playbook's own counters.
- Evidence: `report` (path and SHA-256), `files` (path and SHA-256 each), `applied_commits`, `follow_ups`
  (full `FB-` and `PROP-` IDs).
- Publication (local record only): `destination` (`owner/repo#branch`), `authority`, `attempts` (time, request,
  status class, result), `publication` (`pending`, `published`, `failed` or `unknown`), `history_commit` once
  published, and `updates` (each amendment's fixed file name, state, attempts and history commit). The published
  `record.json` carries every field but these, serialized as canonical JSON.

A run with no findings records `outcome: completed` with zero counts and stays distinguishable from a missing run
by its index line and record. The record's bytes never change after `finish`; later integration state goes into an
amendment, and a publication outcome changes only the local publication fields.

#### 3.4 Publication contract

- Publication is a separately authorized step per run: `init`, `publish` and `update` refuse without
  `--authority`, and the playbook obtains that authority from the user in the conversation for a destination the
  user selected (`CAP-DLV-weekly-report` §4, `ADR-mcp-runtime-and-shared-artifacts`). Invocation and
  `[maintenance.history]` settings grant none; a run's publication stays `pending` until `publish` succeeds. `init`
  writes no local file: its result line carries the authority text, and every publication record carries its own.
- The secret check runs where the content can still change: `finish` runs the `secret_leak` builtin over the
  report and the record before the report SHA-256 is computed, and `publish` and `update` run it over the `--file`
  additions and the amendment only. A hit is `HISTORY_SECRET_FOUND` (`INPUT_ERROR`, naming the path and line). The
  commands call `SecretLeakRule.check` directly with a rule context rooted at the run directory whose changed files
  are the targets and whose exclude list is empty, independent of the project's `[rules]` settings;
  `maintenance_history` declares a feature edge to `rules` for it.
- Before sending, `publish` recomputes the SHA-256 of the report and of each `--file` and refuses a mismatch with
  the digests frozen at `finish` as `HISTORY_EVIDENCE_CHANGED` (`INPUT_ERROR`): changed content is a new run, and
  integration state after `finish` goes into an amendment, never into the report file.
- `publish` reads the repository first: after the rate-limit test, a 401, 403 or 404 there is
  `HISTORY_PUBLISH_FAILED` (outcome `failed`: destination or permission). With the repository readable, a 404 on the branch reference is
  `HISTORY_BRANCH_MISSING` (outcome `pending`; the action names `init`). With the reference read, the root check of
  §3.2 runs. `publish` then reads `runs/<playbook>/<run-id>/record.json` at that head: an identical blob SHA of the
  canonical bytes resolves `published` without resending and looks up `history_commit` with
  `commits?sha=<branch>&path=<record path>`; a different blob is `HISTORY_RECORD_COLLISION` and never overwrites;
  a 404 at the readable head is absence and permits the attempt. `update` applies the same read-before-write to its
  fixed amendment path.
- An attempt uploads blobs, re-reads the index shard from the head it builds on and appends its line to that
  content, builds the tree on the head's tree, creates the commit with the head as parent and updates the reference
  without force. On a rejected update it re-reads the head and repeats the inspection and build, at most three
  attempts; exhaustion is `HISTORY_DEFERRED` with the outcome `pending`.
- Failure classes map onto the existing outcomes: a missing or logged-out `gh` is `HISTORY_GH_UNAVAILABLE` and
  leaves `pending`; authentication, permission, ruleset and collision failures are `failed`; a rate limit, race
  exhaustion, or a 5xx or timeout on any read or on any content-creating request before the reference update is
  `HISTORY_DEFERRED` and leaves `pending`, because blobs, trees and commits are content-addressed and unreferenced
  until the update; only a lost response on the reference update itself is `HISTORY_PUBLISH_UNKNOWN` (`unknown`)
  until an inspection resolves it. Every outcome is distinct from the run's own `outcome`.
- The commands never write the local index, refs, HEAD or working tree outside the run directory. Tests compare
  `git for-each-ref`, the index checksum and `git status --porcelain` outside `<dir>` before and after each
  command, `init` included.

Codes, channels and exit codes (`ARCH-08-cross-cutting` §4; modes per `CAP-ADV-agent-advisory-protocol` §5):

| Code | Command | Channel | Exit | Mode and `[ACTION]` |
| --- | --- | --- | --- | --- |
| `HISTORY_BRANCH_READY` | `init` | stdout | 0 | result line with the root and head SHAs |
| `HISTORY_BRANCH_FOREIGN` | `init`, `publish`, `update` | `[ERROR]` | 2 | `BLOCKED`: the branch does not descend from the history root; choose another branch; the branch is untouched |
| `HISTORY_BRANCH_MISSING` | `publish`, `update` | `[ERROR]` | 2 | `INTERACTION`: run `init` once the user authorizes it; the publication stays `pending` |
| `HISTORY_REPOSITORY_EMPTY` | `init` | `[ERROR]` | 2 | `BLOCKED`: the repository needs an initial commit first |
| `HISTORY_AUTHORITY_MISSING` | `init`, `publish`, `update` | `[ERROR]` | 2 | `INPUT_ERROR`: pass `--authority` after the user's decision |
| `HISTORY_GH_UNAVAILABLE` | all GitHub commands | `[ERROR]` | 2 | `INTERACTION`: install or log in `gh`; only a missing or logged-out `gh`; the local record stays `pending` |
| `HISTORY_DEFERRED` | all GitHub commands | `[ERROR]` | 1 | `DEFER` with `retry_after`: rate limit, race exhaustion, or a 5xx or timeout on any read or any request before the reference update; rerun later with the same inputs |
| `HISTORY_RUN_STARTED`, `HISTORY_RUN_FINISHED`, `HISTORY_RUN_UPDATED` | `start`, `finish`, `update` | stdout | 0 | result line with the run ID and path |
| `HISTORY_RUN_DRIFTED` | `finish` | `[WARN]` | 0 (`--strict`: 1) | `CONTINUE`: revalidate the evidence as the playbook says |
| `HISTORY_SNAPSHOT_FAILED` | `start`, `finish` | `[ERROR]` | 2 | `INPUT_ERROR`: fix the clean filter or exclude the path |
| `HISTORY_REPORT_MISMATCH` | `finish` | `[ERROR]` | 2 | `INPUT_ERROR`: `--report` differs from the path given at `start` |
| `HISTORY_PUBLISHED` | `publish` | stdout | 0 | result line with the history commit SHA |
| `HISTORY_SECRET_FOUND` | `finish`, `publish`, `update` | `[ERROR]` | 1 | `INPUT_ERROR` with the path and line: remove the secret from the report or record (`finish`) or deselect the file (`publish`, `update`), then rerun |
| `HISTORY_EVIDENCE_CHANGED` | `publish` | `[ERROR]` | 1 | `INPUT_ERROR` naming the file: the report or a selected file no longer matches the digest frozen at `finish`; changed content is a new run |
| `HISTORY_PUBLISH_FAILED` | `publish`, `update` | `[ERROR]` | 1 | `INTERACTION`: fix credentials, permission or ruleset, then rerun with the same run |
| `HISTORY_RECORD_COLLISION` | `publish`, `update` | `[ERROR]` | 1 | `BLOCKED`: the path holds different content; a changed record is a new run |
| `HISTORY_PUBLISH_UNKNOWN` | `publish`, `update` | `[ERROR]` | 1 | `INTERACTION`: inspect the destination; a rerun resolves it by inspection, never by blind resend |
| `HISTORY_LIST` | `list` | stdout | 0 | summary line with the count; zero runs is a valid result, and an absent branch prints count 0 with a `[NOTICE]` naming `init` |
| `HISTORY_RUN` | `list` | stdout | 0 | one line per run |
| `HISTORY_RUN_MISSING` | `get` | `[ERROR]` | 1 | `INPUT_ERROR`: check the run ID with `list`; also the result on an absent branch |

#### 3.5 Playbook changes

Where `devkit maintenance` is installed, each of the four playbooks gains a run-record step at intake
(`history start`), at completion (`history finish`) and an optional publication step that names the destination,
the user's authority and `init` as a separately authorized action when the branch is absent. The review-refactor
and performance-pass step that updates a report's outcome when a work item integrates or stops calls `history
update` instead of editing the report file: the amendment replaces the in-file outcome update of
`CAP-DLV-review-refactor` §5 and `CAP-DLV-performance-pass` §6, whose clauses change accordingly. Without `devkit maintenance`, each playbook keeps its current local record. The
weekly report's companion record becomes this record; the drift playbook gains a run ID. The playbooks' review,
decision and application procedures do not change (`MS-maintenance-run-history` non-goals). Only the Host or the
playbook's own step runs the commands; subagents never write a run's records.

#### 3.6 Verification

- Integration tests with an injected `gh` runner that models the Git Database, contents, commits and compare
  endpoints in memory: initialization against an empty, absent, matching and foreign branch; multi-file
  publication; a no-finding run; a failed run; a duplicate retry; two interleaved writers whose final head holds
  both run directories and both index lines; a lost response resolved by inspection; a collision; a rate-limited
  attempt, a 403 with `x-ratelimit-remaining: 0` on the repository read and a 502 on a blob upload, each deferred;
  a report edited after `finish` refused at `publish`; a 404 on a private repository; an absent branch on `publish`, `list` and
  `get`; an amendment and its retry after a lost response; `list` across two year shards; `get`; and unchanged local
  Git state outside the run directory for every command. A PATH-shim `gh` covers a missing or unauthenticated `gh` and the runner's
  timeouts.
- Unit tests on a temporary repository: identical dirty content gives identical `inspected_tree` under different
  `diff.algorithm` and `diff.noprefix` settings and under the same global excludes file, a global excludes file that
  hides an untracked path changes it, `diff_digest` is recomputed from the retained file alone, a changed file
  changes both, the run directory and the report path never count as drift inside or outside the worktree, a
  `finish --report` that differs from `start` is refused, two amendments in one second get distinct paths, and
  canonical JSON bytes are stable across key order.
- Content tests keep each playbook self-contained and within budget.
- A live exercise against a throwaway repository, labelled as such, confirms the unverified API facts (exact error
  responses, repeated POST behaviour, same-sha reference update, 404 semantics) before the capability states them.

#### 3.7 Living Spec impact

- New: the delivery capability `maintenance-history` (its ID is assigned at spec-sync; the command family, record,
  branch layout, root constant and publication contract) and the use cases `record-a-maintenance-run` and
  `find-the-latest-maintenance-run` under `docs/usecases/governance/`.
- Changed: `CAP-DLV-weekly-report` (the companion record and publication clauses cite the new capability; the scope
  sentence names it as the separate history backend), `CAP-DLV-drift-reconciliation` (run ID),
  `CAP-DLV-review-refactor` and `CAP-DLV-performance-pass` (run record, publication and amendment steps; the
  in-file outcome update becomes an amendment), the
  glossary (`playbook run`, `run record`, `publication destination`, `source SHA`), the `devkit_agt` feature edges
  in `.devkit/architecture.toml`, the `devkit.commands` and config-table entries of `packages/devkit/pyproject.toml`,
  `packages/devkit/README.md` and `docs/development/reference/`.
- Unchanged: `CAP-COLL-shared-artifacts` and `devkit_dist.features.shared` (the history branch is not a shared
  artifact and is not subject to its seven-day TTL), `ADR-local-and-pull-request-integration` (PR operations keep
  their protocol) and the `[integration]` and `pull_request` policies, which do not cover the history branch.

#### 3.8 Non-goals

Scheduler or trigger design, the maintenance procedures themselves, records on the default code branch, merging
the history branch, automatic code changes or integration, a general-purpose store, destructive history compaction
or retention cleanup, a non-GitHub provider, publishing the retained diff by default, and a web view of the history.

### Planning decisions

- Publication mechanism: the Git Database API sequence (`ADR-history-branch-publication`); the Contents API and
  GraphQL `createCommitOnBranch` are rejected for now with the condition recorded in the PADR.
- Code placement (user, `answer-01` q1): a `devkit-agt` feature; the content-only catalog keeps the playbook
  text. Size moves from `M` to `L` for the feature, its fakes and the capability work.
- Publication authority (user, `answer-01` q3): per run, explicit, for `init`, `publish` and `update`, with
  `pending` as the default outcome; the configured repository and branch are inputs. A standing opt-in in
  configuration was rejected because it would need a superseding ADR and would grant publication authority by
  policy.
- Inspected-state identity (user, `answer-01` q4): `ADR-inspected-state-identity`; `source_sha` stays a commit,
  and the diff is published only when the run selects it.
- Record layout: run directories, append-only amendments and a per-playbook index sharded by the run ID's year;
  size-based rollover, a recursive tree walk and a search endpoint are rejected (`docs/materials/2026-11/20261104-maintenance-history/planning-options.md`
  set 5 and historical Git `2cf7879a74b50b687867e2184188dee6c29a2fbc:docs/proposals/PROP-maintenance-history/envelopes/challenger-01.yaml` findings 1, 3 and 4).
- Branch validation: a constant, frozen root commit and one compare request whose error classes follow the
  advisory modes (challenger-01 finding 5, challenger-02 findings 4 and 8).
- Secret check: at `finish` over the report and record, at `publish` and `update` over added files, as an
  `INPUT_ERROR` (challenger-02 finding 5); `init` writes no local file (finding 2).
- Digest claims: `inspected_tree` is the content identity under the same ignore rules and clean filters, consumed
  by the start-versus-finish comparison; `diff_digest` binds the record to the retained file (challenger-02 finding
  1, challenger-03 finding 3). `publish` rechecks the frozen digests before sending (challenger-03 finding 4).
- Outcome vocabulary: a common `outcome` field with three values and a playbook-specific `result` field, so the
  performance pass keeps its own values; integration state after `finish` is an amendment, never a record change.
- Playbook coverage (user, `answer-01` q2): all four maintenance playbooks, each step guarded by the presence of
  `devkit maintenance`.
- Commit identity (user, `answer-01` q5, challenger-01 finding 19): the run commits and the root commit carry the
  fixed devkit identity; the publisher's git identity and the `gh` account identity were rejected because they make
  the commit SHA reproducible only per publisher or cost a lookup per publication.
- `dev_effort` stays `medium` (challenger-01 finding 18 waived): the race, retry and inspection paths are integration
  tests with the modelled runner, the mandatory `code-reviewer` pass covers them, and the implementer calls the
  reviewer again for uncertain correctness; the user may raise it at `plan-accept`.
- Terminology: playbook run, run record, report, publication destination, source SHA; bare "artifact", "receipt"
  and "revision" are avoided for history objects.

### 4. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr maintenance-history "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept maintenance-history --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff maintenance-history.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->

