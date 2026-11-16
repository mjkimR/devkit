# Formal document inventory

Reader-question inventory for `PROP-formal-document-coverage`, from four parallel scouts over the 18 capability areas,
architecture, reference and source (scout envelopes `scout-01` to `scout-04`). A candidate survives only when no
capability, architecture, reference, use case, glossary (`docs/steering/glossary.md`) or existing formal document
already answers its one reader question (`CAP-DOCS-documentation-ownership` §3.1, §3.3). Line numbers are evidence
at the Planning head, not contracts.

## Kept candidates

| # | Kind | ID | Area / path | One reader question |
| --- | --- | --- | --- | --- |
| 1 | DESIGN | `DESIGN-envelope-return-timestamp-ordering` | delivery, `docs/designs/delivery/` | Why is an envelope stamped in the same second as a return voided, and when does a return reopen an earlier round? |
| 2 | DESIGN | `DESIGN-workflow-stage-evaluation` | delivery, `docs/designs/delivery/` | For one Unit's records, which stage does `devkit workflow next` report, and why are later stages' checks, approvals and holds not shown? |
| 3 | OPS | `OPS-assignment-attention-routing` | flat, `docs/operations/` | An adaptive assignment `list` row carries an attention value: which evidence distinguishes the case, and which existing owner acts? |
| 4 | OPS | `OPS-host-hook-dispatch-routing` | flat, `docs/operations/` | A configured host hook shows no observation or visible effect: which evidence separates not registered, invalid, sync interrupted, not trusted or not on PATH, handler failed and not dispatched, and which owner acts? |
| 5 | OPS | `OPS-mcp-runtime-refusals` | flat, `docs/operations/` | A devkit MCP tool refuses a call or a registration is not active: which symptom is it, which owner acts, and what observation shows the normal state? |
| 6 | OPS | `OPS-search-mode-and-model-routing` | flat, `docs/operations/` | Document search returned lexical-only results or failed with a `SEARCH_*` model error: which evidence selects the owner, and what output confirms the normal state? |
| 7 | DOMAIN | `DOMAIN-override-lifecycle` | distribution, `docs/domain/distribution/` | Which state is a project override in (tracked, drifted, reconciled, removed, retained, orphaned), and which command or sync moves it? |

### 1. `DESIGN-envelope-return-timestamp-ordering`

- Sources: `packages/devkit/src/devkit_agt/features/workflow/models/decision_records.py` (`Instant`, `record_instant`,
  `returns_end`), `.../workflow/services/envelope/authoring.py` (`envelope_timestamp`), `.../workflow/usecases/evaluate.py`
  (`current_envelopes`, `_after_returns`); `CAP-DLV-workflow-envelopes`, `CAP-DLV-human-interaction` §5.
- Must not duplicate: `CAP-DLV-human-interaction` §5 (return voids approvals), `CAP-DLV-workflow-envelopes` (rounds,
  authoring), `docs/development/reference/workflow.md` (library usage).
- Gap evidence: no document states the timestamp-precision rule; only source docstrings do. The worked example must be
  checked against a test or the source before quoting.

### 2. `DESIGN-workflow-stage-evaluation`

- Sources: `.../workflow/usecases/evaluate.py` (`_Evaluator`, `_held_from`, `_waiting_for`, `evaluate_definition`);
  `CAP-DLV-workflow-orchestration` §1, §3; `CAP-DLV-workflow-envelopes` §4.
- Must not duplicate: `CAP-DLV-workflow-orchestration`, `CAP-DLV-workflow-envelopes`, `CAP-DLV-human-interaction` §5,
  `CAP-DLV-cli-and-output` (sentinels), `docs/development/reference/workflow.md`.
- Condition: a worked example over a sample Unit state that cites the capability for every rule and states no MUST.

### 3. `OPS-assignment-attention-routing`

- Sources: `CAP-DLV-adaptive-assignments` §4 (`list`, attention values, `return`, `verify`, `close`); adaptive-dev
  references `current-context.md` and `delegation.md` under `packages/devkit-adaptive/src/devkit_adaptive/bundles/`.
