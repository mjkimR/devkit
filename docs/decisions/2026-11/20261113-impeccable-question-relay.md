---
id: ADR-impeccable-question-relay
title: Capability-gated Impeccable question relay
summary: "For interactive Impeccable work, we relay questions through a verified resumable child with every answer user-confirmed, to keep one request context, accepting user-session fallback where host capabilities are unverified."
proposal: SPEC-uiux-improve-impeccable-routing
supersedes: [ADR-impeccable-session-authority]
status: accepted
created_at: 2026-11-13
---

# [ADR-impeccable-question-relay] Capability-gated Impeccable question relay

- **Status**: Draft; direction ready for plan acceptance.
- **Date**: 2026-11-13

## 1. Context & Problem Statement

`ADR-impeccable-session-authority` keeps interactive Impeccable commands in a user-operated session. A coordinator
can relay a complete question packet without answering for the user, but a writing phase needs the same child's
state, native skill loading and the tools that the upstream command requires. Pilot cache reads establish none of
those capabilities. `MAT-impeccable-routing-planning` separates documentation, a continuation probe and unmet live checks.

## 2. Decision Drivers

- Keep every answer attributable to explicit user confirmation.
- Preserve supported host skill loading and current-project enablement.
- Gate dependent writes on observed capabilities and unchanged relevant source facts.
- Preserve the consumer's permissions, context-file ownership and coordinator acceptance.
- Keep a user-operated fallback without adding runtime or persistent records.

## 3. Considered Options

- Keep every interactive command user-operated: unchanged authority, with a manual handoff even on capable hosts.
- Capability-gated relay: a read-only question phase, complete user confirmation and same-child continuation;
  preserves answer ownership at the cost of host checks and fallback where unverified.
- Unconditional relay with cache reads: convenient under a missing native load path, but unsupported by a stable
  cache contract and unable to establish skill enablement or nested-role coverage.

## 4. Decision Outcome

Selected direction: capability-gated relay. The user sets empirical validation to best-effort for this personal
project. The two requested native plugin-load checks remain unverified and do not hold Planning; this draft
certifies no live-supported host.

- After the user selects Impeccable, relay is available only when native loading and same-child continuation are
  observed for the actual host and project; otherwise the command remains user-operated.
  → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The question phase writes no retained files, product files, index or HEAD. Every answer, including source-cited
  pre-fills, is confirmed by the user before the same child writes under the brief. Additional questions or changed
  relevant source facts return to confirmation. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- Commands requiring nested roles additionally need those capabilities available in the child; unavailable or
  unverified capabilities use the user-operated session. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- Load failures disclose observed current-project enablement and native availability. Cache reads are not a
  sanctioned loading route; installation and enablement retain existing user-requested authority.
  → `CAP-DLV-uiux-improvement` rules 10 and 19 (MUST).
- Existing context-file permissions, exclusive product-writer interval and coordinator acceptance remain in force.
  → `CAP-DLV-uiux-improvement` rules 16, 17 and 19 (MUST).

Supersedes in part `ADR-impeccable-session-authority`: Decision Outcome clause restricting fresh children to answer-free refinement and routing every interactive command to a user-operated session.

Its native skill-loading requirement and all other in-force clauses remain. Consumer workflow authority is owned
separately by `SPEC-uiux-improve-run-model`; this decision neither chooses nor changes that proposal's outcome.

## 5. Consequences

- A capable host can retain the user's interactive work in one coordinated request without the coordinator choosing
  answers for the user.
- The coordinator must present every pre-fill and source, even when existing documents appear to settle an answer.
- A host or plugin configuration that has not passed the capability checks still requires a user-operated session.
- Native Impeccable loading on Claude Code and Codex and end-to-end relay remain unverified. A same-child Codex
  continuation probe and documentation statements are narrower evidence.
- The pilot cache read remains documented as an observed workaround, without becoming a supported route.
- Product-write boundaries remain behavioral on hosts without native path enforcement; existing comparisons report
  unexpected changes rather than silently accepting or reverting them.

## 6. Confirmation

- `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`: instruction assertions for selection,
  native loading, complete confirmation, same-child resume, capability fallback, write pause and existing permissions.
- Review only: packet completeness, answer attribution, changed-source re-confirmation and whether an upstream
  command's nested roles are actually available to the child.
- Native plugin-load and interactive checks on both hosts remain unmet until performed with the current project
  enabled. No assertion or generic continuation probe substitutes for those observations.
