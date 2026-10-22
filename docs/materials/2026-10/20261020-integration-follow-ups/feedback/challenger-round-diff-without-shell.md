---
id: FB-challenger-round-diff-without-shell
title: Later challenger rounds cannot read their round's diff without a shell
scope: repo
kind: friction
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundle/subagents/challenger.md (x-git-actions, tools)
origin: agent
severity: workaround
recurring: false
status: resolved
resolved_at: 2026-10-19
disposition: "Granted read-only shell access in challenger subagent definition (Bash with Write/Edit disallowed on Claude Code; run_command with sandbox execution policy on Antigravity), matching x-git-actions: [read] and code-reviewer pattern."
created_at: 2026-10-19
---

# [FB-challenger-round-diff-without-shell] Later challenger rounds cannot read their round's diff without a shell

## 1. Friction / Question (friction, question)

- **Context**: A `high` Planning run of PROP-integration-follow-ups ran four challenger rounds. The bounded review
  loop says each later round "reviews every fix made since the previous round and what it affects, never a subset",
  and the payload of each later round passed a commit range for `git diff`.
- **Expectation**: The challenger can read the round's diff scope it is given, as `code-reviewer` can (it has Bash).
- **Actual**: The projected challenger has Read, Grep and Glob only (`x-git-actions: [read]` projects to no shell).
  Rounds 2, 3 and 4 each reported "no shell, did not run the diff" and reviewed the files at the head instead, with
  the round's scope inferred from the previous findings. Coverage of "every fix since the previous round" was an
  assumption each round recorded.
- **Workaround (or Interpretation Chosen)**: Named the fixed sections in the round's prompt and accepted head-state
  review; each envelope carries the assumption.
- **Suggestion**: Either give the challenger read-only Git access for diff scopes (as `x-git-actions: [read]`
  suggests), or have the Planning worker pass the round's diff text in the prompt, and say which in review-loop.md
  section 1.

## Evidence

```text
challenger frontmatter: x-git-actions: [read]; projected tools: Read, Grep, Glob
round 2 summary: "I had no shell, so I read the files as they stand at the worktree head (fa5528c) and did not run the git diff."
round 3 / round 4 assumptions: "no shell, so the <base>..<head> diff was not run"
envelopes/challenger-02.yaml, challenger-03.yaml, challenger-04.yaml (assumptions)
```
