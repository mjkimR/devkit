---
id: PROP-single-sync-readiness-gate
title: One readiness gate for a synchronized checkout
summary: "Makes devkit sync --check the single readiness gate of a synchronized checkout, since it detects every problem devkit status does and more, and documents devkit status as a diagnostic report."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/distribution/
priority: low                         # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/distribution/
    - docs/development/reference/distribution.md
    - packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/
    - packages/devkit-dist/src/devkit_dist/features/distribution/cli/selection.py
    - packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/playbooks/agent-asset-conversion/references/project-bundle.md
    - docs/usecases/delivery/UC-import-third-party-agent-assets.md
    - guides/
  excludes:
    - docs/decisions/
    - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-single-sync-readiness-gate] One readiness gate for a synchronized checkout

## 1. Background & Hypothesis

The devkit bundle's completion criterion requires both `devkit status` and `devkit sync --check` to exit 0. Their
problem catalogs overlap (`NOT_SYNCHRONIZED`, `SYNC_CONFLICT`, `WORKSPACE_UNSAFE`, `TRANSACTION_PENDING`,
`SELECTION_INVALID`), but separate implementations produce them (`get_project_status` and the sync planner). So each
new problem class is added, documented and tested twice. Source: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` C1-4.

## 2. Technical Spike Questions

- **Q1**: Which problems does each command detect that the other does not (measured on fixtures)?
  - **Answer**: [detection matrix](materials/detection-matrix.md). On 17 fixture scenarios, every problem that fails
    `status` also fails `sync --check`. `sync --check` alone fails four of them: a removed guidance block, a preset added
    to `config.toml` without a sync, `guidance_block = false` without a sync and a deleted receipt. By code it also
    fails an installed package content change, which `status` cannot see. `status` compares the disk with the receipt
    (what the last sync wrote); `sync --check` compares it with the desired state (what a sync would write now).
  - Where both fail, `sync --check` exits `2` with the planner's first refusal and `status` exits `1` with every
    problem listed. The overlap is smaller than the hypothesis assumed: `status` already reuses the planner's conflict,
    guidance-block, subagent and selection helpers; its own logic is the file-state classification and the report fields.
- **Q2**: Can `sync --check` be the single gate, with `status` kept as a diagnostic report?
  - **Answer**: yes. Requiring both adds no detection; requiring only `status`, as the in-repo bundle and project-bundle
    criteria do today, misses desired-state changes.

## 3. Proposed Design & Impact

### Decision

`devkit sync --check` exiting `0` is the one readiness criterion of a synchronized checkout. `devkit status` stays a
read-only diagnostic report of the installed state against the receipt: its JSON fields, its `errors`, its exit
codes and its detection logic are unchanged. It is the command to run when the gate fails or to read installed
facts (selection, file states, tool version, host hooks); it is not a readiness gate.

A new problem class therefore needs the planner (which the gate runs) and the reference; adding it to `status` is
an optional diagnostic, no longer a second gate to keep in step.

### Changes (Development)

1. **Contract**: `docs/capabilities/distribution/` states the readiness criterion: `sync --check` exit `0` is the
   gate for a synchronized checkout, and `devkit status` is a report that does not detect desired-state changes
   (a selection, configuration or installed-package change without a sync, a removed guidance block, a missing
   receipt). Development picks the CAP-DIST document that owns sync checking (`CAP-DIST-sync-and-transactions`
   already says "`sync --check` remains the general synchronization gate").
2. **Reference**: the `devkit status` section of `docs/development/reference/distribution.md` says the same in one
   sentence, replacing its closing "`sync --check` remains the check that says whether a sync is needed".
3. **Completion criteria** become "`uv run devkit sync --check` exits `0`" (with any other non-readiness condition
   they carry kept):
   - the devkit bundle's `consumption.md` Completion section (both commands → `sync --check` only);
   - the devkit bundle's `in-repo-bundle.md` "Done when" (`status` → `sync --check`);
   - devkit-adaptive's `agent-asset-conversion/references/project-bundle.md` Completion (`status` exits `0` → `sync --check`
     exits `0`; the fact that the bundle is selected is read from `devkit list` or the `status` selection, as a fact,
     not a gate);
   - Scenario 7 of `UC-import-third-party-agent-assets` (its Then clause).
4. **Guides**: `guides/INSTALL_GUIDE.md` Step 5 keeps `sync --check` as the verification and presents `status` as
   the diagnosis for a failed check; `guides/install/existing-repository.md` "Already installed" keeps `status` as a
   report and adds `sync --check` as the readiness check after `sync --locked`.
5. **CLI help**: the `devkit status` help (`cli/selection.py`) names `sync --check` as the readiness gate and drops
   "MCP registration still to set up" from its notices list, which contradicts the reference and
   `ADR-mcp-runtime-and-shared-artifacts` (general status emits no `MCP_REGISTRATION_PENDING`).

### Non-Goals

- No change to `status` or planner detection, codes, exit codes or JSON (`usecases/` is excluded).
- No routing of `status` through the planner: the planner raises its first refusal, so `status` would lose its
  listing of every problem at once, and the gate no longer depends on `status`.
- No change to `sync --check`'s exit `2` for a refusal (conflict, unsafe path, journal, invalid selection): a
  criterion of "exits `0`" already treats it as not ready.
- No new document kind, ADR or feature edge.

### Verification

- `just test-affected` for the help text change; CLI help snapshot tests are updated if they cover `status`.
- `uv run devkit rules check` on the changed documents and bundle assets, `uv run devkit bundle validate` for the
  two changed bundles, and a search showing no remaining "`devkit status` ... exit `0`" readiness criterion in
  bundles, guides or use cases.

## Planning decisions

- `sync --check` is the gate and `status` the report (Q1 and Q2 evidence). Recorded here, not as a PADR: it
  narrows how existing commands are documented and changes no command contract.
- The excluded `usecases/` path keeps detection code out of scope; the matrix shows no detection gap to close in
  the gate.
- `size` lowered from `M` to `S`: the change is documentation, bundle text and one help string.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr single-sync-readiness-gate "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept single-sync-readiness-gate --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff single-sync-readiness-gate.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
