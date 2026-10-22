# Feedback template

Read this when writing a feedback file. Copy the block inside the four-backtick fence, replace every `<...>`
placeholder, follow the comment, then delete it.

````markdown
---
id: FB-<name>
title: <title>
scope: repo                         # repo | upstream | unknown
kind: friction                      # friction | suggestion | change-request | question
category: other                     # see Categories below
target: <asset path or command>     # e.g. the spec-specify skill, devkit spec list, CAP-<AREA>-<slug>
skill: none                         # active skill when observed, or none
agent: <claude-code | codex | antigravity | ...>
origin: agent                       # agent | user
severity: workaround                # critical | blocked | workaround | noise
recurring: false
status: open
created_at: <YYYY-MM-DD>
---

# [FB-<name>] <title>

<!--
friction / question: fill Section 1 and remove Section 2; suggestion / change-request: the reverse.
Evidence is only what you observed: excerpts of instructions or documents, summarized command output, file state.
Never quote or paraphrase the user; their remark is not evidence.
Mask local paths, usernames and identifiers (<repo>, <worktree>) and include no secrets: the file is shared in the PR.
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

## Categories

| category | Meaning |
| :--- | :--- |
| `instruction-conflict` | Instructions conflict with each other, or with repository reality |
| `tool-error` | CLI or skill command failed, or an advisory gave wrong guidance |
| `spec-ambiguity` | spec/plan/tasks wording left the decision open |
| `context-overflow` | Required reading was too large; something was skipped or summarized |
| `missing-capability` | A needed command, field, template or rule does not exist |
| `docs-mismatch` | Guide or capability document differs from actual behavior |
| `redundant-step` | A step that does not contribute to the result; duplicate reads or checks |
| `token-cost` | Text read every session but not used |
| `other` | None of the above |

## Detail level

`FEEDBACK_POLICY detail` in `devkit spec policy` sets the level; frontmatter and your assessment are complete at every
level.

- **brief**: the applicable section's context, the observation or proposed change, a short assessment and Evidence.
- **standard**: the applicable section and Evidence.
- **detailed**: standard plus this section before Evidence. Write `unknown` for a missing fact instead of rerunning a
  risky or expensive command, and `not applicable` for a field that does not apply.

```markdown
## Diagnostic Details

- **Reproduction**: Observed steps and command, or unknown when not reproduced.
- **Expected / Actual**: Expected behavior and the directly observed result.
- **Versions**: Known tool/package versions or revision.
- **Conditions**: Relevant repository, configuration, host and occurrence conditions.
- **Workarounds Attempted**: Attempts and their outcomes, or not attempted.
- **Related Assets**: Observed command, source paths, instructions or document IDs.
```
