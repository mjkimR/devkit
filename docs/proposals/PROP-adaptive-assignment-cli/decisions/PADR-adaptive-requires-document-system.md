---
id: PADR-adaptive-requires-document-system
title: devkit-adaptive requires the document system
summary: For the adaptive distribution, whose commands validate governing documents and whose guidance links project documents, we require devkit-docs with an exact pin, to give every installation the document system and the harness, accepting release coupling and the loss of snapshot eligibility.
proposal: PROP-adaptive-assignment-cli
supersedes: [ADR-adaptive-development-and-research]
status: draft
created_at: 2026-11-10
---

# [PADR-adaptive-requires-document-system] devkit-adaptive requires the document system

- **Status**: Draft
- **Date**: 2026-11-10

---

## 1. Context & Problem Statement

`ADR-adaptive-development-and-research` keeps adaptive development installable beside the document system without
`devkit-spec`: a consumer declares `devkit-docs` and the wheel that ships the `adaptive-dev` bundle as two
requirements. The bundle guidance therefore conditions every document step on the docs bundle being selected, and its
orchestration reference assumes no harness.

Adaptive development is being raised from a content bundle to a package with commands
(`PADR-adaptive-assignment-commands`). An assignment names its governing documents by ID or path
(`CAP-DLV-adaptive-development` rule 26). A command can check those names only when the document index is importable.
`devkit-docs` already requires `devkit-agt`, which requires `devkit-dist`, so the two-requirement installation
already carries the harness; the guidance and several guides describe it as if it did not.

## 2. Decision Drivers

- The commands resolve governing document IDs through the document index instead of a second parser.
- One requirement installs adaptive development; the consumer cannot install it without the document system.
- Guidance states document and worktree steps without an installation condition.
- Installation without `devkit-spec` stays possible, and no SDD lifecycle enters adaptive development.
- No consumer outside this repository uses the bundle, so compatibility with an existing installation is not a driver.

## 3. Considered Options

- **Require `devkit-dist` only**: adaptive development installs without the harness and the document system. The
  commands cannot validate a governing ID, and every document step in the guidance stays conditional.
- **Require `devkit-agt`**: harness modules become importable. The document index stays optional, so document
  validation and the conditional guidance do not change.
- **Require `devkit-docs`** (chosen): the document index and, through it, the harness are present in every
  installation. The wheel is released whenever `devkit-docs` is, and it stops being a snapshot source.

## 4. Decision Outcome

Chosen: `devkit-adaptive` requires `devkit-docs`. This replaces one part of a clause of
`ADR-adaptive-development-and-research`: "independent docs/catalog installation" no longer means two requirements
the consumer declares side by side. The independence from `devkit-spec` in the same clause stays in force.

- The `devkit-adaptive` wheel declares `devkit-docs` at the exact version the release inventory selects, as every
  internal requirement does. → `ARCH-07-deployment` (MUST), `ARCH-05-1-containers`.
- `devkit_adaptive` imports `devkit_docs`, `devkit_dist`, `devkit_core` and `devkit.advisory`. It never imports
  `devkit_spec`, and `devkit-spec` never becomes a requirement. → `ARCH-05-2-components`,
  `CAP-DLV-adaptive-development` rule 2 (MUST).
- A consumer installs adaptive development with the one requirement `devkit-adaptive`. The `docs` and `harness`
  bundles are auto-selected by their own declarations; `adaptive-dev` still deploys only after explicit selection.
  → `CAP-DLV-adaptive-development` §4, `ARCH-07-deployment`.
- Recording an assignment validates its governing documents: an ID through the document index, a path by existence.
  → CAP-DLV-adaptive-assignments §3 (MUST).
- The document system's kinds, destinations and checks are the default for adaptive documents. A project's own
  document conventions stay in force where it has them. → `CAP-DLV-adaptive-development` rules 26 and 27.
- A document is written only where its subject warrants one. No document tree is seeded for a project that has no
  document, and document work adds no per-change record. → `CAP-DLV-adaptive-development` rule 27 (MUST).
- The requirement adds no SDD stage, gate, envelope or approach change. The approach check of the `/adaptive-dev`
  entry is unchanged.
- `ADR-worktree-isolated-parallel-workers` stays in force unchanged. Its clause "Use the existing harness lifecycle
  when available, otherwise the consuming project's documented Git procedure" now always meets an installed
  harness, so the orchestration guidance names `uv run devkit worktree` first. → `UC-advance-an-idea` 5b3.

## 5. Consequences

- Positive: one installation statement in every guide; the guidance drops its installation conditions; a mistyped or
  missing governing document is refused when the assignment is recorded.
- Negative: `devkit-adaptive` takes a new version whenever `devkit-docs`, `devkit-agt`, `devkit-dist` or
  `devkit-core` does, because its exact pin changes (`ADR-selective-package-versions`).
- Negative: `devkit bundle snapshot` refuses the `devkit-adaptive` source with `BUNDLE_SNAPSHOT_UNSUPPORTED`,
  because a snapshot source declares no runtime requirement and no command entry point. No guide offers the
  `adaptive-dev` bundle as a snapshot source.
- Negative: every adaptive installation deploys the docs bundle's instructions and document rules unless the project
  opts out with `uv run devkit remove docs`. The former two-requirement installation deployed them as well.
- Follow-up: none. A later need to install the bundle text without Python code would reopen the choice.

## 6. Confirmation

The installed-consumer test of `devkit-adaptive` (requirement metadata, the `docs` and `harness` presets in the
receipt, no `devkit-spec` distribution), the import test that finds no `devkit_spec` module, `RULE-architecture` on
the package declaration, the lockstep test that asserts exact pins, and the snapshot refusal test.
