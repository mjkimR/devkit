---
id: FB-writing-style-rules
title: Encode the mechanical parts of the writing guidance as hygiene rules
scope: repo
kind: suggestion
category: other
target: authoring bundle rules
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-writing-style-rules] Encode the mechanical parts of the writing guidance as hygiene rules

Deferred work retained by `SPEC-writing-guidance-layers` (Non-Goal 2).

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `document-writing` and `agent-asset-writing` state the hedge-word, emphatic-capital and
  time-relative-word rules; only review enforces them.
- **Proposed Procedure**: Hygiene-phase warning rules for hedged directives ("likely", "might", "probably"),
  emphatic capitals outside defined keywords (RFC 2119, EARS) and time-relative words in bundle assets; bare
  prohibitions stay a review item because detection has false positives.
- **Expected Benefit**: The rules hold without a reviewer reading every line.
- **Cost & Risk**: False positives in quoted text and examples; the rules need an allowlist for quotations and code.
- **Attempted**: Hypothesis; restart after the rollout (`FB-writing-guidance-rollout`) shows which patterns recur.

## Diagnostic Details

- **Reproduction**: not applicable.
- **Expected / Actual**: not applicable.
- **Versions**: devkit-spec at the `SPEC-writing-guidance-layers` integration.
- **Conditions**: Depends on the rollout giving evidence of recurring patterns.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `ADR-writing-and-terminology-guidance`, the `document-writing` and `agent-asset-writing` instructions.

## Evidence

```text
Acceptance checks: each rule reports the file and line, runs in the hygiene phase only, and its tests cover a
quotation or code block that must not be reported.
```
