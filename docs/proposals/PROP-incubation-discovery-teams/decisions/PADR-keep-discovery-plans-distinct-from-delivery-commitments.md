---
id: PADR-keep-discovery-plans-distinct-from-delivery-commitments
title: Keep discovery plans distinct from delivery commitments
summary: "For pre-development discovery, we retain labelled project-owned research and planning notes, to prepare useful documents and roadmaps without claiming implemented behavior, accepting semantic review."
proposal: PROP-incubation-discovery-teams
status: draft
created_at: 2026-10-29
---

# [PADR-keep-discovery-plans-distinct-from-delivery-commitments] Keep discovery plans distinct from delivery commitments

## 1. Context & Problem Statement

Early discovery needs initial documents and a roadmap before implementation. Existing capability, decision,
milestone and proposal documents have meanings that cannot be inferred from a research recommendation.
Incubation consumers may install docs/catalog without devkit-spec.

## 2. Decision Drivers

- Keep initial plans useful without representing planned behavior as current capability.
- Preserve uncertainty, evidence provenance and meaningful alternative reopening conditions.
- Reuse document conventions and mutable current context without another parser or lifecycle.
- Produce a proportionate result with no invented approval, dates or automatic implementation.

## 3. Considered Options

- Context file only: minimal; broad research and several roadmap alternatives become difficult to inspect.
- Fixed mandatory PRD/ADR/capability/milestone suite: familiar names; premature commitments and unnecessary volume.
- Project-owned research/planning notes linked from context: flexible and SDD-independent; semantic review is needed.

## 4. Decision Outcome

Use proportionate project-owned notes for the product brief, evidence/alternatives, direction/architecture
recommendation and outcome/dependency roadmap. Reuse existing useful destinations. Default new evidence and
synthesis notes to `docs/materials/`, labelled as discovery/planning. Follow indexed material instructions when
document identity is needed; do not introduce a new document kind or prescribe a fixed file count.

Only the coordinator saves retained synthesis and updates `.devkit/incubation.md`. Keep user decisions,
recommendations, assumptions, observations and unverified areas distinguishable. Keep surviving alternatives
and reopening conditions where they inform the next decision; do not reconstruct immutable experiment history.

Apply native document semantics only when the subject warrants them. A roadmap note is not automatically a
milestone or a delivery Unit. Research completion grants no implementation, integration, publication or SDD
adoption authority. A later user-authorized product action can consume these documents through existing entries.

## 5. Consequences

- Positive: useful pre-development documents and roadmap without a parallel delivery lifecycle.
- Negative: free-form notes require content review; filenames alone cannot establish evidence quality.
- Risk: a summary can erase uncertainty; the master checks the draft against research evidence and user decisions.
- Reconsider a standardized template only after repeated concrete output failures demonstrate a need.

## 6. Confirmation

Document rules check applicable identity and references. Semantic walkthroughs inspect proposed/current
distinctions, source support, unknowns, coherent dependencies and fresh-context resume. Review only for the
substantive validity of a product recommendation and any actual user commitment.
