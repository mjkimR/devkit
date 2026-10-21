# Feedback template

Read this when writing a feedback file (step 3 of the `spec-feedback` recording procedure). Copy the block inside the four-backtick fence, replace every `<...>` placeholder, follow and then delete the comment.

````markdown
---
id: FB-<name>
title: <title>
scope: repo                         # repo | upstream | unknown; ownership of the observed asset, filled by the agent
kind: friction                      # friction | suggestion | change-request | question
category: other                     # instruction-conflict | tool-error | spec-ambiguity | context-overflow | missing-capability | docs-mismatch | redundant-step | token-cost | other
target: <asset path or command>     # e.g. the spec-specify skill, devkit spec list, CAP-<AREA>-<slug>
skill: none                         # active skill when observed (spec, spec-specify, spec-review, ...) or none
agent: <claude-code | codex | antigravity | ...>
origin: agent                       # agent | user  (user = raised by the user)
severity: workaround                # critical | blocked | workaround | noise
recurring: false                    # true if observed 2+ times
status: open                        # only actionable status; promoted/resolved/dismissed/forwarded are terminal
created_at: <YYYY-MM-DD>
---

# [FB-<name>] <title>

<!--
One incident per file, at the configured detail level (brief/standard take about one minute).
friction / question: fill Section 1 and remove Section 2; suggestion / change-request: the reverse.
Evidence is only what you observed yourself: instruction or document excerpts, summarized command output, file state.
Excerpt key lines instead of raw output, and mask local paths and identifiers (<repo>, <worktree>).
The user's remark is not evidence; never quote or paraphrase the user anywhere in the file.
Never include secrets, tokens or personal data (local usernames and absolute paths included): the file is shared in the PR.
If category is other, state the nature in the first line below.
-->

## 1. Friction / Question (friction, question)

- **Context**: What was being done
- **Expectation**: What the documentation/instructions promised
- **Actual**: What actually happened
- **Workaround (or Interpretation Chosen)**: How it was bypassed or interpreted
- **Suggestion**: What to fix so future runs avoid getting blocked here

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: How it is currently done
- **Proposed Procedure**: How it should change
- **Expected Benefit**: Reduced steps, tokens, or decision fatigue
- **Cost & Risk**: What could break if changed
- **Attempted**: Tested in this session vs hypothesis

## Evidence

```text
<Directly observed excerpts, summarized command output, or file state.>
```
````

## Configured detail

`FEEDBACK_POLICY detail` from `devkit spec policy`. Every level keeps complete frontmatter, the rules of the comment
above and the agent's own assessment.

- **brief**: retain the applicable section with context/current procedure, actual observation or proposed change,
  a short assessment and Evidence. Omit unused template bullets.
- **standard**: fill the applicable kind-specific section and Evidence as shown above.
- **detailed**: standard plus the following section before Evidence. Fill missing facts with `unknown` (never
  fabricate output, versions or reproduction results) and `not applicable` where a field does not apply; do not rerun
  risky or expensive commands just to complete the record.

```markdown
## Diagnostic Details

- **Reproduction**: Observed steps and command, or unknown when not reproduced.
- **Expected / Actual**: Expected behavior and the directly observed result.
- **Versions**: Known tool/package versions or revision; unknown for unavailable versions.
- **Conditions**: Relevant repository, configuration, host and occurrence conditions, without personal data.
- **Workarounds Attempted**: Attempts and their outcomes, or not attempted.
- **Related Assets**: Observed command, source paths, instructions or document IDs.
```
