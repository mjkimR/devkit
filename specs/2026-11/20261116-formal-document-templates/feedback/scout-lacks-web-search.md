---
id: FB-scout-lacks-web-search
title: "The scout contract allows external research but grants no web search on Claude Code"
scope: repo
kind: friction
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/scout.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-scout-lacks-web-search] The scout contract allows external research but grants no web search on Claude Code

## 1. Friction / Question (friction, question)

- **Context**: A Planning run needed surveys of external template repositories and template-management systems
  (KEP, MADR, arc42, runbook templates, Copier) to polish a proposal.
- **Expectation**: The scout contract's procedure step 4 admits external material when `task_goal` asks for it, so a
  native scout should be able to find the sources.
- **Actual**: The Claude Code host entry lists `tools: [Read, Grep, Glob, WebFetch, Bash]`. Without web search a
  scout can only fetch URLs the caller already knows, which defeats a survey whose sources are not known in advance.
- **Workaround (or Interpretation Chosen)**: Three external surveys ran as `role-worker` subagents emulating the
  scout contract, with "write nothing" in the payload; the caller compared Git snapshots before and after and
  recorded the returns as `scout` envelopes with the emulation stated in `assumptions`.
- **Suggestion**: Add `WebSearch` to the scout's Claude Code tools (it remains read-only), or state in the contract
  that external discovery requires an emulated route and how to record it.

## Diagnostic Details

- **Reproduction**: Delegate a scout whose `task_goal` asks for a survey of external sources not named in the payload.
- **Expected / Actual**: Expected source discovery; actual tool set allows only fetching given URLs.
- **Versions**: devkit worktree at the Planning head of `SPEC-formal-document-templates`.
- **Conditions**: Claude Code host, `native` scout route.
- **Workarounds Attempted**: `role-worker` emulation; succeeded, with the diff check as the only write guard.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/scout.md`, the
  `spec-delegate` skill.

## Evidence

```text
scout.md hosts.claude-code: status: native, tools: [Read, Grep, Glob, WebFetch, Bash]
scout.md Procedure 4: "Use external material only when task_goal asks for it: official and primary sources ..."
```
