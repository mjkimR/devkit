---
id: PADR-split-deep-research-bundle
title: Split explicit research into an approach-neutral deep-research bundle
summary: For explicit research that SDD and adaptive projects both need, we move the research entry and its research roles into a self-contained deep-research bundle without an approach gate, accepting one near-duplicate researcher contract.
proposal: PROP-deep-research-bundle
status: draft
created_at: 2026-10-30
supersedes: ADR-extend-incubation-with-optional-discovery-teams
---

# [PADR-split-deep-research-bundle] Split explicit research into an approach-neutral deep-research bundle

- **Status**: Draft
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

## 4. Decision Outcome

Chosen: a self-contained `deep-research` catalog bundle with its own researcher, because it meets every driver at
the cost of one duplicated contract.

- `deep-research:core` holds the `/deep-research` entry (`invocation = "user"`), its `orchestration`, `workspace`
  and `synthesis` references, `direction-explorer`, `discovery-critic`, `discovery-planner` (moved, same IDs) and
  a new `research-investigator` (one question per instance; optional bounded experiment in its assigned scratch).
- The entry has no approach gate, reads no approach-specific context file and writes no `.devkit/incubation.md`.
  It never implements, publishes, commits or creates SDD Units, approvals or envelopes.
- No skill, guidance pointer, guide or role suggests the entry, also on a topic match. The bundle ships no
  guidance asset; install guides list it only as a bundle the user selects.
- The incubation bundle keeps `/incubate`, `product-clarifier`, `incubation-researcher`, `usage-reviewer`, the
  pointer and the current-context template; it loses the entry, its references and the three research roles.
- Retained from the superseded decision: content-only catalog ownership, explicit selection, installation with
  docs and catalog without devkit-spec, the invoking agent as coordinator, bounded assignments with no mandatory
  role sequence, source provenance, and plans distinct from delivery commitments.

## 5. Consequences

- Positive: SDD and adaptive projects run the same research entry; neither bundle needs the other.
- Negative: `research-investigator` and `incubation-researcher` share most constraints and drift independently.
- Risk: a consumer with `incubation:core` loses the entry on upgrade; sync removes the unmodified projections and
  announces `deep-research` once with `BUNDLE_UNSELECTED`, and the guides name `uv run devkit add deep-research`.
- Follow-up: if a third bundle needs the same researcher, reconsider a shared-role mechanism in distribution.

## 6. Confirmation

`packages/devkit-catalog/tests/integration/bundles/` gains a deep-research test that checks the preset contents,
explicit invocation projection on every host, selection with `incubation:core` without `BUNDLE_CONFLICT`, and
that no asset of either bundle names the entry. The installed-consumer e2e test runs the entry's assets under the
default `sdd` approach without devkit-spec. Approach-neutral behavior and the absence of suggestion beyond the text
checks are review only.
