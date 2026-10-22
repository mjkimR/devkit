---
id: FB-proposal-template-feedback-resolution-stale
title: Proposal template still implies promoted feedback waits for verified completion
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundle/templates/proposal.md Source feedback comment
skill: spec
agent: codex
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-proposal-template-feedback-resolution-stale] Proposal template still implies promoted feedback waits for verified completion

## 1. Friction / Question

- **Context**: Inspecting the proposal template while clarifying Planning decomposition recovery.
- **Expectation**: Template guidance matches the terminal lifecycle in `ADR-feedback-lifecycle`.
- **Actual**: Its Source feedback comment says promotion routes an observation and only verified task completion
  resolves it, which invites the superseded promoted-to-resolved transition.
- **Workaround (or Interpretation Chosen)**: Applied the current completion procedure: only explicitly linked open
  direct-fix sources were resolved; terminal sources were not edited.
- **Suggestion**: Align the comment with promotion as terminal handoff and resolution as a direct verified fix.
  No feedback-state migration is needed.

## Diagnostic Details

- **Reproduction**: Read the template Source feedback comment at the worker base.
- **Expected / Actual**: Expected terminal distinction; actual wording implies deferred source resolution.
- **Versions**: Repository base b4a1aaa2b9699b065b33225b9fc8a4d7d6552a1e.
- **Conditions**: Source template is agent-facing guidance copied into proposals; this is a documentation mismatch.
- **Workarounds Attempted**: Followed the current completion skill and accepted ADR; no template edit in this task.
- **Related Assets**: `ADR-feedback-lifecycle`, spec completion reference and proposal template.

## Evidence

```text
Source feedback comment:
Promotion routes the observation; only verified task completion resolves it.
Current completion procedure:
promoted is terminal once handed to identified follow-up work.
```

## Disposition

The session corrected `packages/devkit-spec/src/devkit_spec/bundle/templates/proposal.md` to match
`ADR-feedback-lifecycle`: promotion is terminal handoff, and resolution is a verified direct fix
without promotion. Official bundle sync updated the installation receipt. No feedback-state migration was made.

Verification: low-effort self-review compared the final template with the accepted terminal-state contract;
`just lint-check spec`, `just check spec` and `just test-affected --base main` passed (1,111 tests).
