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
    - .devkit/architecture.toml
    - docs/capabilities/delivery/
    - docs/usecases/governance/
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
`PADR-history-branch-publication` and `PADR-inspected-state-identity`.

### 3.1 Command family

`devkit maintenance history` is a new feature of `devkit-agt` (`packages/devkit/src/devkit_agt/features/
maintenance_history/`) with `cli`, `usecases`, `services` and `repositories` layers. It calls GitHub only through
`gh api` behind an injectable runner beside `run_gh`; `gh` owns authentication. The catalog playbooks stay content
and call the commands. Every command follows `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol`: one
`[KIND: ...]` line per fact, stable `UPPER_SNAKE` codes with `[ACTION]`, one JSON object under `--format json`.

| Command | Effect | Result codes |
| --- | --- | --- |
| `init [--repository <owner/repo>] [--branch <name>]` | Creates the parentless root commit (`README.md`, empty `index/`) and the branch, or validates an existing branch: its root commit has no parents and its `README.md` carries the history marker | `HISTORY_BRANCH_READY`, `HISTORY_BRANCH_FOREIGN` (exists with unrelated history; never updated), `HISTORY_REPOSITORY_EMPTY` |
| `start --playbook <id> --scope "<text>" --into <dir>` | Captures the inspected state (§3.3) and writes the local run record `<dir>/<run-id>/record.json` | `HISTORY_RUN_STARTED` |
| `finish --run <dir> --outcome completed\|failed\|interrupted [--result "<text>"] [--report <file>] [--applied-commit <sha>]... [--follow-up <ID>]...` | Recaptures HEAD and dirty state, marks drift since intake, computes the report SHA-256, closes the record | `HISTORY_RUN_FINISHED`, `HISTORY_RUN_DRIFTED` |
| `publish --run <dir> --authority "<text>" [--repository] [--branch] [--file <path>]...` | Publishes `record.json`, the report and the named files as one commit on the history branch; writes the publication fields into the local record | `HISTORY_PUBLISHED`, `HISTORY_PUBLISH_PENDING`, `HISTORY_PUBLISH_FAILED`, `HISTORY_PUBLISH_UNKNOWN`, `HISTORY_PUBLISH_DEFERRED`, `HISTORY_RECORD_COLLISION` |
| `list --playbook <id> [--source-sha <sha>] [--outcome <value>] [--limit <n>]` | Reads `index/<playbook>.jsonl` from the branch head and prints one `[HISTORY_RUN: ...]` line per run, newest first | `HISTORY_INDEX_MISSING` |
| `get --run-id <id> [--file record.json\|report.md\|<path>]` | Prints one published file of a run | `HISTORY_RUN_MISSING` |

`--repository` defaults to `[maintenance.history] repository` in `.devkit/config.toml`, else to the `origin` remote
read with `git remote get-url origin`; `--branch` defaults to `[maintenance.history] branch`, else
`maintenance-history`. The configuration supplies inputs only; it grants no publication authority.

### 3.2 History branch layout

```
README.md                          # history marker, layout, "never merge into a code branch"
runs/<playbook>/<run-id>/record.json
runs/<playbook>/<run-id>/report.md
runs/<playbook>/<run-id>/<file>    # files the run selected with --file
index/<playbook>.jsonl             # one line per published run: run_id, source_sha, inspected_tree, outcome, result, finished_at, path
```

The run ID is `<UTC start time as YYYYMMDDTHHMMSSZ>-<8 hex random>`, generated by `start`, so listings sort by
time and two runs never share a path. Every published commit's message is `history: <playbook> <run-id>`; its author
and committer identity and dates are pinned from the record, so a rebuilt commit for the same content has the same
SHA. Source SHAs and history commit SHAs stay distinct fields. The index rolls over to `index/<playbook>-<year>.jsonl`
when a file passes 1 MB, the contents GET limit for full responses.

### 3.3 Run record

One record type serves the four playbooks and is the companion record that `CAP-DLV-weekly-report` §4 defines:

- Identity: `run_id`, `playbook`, `repository` (credential-free `owner/repo`), `scope`, `started_at` and
  `finished_at` with timezone and UTC offset.
- Inspected state (`PADR-inspected-state-identity`): `source_sha` (HEAD at intake), `dirty` (boolean),
  `dirty_paths` (from `git status --porcelain`), `inspected_tree` (a `write-tree` of a temporary index after
  `read-tree HEAD` and `add -A`), `diff_digest` (SHA-256 of `git diff --binary HEAD` followed by untracked file
  bytes in path order) and `diff_path` (the retained local diff). A clean run records `inspected_tree` equal to
  `HEAD^{tree}` and null diff fields. `finish` adds `drifted_at_finish` when HEAD or the inspected tree changed.
- Outcome: `outcome` (`completed`, `failed` or `interrupted`, the same for every playbook) and `result` (the
  playbook's own vocabulary, such as the performance pass's `stopped at decision round`). `counts` holds the
  playbook's own counters (detected, resolved, deferred, waived, pending).
