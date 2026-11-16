# Formal document inventory

Reader-question inventory for `SPEC-formal-document-coverage`, from four parallel scouts over the 18 capability areas,
architecture, reference and source (scout envelopes `scout-01` to `scout-04`). A candidate survives only when no
capability, architecture, reference, use case, glossary (`docs/steering/glossary.md`) or existing formal document
already answers its one reader question (`CAP-DOCS-documentation-ownership` §3.1, §3.3). Line numbers are evidence
at the Planning head, not contracts.

## Kept candidates

Folded after `challenger-01`: candidate "envelope-return timestamp ordering" moved to the dropped list (F1); every
kept candidate carries the writing condition its row names (F2-F7).

| # | Kind | ID | Area / path | Unit | One reader question |
| --- | --- | --- | --- | --- | --- |
| 1 | DESIGN | `DESIGN-workflow-stage-evaluation` | delivery, `docs/designs/delivery/` | A | On one sample Unit, in what order does `devkit workflow next` apply stage policy, exit checks, the gate, holds and return voiding, and why does it report only the first unmet stage? |
| 2 | OPS | `OPS-assignment-attention-routing` | flat, `docs/operations/` | A | An adaptive assignment `list` row carries an attention value: which evidence distinguishes the case, and which existing owner acts? |
| 3 | OPS | `OPS-host-hook-dispatch-routing` | flat, `docs/operations/` | B | A configured host hook shows no visible warning and no observation: which evidence separates invalid registration, an interrupted sync, a failed handler and what devkit cannot see, and which owner acts? |
| 4 | OPS | `OPS-mcp-runtime-refusals` | flat, `docs/operations/` | B | Some devkit MCP tools run while others refuse, or a registration is not active: which surface's evidence identifies the case, and which owner acts? |
| 5 | DOMAIN | `DOMAIN-override-lifecycle` | distribution, `docs/domain/distribution/` | C | After a project override is created, which capability state is it in (recorded, drifted, not deployed, retained, bundle mismatch, removed upstream), how does it differ from an `ORPHAN_LEFT` file, and which command or sync changes it? |
| 6 | OPS | `OPS-search-mode-and-model-routing` | flat, `docs/operations/` | C | Document search ran lexical-only or failed with a `SEARCH_*` model error: which evidence, including an explicit `--mode hybrid` run, selects the owner, and what output confirms the normal state? |

### 1. `DESIGN-workflow-stage-evaluation`

- Sources: `packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py` (`_Evaluator`, `_held_from`,
  `_waiting_for`, `evaluate_definition`, `current_envelopes`); `.../workflow/models/decision_records.py`;
  `CAP-DLV-workflow-orchestration` §1, §3; `CAP-DLV-workflow-envelopes` §4; `CAP-DLV-human-interaction` §5.
- Must not duplicate: `CAP-DLV-workflow-orchestration`, `CAP-DLV-workflow-envelopes`, `CAP-DLV-human-interaction` §5
  (return voiding and timestamp precision, lines 101 and 113), `CAP-DLV-cli-and-output` (sentinels),
  `docs/development/reference/workflow.md`.
- Condition: a worked example over one sample Unit state showing evaluation order; it cites the capability for every
  rule and states no MUST. It absorbs the return-voiding example as one step, citing `CAP-DLV-human-interaction` §5.
- Why kept while the DOMAIN stage-passing comparison is dropped (F2): that DOMAIN would restate the list of gate
  sources `CAP-DLV-human-interaction` §5 already gives; no owner shows the order in which `next` combines them on a
  concrete Unit, which is the DESIGN worked-example role (`CAP-DOCS-documentation-ownership` §3.1).

### 2. `OPS-assignment-attention-routing`

- Sources: `CAP-DLV-adaptive-assignments` §4 (`list`, attention values, `return`, `verify`, `close`);
  `packages/devkit-adaptive/src/devkit_adaptive/features/assignment/services/verification.py`; adaptive-dev references
  `current-context.md` and `delegation.md` under `packages/devkit-adaptive/src/devkit_adaptive/bundles/`.
- Must not duplicate: `CAP-DLV-adaptive-assignments`, `CAP-WT-task-worktrees`, `ADR-adaptive-assignment-commands`.
- Gap evidence: the five values are defined (`CAP-DLV-adaptive-assignments` §4) and guidance lists actions, but no
  owner maps a value to its evidence and owner.
