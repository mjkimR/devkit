---
id: SPEC-consolidation-terminology
title: Rename record compaction to consolidation
summary: Rename the record-merging term compaction to consolidation across the spec bundle playbooks, feedback records, ADR wording and Living Spec, keeping the old playbook and record IDs as aliases, so the term no longer collides with the everyday sense of shortening.
status: completed
created: 2026-11-04
related_capabilities:
  - CAP-HARN-agent-guidance
  - CAP-DOCS-document-model
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-consolidation-terminology] Rename record compaction to consolidation

## 1. Problem Statement & Motivation

devkit uses "compaction" for merging related records into one (`adr-compaction` and `feedback-compaction`
playbooks, `FB-compacted-<area>-<status>` records, `ADR-decision-ledger` and `ADR-feedback-lifecycle-ledger`). In
everyday use, and in the user's language, "compaction" (압축) means shortening. The same word also names two
unrelated devkit concepts, `Compact output` (`devkit run`) and the `compact` subagent level. An agent that reads the
user's everyday word mapped it to the record-merging playbooks and gave the opposite advice (a file-length question
answered as an ADR-merge question). The user decided to replace the record-merging term with "consolidation", which
names what the playbooks do (consolidate related records) and does not collide with shortening.

## 2. User Stories

- **US-1**: As a user, I want the playbooks and records that merge ADRs and feedback to be called consolidation, so
  that "compaction" keeps its everyday meaning in conversation and documents.
- **US-2**: As a consumer of the `spec` bundle, I want `spec/adr-compaction`, `spec/feedback-compaction` and every
  `FB-compacted-...` ID to keep resolving, so that installed guidance, memories and references do not break.

## 3. Non-Goals

1. **Scope Excluded**: the other senses of the word: `Compact output` and `devkit_agt.features.compact` (`devkit
   run`), `compact_dict`, the `compact` subagent level, "compact" as an ordinary adjective (a compact Y-statement,
   compact JSON), and "context compaction" of an agent's conversation.
2. **Scope Excluded**: retired alias IDs (ADR-adr-compaction, ADR-group-compaction-by-topic,
   ADR-closed-feedback-compacts-into-per-area-records-with-aliases, feedback aliases) stay as written; aliases are
   history, not current names.
3. **Scope Excluded**: completed spec bundles, their envelopes and `docs/materials/` keep their wording (history).
4. **Scope Excluded**: any change to what the playbooks do; wording and identifiers only.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The playbooks are named consolidation and keep their old IDs as aliases
- **Given** the `spec` bundle after the change
- **When** `uv run devkit playbook get spec/adr-consolidation`, `spec/feedback-consolidation`, `spec/adr-compaction`
  and `spec/feedback-compaction` run
- **Then** each exits 0; the first two are the asset IDs (`bundle.toml`, frontmatter `name`) and the last two resolve
  through the playbooks' `aliases`; `uv run devkit playbook search "consolidate ADRs"` lists `adr-consolidation`

### [AC-02] Playbook bodies and bundle guidance use the new term
- **Given** the `spec` bundle sources
- **When** `rg -n -i 'compaction|compacted|compact record' packages/devkit-spec/src/devkit_spec/bundles` runs
- **Then** it reports nothing; the renamed playbooks describe consolidation, the record naming contract is
  `FB-consolidated-<area>-<status>` and `specs/<YYYY-MM>/feedback/<YYYYMMDD>-consolidated-<area>-<status>.md`, and
  the `spec` bundle tests (`just test devkit-spec bundles`) pass with their renamed test module

### [AC-03] Feedback records are renamed with their old IDs as aliases
- **Given** the 25 `FB-compacted-<area>-<status>` records under `specs/*/feedback/`
- **When** `uv run devkit docs resolve FB-compacted-delivery-promoted` and `uv run devkit docs list feedback --history
  --all-namespaces -n 0` run
- **Then** the resolve prints the FB-consolidated-delivery-promoted record with `alias=FB-compacted-delivery-promoted`;
  the listing shows no FB-compacted- ID as a document ID; every record keeps its status, entries and prior aliases;
  `uv run devkit rules check` exits 0 after `devkit rules fix` rewrote references in current documents

### [AC-04] Living Spec and ADR wording use the new term, decisions unchanged
- **Given** `docs/` after the change
- **When** `rg -n -i 'compaction|compacted|compacts\b' docs/capabilities docs/steering docs/decisions docs/usecases
  docs/architecture docs/development docs/proposals docs/roadmap` runs
- **Then** the only hits are retired alias IDs in `aliases:` lists, `proposal:` fields naming historical spec IDs and
  quoted historical option names; `ADR-feedback-lifecycle-ledger` and `ADR-decision-ledger` keep every clause with
  the term replaced; the glossary defines **Consolidation** as merging related records into one with aliases, distinct
  from Compact output; a new ADR records the rename with its reason

### [AC-05] Other senses untouched
- **Given** the change's diff
- **When** `git diff --name-only <base> HEAD` runs
- **Then** it lists no file under `packages/devkit/src/devkit_agt/features/compact/`, `docs/capabilities/compact/`,
  `docs/development/reference/compact.md`, no subagent contract and no `docs/materials/` or completed spec bundle
  except this unit; `rg -n 'level: compact' packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/scout.md`
  still matches

### [AC-06] Managed copies and receipt regenerated
- **Given** the committed head
- **When** `uv run devkit sync --check` and `uv run devkit generated check` run
- **Then** both exit 0, and `uv run devkit rules check --ci --base <base>` reports errors=0

## Assumptions

- The `name` frontmatter field of a playbook is its asset ID, and `aliases` in that frontmatter are previous IDs
  resolved by `devkit playbook get` (`ADR-playbook-retrieval`).
- The feedback record file name sets the ID, so each record file is renamed with its ID.
- Editing the two ledger ADRs' titles and wording changes no decision (a permitted wording edit); the new ADR is the
  record of the rename decision and supersedes nothing.
