---
id: SPEC-shipped-bundle-citations-and-doc-fixes
title: Forbid repository document IDs in shipped bundle text and fix two contract gaps
summary: State and test that shipped bundle text cites no repository document ID, name the locked restore as the stale local render remedy in the sync capability, and add the moved-base composed acceptance extensions to UC-plan-and-hand-off-a-proposal.
status: planned
created: 2026-10-30
related_capabilities:
  - CAP-DIST-content-packages
  - CAP-DIST-sync-and-transactions
  - CAP-DLV-proposal-planning
related_usecases:
  - UC-plan-and-hand-off-a-proposal
workflow: sdd-spec-feature
---

# [SPEC-shipped-bundle-citations-and-doc-fixes] Forbid repository document IDs in shipped bundle text and fix two contract gaps

## 1. Problem Statement & Motivation

Three open feedback items name small gaps between this repository's contracts and its shipped text.

- Bundles ship to projects that have none of this repository's `docs/`. The `agent-asset-writing` instruction of the
  `authoring` bundle already tells authors not to cite the authoring repository's ADR, capability, spec or path, but
  it names only some document kinds, its completion `rg` misses IDs whose slug starts with a digit, and no test pins
  the convention. A Development worker could not find the rule, and one shipped guide still cites
  `CAP-GOV-rule-authoring`.
- `CAP-DIST-sync-and-transactions` still names a plain sync as the remedy for `CONFIG_LOCAL_RENDER_STALE`, while the
  advisory, `CAP-DIST-context-and-playbooks` and the distribution reference name `devkit sync --locked` first.
- `UC-plan-and-hand-off-a-proposal` has no extension for composed acceptance on a moved base, which
  `CAP-DLV-proposal-planning` states.

## 2. User Stories

- **US-1**: As an agent authoring bundle text, I want one stated rule and a failing test when shipped text cites this
  repository's document IDs, so that consuming projects never meet a dangling citation.
- **US-2**: As an agent reading the sync capability, I want the stale local render remedy to match the advisory, so
  that I do not run a plain sync that writes outside my scope.
- **US-3**: As an agent following `UC-plan-and-hand-off-a-proposal`, I want the moved-base refusals of composed
  acceptance and their recovery in the use case, so that I recover without reading the capability first.

## 3. Non-Goals

1. **Scope Excluded**: no runtime rule or `devkit rules` check for citations; the convention is a repository test
   plus the instruction. The repository-only `devkit-dev` bundle under `tools/` is exempt.
2. **Scope Excluded**: unbackticked IDs (plain-text examples and fixture strings, such as rule test fixtures) are not
   citations and are not scanned.
3. **Scope Excluded**: no behavior change to sync, composed acceptance or unit integration preparation; composed
   acceptance keeps refusing every conflict.
4. **Scope Excluded**: no change to `scripts/affected_tests.py`; the test reaches affected selection through its
   imports.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Shipped bundle text cites no repository document ID
- **Given** every bundle whose `bundle.toml` lies under `packages/*/src/`
- **When** `just test devkit-dev` runs the citation test against the repository's `docs/` and `specs/`
- **Then** it passes: no backticked span in any file of those bundles contains a document ID of an indexed kind that
  resolves (by ID or alias) to a document of this repository, unless a shipped bundle seeds a document with that ID

### [AC-02] The scan reports a resolving citation and accepts placeholders and seeded IDs
- **Given** a bundle file citing a resolving ID in backticks, and other lines with backticked placeholders
  (`ADR-<slug>`, `CAP-<AREA>-<slug>`, `RULE-*`), examples that resolve to nothing (such as ADR-example, a numbered use case example or
  MS-release-1-0, backticked) and a backticked ID that a shipped bundle seeds
- **When** the test's scan reads the file
- **Then** it reports exactly one finding, `<path>:<line>: <ID>` for the resolving citation, and none for the others

