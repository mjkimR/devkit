---
id: CAP-DLV-maintenance-history
title: Maintenance run history
summary: "Captures immutable maintenance evidence and publishes authorized atomic history commits on a dedicated GitHub branch, with inspected retries and append-only integration amendments."
area: delivery
status: draft
usecases:
  - UC-record-a-maintenance-run
  - UC-find-the-latest-maintenance-run
---

# [CAP-DLV-maintenance-history] Maintenance run history

## 1. Summary

The devkit-agt command family identifies inspected content, freezes run evidence and keeps durable history apart from code history. `ADR-history-branch-publication` and `ADR-inspected-state-identity` record the design. The injected Git Database model verifies local behavior; the labelled live exercise of `SPEC-maintenance-history` remains pending explicit destination authority.

## 2. Scope & Boundary

- **In-Scope**: local run capture, evidence freezing, dedicated history initialization, atomic publication, amendments and retrieval for four maintenance playbooks.
- **Out-of-Scope**: scheduling and GitHub authentication (external systems), code integration (`CAP-DLV-delivery-workflows`), shared artifacts (`CAP-COLL-shared-artifacts`), retention cleanup and a web viewer.

## 3. Business Rules & Policies

1. **Inspected identity**: WHEN a run starts, the service MUST record HEAD, dirty paths, a temporary-index content tree and a retained dirty diff SHA-256, excluding the fixed run/report paths. Tests: `packages/devkit/tests/unit/features/maintenance_history/test_runs.py`.
2. **Local Git preservation**: the service MUST leave the real index, HEAD, refs and working tree outside the run directory unchanged, with loose snapshot objects accepted. Tests: `packages/devkit/tests/unit/features/maintenance_history/test_runs.py`.
3. **Frozen evidence**: WHEN finish succeeds, the service MUST freeze report and registered file digests after secret-checking their bytes and the record independently of project exclusions. Tests: `packages/devkit/tests/unit/features/maintenance_history/test_runs.py`.
4. **Authority**: WHEN init, publish or update lacks explicit authority, the service MUST refuse with `HISTORY_AUTHORITY_MISSING`; configuration supplies destination inputs only. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_cli.py`.
5. **Dedicated root**: IF a branch does not descend from the frozen root, THEN the service MUST refuse `HISTORY_BRANCH_FOREIGN` without updating it. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_publication.py`.
6. **Atomic publication**: WHEN a run is published, the service MUST make selected files, its canonical record and year-index line visible through one non-forced ref update. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_publication.py`.
7. **Inspected retries**: WHEN the canonical remote bytes match, the service MUST resolve the original publication without resending; different bytes are `HISTORY_RECORD_COLLISION`. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_publication.py`.
8. **Concurrent writers**: WHEN another writer advances the head, the service MUST rebuild on that head for at most three attempts, preserving prior history and deferring exhaustion. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_publication.py`.
9. **Outcome separation**: the service MUST keep run outcome (completed, failed, interrupted) distinct from local publication state (pending, published, failed, unknown). Tests: `packages/devkit/tests/integration/features/maintenance_history/test_publication.py`.
10. **Amendments**: WHEN integration state changes after publication, the service MUST append a retry-stable amendment and index line without editing published evidence. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_publication.py`.
11. **Empty history**: WHEN the branch is absent, list MUST return zero with a notice while get returns `HISTORY_RUN_MISSING`. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_publication.py`.
12. **Agent output**: commands MUST follow `ARCH-08-1-agent-output`: sentinel facts or one JSON result, with the shared CLI boundary handling errors. Tests: `packages/devkit/tests/integration/features/maintenance_history/test_cli.py`.

## 4. Interfaces & Data Contracts

Commands are under `devkit maintenance history`; each accepts `--workspace-root` and `--format json`.

| Command | Input and result |
| --- | --- |
| `init` | `--authority`, optional repository/branch; HISTORY_BRANCH_READY with root/head SHA and authority; no local file |
| `start` | `--playbook`, `--scope`, `--into`, `--report`; optional IANA `--timezone`, repeated `--prior-run`, `--supersedes`; HISTORY_RUN_STARTED |
| `finish` | `--run`, `--outcome`; optional `--result`, fixed `--report`, repeated `--file`, `--applied-commit`, `--follow-up`; HISTORY_RUN_FINISHED |
| `publish` | `--run`, `--authority`, optional repository/branch and repeated `--file` selecting frozen files; HISTORY_PUBLISHED |
| `update` | `--run`, `--authority`, `--integration-state`, optional repeated `--applied-commit`; HISTORY_RUN_UPDATED |
| `list` | `--playbook`, optional `--source-sha`, `--outcome`, `--include-superseded`, positive `--limit` (20); HISTORY_LIST and HISTORY_RUN |
| `get` | `--run-id`, optional `--file` (record.json); HISTORY_FILE with base64 content preserving arbitrary bytes |

Destination defaults: `[maintenance.history] repository`, else credential-free GitHub origin; branch defaults to `[maintenance.history] branch`, else maintenance-history. These values grant no publication authority.

`finish --file evidence.txt` registers added evidence and freezes its digest. `publish --file evidence.txt` selects it; without file arguments only record/report are published. Unregistered selections fail before network mutation. Changed frozen evidence is HISTORY_EVIDENCE_CHANGED and needs a new run.

A run ID is `<playbook>-<YYYYMMDDTHHMMSSZ>-<8 hex>`. Local record.json contains identity, inspected state, frozen evidence, outcome and publication metadata; dirty content also retains inspected.diff. Canonical JSON has sorted keys, compact UTF-8 and a final newline. The published record excludes destination, authority, attempts, publication, history_commit, updates and published_files. The local authority identifies the authorizing person; history commits use a fixed devkit identity.

Remote files are runs/<playbook>/<run-id>/record.json, report.md, selected files and updates/<UTC time>-<8 hex>.json, plus index/<playbook>/<run-ID year>.jsonl. Index lines include kind, run_id, source_sha, inspected_tree, outcome, result, finished_at, supersedes and path. Update lines add updated_at and integration_state. List merges the greatest update time per run (file order breaks ties), skips superseded runs by default and reads complete year shards newest-first until its limit is met.

The frozen root is `96eb369a841a26ca7094eb2bea25bbf8ccb5d95a`. Its README bytes, devkit maintenance history <maintenance-history@devkit.invalid> identity, 2000-01-01T00:00:00Z date and message are defined in `packages/devkit/src/devkit_agt/features/maintenance_history/models/records.py` and frozen by `ADR-history-branch-publication`.

## 5. Failure Contract

| Code | Exit | Meaning and action |
| --- | --- | --- |
| HISTORY_AUTHORITY_MISSING, HISTORY_INPUT_INVALID, HISTORY_REPORT_MISMATCH, HISTORY_SNAPSHOT_FAILED | 2 | Correct input; snapshot failure creates no run record |
| HISTORY_BRANCH_FOREIGN, HISTORY_REPOSITORY_EMPTY | 2 | Choose a valid branch or initialize the repository first |
| HISTORY_BRANCH_MISSING | 2 for publish/update | Publication pending; request separate initialization authority |
| HISTORY_GH_UNAVAILABLE | 2 | Install or authenticate gh; pending |
| HISTORY_DEFERRED | 1 | Rate limit, race exhaustion, temporary read/object failure; retry_after and pending |
| HISTORY_PUBLISH_FAILED, HISTORY_RECORD_COLLISION | 1 | Permission/destination/ruleset failure or immutable collision; failed |
| HISTORY_PUBLISH_UNKNOWN | 1 | Ref-update outcome cannot be confirmed; inspect before retry |
| HISTORY_SECRET_FOUND, HISTORY_EVIDENCE_CHANGED, HISTORY_RUN_MISSING | 1 | Remove secret, create a run for changed bytes, or check run ID |
| HISTORY_RUN_DRIFTED | 0 (strict: 1) | Source SHA or inspected tree changed; revalidate evidence |

Rate limits are checked before status mapping on every request: 429, or 403 with Retry-After or zero remaining. Other repository 401/403/404 responses fail; a missing ref at a readable repository stays pending. Root comparison accepts identical/ahead and rejects other/404 results. Error message text is never parsed. Read/object timeouts defer; lost ref-update responses become unknown.
