---
id: ADR-reject-ux-rules-path-exclusion
title: Reject a path-scoped opt-out of the UX document rules
summary: "For a namespace the screen contract seems not to fit, we reject a rule-owned exclude setting on the UX rules in favor of writing guidance for surfaces beyond pages and forms, to keep every UX rule on every document, accepting that an opt-out returns only on evidence from a real document."
status: accepted
created_at: 2026-11-04
---

# [ADR-reject-ux-rules-path-exclusion] Reject a path-scoped opt-out of the UX document rules

- **Status**: Accepted
- **Date**: 2026-11-04
- **Deciders**: the repository owner
- **Involved Components/Capabilities**: `capabilities/governance/`, `capabilities/harness/`, the docs bundle's `ux-writing` instruction

---

## 1. Context & Problem Statement

The proposal ~~`PROP-ux-rules-path-exclusion`~~ (rejected in commit `aa67659f`, deleted in this ADR's commit)
hypothesized that `RULE-ux-links` and `RULE-ux-coverage` describe a game package's interface, where controls and a
real-time viewport share one surface, worse than prose, and proposed a rule-owned `exclude` setting on both rules so a
namespace could switch the screen contract off while the identity, reference and summary rules kept checking the same
documents. Its Planning (~~`PADR-ux-rules-path-exclusion`~~, deleted with the proposal) settled the design: one setting
per rule, applied where each rule selects its documents, the shared UX model unchanged.

Planning also found that the rules refuse nothing a real-time or other non-page surface needs: the rules check only
the shape of the contract (`CAP-GOV-spec-rules` 3.15, 3.16), a viewport maps onto `screen`, an always-visible overlay
onto `panel` and an interrupting overlay onto `modal`, continuous input needs no row, and
`ADR-explicit-ux-coverage-exception-notation` classifies the controls that serve no step. The hypothesis rested on no
UX document of such a namespace.

---

## 2. Decision Drivers

- Every UX document keeps every UX rule; a namespace-wide switch hides contract violations with the mismatch it meant
  to tolerate.
- A rule change is made on evidence from a real document, not on a hypothesis.
- The smallest sufficient response to a writing problem is writing guidance.

---

## 3. Considered Options

### Option 1: Reject the opt-out and extend the `ux-writing` guidance (Selected)
- **Overview**: `SPEC-ux-writing-non-page-surfaces` adds criteria for surfaces beyond pages and forms to
  `ux-writing` and `usecase-writing`; a surface the criteria cannot describe is recorded as feedback with the document
  as evidence.
- **Pros**: no rule, engine or contract change; the guidance serves every domain, not one namespace.
- **Cons**: a namespace whose surface truly does not fit keeps reporting errors until a later change.

### Option 2: Accept the opt-out as a safety valve
- **Overview**: ship the `exclude` setting first and the guidance later.
- **Pros**: an immediate escape for a mismatched namespace.
- **Cons**: an excluded document's `element`, Interactions table and step links are checked by nothing; the setting
  would exist before any document showed the need.

### Option 3: Keep the proposal queued
- **Overview**: return the draft to Backlog until a game document exists.
- **Cons**: the Planning result would age beside the guidance that changes the premise.

---

## 4. Decision Outcome

We decided to adopt **Option 1**. The user's reason, from the rejection commit, unrewritten: "2번으로 일단 기각하고
지침 보강만 진행한 다음, 실제로 사용해보고 좀 안맞으면 그 때 해도 되나? ... 게임 국한하지는 말고 앱 말고 뭔가 특정 상황에서
쓰는 방법에 대한 포괄적인 지침으로 구성 가능하면 그게 더 좋음".

- `RULE-ux-links` and `RULE-ux-coverage` declare no path-scoped `exclude` setting; `[rules] exclude` stays the only
  path-scoped exclusion and switches off every rule.
- Surfaces beyond pages and forms are written under the criteria of the `ux-writing` instruction, catalogued in
  `CAP-HARN-agent-guidance` 4.3; a mismatch the criteria cannot resolve is recorded as feedback with the document.
- A later opt-out or a relaxed `element` kind starts as a new proposal that cites such a feedback record as its
  evidence; the Planning answers of the rejected proposal (one setting per rule, model unchanged) are reusable from
  commit `b7ff0ff8`.

---

## 5. Consequences

- **Positive**: the identity, reference, summary and both UX rules keep checking every UX document of every
  namespace; the guidance applies to games, kiosks, voice, terminal and status surfaces alike.
- **Negative / Risks**: a namespace whose surface still does not fit carries errors until its feedback becomes a
  proposal.
- **Follow-ups**: a feedback record of a surface the criteria cannot describe reopens the question as a new proposal.

---

## 6. Confirmation

Review only: `uv run devkit rules explain RULE-ux-links` and `RULE-ux-coverage` list no `exclude` setting, and the
`ux-writing` criteria are pinned by `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`.