### [AC-03] Bundle discovery covers every shipped bundle
- **Given** the shipping modules the test imports (`devkit_agt.bundles`, `devkit_catalog`, `devkit_dist.bundles`,
  `devkit_docs.bundles`, `devkit_spec.bundles`, `devkit_starter`)
- **When** the test collects their bundles
- **Then** the collected set equals every `bundle.toml` under `packages/*/src/`, and a change to the bundle text of
  any of those packages selects the test in `just test-affected`

### [AC-04] The authoring instruction states the convention once
- **Given** the `agent-asset-writing` instruction of the `authoring` bundle
- **When** an author reads its Self-Containment section
- **Then** it forbids citing the authoring repository's document IDs of every kind, allows placeholders, plain-text
  examples and documents a bundle seeds, its completion `rg` matches IDs whose slug starts with a digit, and
  `uv run devkit rules check --phase hygiene` reports no `RULE-agent-asset-wording` warning on it

### [AC-05] The content package capability states the convention
- **Given** `CAP-DIST-content-packages`
- **When** a reader looks up the repository's bundle source convention
- **Then** one rule states that bundle text a wheel of this repository ships cites none of its document IDs except
  documents a shipped bundle seeds, ending with the enforcing test path

### [AC-06] The flagged shipped text is reworded
- **Given** the citations the test finds on the base (`CAP-GOV-rule-authoring` in the advisory bundle's `unique_code`
  guide, `ARCH-01-introduction-and-goals` in the docs bundle seed and the spec bundle's roadmap reference)
- **When** the change is complete
- **Then** the guide states its descriptor reference without the capability ID, and the two
  `ARCH-01-introduction-and-goals` citations stay because the auto-selected docs bundle seeds that document into every
  project that installs `devkit-spec`

### [AC-07] The sync capability names the locked restore first
- **Given** the personal rendering paragraph of `CAP-DIST-sync-and-transactions`
- **When** it describes `CONFIG_LOCAL_RENDER_STALE`
- **Then** it reads "(exit 1; `devkit sync --locked`, a plain sync only when it reports `RECEIPT_STALE`)"

### [AC-08] The proposal use case covers composed acceptance on a moved base
- **Given** `UC-plan-and-hand-off-a-proposal`
- **When** a reader looks for composed acceptance while the base moved
- **Then** an extension names the refusals before the acceptance commit (`SPEC_PROPOSAL_APPROVAL_NOT_READY` for a
  failing CI rule on the prospective result or a base change to the proposal directory, `WORKTREE_MERGE_CONFLICT` for
  a conflict) with their recovery, an extension names the conflict-free landing without a merge into `plan-<slug>`
  and the result fields `target_sha`, `landed_sha` and `disclosure`, and a scenario covers each

## 5. Assumptions

- The convention covers backticked spans only: the spec skill's own rule writes example IDs as plain text and
  requires backticked IDs to resolve, so a backtick is what marks a citation.
- "Seeded by a shipped bundle" rather than "seeded by the same bundle": the spec bundle's roadmap reference cites the
  docs bundle's seeded `ARCH-01-introduction-and-goals`; `devkit-spec` requires `devkit-docs`, whose `docs` bundle is
  auto-selected and seeds that document, and the docs bundle's milestone template names the same document.
- The test lives in `tools/devkit-dev/tests/integration/`: `ARCH-05-2-components` keeps package tests to package
  ownership, and the repository's own `devkit-dev` tool already holds the integration tests that scan every package
  (`test_architecture.py`).

## 6. Source feedback

- `FB-bundle-text-document-id-citations`: state the convention in the bundle-authoring instruction and pin it with a
  test over every shipped bundle (AC-01 to AC-06).
- `FB-sync-capability-render-stale-remedy-generic`: align the remedy in `CAP-DIST-sync-and-transactions` (AC-07).
- `FB-proposal-usecase-moved-base-acceptance`: add the moved-base composed acceptance extensions and scenarios to
  `UC-plan-and-hand-off-a-proposal` (AC-08).
