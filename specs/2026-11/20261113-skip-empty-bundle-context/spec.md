---
id: SPEC-skip-empty-bundle-context
title: Skip Context Loading for Bundles Without Context Sources
summary: Skip automatic get-context calls for bundles without declared context sources. Keep required loading for constitutions, selected instructions and declared context documents consistent across guidance, skills and playbooks.
status: completed
created: 2026-11-13
related_capabilities: [CAP-DIST-context-and-playbooks, CAP-DIST-workspace-ownership, CAP-DIST-agent-projections]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-skip-empty-bundle-context] Skip Context Loading for Bundles Without Context Sources

## 1. Problem Statement & Motivation

Generated guidance currently requires empty context loads and omits skill prerequisites for document-only bundles.
Use declared synchronized sources consistently across the three entry paths.

## 2. User Stories

- **US-1**: As an agent, I can decide whether bundle context is required from generated guidance or playbook metadata without probing.

## 3. Non-Goals

- **Scope Excluded**: Combined contexts, context dependencies, persistent loading state and new commands.
- **Scope Excluded**: Changes to bundle-authored explicit context instructions, nonempty context pruning and asset moves.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] No sources

- **Given** a synchronized bundle without a constitution, selected instructions or declared
  context documents
- **When** an agent follows generated root guidance and a deployed skill
- **Then** neither requires a
  `get-context` call for that bundle.
### [AC-02] Playbook without sources

- **Given** a playbook in such a bundle
- **When** it is retrieved by exact ID or a
  declared alias
- **Then** retrieval metadata and the generated execution instructions permit proceeding without a
  context call. Retrieval still validates the playbook and grants no execution authority.
### [AC-03] Required sources

- **Given** a constitution-only, selected-instruction-only or document-only bundle
- **When**
  its assets are used
- **Then** guidance, skill prerequisites and playbook metadata retain the loading requirement.
  Include a constitution template and an instruction template in this coverage.
### [AC-04] Runtime document listings

- **Given** a document-only bundle whose declared directory is absent or empty,
  when guidance is generated
- **Then** it still requires context loading. Documents or provider results available at
  execution time remain discoverable without a new sync.
### [AC-05] Mixed selection and refresh

- **Given** bundles with and without sources
- **When** sync generates guidance,
  then only the bundles with sources require loading. Selecting or deselecting an instruction-only preset and
  syncing updates that requirement consistently across generated entry paths.
### [AC-06] Explicit inspection

- **Given** a synchronized bundle without sources
- **When** the user explicitly runs
  `uv run devkit get-context <bundle>`
- **Then** the command retains its existing successful empty JSON result. Missing
  or unsynchronized bundles retain their existing errors.
### [AC-07] No discovery call

- **Given** any selection above
- **When** the agent decides whether to load context
- **Then**
  generated guidance or returned playbook metadata supplies the decision without another inspection command.


## 5. Approved Implementation Choices


#### Q1 — Additive playbook metadata

Add boolean `context.required` to `playbook get` output. Retain `context.bundle`, `context.argv` and
`context.policy` with their existing values, including `once-per-agent-context` for policy. Policy describes reuse
when a load is required; `required` determines whether the generated procedure calls the argv. For a bundle
without sources, return `required: false` while retaining the executable argv for explicit inspection. For a bundle
with sources, return `required: true`. Exact IDs and aliases return the same requirement.

Existing consumers that ignore the additive field retain their previous behavior and may issue an empty load.
Generated consumption guidance uses the field before executing the procedure. For discovery, retrieve the selected
playbook by exact ID before execution and apply the same metadata rule; do not use `get-context` as a probe.

#### Q2 — One source-presence predicate

Keep the predicate in the existing distribution `services/bundles/` layer. It accepts source facts: constitution
presence, selected instruction presence and a declared context document directory. It returns their logical OR.
The sync inventory supplies facts from `Bundle.constitution`, the selected assets and `Bundle.context_documents`.
It retains the required bundle names for guidance generation and uses the result for skill prefixes.

Receipt-backed retrieval supplies the same facts from the recorded managed `AGENTS.md`, instruction assets of the
bundle and `declared_directory(read_owned(... bundle.toml ...))`. Read under the existing shared lock and validate
the managed manifest through `read_owned`; do not discover installed sources, infer sources from guidance text or
call document providers to decide presence. Preserve existing override and personal-render validation paths.

No receipt schema change or cross-feature dependency is needed. Do not serialize a second cached requirement in
the receipt: its existing facts are sufficient. A content-free constitution or selected instruction remains a
source. Rendered templates count through their deployed outputs; instruction overrides cannot deselect a source.

#### Q3 — Root guidance and verification

Root guidance retains the selected bundle inventory and separately names only bundles requiring context loads.
When selected bundles have no sources, state that no automatic bundle context load is required. An empty selection
retains the existing selection guidance. Keep stable bundle ordering and the reload-after-context-loss rule.

Use the existing integration test owners: `test_guidance_block.py`, `test_context.py`, `test_context_documents.py`,
`test_playbook_get.py` and `test_skill_invocation.py`. Extend the fixture matrix for no sources, constitution-only
and templated constitution, instruction-only and templated instruction, document-only with missing and empty
directories, mixed selections, and preset deselection followed by resync. Include exact and alias retrieval,
manifest tampering rejection and effective overridden instructions/playbooks. Assert preserved argv/policy fields
beside the boolean and unchanged explicit empty `get-context` output. Create a document or provide a provider
result after sync to verify runtime discovery without resync.

The implementation remains within the existing distribution feature. These local implementation choices need no
PADR; the capability changes are limited to the three declared targets. Before editing source bundle guidance,
Development loads `authoring` and applies `agent-asset-writing`. Sync-generated tracked projections and receipt
changes are derived outputs; review them alongside the source changes.