- Condition (F7): each row routes a value to its evidence (`verify` base/head checks, `show`, worktree state) and owner;
  the choice among actions stays with `current-context.md`; no row prescribes an action.
- Normal state: JSON `attention: []` (`CAP-DLV-adaptive-assignments` §4), text `attention=-`.

### 3. `OPS-host-hook-dispatch-routing`

- Sources: `CAP-HOST-lifecycle-observation` §1, §3-§5; `docs/development/reference/host.md`;
  `packages/devkit-dist/src/devkit_dist/features/host/usecases/status.py`, `.../host/services/observation.py`,
  `.../host/usecases/runner.py` (a sync journal makes dispatch fail with `HOST_HOOK_DISPATCH_FAILED`).
- Must not duplicate: `CAP-HOST-lifecycle-observation`, `OPS-distribution-sync`, `CAP-DIST-sync-and-transactions`,
  the `host.md` code table.
- Gap evidence (F3): failures warn on stderr by contract (`CAP-HOST-lifecycle-observation` §4), but whether the host
  shows that warning is host-defined; no owner routes "no visible warning and no observation" through `host status`
  validity and last `received_at`.
- Condition: trust and PATH form one row whose evidence is "devkit reports `unknown`" and whose owner is the host;
  `HOST_HOOK_DISPATCH_FAILED` routes to the `host.md` row by reference.

### 4. `OPS-mcp-runtime-refusals`

- Sources: `CAP-MCP-runtime-registration` (Runtime and Registration contracts, `mcp status`);
  `docs/development/reference/host.md` MCP rows; `packages/devkit-mcp/src/devkit_mcp/features/runtime/`;
  `packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py` (runtime field).
- Must not duplicate: `CAP-MCP-runtime-registration`, `ADR-mcp-runtime-and-shared-artifacts`,
  `CAP-DIST-sync-and-transactions`, `OPS-distribution-sync`, the `host.md` code rows.
- Condition (F4): rows only for symptoms that cross the tool-call payload, sync/setup notice and `mcp status` runtime
  field (for example read-only tools running while mutating tools refuse); the next owner is "`host.md` MCP row for
  `<CODE>`" or a capability ID, never action text. Kept separate from item 3: different symptom and capability owner.

### 5. `DOMAIN-override-lifecycle`

- Sources: `CAP-DIST-workspace-ownership` §3 (create, receipt record, drift, not deployed, `remove`, bundle mismatch,
  reconciliation, removed upstream; `ORPHAN_LEFT`); `CAP-DIST-sync-and-transactions` §1 (receipt);
  `docs/development/reference/distribution.md`;
  `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/override_commands.py`.
- Must not duplicate: `CAP-DIST-workspace-ownership`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-agent-projections`,
  `DOMAIN-bundle-selection-and-installation`, glossary "Project override".
- Condition (F5): use the capability's own states and codes; coin no state name ("orphaned" is forbidden: it means an
  undesired owned file); "reconciled" is a command outcome, not a state; definitions point to the glossary.

### 6. `OPS-search-mode-and-model-routing`

- Sources: `CAP-SRCH-document-search` §2, §5; `CAP-DOCS-document-search` §3 rule 5, §4.2;
  `docs/development/reference/search.md`; `packages/devkit-dist/src/devkit_dist/features/search/services/index.py`,
  `.../search/models/errors.py`.
- Must not duplicate: `CAP-SRCH-document-search`, `CAP-DOCS-document-search`, the reference error rows, advisory FIX text.
- Condition (F6): the discriminating row is an explicit `--mode hybrid` run (auto falls back silently); without it the
  table repeats `CAP-SRCH-document-search` §2 and the document is dropped. Normal state: `[SEARCH: ... mode=hybrid]`
  (`CAP-DOCS-document-search` §4.2).

## Dropped candidates

| Candidate | Already answered by |
| --- | --- |
| DESIGN envelope-return timestamp ordering (F1) | `CAP-DLV-human-interaction` §5 (precision and same-second voiding), `CAP-DLV-workflow-envelopes` §1-§2 |
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

| Area (OPS: topic) | DESIGN | DOMAIN | OPS | Unit |
| --- | --- | --- | --- | --- |
| delivery | 1 | 0 | 1 | A |
| host | 0 | 0 | 1 | B |
| mcp | 0 | 0 | 1 | B |
| distribution | 0 | 1 | 0 | C |
| search | 0 | 0 | 1 | C |
| other 13 areas | 0 | 0 | 0 | - |
| Total (6) | 1 | 1 | 4 | |