- Must not duplicate: `CAP-DLV-adaptive-assignments`, `CAP-WT-task-worktrees`, `ADR-adaptive-assignment-commands`.
- Gap evidence: guidance says to inspect attention but maps no value to an owner.
- Check before writing: the empty-attention encoding in `list` JSON (normal-state observation).

### 4. `OPS-host-hook-dispatch-routing`

- Sources: `CAP-HOST-lifecycle-observation` §1, §3-§5; `docs/development/reference/host.md`;
  `packages/devkit-dist/src/devkit_dist/features/host/usecases/status.py`, `.../host/services/observation.py`,
  `.../host/usecases/runner.py` (no dispatch while a sync journal exists).
- Must not duplicate: `CAP-HOST-lifecycle-observation`, `OPS-distribution-sync`, `CAP-DIST-sync-and-transactions`,
  the `host.md` code table.
- Gap evidence: dispatch failures are silent to the host conversation by contract; the reference is keyed by emitted
  codes and has no row for silent dispatch.

### 5. `OPS-mcp-runtime-refusals`

- Sources: `CAP-MCP-runtime-registration` (Runtime and Registration contracts); `docs/development/reference/host.md`
  MCP rows; `packages/devkit-mcp/src/devkit_mcp/features/runtime/` (`usecases/loaded_code.py`, `mcp/server.py`,
  `cli/output.py`); `packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py` (runtime field).
- Must not duplicate: `CAP-MCP-runtime-registration`, `ADR-mcp-runtime-and-shared-artifacts`,
  `CAP-DIST-sync-and-transactions`, `OPS-distribution-sync`, the `host.md` code rows.
- Condition: rows stay discriminators across the three surfaces (tool-call payload, sync/setup notice, `status`
  runtime field) and point to owners; no recovery text is copied.

### 6. `OPS-search-mode-and-model-routing`

- Sources: `CAP-SRCH-document-search` §2, §5; `CAP-DOCS-document-search` §4.2;
  `docs/development/reference/search.md`; `packages/devkit-dist/src/devkit_dist/features/search/models/errors.py`,
  `.../search/services/index.py`; `justfile` `model-build`.
- Must not duplicate: `CAP-SRCH-document-search`, `CAP-DOCS-document-search`, the reference error rows, advisory FIX text.
- Check before writing: the `SEARCH_MODEL_INVALID` message and the editable-install case.

### 7. `DOMAIN-override-lifecycle`

- Sources: `CAP-DIST-workspace-ownership` §3 (create, drift, reconciliation); `CAP-DIST-sync-and-transactions` §1
  (receipt); `docs/development/reference/distribution.md`; `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/override_commands.py`.
