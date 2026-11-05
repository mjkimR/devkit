---
id: SPEC-deep-research-practical-orchestration
title: Make deep-research deliverable-driven and proportionate
summary: "Refine research assignments, synthesis and retrieval recovery around the requested deliverable while preserving opt-in roles and existing research authority."
status: in-progress
created: 2026-11-05
related_capabilities: [CAP-DLV-deep-research]
related_usecases: [UC-research-an-idea-and-shape-a-roadmap]
workflow: sdd-spec-feature
---

# [SPEC-deep-research-practical-orchestration] Make deep-research deliverable-driven and proportionate

## 1. Problem Statement & Motivation

A source-supported research answer can still omit the practical artifact the user requested or impose unwanted
follow-up work. The pilot recorded in `MAT-agent-team-design-pilot` also exposed duplicate source investigation
and wording that conflated a technical retrieval failure with a permission refusal. `ADR-deliverable-driven-research`
settles the bounded instruction changes. `UC-research-an-idea-and-shape-a-roadmap` owns the affected user journey.

## 2. User Stories

- **US-1**: As a research requester, I want assignments and synthesis to deliver the artifact I can use next.
- **US-2**: As a coordinator, I want selective verification and bounded recovery without relaxing access authority.
- **US-3**: As a consumer, I want optional skill-local roles and proportionate follow-up without an adoption benchmark.

## 3. Non-Goals

- **Scope Excluded**: new roles, team counts, runtimes, automatic retries, package dependencies or feature edges.
- **Scope Excluded**: comparative-effectiveness experiments, measured token savings or proof of team superiority.
- **Scope Excluded**: changes to material retention, explicit invocation, Git or publication authority, or consumer implementation.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Frame the useful deliverable

- **Given** a request for reusable repository configurations and supplied cost constraints.
- **When** the coordinator frames the run and assignments.
- **Then** the brief names the requested artifact, intended use, constraints and stop condition; each assignment names its contribution, and synthesis supplies repository/file references and reuse guidance without a mandatory form.

### [AC-02] Review usefulness before retention

- **Given** a supported draft that omits the requested artifact or imposes an unwanted prerequisite.
- **When** the coordinator checks it or invokes discovery-critic.
- **Then** the check identifies the output gap or burden against the supplied goal and constraints, with a concrete repair; a critic can return zero findings and is not required on every run.

### [AC-03] Verify consequential gaps selectively

- **Given** a role return with inspected source identity, relevant location or finding and limits.
- **When** the coordinator validates it.
- **Then** it reviews that evidence without repeating the whole investigation by default; consequential gaps, contradictions or suspect support trigger targeted reopening or an explicit unverified claim.

### [AC-04] Recover from an ordinary retrieval failure

- **Given** a public-source timeout, broken link or unreadable result without an access refusal.
- **When** permitted retrieval remains within the original assignment bound.
- **Then** a bounded retry or legitimately accessible primary source is allowed, the failed retrieval and actual inspected replacement are reported, and a replacement that does not support the claim leaves it unverified.

### [AC-05] Stop denied or ambiguous access

- **Given** a permission, sandbox, trust or access refusal, or ambiguous authorization.
- **When** the coordinator or a role classifies the result.
- **Then** access to that resource stops without another tool, path, process, identity or setting bypass; independently useful permitted work can continue with the missing coverage explicit.

### [AC-06] Keep follow-up proportionate

- **Given** a small inquiry or a user who declines comparative validation.
- **When** the result and conditional roadmap are prepared.
- **Then** the request can finish inline, optional checks remain optional, and uncertain benefits are disclosed without making a comparison or further research an adoption prerequisite.

### [AC-07] Preserve deployed authority and ownership

- **Given** an installed consumer that explicitly selects deep-research.
- **When** sync and existing bundle/consumer checks run.
- **Then** the user-only entry and four local roles deploy with their references, no global research roles appear, removal preserves materials, and coordinator-only retention and no-commit authority remain intact.

## 5. Assumptions and Verification Limits

The approved proposal's premises still hold at handoff HEAD. This is a content-only change in one catalog feature;
no product screens change. Semantic review walks the six examples in `PROP-deep-research-practical-orchestration-target`.
Distribution tests verify installation and authority wording, not model obedience, research usefulness or superiority.
No before/after performance measurement is requested or claimed.
