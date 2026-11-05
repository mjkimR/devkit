---
id: ADR-explicit-solution-exploration
title: Keep general solution exploration explicitly invoked and self-contained
summary: "For general solution design, we ship an independent user-invoked skill with local optional roles, to explore distinct mechanisms without ambient role guidance, accepting repeated coordination text."
proposal: SPEC-design-solution-exploration
status: accepted
created_at: 2026-11-05
---

# [ADR-explicit-solution-exploration] Keep general solution exploration explicitly invoked and self-contained

## 1. Context & Problem Statement

General solution design needs different mechanisms and tradeoffs for architecture, models and workflows. Its
result can be useful without a sourced research report or implementation. The user wants explicit invocation and
role files loaded for that work, avoiding specialist guidance in unrelated tasks. `ADR-skill-local-research-roles`
provides a distribution precedent but governs research roles, not this independent design capability.

## 2. Decision Drivers

- Preserve the supplied problem's goal and hard constraints while exploring different mechanisms.
- Avoid mandatory implementation, research reports or comparative-benefit validation.
- Keep optional role bodies out of ambient project guidance and global specialist registration.
- Reuse existing catalog distribution without a shared orchestration runtime or mandatory companion bundle.

## 3. Considered Options

- Extend deep-research: reuses an entry but brings an investigation/material outcome into general design discussion.
- Keep general design in ordinary conversation: requires no bundle but offers no reusable explicit entry or role packet.
- Add an independent user-invoked skill with local roles: fits the goal, while repeating concise coordination text.

## 4. Decision Outcome

- General solution exploration has one independent `design-explore` entry and opt-in content-only catalog bundle.
  It does not invoke or depend on deep-research, UI/UX improvement or adaptive-dev.
  → `CAP-DLV-design-exploration` rules 1–2 (MUST) and section 2.
- The skill loads selected local role documents and passes bounded assignments to general children with fresh
  contexts where supported. It registers no specialist subagents or always-loaded guidance.
  → `CAP-DLV-design-exploration` rules 1, 3 (MUST), 4 (SHOULD) and 5 (MUST).
- The result explains useful solution mechanisms, tradeoffs and decision-changing assumptions. It returns in
  conversation unless the user requests another destination; coordinator-owned retention confers no implementation,
  commit, delivery approval or publication authority.
  → `CAP-DLV-design-exploration` rules 6–9 (MUST) and 11 (SHOULD).

This decision changes no existing research ADR.

## 5. Consequences

The entry serves general design without a mandatory report or delivery workflow. Roles and premises can be selected
for the problem instead of always starting a cast. Coordination text is repeated across independent bundles and must
be maintained locally. Fresh contexts reduce carryover but do not isolate files, credentials or ambient instructions;
when unavailable, inline passes disclose that limitation.

## 6. Confirmation

Catalog integration and installed-consumer tests verify opt-in selection, user-only metadata, local role packaging,
no global role projection and independent removal. Review checks the goal, role payloads, inline fallback and
retention authority. No test measures creativity or proves team benefit. `CAP-DLV-design-exploration` restates the retained contracts;
`UC-explore-a-design-problem` maps their observable outcomes.
