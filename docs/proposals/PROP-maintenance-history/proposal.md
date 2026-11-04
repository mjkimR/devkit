---
id: PROP-maintenance-history
title: Maintenance execution history on a GitHub orphan branch
summary: "Persists maintenance playbook execution records on a dedicated GitHub orphan branch through gh api, linked to the inspected source revision, without touching the local checkout or code history."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: delivery/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-maintenance-run-history
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/maintenance/
    - packages/devkit-catalog/tests/
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit/tests/
    - packages/devkit/pyproject.toml
    - packages/devkit/README.md
    - .devkit/architecture.toml
    - docs/capabilities/delivery/
    - docs/usecases/governance/
    - docs/development/reference/
    - docs/steering/glossary.md
  excludes:
    - docs/decisions/
    - packages/devkit-dist/src/devkit_dist/features/shared/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-maintenance-history] Maintenance execution history on a GitHub orphan branch

## 1. Background & Hypothesis

Maintenance playbooks (`weekly-report`, `drift-reconciliation`, `review-refactor`, `performance-pass`) produce
findings and decisions that later runs and reports need, but nothing keeps them beyond the run. Recording each run
on a dedicated GitHub orphan branch through `gh api` keeps durable, revision-linked history apart from code history,
without switching branches, staging files, creating local commits or pushing. Manual playbook delivery does not
depend on it. This draft is the direct member of `MS-maintenance-run-history`, which took this scope over from
`MS-maintenance-operations`.

## 2. Technical Spike Questions

- **Q1**: Which GitHub Contents or Git Database endpoints give atomic multi-file publication and non-forced,
  retry-safe branch updates under concurrent writers?
  Answer (`materials/github-publication-api.md`): only the Git Database sequence (blobs, a tree with `base_tree`,
  a commit, one `PATCH git/refs/heads/<branch>` with `force` omitted) publishes several files in one commit and
  refuses a non-fast-forward update. The Contents API writes one commit per file. GraphQL `createCommitOnBranch`
  carries an expected head but its atomicity, branch creation and orphan behavior are undocumented. API-level
  idempotency and exact error texts are unverified; Development confirms them in a labelled live exercise.
- **Q2**: How does a run that inspected uncommitted changes identify that state, given a commit SHA alone does not?
  Answer (`materials/internal-constraints.md` §4): by the source SHA, the dirty path list, a tree hash from a
  temporary index and a SHA-256 digest of the retained local diff (`PADR-inspected-state-identity`).

## 3. Proposed Design & Impact

The comparison behind each choice is `materials/planning-options.md`; the decisions are
`PADR-history-branch-publication` and `PADR-inspected-state-identity`. The challenger findings of
`envelopes/challenger-01.yaml` are folded into this section.

### 3.1 Command family

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
| `init --authority "<text>" [--repository <owner/repo>] [--branch <name>]` | Creates the deterministic root commit and the branch, or validates an existing branch against the constant root (§3.2); refuses a foreign branch without updating it |
| `start --playbook <id> --scope "<text>" --into <dir> [--timezone <IANA name>] [--supersedes <run-id>]... [--prior-run <run-id>]...` | Captures the inspected state (§3.3) and writes the local run directory `<dir>/<run-id>/` with `record.json` |
| `finish --run <dir> --outcome completed\|failed\|interrupted [--result "<text>"] [--report <file>] [--applied-commit <sha>]... [--follow-up <ID>]...` | Recaptures the inspected state, warns on drift, computes the report SHA-256, closes the record |
| `publish --run <dir> --authority "<text>" [--repository] [--branch] [--file <path>]...` | Publishes the record, the report and the named files as one commit on the history branch; writes the publication fields into the local record |
| `update --run <dir> --authority "<text>" --integration-state "<text>" [--applied-commit <sha>]...` | Publishes an append-only amendment `updates/<UTC time>.json` for a run whose work items integrated or stopped after `finish` |
| `list --playbook <id> [--source-sha <sha>] [--outcome <value>] [--include-superseded] [--limit <n>]` | Reads the index shards newest year first until `--limit` is met and prints one `[HISTORY_RUN: ...]` line per run |
| `get --run-id <id> [--file record.json\|report.md\|<path>]` | Prints one published file of a run; the run ID carries the playbook, so no second flag is needed |

