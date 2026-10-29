---
id: ADR-extend-incubation-with-optional-discovery-teams
title: Extend incubation with optional discovery teams
summary: "For ambiguous product direction, we add an explicit incubation research entry and bounded discovery teams, to compare evidence before development, accepting additional optional guidance."
proposal: SPEC-incubation-discovery-teams
status: accepted
supersedes: ADR-keep-incubation-guidance-opt-in-and-current-state-based
created_at: 2026-10-29
---

# [ADR-extend-incubation-with-optional-discovery-teams] Extend incubation with optional discovery teams

## 1. Context & Problem Statement

`ADR-keep-incubation-guidance-opt-in-and-current-state-based` places one iterative entry, three optional
roles and mutable context in the opt-in catalog bundle. Broad early research also needs a deliberate entry,
independent alternatives, shared-assumption examination and document/roadmap synthesis. Invoking a spec
challenger would make the incubation path depend on an optional SDD package.

## 2. Decision Drivers

- Make broad-team research an explicit user action.
- Retain shared approach policy, SDD-independent installation and the existing lightweight entry.
- Broaden alternatives and evidence without mandatory tiers, personalities or runtime infrastructure.
- Keep product decisions and authority with the user and invoking Host.
- Verify semantic outcomes beyond distributed file integrity.

## 3. Considered Options

- Existing single-entry guidance only: smallest surface; broad discovery initiation remains implicit.
- Explicit research skill inside incubation: clear intent and reused ownership; one additional skill to maintain.
- Separate discovery bundle: clearer standalone branding; duplicated context/policy and installation selection.
- New master subagent and swarm runtime: execution control, with unnecessary infrastructure and host coupling.

## 4. Decision Outcome

Add `/incubate-research` and three optional contracts to `incubation:core`. The invoking Host is master.
Retain `/incubate`, product-clarifier, incubation-researcher and usage-reviewer. Add direction-explorer,
discovery-critic and discovery-planner, for six optional roles total. The master commissions bounded assignments
and synthesizes returned evidence; native peer communication is optional and no role sequence is mandatory.

Preserve the superseded decision's content-only catalog ownership, explicit installation, shared approach check,
independent docs/catalog installation, source-specific evidence and mutable coordinator-owned current context.
No entry switches approach, authorizes publication, creates SDD records or requires eventual SDD adoption.

## 5. Consequences

- Positive: clear research intent and reusable responsibilities for broad product discovery.
- Negative: three additional role contracts and conditional guidance need maintenance and consumer checks.
- Risk: many similar agents can amplify one assumption; independent candidate premises and evidence comparison
  require semantic evaluation.
- Reconsider separate ownership only when independently useful non-incubation research behavior establishes a
  concrete need; this feature does not build that extension.

## 6. Confirmation

Catalog manifest/projection and docs-only installation tests check distribution, native role metadata and
retained IDs. Bounded observed research and fresh-context resume exercises check orchestration, comparison,
honest evidence and the distinction between recommendations and user decisions. Review only for product
strategy quality beyond the selected scenarios; no deterministic rule proves global optimality.
