---
id: PROP-skip-empty-bundle-context
title: Skip Context Loading for Bundles Without Context Sources
summary: "Skip automatic get-context calls for bundles without declared context sources. Keep required loading for constitutions, selected instructions and declared context documents consistent across guidance, skills and playbooks."
status: reviewing
created_at: 2026-11-13
target_area: distribution/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/
    - packages/devkit-dist/tests/
    - packages/devkit-dist/README.md
    - docs/capabilities/distribution/
    - docs/proposals/PROP-skip-empty-bundle-context/
  excludes:
    - packages/devkit-spec/
    - packages/devkit-catalog/
    - docs/architecture/
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-skip-empty-bundle-context] Skip Context Loading for Bundles Without Context Sources

## 1. Background & Hypothesis

A bundle is a distribution unit; shipping a skill through devkit-dist does not require that bundle to provide
shared execution context. `CAP-DIST-context-and-playbooks` defines bundle context as a constitution, selected
instruction headers and declared context document listings.

The automatic loading paths apply different criteria:

- Skill deployment adds a `get-context <bundle>` prerequisite only when the bundle has a constitution or selected
  instructions.
- The root guidance block requires loading context before using any selected bundle's assets, including bundles
  without context sources.
- Exact playbook retrieval always returns a context command. Its execution contract requires running that command
  even when the context is empty.

For example, the selected `response-style` bundle provides a skill and a guidance fragment, but its context result
has `constitution: null` and empty instruction and document lists. The root loading rule still requires a command
that contributes no bundle guidance. More selected bundles of this kind create more unnecessary calls.

Hypothesis: determine the loading requirement from the synchronized bundle's declared context sources, and expose
that requirement consistently before execution. Agents can then skip empty context loads without a preliminary
`get-context` call. Bundles retain separate contexts.

## 2. Technical Spike Questions

- **Q1:** How should `playbook get` expose that no context load is required while preserving compatibility for
  consumers of its existing `context` object, `argv` and `policy` fields? Evaluate an additive signal before
  removing or changing existing fields.
- **Q2:** Where should the shared source-presence decision live so sync-generated guidance, skill prerequisites
  and receipt-backed playbook retrieval agree without duplicating selection logic?
- **Q3:** How should mixed selections and bundles with only `context_documents` appear in root guidance so an
  agent can identify required loads without inspecting manifests or probing context results?

## 3. Proposed Design & Impact

### Loading requirement

A synchronized bundle requires context loading when at least one source exists:

1. A bundle constitution, including a rendered constitution template.
2. At least one instruction selected by the synchronized presets.
3. A declared `context_documents` directory.

For this proposal, an empty bundle context means none of these sources exists. A declared context document
directory remains a source when its current listing is empty or its directory is absent: project documents and
provider results are resolved at execution time. Do not infer emptiness from one invocation's JSON result.

Compute the requirement from synchronized metadata. Changing presets affects the requirement after sync, using the
same deployed selection that context retrieval reads.

### Agent-facing behavior

- Root guidance names the bundles that require context loading instead of requiring it for every selected bundle.
  A selection containing only bundles without context sources requires no context loads.
- Skill prerequisite generation uses the same source-presence criterion, including document-only bundles.
- Playbook retrieval exposes the loading requirement before procedure execution. Generated playbook guidance and
  the devkit consumption instruction honor it, so a playbook without bundle context runs without a redundant call.
- An agent does not call `get-context` merely to discover that the call can be skipped.
- Explicit `get-context <bundle>` remains available for any synchronized bundle. Its JSON shape and empty-result
  behavior remain unchanged.
- Existing per-agent-context reuse and reload-after-context-loss behavior applies to bundles that require loading.

### Acceptance checks

- **AC-01 — No sources:** Given a synchronized bundle without a constitution, selected instructions or declared
  context documents, when an agent follows generated root guidance and a deployed skill, then neither requires a
  `get-context` call for that bundle.
- **AC-02 — Playbook without sources:** Given a playbook in such a bundle, when it is retrieved by exact ID or a
  declared alias, then retrieval metadata and the generated execution instructions permit proceeding without a
  context call. Retrieval still validates the playbook and grants no execution authority.
- **AC-03 — Required sources:** Given a constitution-only, selected-instruction-only or document-only bundle, when
  its assets are used, then guidance, skill prerequisites and playbook metadata retain the loading requirement.
  Include a constitution template and an instruction template in this coverage.
- **AC-04 — Runtime document listings:** Given a document-only bundle whose declared directory is absent or empty,
  when guidance is generated, then it still requires context loading. Documents or provider results available at
  execution time remain discoverable without a new sync.
- **AC-05 — Mixed selection and refresh:** Given bundles with and without sources, when sync generates guidance,
  then only the bundles with sources require loading. Selecting or deselecting an instruction-only preset and
  syncing updates that requirement consistently across generated entry paths.
- **AC-06 — Explicit inspection:** Given a synchronized bundle without sources, when the user explicitly runs
  `uv run devkit get-context <bundle>`, then the command retains its existing successful empty JSON result. Missing
  or unsynchronized bundles retain their existing errors.
- **AC-07 — No discovery call:** Given any selection above, when the agent decides whether to load context, then
  generated guidance or returned playbook metadata supplies the decision without another inspection command.

Validate these checks with focused distribution integration tests for guidance generation, skill deployment,
playbook retrieval and context documents. Preserve receipt validation, override handling and synchronization checks.

### Non-Goals

- **Scope Excluded:** Combining contexts across bundles, introducing context dependencies or loading all installed
  bundles at startup.
- **Scope Excluded:** Moving context initialization into `spec` or a new worker skill, or redesigning Host and
  worker entrypoints.
- **Scope Excluded:** Adding multi-bundle context commands, persistent loading state, token budgets or benchmarks.
- **Scope Excluded:** Pruning nonempty context content, consolidating guidance fragments or moving bundle assets
  between packages.
- **Scope Excluded:** Suppressing explicit context commands authored inside an individual bundle's own procedure.
  This work changes devkit-generated requirements and devkit's generic consumption instructions.

## 4. Lifecycle & Retirement Criteria

This is a Backlog draft; creating it starts neither Planning nor Development. The size is M because one change must
align generated guidance, skill prerequisites and playbook metadata while preserving runtime document discovery.

Before acceptance, settle the playbook metadata compatibility question and identify the focused verification cases.
Acceptance and handoff follow the proposal lifecycle; the handed-off spec owns implementation and the Living Spec
updates listed in the target blueprint. Delivery requires AC-01 through AC-07 and the repository's affected checks.
