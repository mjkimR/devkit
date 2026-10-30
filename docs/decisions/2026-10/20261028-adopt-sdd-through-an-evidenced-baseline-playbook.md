---
id: ADR-adopt-sdd-through-an-evidenced-baseline-playbook
title: Adopt SDD through an evidenced baseline playbook
summary: "For voluntary incubation graduation, we prepare an evidenced retained baseline through a spec playbook before activating SDD, to avoid invented delivery history, accepting a semantic readiness review."
proposal: SPEC-incubation-sdd-baseline
status: accepted
created_at: 2026-10-28
---

# [ADR-adopt-sdd-through-an-evidenced-baseline-playbook] Adopt SDD through an evidenced baseline playbook

## 1. Context & Problem Statement

`MS-idea-incubation` permits voluntary SDD adoption from the implemented product. Brownfield adoption contains legacy rule debt; feature sync requires a completed Unit; drift reconciliation reviews a bounded batch without defining adoption readiness. None establishes the transition without inventing delivery history.

## 2. Decision Drivers

- Preserve user-selected adoption and truthful current-state evidence.
- Reuse existing document tools and delivery assets rather than build another runtime engine.
- Keep baseline preparation distinct from policy activation and from historical feature delivery.
- Leave concurrent policy and live-context ownership with their prerequisites.

## 3. Considered Options

- Keep brownfield adoption unchanged: no new asset, but rule debt containment and later migration do not prove the retained baseline before SDD.
- Add an incubation branch to brownfield adoption: shares installation instructions, but one playbook would mix gradual debt containment with evidence-complete activation and expose the wrong default for each path.
- Create a baseline Unit/CLI/workflow: gives machine tracking, but adds a new runtime model and invites retrospective lifecycle artifacts without a demonstrated requirement.
- Add a focused `sdd-baseline` playbook in the existing spec bundle: reuses docs formats and evidence methods while owning the missing readiness/activation contract; adds a separate entry and semantic verification cost.

## 4. Decision Outcome

Adopt the focused playbook to keep retained-product readiness separate from legacy debt containment.

1. Ship it in spec:core and invoke only for explicitly requested or confirmed graduation. Package/asset installation is a prerequisite, not activation.
2. Prepare an ordinary material report and needed current-state documents while incubation policy remains effective. Require evidence coverage of the user-selected retained product, with no unresolved retained-scope mismatch or required missing check evidence.
   Superseded in part by `ADR-adaptive-dev-approach-name`: the approach value is `adaptive-dev`.
3. Present the exact ready source/scope/effects for the user's activation decision, reusing a decision already bound to them. Change the authoritative approach through the accepted policy contract, include necessary missing-provider configuration or a project-to-spec integration provider switch among the explicitly authorized effects, then sync and verify consistency.
4. Start ordinary SDD for later changes. Create no historical Units/approvals or discarded-experiment ADRs and preserve existing SDD history.

## 5. Consequences

- Positive: the transition remains voluntary, inspectable and based on actual retained behavior; it reuses current document and verification tools.
- Negative: semantic completeness requires a reviewer/exercise rather than a new deterministic readiness command. A bounded report cannot prove unexamined product areas.
- Risk: source changes or failed installation/sync make earlier evidence stale; the playbook rechecks source and reports partial state without claiming activation.
- Dependency: policy and guidance contracts must be integrated before end-to-end completion; their schema and context format are not chosen by this decision.

## 6. Confirmation

Asset inventory and guidance assertions verify entry/ownership and prohibited retrospective artifacts. Seeded app exercises cover ready, missing-evidence, source-change and partial-failure paths, recording coverage and real versus simulated decisions. Existing brownfield adoption tests preserve its legacy containment behavior. Semantic retained-scope coverage is review-only; deterministic format checks alone never establish it.
