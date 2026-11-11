---
id: SPEC-single-sync-readiness-gate
title: One readiness gate for a synchronized checkout
summary: "Makes devkit sync --check the single readiness gate of a synchronized checkout, since it detects every problem devkit status does and more, and documents devkit status as a diagnostic report."
status: completed
created: 2026-11-11
related_capabilities:
  - CAP-DIST-sync-and-transactions
related_usecases:
  - UC-import-third-party-agent-assets
workflow: sdd-spec-feature
---

# [SPEC-single-sync-readiness-gate] One readiness gate for a synchronized checkout

## 1. Problem Statement & Motivation

Handed off from proposal PROP-single-sync-readiness-gate.

- **Preserved Materials**: `docs/materials/2026-11/20261111-single-sync-readiness-gate`
- **Source**: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` C1-4.

The devkit bundle's completion criterion requires both `devkit status` and `devkit sync --check` to exit `0`, while
the in-repo bundle, the project-bundle conversion reference and Scenario 7 of `UC-import-third-party-agent-assets`
require only `devkit status`. The detection matrix of the preserved materials (17 measured fixture scenarios plus
code reading) shows that every problem that fails `status` also fails `sync --check`, and that `sync --check` alone
fails desired-state changes `status` cannot see: a removed guidance block, a preset or `guidance_block` change in
`config.toml` without a sync, a deleted receipt and an installed package content change. `status` compares the disk
with the receipt (what the last sync wrote); `sync --check` compares it with the desired state (what a sync would
write now). Requiring both adds no detection, and requiring only `status` misses desired-state changes.

This change documents `devkit sync --check` exiting `0` as the one readiness criterion of a synchronized checkout,
keeps `devkit status` as a read-only diagnostic report, and aligns every completion criterion, guide and the
`devkit status` help with that.

## 2. User Stories

- **US-1**: As an agent finishing installation or bundle work, I want one command whose exit `0` means the checkout
  is synchronized, so that I do not run two overlapping checks or pass a check that misses a desired-state change.
- **US-2**: As an agent whose readiness check failed, I want `devkit status` named as the report that lists every
  installed-state problem at once, so that I can diagnose without mistaking it for the gate.
- **US-3**: As a maintainer adding a problem class, I want the planner (which the gate runs) to be the one place it
  must be detected, so that `status` is an optional diagnostic rather than a second gate to keep in step.

## 3. Non-Goals

1. **Scope Excluded**: any change to `devkit status` or planner detection, error codes, exit codes or JSON fields;
   `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/` is not edited.
2. **Scope Excluded**: routing `devkit status` through the planner.
   - **Rationale**: the planner raises its first refusal, so `status` would lose its listing of every problem at once.
3. **Scope Excluded**: changing the exit `2` of `sync --check` for a refusal (conflict, unsafe path, pending journal,
   invalid selection); a criterion of "exits `0`" already treats it as not ready.
4. **Scope Excluded**: excluding planned optional MCP registration writes from `sync --check`.
   - **Rationale**: it would change the planner under the excluded `usecases/` path; the user decided that planned
     registration writes count as not ready.
5. **Scope Excluded**: `devkit.status_checks` warnings (gate-hook health) as part of readiness; they change no exit
   code and `devkit gate status` remains their check.
6. **Scope Excluded**: a new document kind, ADR or feature edge.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The capability states the readiness gate
- **Given** `CAP-DIST-sync-and-transactions`
- **When** a reader looks up what makes a checkout ready
- **Then** one section states that `uv run devkit sync --check` exiting `0` is the readiness criterion of a
  synchronized checkout, that `devkit status` is a read-only report of the installed state against the receipt that
  misses desired-state changes other than subagent projection and render environment changes (a preset,
  `guidance_block` or installed-package change without a sync, a removed guidance block, a missing receipt), and that planned optional MCP registration writes keep `sync --check`
  at exit `1` (`NOT_SYNCHRONIZED`) until `uv run devkit sync --registrations-only` or a plain sync applies them.

### [AC-02] The reference names the gate in the status section
- **Given** the `devkit status` section of `docs/development/reference/distribution.md`
- **When** it is read
- **Then** its closing sentence "`sync --check` remains the check that says whether a sync is needed" is replaced
  by one sentence naming `uv run devkit sync --check` exit `0` as the readiness gate and `devkit status` as the
  diagnostic report, and `rg -n "remains the check that says whether a sync is needed" docs/` finds no match.

### [AC-03] Completion criteria use the single gate
- **Given** the devkit bundle's `consumption.md` Completion section and `in-repo-bundle.md` "Done when", the
  adaptive-dev `agent-asset-conversion` playbook's `references/project-bundle.md` Completion, and Scenario 7 of
  `UC-import-third-party-agent-assets`
- **When** each criterion is read
- **Then** each names `uv run devkit sync --check` exits `0` as the readiness condition and keeps its other
  conditions (bundle validation, the selected bundle read as a fact, the constitution check), and
  `rg -n "devkit status.{0,60}exit" packages/*/src/*/bundles guides docs/usecases` finds no match.

### [AC-04] Guides present status as diagnosis
- **Given** `guides/INSTALL_GUIDE.md` Step 5 and `guides/install/existing-repository.md` "Already installed"
- **When** they are read
- **Then** Step 5 keeps `uv run devkit sync --check` as the verification with exit `0` meaning ready and presents
  `uv run devkit status` as the report to run when that check fails; "Already installed" keeps `status` as a report
  and lists `uv run devkit sync --check` as the readiness check after `uv run devkit sync --locked` and the optional
  `uv run devkit sync --registrations-only`, in the order `guides/install/mcp.md` uses.

### [AC-05] The status help names the gate and drops the MCP notice
- **Given** the `devkit status` command
- **When** `devkit status --help` runs
- **Then** it exits `0`, its text contains `sync --check` named as the readiness gate, and it no longer contains
  "MCP registration".

### [AC-06] Detection and outputs are unchanged
- **Given** the diff against the handoff commit
- **When** it is inspected and the affected tests run
- **Then** no file under `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/` changes, and
  `just test-dist` and `just test-affected` pass with the existing `status` and `sync --check` exit-code and JSON
  tests unchanged.

### [AC-07] Changed bundle assets stay valid and self-contained
- **Given** the changed devkit and adaptive-dev bundle sources
- **When** `uv run devkit bundle validate` runs on each bundle and `uv run devkit rules check --ci --base main` runs
- **Then** both exit `0`, and the changed bundle files cite no authoring-repository document ID.

## 5. Assumptions

- The readiness section is a new `### Readiness Gate` subsection of `CAP-DIST-sync-and-transactions` after
  "Locked Synchronization", since that capability already calls `sync --check` the general synchronization gate
  and owns locked restoration and the `--registrations-only` order it must reference.
- `guides/install/mcp.md` is the order reference and is not edited: its teammate block already orders
  `sync --locked` then `sync --registrations-only`.
- The help text test is added to the existing CLI contract test module of the distribution feature, beside the
  other `status` exit-code tests, rather than a new module.
