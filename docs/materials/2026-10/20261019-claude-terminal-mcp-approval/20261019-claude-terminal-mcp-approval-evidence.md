---
id: MAT-claude-terminal-mcp-approval-evidence
title: Claude Code terminal MCP integration approval evidence
summary: "Observations from one interactive Claude Code terminal session that ran integration_integrate through native MCP form elicitation for no-approval, decline, cancel and approve outcomes."
created_at: 2026-10-19
---

# [MAT-claude-terminal-mcp-approval-evidence] Claude Code terminal MCP integration approval evidence

Evidence for `SPEC-claude-terminal-mcp-approval`, collected on 2026-10-19 from one interactive Claude Code terminal
session. It records what was observed and what the run did not establish; the contract is `CAP-INT-mcp-services`.

## 1. Environment and setup

- Host: Claude Code 2.1.303, interactive terminal CLI on macOS (Darwin 24.6.0).
- Server: the unchanged devkit MCP server from the retained base checkout and its `.venv`, registered in Claude Code
  user scope with the `command` and `args` that `devkit host mcp config --format json` printed:

  ```bash
  claude mcp add --scope user devkit -- <base>/.venv/bin/python3 -m devkit host mcp serve --workspace-root <base>
  ```

  `claude mcp get devkit` reported user scope, stdio and `Connected`.
- Base: `main` at `8fc64ef`, clean, equal to `origin/main`; `[integration] provider = "spec"`,
  `dev-integration=ask`, `pull_request=auto`, `delete_branch=yes`.
- Task: a session task on `dev-claude-approval-test`, created with `devkit worktree start`, holding one empty commit
  (`4c396e2`). Calls used `task_kind="session"`, `task_id="claude-approval-test"` and passing feature/low claims.
- A new Claude Code terminal session started in the base exposed the devkit integration tools and called them.

## 2. Observed outcomes

Each row is one `integration_integrate` call answered in the native form that Claude Code rendered.

| Form response | Result | Git effect |
| --- | --- | --- |
| Submitted without checking approval | `status: not_approved`, `ui_action: accept` | none |
| Decline | `status: declined`, `ui_action: decline`, no authority | none |
| Escape | `status: cancelled`, `ui_action: cancel` | none |
| Approval checked and submitted | `status: completed`, `authority: mcp-elicitation` | see below |

The three non-approving calls reported the same request digest (prefix `71be5f9c`), so the form scope did not change
between them. After the approving call, every step reported `completed`: fast-forward, worktree removal, branch
deletion and the devkit-spec scoped cleanup. Git state confirmed it: local `main` moved from `8fc64ef` to `4c396e2`,
the worktree directory and registration were gone, the local branch was deleted and `origin/main` stayed at
`8fc64ef` (no push). The empty test commit was then removed from local `main` with `git reset --keep origin/main`.

## 3. Not established

- Behavior under Claude Code auto mode or other permission modes; the run did not compare them.
- How many prompts appeared per call: the Claude Code MCP tool permission prompt and the devkit form were not counted
  separately.
- Claude Desktop, the VS Code extension and Agent SDK sessions; upstream reports describe elicitation declined
  without a visible form there (`MAT-native-approval-host-comparison` §3).
- Stale-scope invalidation and partial-cleanup resume in a native Claude session; SDK tests cover them.
- Unit (spec bundle) tasks; only a session task was integrated.
