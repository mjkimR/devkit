---
id: FB-projection-guard-after-mid-session-install
title: An explicit-only projected skill gives no route after a mid-session install
scope: repo
kind: question
category: spec-ambiguity
target: CAP-DIST-agent-projections
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-projection-guard-after-mid-session-install] An explicit-only projected skill gives no route after a mid-session install

## 1. Friction / Question (friction, question)

- **Context**: In a consumer repository, `app-uiux-improve` was added with `devkit add` during a Claude Code session.
  The projected skill carries `disable-model-invocation: true` and the entry guard "run only when the user explicitly
  invokes this entry". The coordinator named the skill and the user agreed to proceed in natural language.
- **Expectation**: Either the agreement counts as explicit invocation and the skill runs, or the guard says what
  the user must do instead.
- **Actual**: The coordinator could not invoke the skill through the host's skill mechanism and followed the projected
  `SKILL.md` text manually, which bypasses the guard the projection exists to enforce.
- **Workaround (or Interpretation Chosen)**: Manual reading of the projected `SKILL.md`.
- **Suggestion**: Decide in `CAP-DIST-agent-projections` (it owns the `disable-model-invocation` projection) what
  a mid-session install should tell the user: for example, to reload the session or type the slash command, and
  whether reading the projected file manually is acceptable. Unverified: whether the slash command was unavailable
  for the rest of the session or only until the host reloaded its skill list; check that first.

## Diagnostic Details

- **Reproduction**: unknown; observed once. Install an `invocation = "user"` bundle mid-session in Claude Code, then
  ask the agent to run it after a natural-language agreement.
- **Expected / Actual**: Expected a defined route; actual no invocation and a manual workaround.
- **Versions**: `app-uiux-improve` 0.1.6; Claude Code version unknown.
- **Conditions**: consumer repository, mid-session `devkit add`, Claude Code host.
- **Workarounds Attempted**: manual reading of the projected `SKILL.md` (works, bypasses the guard).
- **Related Assets**: `CAP-DIST-agent-projections`, `CAP-DLV-uiux-improvement` rule 2, `MAT-uiux-improve-pilot`
  finding A6.

## Evidence

```text
CAP-DIST-agent-projections: user-invocation skills project `disable-model-invocation: true` as the last
frontmatter key. Pilot finding A6: after the mid-session install the coordinator could not invoke the skill and
followed the projected SKILL.md text manually.
```