`--repository` defaults to `[maintenance.history] repository` in `.devkit/config.toml`, else to the `origin` remote
read with `git remote get-url origin`; `--branch` defaults to `[maintenance.history] branch`, else
`maintenance-history`. The configuration supplies inputs only; it grants no authority. `init`, `publish` and
`update` are the only commands that mutate GitHub; each refuses without `--authority`, and `publish` never
initializes a branch.

### 3.2 History branch layout

```
README.md                                           # fixed bytes: history marker, layout, "never merge into a code branch"
runs/<playbook>/<run-id>/record.json                # canonical JSON (sorted keys, compact separators, UTF-8, newline-terminated)
runs/<playbook>/<run-id>/report.md
runs/<playbook>/<run-id>/<file>                     # files the run selected with --file
runs/<playbook>/<run-id>/updates/<YYYYMMDDTHHMMSSZ>.json   # append-only amendments
index/<playbook>/<YYYY>.jsonl                       # one line per published run or update, sharded by the run ID's year
```

- The run ID is `<playbook>-<UTC start time as YYYYMMDDTHHMMSSZ>-<8 hex random>`, generated by `start`; listings
  sort by time, two runs never share a path and `get` derives the playbook from the ID.
- The root commit is deterministic: fixed `README.md` bytes, a fixed `devkit maintenance history` identity and a
  fixed date give one constant root commit SHA, computed once in Development and recorded in the capability. `init`
  validates an existing branch with one `GET compare/<root>...<head>` request: `identical` or `ahead` passes,
  anything else is `HISTORY_BRANCH_FOREIGN`, and the branch is never updated.
- An index line is `{"kind":"run"|"update","run_id","source_sha","inspected_tree","outcome","result",
  "finished_at","supersedes","path"}`; an `update` line carries `integration_state` and `updated_at`. `list` merges
  lines by `run_id` with the later line winning and skips superseded runs unless `--include-superseded`.
- Every published commit's message is `history: <playbook> <run-id>` (or `history: update <run-id>`); its author,
  committer and dates are pinned from the record so a rebuilt commit for the same content has the same SHA. The
  identity the run commits carry is open question `q5`. Source SHAs and history commit SHAs stay distinct fields.

### 3.3 Run record

One record type serves the four playbooks and is the companion record that `CAP-DLV-weekly-report` §4 defines:

- Identity: `run_id`, `playbook`, `repository` (credential-free `owner/repo`), `scope`, `timezone` (the IANA name
  from `--timezone`, else the system zone marked `source: system`), `started_at` and `finished_at` as UTC and local
  time with offset, `supersedes` (run IDs this run replaces) and `prior_runs` (earlier run IDs the playbook compared).
- Inspected state (`PADR-inspected-state-identity`): `source_sha` (HEAD at intake), `dirty`, `dirty_paths`,
  `inspected_tree`, `diff_digest` and `diff_path`. The comparison set excludes the run directory, the report path and
  `diff_path`: they are left out of `dirty_paths`, of the temporary index (`git add -A -- . ':!<run dir>'`) and of
  the retained diff, so a run's own output never counts as drift. Each command uses its own temporary index file in
  the Git directory and deletes it after `write-tree`; growth of the object store is accepted and is not a checkout
  change. A failing clean filter is `HISTORY_SNAPSHOT_FAILED`, and no record is written.
  The retained diff file is the digest input: `git -c diff.noprefix=false -c core.quotepath=false diff --no-ext-diff
  --no-textconv --no-renames --binary HEAD`, followed by one entry per untracked path in byte order holding the
  length-prefixed path and the length-prefixed bytes; `diff_digest` is the SHA-256 of that file. A clean run records
  `inspected_tree` equal to `HEAD^{tree}` and null diff fields. `finish` adds `drifted_at_finish` when HEAD or the
  inspected tree changed and prints `HISTORY_RUN_DRIFTED` as a warning.
