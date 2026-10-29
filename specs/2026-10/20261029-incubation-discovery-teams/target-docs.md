---
id: PROP-incubation-discovery-teams-target
title: Target Living Spec for incubation discovery teams
summary: "Extend incubation contracts with an explicit research entry, adaptive teams and honest pre-development document and roadmap synthesis."
status: draft
proposal: SPEC-incubation-discovery-teams
created_at: 2026-10-29
targets:
  - file: docs/capabilities/delivery/CAP-DLV-idea-incubation.md
  - file: docs/usecases/delivery/UC-incubate-an-idea.md
  - file: docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  - file: guides/INSTALL_GUIDE.md
  - file: guides/install/bundle-recommendations.md
  - file: guides/install/new-repository.md
  - file: guides/install/existing-repository.md
---

# Target Living Spec for PROP-incubation-discovery-teams

This blueprint describes the proposed retained contracts, not implemented behavior.

## 1. Capabilities

Extend `CAP-DLV-idea-incubation` with explicit research entry, adaptive master/team assignments, research source
limits, independent alternatives, optional cross-candidate criticism, initial document/roadmap synthesis and resume.
Keep existing next-action iteration, approach inspection, six-role optionality and project-owned context rules.

## 2. Use Cases

Update `UC-incubate-an-idea` to distinguish a suggested research invocation from automatic broad discovery or
implementation. Existing small inline work and actual-usage verification remain supported.

Add UC-research-an-idea-and-shape-a-roadmap under `docs/usecases/delivery/`. Its main scenario is explicit
invocation, policy/context recovery, scoped research allocation, validated comparison, document synthesis and
return of an initial roadmap and unresolved user decisions. Extensions cover missing user facts, invalid approach,
insufficient evidence, absent delegation, duplicate directions, failed/out-of-scope returns and fresh-context resume.
Link the use case and capability both ways. No screens or product UI are introduced.

## 3. Decisions and Architecture

PADR-extend-incubation-with-optional-discovery-teams supersedes
`ADR-keep-incubation-guidance-opt-in-and-current-state-based`, preserving its opt-in/content-only ownership,
source-specific evidence and mutable current context while adding the explicit entry and three optional roles.

PADR-keep-discovery-plans-distinct-from-delivery-commitments defines labelled project-owned discovery output
rather than invented current capability or implicit SDD work. Both are promoted through ordinary proposal handoff.

`ARCH-05-2-components` already permits catalog-owned content-only incubation assets; no component, runtime or
dependency direction changes. There is no architecture-document target unless implementation discovers one.

## 4. Assets and References

Within `packages/devkit-catalog/src/devkit_catalog/incubation/bundle/`:

- Add `skills/incubate-research/SKILL.md` with conditional references for orchestration and synthesis.
- Add `subagents/direction-explorer.md`, `subagents/discovery-critic.md` and `subagents/discovery-planner.md`.
- Update `bundle.toml`, the existing incubation entry/references, guidance pointer and current-context template
  only where needed to describe the research doorway, role boundaries and retained discovery pointers.
- Reuse existing role IDs and one-question research contracts; update tool access only where actual web research
  requires a supported native capability.

Update the catalog README with invocation examples and output/authority limits. Consumer guidance contains no
repository-specific CAP/ADR IDs and does not require a spec bundle.

## 5. Verification and Before/After

Before: one iterative entry and three optional support roles; direction comparison and document synthesis are
left mostly to the coordinator's general judgment.

Proposed: one additional explicitly invoked research skill, six optional role contracts, adaptive assignments and
a proportionate pre-development research/document/roadmap result. Existing incubation remains useful by itself.

Use catalog integration/e2e tests for distribution, docs-only installation, retained IDs, native projection and
context preservation. Use observed bounded walkthroughs for substantive candidate comparison, evidence support,
critic behavior, synthesis and fresh-context resume. Missing live-agent coverage remains explicit.
