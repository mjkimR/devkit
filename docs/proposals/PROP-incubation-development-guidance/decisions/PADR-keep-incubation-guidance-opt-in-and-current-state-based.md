---
id: PADR-keep-incubation-guidance-opt-in-and-current-state-based
title: Keep incubation guidance opt-in and current-state based
summary: "For developing ideas without SDD, we ship an opt-in incubation catalog bundle and mutable current context, to resume useful work without delivery records, accepting semantic evaluation of guidance."
proposal: PROP-incubation-development-guidance
status: draft
created_at: 2026-10-28
---

# [PADR-keep-incubation-guidance-opt-in-and-current-state-based] Keep incubation guidance opt-in and current-state based

## 1. Context & Problem Statement

Document formats are independently available under `ADR-document-and-sdd-bundles`. Incubation also needs agent
coordination, optional support roles and resumable current facts without SDD records. Shared docs authoring policy
must serve other development approaches, while spec assets intentionally impose SDD.

## 2. Decision Drivers

- Incubation installs without devkit-spec and does not activate in existing SDD repositories implicitly.
- Reuse distribution and projection mechanisms without another release wheel or runtime service.
- Preserve enough current context to resume, without reconstructing delivery history.
- Verify actual discovery and usage behavior in addition to asset integrity.

## 3. Considered Options

- Keep existing SDD skills: smallest asset count, but product discovery still enters a delivery lifecycle.
- Put guidance into docs: fewer selections, but approach-specific entry contaminates generic document installation.
- Add a dedicated incubation wheel: independent release ownership, with extra wheel/release wiring and no distinct
  runtime dependency currently requiring it.
- Use an opt-in incubation bundle in devkit-catalog: existing independent content distribution and explicit selection,
  at the cost of catalog installation alongside docs and a separate applicability check.
- Keep resume state only in conversation: no file, but the next session cannot resume without history.
- Use SDD records or immutable product decisions: existing formal artifacts, but impose the lifecycle being omitted.

## 4. Decision Outcome

Recommend `incubation:core` in devkit-catalog, one `/incubate` coordinator, three optional support contracts and a
project-owned mutable `.devkit/incubation.md`. The skill reads the common effective approach before acting; bundle
selection itself grants no runtime approach change. Shared document instructions remain in docs.

Context records current goal, retained choices versus assumptions, run and verification evidence, unresolved questions
and next useful action. Only the coordinator updates it. Retention follows current usefulness rather than immutable
history. The baseline proposal consumes semantic facts and does not require parsing this filename.

## 5. Consequences

- Positive: the complete incubation path is opt-in, independent of SDD assets and resumable across sessions.
- Negative: consumers install catalog and docs, and guidance behavior needs semantic walkthrough evidence.
- Risks: stale context can mislead a later session; source identity, current checks and explicit uncertainty limit that
  risk. Applicable policy must be refreshed against the accepted lifecycle-policy interface before Development.
- Follow-up: optional SDD adoption remains `PROP-incubation-sdd-baseline`; runtime applicability remains
  `SPEC-incubation-lifecycle-policy`.

## 6. Confirmation

Build-wheel isolation, catalog manifest/projection/reference tests and context-byte preservation exercise distribution.
Bounded scenario walkthroughs exercise incomplete-goal discovery, research/experiments, inline and delegated iteration,
usage verification and cross-session resume. Review compares results to AC-01 through AC-06; token checks alone are
insufficient. The implementation plan selects exact test paths after the policy interface is accepted.
