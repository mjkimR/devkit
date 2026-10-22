---
id: FB-role-subagents-outside-session-root
title: Projected role subagents are not loadable when the agent session is rooted above the repository
scope: repo
kind: friction
category: missing-capability
target: spec-delegate skill references/hosts.md
skill: spec-delegate
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-role-subagents-outside-session-root] Projected role subagents are not loadable when the agent session is rooted above the repository

## 1. Friction / Question (friction, question)

- **Context**: A Claude Code session started in a parent workspace directory (holding several repositories) ran this
  spec Unit in the devkit task worktree, and the review stages named `code-reviewer` and `reconcile-reviewer`.
- **Expectation**: `hosts.md` lists both roles as `native` for Claude Code, through the projected `.claude/agents/`.
- **Actual**: The session's agent list held only the host's built-in types; the projected roles of the repository
  were not offered, because Claude Code loads `.claude/agents/` from the session root, not from the worktree.
- **Workaround (or Interpretation Chosen)**: Each round used a generic subagent that read the effective contract under
  `.devkit/managed/spec/subagents/`, stated as emulation in the envelopes' assumptions.
- **Suggestion**: Name this case in `hosts.md` (session root outside the repository) as a known cause of an
  unavailable named role, so the emulation fallback is chosen without diagnosis.