- Evidence: `report` (path and SHA-256), `files` (path and SHA-256 each), `applied_commits` (code commits a run's
  decisions produced), `follow_ups` (full `FB-` and `PROP-` IDs).
- Publication (local record only): `destination` (`owner/repo#branch`), `authority`, `attempts` (time, request,
  status class, result) and `publication` (`pending`, `published`, `failed` or `unknown`) with `history_commit`
  once published. The published copy of `record.json` carries every field but these.

A run with no findings records `outcome: completed` with zero counts; it stays distinguishable from a missing run
because its index line and record exist. The record's bytes never change after `finish`; a publication outcome
changes only the local record's publication fields.

### 3.4 Publication contract

- Publication is a separately authorized step per run: `publish` refuses without `--authority`, and the playbook
  obtains that authority from the user in the conversation for a destination the user selected
  (`CAP-DLV-weekly-report` §4, `ADR-mcp-runtime-and-shared-artifacts`). Invocation and `[maintenance.history]`
  settings grant none; the default publication outcome is `pending`.
- `publish` reads the branch head, uploads blobs, builds a tree on the head's tree, creates the commit with the head
  as parent and updates the ref without force. On a rejected update it re-reads the head, checks the record path by
  content and rebuilds, at most three attempts; then `HISTORY_PUBLISH_FAILED` with the retry action.
- The run ID in the record path is the idempotency key. Before any attempt and after a lost response, `publish`
  reads `runs/<playbook>/<run-id>/record.json` from the head: an identical digest resolves `published` without
  resending; a different digest is `HISTORY_RECORD_COLLISION` and never overwrites; absence permits the attempt.
  A lost response whose head cannot be read stays `unknown` with an `[ACTION]` to inspect.
- Failure classes map onto the existing outcomes: missing destination, authority or `gh` login is `pending`;
  authentication, permission, ruleset and collision failures are `failed`; a rate limit or `retry-after` is
  `HISTORY_PUBLISH_DEFERRED` (advisory `DEFER`) and leaves the outcome `pending`; a lost response is `unknown`.
  Every outcome is distinct from the run's own `outcome`.
- The commands never write the local index, refs, HEAD or working tree: `start` and `finish` use a temporary index
  file in the Git directory, and `publish` sends bytes only. Tests compare `git for-each-ref`, the index checksum and
  `git status --porcelain` before and after each command.

### 3.5 Playbook changes

Each of the four playbooks gains a run-record step at intake (`history start`), at completion (`history finish`)
and an optional publication step that names the destination and the user's authority. The weekly report's companion
record becomes this record; the drift playbook gains a run ID. The playbooks' review, decision and application
procedures do not change (`MS-maintenance-run-history` non-goals).

### 3.6 Verification

- Integration tests with an injected `gh` runner that models the Git Database endpoints in memory: initialization,
  foreign-branch refusal, multi-file publication, a no-finding run, a failed run, a duplicate retry, two interleaved
  writers, a lost response resolved by inspection, a collision, a rate-limited attempt and unchanged local Git
  state; `list` and `get` against the modelled branch. A PATH-shim `gh` covers missing or unauthenticated `gh`.
- Content tests keep each playbook self-contained and within budget.
- A live exercise against a throwaway repository, labelled as such, confirms the unverified API facts (exact error
  responses, repeated POST behaviour, same-sha ref update) before the capability states them.

### 3.7 Living Spec impact

- New: the delivery capability `maintenance-history` (its ID is assigned at spec-sync; the command family, record, branch layout and publication contract) and the
  use cases `record-a-maintenance-run` and `find-the-latest-maintenance-run` under `docs/usecases/governance/`.
- Changed: `CAP-DLV-weekly-report` (the companion record and publication clauses cite the new capability; the scope
  sentence names it as the separate history backend), `CAP-DLV-drift-reconciliation` (run ID),
  `CAP-DLV-review-refactor` and `CAP-DLV-performance-pass` (run record and publication steps), the glossary
  (`playbook run`, `run record`, `publication destination`, `source SHA`) and the `devkit_agt` feature edges in
  `.devkit/architecture.toml`.
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
- Publication authority: per run, explicit, with `pending` as the default outcome; the configured repository and
  branch are inputs. Open question `q3` offers the alternative of a standing opt-in, which needs a superseding ADR.
- Inspected-state identity: `PADR-inspected-state-identity`; `source_sha` stays a commit (open question `q4`).
- Record layout: run directories plus a per-playbook index file; a recursive tree walk and a search endpoint are
  rejected (`materials/planning-options.md` set 5).
- Outcome vocabulary: a common `outcome` field with three values and a playbook-specific `result` field, so the
  performance pass keeps its own values.
- Playbook coverage: all four maintenance playbooks (open question `q2`).
- Terminology: playbook run, run record, report, publication destination, source SHA; bare "artifact", "receipt"
  and "revision" are avoided for history objects.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr maintenance-history "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept maintenance-history --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff maintenance-history.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->
