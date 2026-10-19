---
id: FB-padr-title-branch-length-limit
title: PADR titles are refused by the activity-branch slug limit
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal padr
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-padr-title-branch-length-limit] PADR titles are refused by the activity-branch slug limit

## 1. Friction / Question (friction, question)

- **Context**: Planning recorded a preliminary decision with `devkit spec proposal padr <slug> "<title>" --summary ...`.
- **Expectation**: A PADR's slug becomes a file name (`decisions/PADR-<name>.md`), never a branch, so only file-name
  limits apply.
- **Actual**: The command refused a 63-character slugged title with `SPEC_PROPOSAL_SLUG_INVALID`, whose message
  justifies the 59-character cap by the activity branches `plan-<slug>` and `dev-<slug>`, which a PADR does not have.
- **Workaround (or Interpretation Chosen)**: Shortened the title.
- **Suggestion**: Give PADR names their own limit and message (or none beyond the file system), or at least a message
  that does not cite activity branches.

## Evidence

```text
devkit spec proposal padr envelope-record-gaps "Close challenger rounds with reverify and count unmarked rounds" --summary ...
[ERROR] (SPEC_PROPOSAL_SLUG_INVALID) title 'close-challenger-rounds-with-reverify-and-count-unmarked-rounds' is 63 characters;
        at most 59, so its activity branches plan-<slug> and dev-<slug> fit 64 characters
packages/devkit-spec/src/devkit_spec/proposals/scaffold.py: new_slug() raises with SLUG_LIMIT for every "what"
```
