---
name: git-commits
description: Read before drafting or creating a commit message.
---

# Git commit conventions

Write Conventional Commits messages with these choices:

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`; take scope names from the repository's history.
- Subject: imperative mood, no trailing period, in the repository's established message language.
- Body only when the subject does not explain the change: what changed and why, as `- ` bullets, one sentence per line, never hard-wrapped to a column.
- Claim only behavior and verification the commit's diff and check results support; add no sign-offs, approvals, citations or source annotations the repository does not require.
- When asked for a message, return only its text, without prose, headings or code fences.

```text
feat(cli): add project instruction discovery

- List instruction names, descriptions and paths so agents can discover project guidance without loading every body.
```
