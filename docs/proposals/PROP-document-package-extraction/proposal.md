---
id: PROP-document-package-extraction
title: Move the document layer into its own package
summary: Moves the decoupled document code into a separate package that the delivery process depends on, without a dependency in return.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: documents/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-idea-incubation
boundaries:
  owns:
    - documents/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-document-layer-package
depends_on: [PROP-document-lifecycle-seams, PROP-document-rule-split]
workflow: sdd-proposal
---

# [PROP-document-package-extraction] Move the document layer into its own package

## 1. Background & Hypothesis

Once the document layer and its rules no longer import the lifecycle, they can leave devkit-spec. See
`docs/materials/2026-10/20261028-document-layer-split/coupling-survey.md` for the move set (about 7,200 lines and 25 test files) and the affected records.

Hypothesis: a separate document package that devkit-spec depends on, with no dependency in return, makes the
document system reusable by other delivery processes such as idea incubation.

## 2. Technical Spike Questions

- **Q1**: Packaging: a new wheel or a second regular package in devkit-spec's wheel, and the version policy under `ADR-package-split-and-namespaces` and `ADR-single-release-version`.
- **Q2**: CLI: one composed `devkit spec` group or a separate document group.
- **Q3**: Error codes: keep the `SPEC_` prefix for document codes or rename them.
- **Q4**: Whether the scanner the document model borrows from devkit-agt moves to devkit-core.

## 3. Proposed Design & Impact

- Move `features/documents`, the document rules, entrypoints paths and apply, the namespace reader, the document
  error classes and `resolve`/`refs`/`list`/`search`, with their tests.
- Rewire the entry points (`devkit.commands` composition, the config template contribution), the root workspace,
  `scripts/affected_tests.py`, `scripts/_lib.sh` and `scripts/release.sh`.
- Amend or check `ADR-spec-package-on-devkit`, `ADR-package-split-and-namespaces` and `ADR-single-release-version`;
  update `ARCH-05-1-containers`, `ARCH-05-2-components`, `ARCH-05-3-command-plugins`,
  `ARCH-04-1-ecosystem-boundaries`, `ARCH-07-deployment`, package READMEs and the AGENTS.md package table.

## 4. Lifecycle & Retirement Criteria

- Retire with acceptance and handoff, or reject if idea incubation no longer needs a document layer without SDD.