- Outcome: `outcome` (`completed`, `failed` or `interrupted`, the same for every playbook) and `result` (the
  playbook's own vocabulary, such as the performance pass's `stopped at decision round`). `counts` holds the
  playbook's own counters.
- Evidence: `report` (path and SHA-256), `files` (path and SHA-256 each), `applied_commits`, `follow_ups`
  (full `FB-` and `PROP-` IDs).
- Publication (local record only): `destination` (`owner/repo#branch`), `authority`, `attempts` (time, request,
  status class, result), `publication` (`pending`, `published`, `failed` or `unknown`), `history_commit` once
  published, and `updates` (each amendment's time, state and history commit). The published `record.json` carries
  every field but these, serialized as canonical JSON.

A run with no findings records `outcome: completed` with zero counts and stays distinguishable from a missing run
by its index line and record. The record's bytes never change after `finish`; later integration state goes into an
amendment, and a publication outcome changes only the local publication fields.

### 3.4 Publication contract

- Publication is a separately authorized step per run: `init`, `publish` and `update` refuse without
  `--authority`, and the playbook obtains that authority from the user in the conversation for a destination the
  user selected (`CAP-DLV-weekly-report` §4, `ADR-mcp-runtime-and-shared-artifacts`). Invocation and
  `[maintenance.history]` settings grant none; a run's publication stays `pending` until `publish` succeeds. `init`
  records its authority in a local init record beside the configuration.
- Before sending, `publish` runs the installed `secret_leak` check over the files to publish and refuses with
  `HISTORY_SECRET_BLOCKED` on a hit, because the branch is never force-updated or deleted.
- `publish` reads the repository and the branch reference first: a 404 there is `failed` (destination or
  permission). It then reads `runs/<playbook>/<run-id>/record.json` at that head: an identical blob SHA of the
  canonical bytes resolves `published` without resending and looks up `history_commit` with
  `commits?sha=<branch>&path=<record path>`; a different blob is `HISTORY_RECORD_COLLISION` and never overwrites;
  a 404 at a readable head is absence and permits the attempt.
- An attempt uploads blobs, re-reads the index shard from the head it builds on and appends its line to that
  content, builds the tree on the head's tree, creates the commit with the head as parent and updates the reference
  without force. On a rejected update it re-reads the head and repeats the inspection and build, at most three
  attempts; exhaustion is `HISTORY_PUBLISH_DEFERRED` with the outcome `pending`.
- Failure classes map onto the existing outcomes: a missing `gh` login is an error that leaves `pending`;
  authentication, permission, ruleset and collision failures are `failed`; a rate limit, a `retry-after` or race
  exhaustion is `HISTORY_PUBLISH_DEFERRED` and leaves `pending`; a lost response whose head cannot be read is
  `unknown`. Every outcome is distinct from the run's own `outcome`.
- The commands never write the local index, refs, HEAD or working tree outside the run directory. Tests compare
  `git for-each-ref`, the index checksum and `git status --porcelain` outside `<dir>` before and after each command.

Codes, channels and exit codes (`ARCH-08-cross-cutting` §4; modes per `CAP-ADV-agent-advisory-protocol` §5):

| Code | Command | Channel | Exit | Mode and `[ACTION]` |
| --- | --- | --- | --- | --- |
| `HISTORY_BRANCH_READY` | `init` | stdout | 0 | result line with the root and head SHAs |
| `HISTORY_BRANCH_FOREIGN` | `init`, `publish`, `update` | `[ERROR]` | 2 | `BLOCKED`: choose another branch; the branch is untouched |
| `HISTORY_BRANCH_MISSING` | `publish`, `update`, `list`, `get` | `[ERROR]` | 2 | `INTERACTION`: run `init` once the user authorizes it |
| `HISTORY_REPOSITORY_EMPTY` | `init` | `[ERROR]` | 2 | `BLOCKED`: the repository needs an initial commit first |
| `HISTORY_AUTHORITY_MISSING` | `init`, `publish`, `update` | `[ERROR]` | 2 | `INPUT_ERROR`: pass `--authority` after the user's decision |
| `HISTORY_GH_UNAVAILABLE` | all GitHub commands | `[ERROR]` | 2 | `INTERACTION`: install or log in `gh`; the local record stays `pending` |
| `HISTORY_RUN_STARTED`, `HISTORY_RUN_FINISHED`, `HISTORY_RUN_UPDATED` | `start`, `finish`, `update` | stdout | 0 | result line with the run ID and path |
| `HISTORY_RUN_DRIFTED` | `finish` | `[WARN]` | 0 (`--strict`: 1) | `CONTINUE`: revalidate the evidence as the playbook says |
| `HISTORY_SNAPSHOT_FAILED` | `start`, `finish` | `[ERROR]` | 2 | `INPUT_ERROR`: fix the clean filter or exclude the path |
| `HISTORY_PUBLISHED` | `publish` | stdout | 0 | result line with the history commit SHA |
| `HISTORY_SECRET_BLOCKED` | `publish`, `update` | `[ERROR]` | 2 | `BLOCKED`: remove the secret or deselect the file |
| `HISTORY_PUBLISH_FAILED` | `publish`, `update` | `[ERROR]` | 1 | `INTERACTION`: fix credentials, permission or ruleset, then rerun with the same run |
| `HISTORY_RECORD_COLLISION` | `publish` | `[ERROR]` | 1 | `BLOCKED`: the path holds different content; a changed record is a new run |
| `HISTORY_PUBLISH_DEFERRED` | `publish`, `update` | `[ERROR]` | 1 | `DEFER` with `retry_after`; rerun later with the same run |
| `HISTORY_PUBLISH_UNKNOWN` | `publish`, `update` | `[ERROR]` | 1 | `INTERACTION`: inspect the destination; a rerun resolves it by inspection, never by blind resend |
| `HISTORY_LIST` | `list` | stdout | 0 | summary line with the count; zero runs is a valid result |
| `HISTORY_RUN` | `list` | stdout | 0 | one line per run |
| `HISTORY_RUN_MISSING` | `get` | `[ERROR]` | 1 | `INPUT_ERROR`: check the run ID with `list` |

### 3.5 Playbook changes

Where `devkit maintenance` is installed, each of the four playbooks gains a run-record step at intake
(`history start`), at completion (`history finish`) and an optional publication step that names the destination,
the user's authority and `init` as a separately authorized action when the branch is absent. The review-refactor
and performance-pass step that updates a report's outcome when a work item integrates or stops calls `history
update` for a published run. Without `devkit maintenance`, each playbook keeps its current local record. The
weekly report's companion record becomes this record; the drift playbook gains a run ID. The playbooks' review,
decision and application procedures do not change (`MS-maintenance-run-history` non-goals). Only the Host or the
playbook's own step runs the commands; subagents never write a run's records.

### 3.6 Verification

- Integration tests with an injected `gh` runner that models the Git Database, contents, commits and compare
  endpoints in memory: initialization against an empty, absent, matching and foreign branch; multi-file
  publication; a no-finding run; a failed run; a duplicate retry; two interleaved writers whose final head holds
  both run directories and both index lines; a lost response resolved by inspection; a collision; a rate-limited
  attempt; a 404 on a private repository; an amendment; `list` across two year shards; `get`; and unchanged local
  Git state outside the run directory. A PATH-shim `gh` covers a missing or unauthenticated `gh` and the runner's
  timeouts.
- Unit tests on a temporary repository: identical dirty content gives identical `inspected_tree` and
  `diff_digest`, a changed file changes both, the run directory never counts as drift, and canonical JSON bytes are
  stable across key order.
- Content tests keep each playbook self-contained and within budget.
- A live exercise against a throwaway repository, labelled as such, confirms the unverified API facts (exact error
  responses, repeated POST behaviour, same-sha reference update, 404 semantics) before the capability states them.

### 3.7 Living Spec impact

- New: the delivery capability `maintenance-history` (its ID is assigned at spec-sync; the command family, record,
  branch layout, root constant and publication contract) and the use cases `record-a-maintenance-run` and
  `find-the-latest-maintenance-run` under `docs/usecases/governance/`.
- Changed: `CAP-DLV-weekly-report` (the companion record and publication clauses cite the new capability; the scope
  sentence names it as the separate history backend), `CAP-DLV-drift-reconciliation` (run ID),
  `CAP-DLV-review-refactor` and `CAP-DLV-performance-pass` (run record, publication and amendment steps), the
  glossary (`playbook run`, `run record`, `publication destination`, `source SHA`), the `devkit_agt` feature edges
  in `.devkit/architecture.toml`, the `devkit.commands` and config-table entries of `packages/devkit/pyproject.toml`,
  `packages/devkit/README.md` and `docs/development/reference/`.
- Unchanged: `CAP-COLL-shared-artifacts` and `devkit_dist.features.shared` (the history branch is not a shared
  artifact and is not subject to its seven-day TTL), `ADR-local-and-pull-request-integration` (PR operations keep
  their protocol) and the `[integration]` and `pull_request` policies, which do not cover the history branch.

### 3.8 Non-goals

Scheduler or trigger design, the maintenance procedures themselves, records on the default code branch, merging
the history branch, automatic code changes or integration, a general-purpose store, destructive history compaction
or retention cleanup, a non-GitHub provider, publishing the retained diff by default, and a web view of the history.

## Planning decisions

- Publication mechanism: the Git Database API sequence (`PADR-history-branch-publication`); the Contents API and
  GraphQL `createCommitOnBranch` are rejected for now with the condition recorded in the PADR.
- Code placement: a `devkit-agt` feature; the content-only catalog keeps the playbook text. Size moves from `M` to
  `L` for the feature, its fakes and the capability work. This choice is open question `q1` until answered.
- Publication authority: per run, explicit, for `init`, `publish` and `update`, with `pending` as the default
  outcome; the configured repository and branch are inputs. Open question `q3` offers the alternative of a standing
  opt-in, which needs a superseding ADR.
- Inspected-state identity: `PADR-inspected-state-identity`; `source_sha` stays a commit (open question `q4`).
- Record layout: run directories, append-only amendments and a per-playbook index sharded by the run ID's year;
  size-based rollover, a recursive tree walk and a search endpoint are rejected (`materials/planning-options.md`
  set 5 and `envelopes/challenger-01.yaml` findings 1, 3 and 4).
- Branch validation: a constant root commit and one compare request (challenger finding 5).
- Outcome vocabulary: a common `outcome` field with three values and a playbook-specific `result` field, so the
  performance pass keeps its own values; integration state after `finish` is an amendment, never a record change.
- Playbook coverage: all four maintenance playbooks (open question `q2`), each step guarded by the presence of
  `devkit maintenance`.
- Commit identity of the run commits: open question `q5` (challenger finding 19); the root commit identity is fixed.
- `dev_effort` stays `medium` (challenger finding 18 waived): the race, retry and inspection paths are integration
  tests with the modelled runner, the mandatory `code-reviewer` pass covers them, and the implementer calls the
  reviewer again for uncertain correctness; the user may raise it at `plan-accept`.
- Terminology: playbook run, run record, report, publication destination, source SHA; bare "artifact", "receipt"
  and "revision" are avoided for history objects.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr maintenance-history "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept maintenance-history --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff maintenance-history.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->
