---
id: FB-auto-integration-without-mcp-session
title: dev-integration=auto has no route when the session lacks the devkit MCP tools
scope: repo
kind: question
category: spec-ambiguity
target: spec skill references/completion.md (Policy)
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-auto-integration-without-mcp-session] dev-integration=auto has no route when the session lacks the devkit MCP tools

## 1. Friction / Question (friction, question)

- **Context**: The repository sets `dev-integration=auto`; the session reached `integrate` without the devkit MCP
  server (it was not registered for the parent directory the session started in).
- **Expectation**: Policy `auto` delegates the gate to the Host after readiness checks.
- **Actual**: The completion reference says auto authorizes local merge only through `integration_integrate`, and
  "without MCP, auto has no automatic CLI substitute; manual execution requires separate authority", so the
  verified result waits for a user decision although the policy is `auto`.
- **Workaround (or Interpretation Chosen)**: The Host asked the user for the CLI fallback
  (`devkit worktree finish <branch> --merge --local-only`) instead of merging on policy.
- **Suggestion**: State in the completion reference whether this is intended (auto is MCP-only by design) and, if so,
  tell the Host to say so in the final report, or name `devkit mcp` onboarding as the step that restores the route.