- Must not duplicate: `CAP-DIST-workspace-ownership`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-agent-projections`,
  `DOMAIN-bundle-selection-and-installation`, glossary "Project override".

## Dropped candidates

| Candidate | Already answered by |
| --- | --- |
| DOMAIN stage-passing records (approval, `--given`, policy, hold) | `CAP-DLV-human-interaction` §5, `CAP-DLV-workflow-envelopes` §4, `CAP-DLV-workflow-orchestration` §3, `ARCH-04-2-delivery-policy` §7 |
| OPS stuck Unit (`BLOCKED`, `PENDING_QUESTION`, waiting gate, stale approval) | spec-next `workflow-signals` reference, spec `worker-records` reference, `CAP-DLV-cli-and-output` |
| OPS/DESIGN envelope commit (`ENVELOPE_COMMIT_*`) | `CAP-DLV-workflow-envelopes` §5, `ADR-explicit-envelope-commits` |
| DOMAIN/DESIGN adaptive assignment lifecycle | `CAP-DLV-adaptive-assignments` §3-§4, `ADR-adaptive-assignment-ledger-storage`, `ADR-adaptive-assignment-commands` |
| DESIGN proposal handoff mechanics | `CAP-DLV-proposal-lifecycle` §4.1, `ADR-proposal-handoff`, `DOMAIN-delivery-relationships` |
| DOMAIN Unit/segment/gate terms | glossary, `ARCH-04-delivery-strategy` §3 |
| DESIGN override drift digest | `CAP-DIST-workspace-ownership` §3 |
| DESIGN/DOMAIN in-repo bundles and source snapshots | `CAP-DIST-in-repo-bundles` §1, §8 |
| DESIGN agent projection mapping | `CAP-DIST-agent-projections` §1-§2 |
| OPS playbook retrieval refusals / DOMAIN playbook identity | `CAP-DIST-context-and-playbooks` §4 |
| OPS override advisories | `CAP-DIST-workspace-ownership` §3 advisories (state question goes to candidate 7) |
| DOMAIN document identity, aliases, namespaces, supersession | `CAP-DOCS-document-model` §3.1-§3.5, `CAP-DOCS-namespaces` §3, `CAP-DOCS-document-lookup` |
| DESIGN index and reference building | `CAP-DOCS-document-model` §3.3-§3.4 |
| DESIGN/DOMAIN/OPS traceability derive and liveness | `CAP-TRACE-code-entrypoints` §3.1-§3.7, §4.2 |
| OPS generated merge conflicts / DESIGN resolve pipeline | `CAP-GEN-tracked-artifacts` §2, §5, §7; reference `generated.md` |
| DESIGN hybrid search ranking / model build | `CAP-SRCH-document-search` §2-§5 |
| governance DOMAIN enforcement levers / DESIGN change-scoped evaluation / OPS rule failures | `CAP-GOV-evaluation-lifecycle` §4-§6; reference `rules.md`, `gate.md` |
| gate DESIGN dispatcher / OPS commit refused | `CAP-GATE-commit-gates` §3-§4; reference `gate.md` |
| harness DOMAIN run vs cleanup / DESIGN supervisor / OPS unknown status | `CAP-HARN-isolated-execution` §3-§4, `ARCH-05-2-components`, `ADR-isolated-test-runs`; reference `exec.md` |
| harness command mount / guidance kinds | `CAP-HARN-command-mount` §4; `ARCH-08-2-resource-taxonomy` |
| worktree DOMAIN checkout kinds, finish vs integrate vs discard / OPS partial finish | `CAP-WT-task-worktrees` §1, §3-§4, `ADR-worktrees-and-scope`; reference `worktree.md` |
| compact DESIGN bounded view | `CAP-CMP-bounded-execution` §3-§4; reference `compact.md` |
| collaboration OPS stale scope / DOMAIN scope record vs observation / DOMAIN shared artifacts | `CAP-COLL-work-scope-registry` §1, §3-§4, `UC-run-parallel-work-safely`; `CAP-COLL-shared-artifacts`; reference `shared.md` |
| host DOMAIN hook states | folded into candidate 4 |
| mcp DESIGN loaded-code baseline / DOMAIN runtime identities | `CAP-MCP-runtime-registration`, `ADR-mcp-runtime-and-shared-artifacts`, `ARCH-05-2-components` |
| integration DOMAIN lifecycle states / OPS partial results | `CAP-INT-mcp-services` §3, partial results and recovery |
| cli DESIGN boundary and exit helpers | `CAP-CLI-agent-cli-toolkit` §3-§4, `ARCH-08-1-agent-output` §5, `devkit-cli` README |
| advisory DESIGN library / DOMAIN level vs mode / DESIGN unique-code cache | `CAP-ADV-agent-advisory-protocol` §2-§10; reference `advisory.md` |
| viewer DESIGN dashboard / planning source / formal identity / reading surfaces | `CAP-VIEW-repository-viewer` §2-§4; reference `viewer.md`; viewer UX and use cases |

## Count per kind and area

| Area | DESIGN | DOMAIN | OPS (flat; topic area) |
| --- | --- | --- | --- |
| delivery | 2 | 0 | 1 |
| distribution | 0 | 1 | 0 |
| host | 0 | 0 | 1 |
| mcp | 0 | 0 | 1 |
| search | 0 | 0 | 1 |
| other 13 areas | 0 | 0 | 0 |
| Total (7) | 2 | 1 | 4 |
