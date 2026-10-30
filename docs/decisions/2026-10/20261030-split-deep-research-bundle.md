---
id: ADR-split-deep-research-bundle
title: Split explicit research into an approach-neutral deep-research bundle
summary: For explicit research that SDD and adaptive projects both need, we move the research entry and its research roles into a self-contained deep-research bundle without an approach gate, accepting one near-duplicate researcher contract.
proposal: SPEC-deep-research-bundle
status: accepted
created_at: 2026-10-30
supersedes: ADR-extend-incubation-with-optional-discovery-teams
---

# [ADR-split-deep-research-bundle] Split explicit research into an approach-neutral deep-research bundle

- **Status**: Accepted
- **Date**: 2026-10-30
- **Supersedes on promotion**: `ADR-extend-incubation-with-optional-discovery-teams`

---

## 1. Context & Problem Statement

`ADR-extend-incubation-with-optional-discovery-teams` placed the explicit research entry and three research
roles in `incubation:core` and rejected a separate discovery bundle until "independently useful non-incubation
research behavior establishes a concrete need". That need now exists: a repository under SDD cannot run the entry,
because it stops unless the shared approach is incubation and writes `.devkit/incubation.md`, and switching the
shared approach for one investigation makes spec extensions refuse new SDD records (`CAP-DLV-project-policy`).

Research implements nothing and creates no SDD Unit, so it needs no approach gate. Bundles declare no dependency
on another bundle, and two selected bundles that ship the same skill or subagent ID fail sync with
`BUNDLE_CONFLICT`, so a role cannot be shared between bundles.

## 2. Decision Drivers

- The entry runs under either approach and only on explicit user invocation.
- `/incubate` keeps its optional support without requiring another bundle.
- No cross-bundle dependency and no `BUNDLE_CONFLICT` when both bundles are selected.
- No new runtime, CLI or distribution mechanism.
- Small duplicated contract text.

## 3. Considered Options

- **Keep the entry in incubation with a relaxed gate**: no new bundle; an SDD project must still select the
  approach bundle it does not use, and the bundle text keeps mixing both concerns.
- **Self-contained `deep-research` bundle with its own researcher**: no dependency or conflict; one
  near-duplicate researcher contract to maintain.
- **`deep-research` owns the shared researcher; `/incubate` delegates to it only when selected**: no duplicate;
  `/incubate` loses its research role without the second bundle, and its text depends on another bundle's IDs.
- **`deep-research` copies all three shared roles under new IDs**: full coverage; three duplicates where the
  coordinator or the researcher covers clarification and usage evidence.
- **Layer the bundles through a Python package dependency plus `auto_select`** (`CAP-DIST-content-packages`): a
  shared role without a dependency engine, which `ADR-document-and-sdd-bundles` rules out across bundles. It works
  only across wheels, and both bundles ship in the opt-in `devkit-catalog` wheel, so it needs a separate wheel.
  Deferred until a real cross-bundle need appears.

## 4. Decision Outcome

Chosen: a self-contained `deep-research` catalog bundle with its own researcher, because it meets every driver at
the cost of one duplicated contract.

- `deep-research` is designed without regard to adaptive development: no role is shared, and no bundle or package
  dependency exists in either direction.
- `deep-research:core` holds the `/deep-research` entry (`invocation = "user"`), its `orchestration`, `workspace`
  and `synthesis` references, `direction-explorer`, `discovery-critic`, `discovery-planner` (moved, same IDs) and
  a new `research-investigator` (one question per instance; optional bounded experiment in its assigned scratch).
- The entry has no approach gate, reads no approach-specific context file and writes no `.devkit/incubation.md`.
  It never implements or publishes and creates no SDD Unit, approval or envelope.
- Under SDD, an explicit `/deep-research` invocation is not development intake: the spec entry does not classify
  it into a depth, and the research run writes only its transient run directory and the retained material. Spec
  routing, `CAP-HARN-agent-guidance` and `UC-route-development-intent` state this exemption.
- No skill, guidance pointer, guide or role suggests the entry, also on a topic match. The bundle ships no
  guidance asset; install guides list it only as a bundle the user selects. Because Antigravity has no native
  explicit-only setting, the skill body opens with the guard "Run only when the user explicitly invokes this
  entry; never suggest or start it otherwise", and its description carries no trigger phrasing.
- The incubation bundle keeps `/incubate`, `product-clarifier`, `incubation-researcher`, `usage-reviewer`, the
  pointer and the current-context template; it loses the entry, its references and the three research roles.
  `PROP-rename-incubation-to-adaptive-dev` later renames it `adaptive-dev` and the researcher `product-researcher`.
- The two researchers differ in scope: `research-investigator` answers one question of a team investigation; the
  incubation researcher gathers one product decision's evidence or runs one bounded experiment.
- `/incubate` never invokes or suggests `/deep-research`; it only reads a retained material by its `MAT-<slug>` ID.
- Retained from the superseded decision: content-only catalog ownership, explicit selection, installation with
  docs and catalog without devkit-spec, the invoking agent as coordinator, bounded assignments with no mandatory
  role sequence, source provenance, and plans distinct from delivery commitments.
- Retained for `/incubate`: the shared approach check before product work and the coordinator-owned, mutable
  `.devkit/incubation.md`.

## 5. Consequences

- Positive: SDD and adaptive projects run the same research entry; neither bundle needs the other.
- Negative: `research-investigator` and `incubation-researcher` share most constraints and drift independently.
- Risk: a consumer with `incubation:core` loses the entry on upgrade; sync removes the unmodified projections and
  announces `deep-research` once with `BUNDLE_UNSELECTED`, and the guides name `uv run devkit add deep-research`.
  Three customizations of a moved role need a manual step the guides name: an `incubation:<role>` role-policy key
  (sync fails until renamed to `deep-research:<role>`), a file override under `.devkit/overrides/incubation/`
  (silently stops applying until moved to `.devkit/overrides/deep-research/`) and an edited projection left with
  `ORPHAN_LEFT` (blocks `devkit add deep-research` until moved or deleted).
- Follow-up: if a real cross-bundle need appears (a third bundle needs the same researcher, or a bundle must
  require another), reconsider the deferred package-dependency layering with a separate wheel.

## 6. Confirmation

`packages/devkit-catalog/tests/integration/bundles/` gains a deep-research test that checks the preset contents,
explicit invocation projection on every host with the body guard, selection with `incubation:core` without
`BUNDLE_CONFLICT`, an `incubation:<moved-role>` role key failing while `deep-research:<role>` passes, no incubation
bundle file naming `incubate-research` or `deep-research`, and no deep-research file naming
`configuration.development.approach`, `.devkit/incubation.md` or `incubation`. The installed-consumer e2e test runs
the entry's assets under the default `sdd` approach without devkit-spec. Approach-neutral behavior and the absence
of suggestion beyond these text checks are review only.
