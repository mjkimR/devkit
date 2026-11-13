---
id: SPEC-idea-discovery
title: Idea discovery before research and delivery
summary: "Add a discovery entry with bounded interviewing, autonomous exploration and uncertainty-driven routing while preserving the research entry."
status: planned
created: 2026-11-13
related_capabilities:
  - CAP-DLV-deep-research
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-idea-discovery] Idea discovery before research and delivery

## 1. Problem Statement & Motivation

A vague idea needs clarification, alternative premises and pressure-testing before a research question or delivery
scope is settled. The research entry assumes an investigation and retains a material for every run. Add a discovery
entry to the same selected bundle so a person can receive concrete first proposals with little interruption.

Base: main at fc35dd50285cb20bef9e7541b7a547449583c04f. No prerequisite dependencies.
The user authorized the previously discussed direction. Development effort: medium.

## 2. User Stories

- **US-1**: As an idea owner, I want the agent to ask only indispensable initial questions and explore independently,
  so I can react to concrete proposals instead of completing a long questionnaire.
- **US-2**: As an idea owner, I want uncertainty to determine the next step, so research, clarification and rejection
  remain valid outcomes without forcing development.
- **US-3**: As a bundle consumer, I want existing research selection and overrides to keep working.

## 3. Non-Goals

1. **Scope Excluded**: Rename the bundle, move existing research roles or references, change its retained-material
   contract, or migrate existing overrides and materials.
2. **Scope Excluded**: Add a runtime, CLI command, new package, shared orchestration module, automatic implementation,
   persistent decision tracker or third-party dependency.
3. **Scope Excluded**: Modify the separate general solution exploration bundle or prove multi-agent superiority.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Additive selection and projection
- **Given** a consumer selecting the existing research core preset
- **When** sync deploys it to Codex, Claude Code and Antigravity
- **Then** both discovery and research entries are available with explicit invocation policy, all discovery-local
  role/reference paths resolve, no global discovery roles are registered, and remove/reselect preserves materials.

### [AC-02] Minimum useful interview
- **Given** a vague idea and supplied project context
- **When** discovery frames the first investigation
- **Then** it recovers the desired change, audience/use scene, consequential constraints and session outcome,
  asks only unanswered questions whose answers change the first proposals or avoid substantial wasted exploration,
  and keeps deferrable choices as assumptions or alternative premises.

### [AC-03] Autonomous first proposals
- **Given** enough grounding to explore
- **When** the coordinator allocates a bounded first wave
- **Then** optional local explorer, researcher and challenger roles receive explicit boundaries and stop conditions,
  develop independent premises before critique, and return evidence-backed concrete proposals with usage examples,
  benefits, costs, assumptions and failure conditions; no fixed cast or option quota applies.

### [AC-04] Uncertainty-driven routing and completion
- **Given** first proposals and actual findings
- **When** the coordinator selects the next step
- **Then** user-only choices lead to a focused question, factual gaps to bounded research, experiential gaps to a
  proposed example or separately authorized experiment, failed premises to reframing/hold/rejection, and sufficient
  clarity to a brief; another round names what result changes the recommendation.
- **Then** clarified, validation-needed, held and rejected outcomes are valid, with user decisions separate from
  assumptions and recommendations; development starts only from separate authorization.

### [AC-05] Conversation and write boundaries
- **Given** a discovery invocation
- **When** no destination is requested
- **Then** results stay in conversation and no retained material is mandatory; scratch writes use a verified ignored
  transient workspace, roles leave product files/index/HEAD unchanged, and missing delegation or evidence is reported.
- **Then** an explicitly requested retained result follows the existing material identity, collision, partial-resume
  and complete-material immutability conventions without commit or publication authority.

### [AC-06] Existing research compatibility and SDD separation
- **Given** the existing research entry and an SDD consumer
- **When** the bundle is upgraded or discovery is explicitly invoked
- **Then** existing research files, behavior and overrides remain intact, discovery creates no delivery Unit,
  approval or envelope, and later development follows ordinary intake without invoking the research entry implicitly.

## 5. Assumptions

- Keep the bundle name and its research-only guard; discovery is a second explicitly invoked entry in that bundle.
- Keep discovery's result in conversation by default, consistent with minimizing overhead before an idea is ready.
- General solution exploration starts from a supplied design problem; discovery can question the problem and goal.

## 6. Validation

Distribution integration tests prove selection, paths and host policy. A wheel consumer checks actual packaging.
An isolated behavioral pass exercises initial interviewing and autonomous proposal/routing decisions; review checks
semantic boundaries and compatibility. Native lint, type checks, affected tests and document rules remain required.
