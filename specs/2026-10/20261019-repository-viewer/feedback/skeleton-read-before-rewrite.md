---
id: FB-skeleton-read-before-rewrite
title: Skeleton files written by devkit commands are rewritten without a prior read
scope: repo
kind: change-request
category: redundant-step
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec-plan/SKILL.md
skill: spec-plan
agent: claude-code
origin: user
severity: workaround
recurring: true
status: open
created_at: 2026-10-19
---

# [FB-skeleton-read-before-rewrite] Skeleton files written by devkit commands are rewritten without a prior read

Applies equally to `spec-specify` (spec.md), `spec-tasks` (tasks.md) and the PADR step of Planning
(`devkit spec proposal padr`).

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `devkit spec proposal handoff`, `devkit spec new` and `devkit spec proposal padr` create
  skeleton files from the shell; the skills then say "Rewrite `plan.md` in place" (likewise `spec.md`, `tasks.md`)
  without telling the executor to read the skeleton first. Claude Code's Write tool refuses to overwrite an existing
  file the conversation has not read, so each whole-file rewrite fails once and is retried after a read.
- **Proposed Procedure**: in `spec-specify`, `spec-plan`, `spec-tasks` and the Planning PADR guidance, state that the
  executor reads the skeleton the command wrote (it carries the frontmatter to keep) before rewriting it.
- **Expected Benefit**: one failed tool call and one extra round trip fewer per rewritten file; the skeleton's carried
  frontmatter is seen before it is replaced, which the skills already require keeping.
- **Cost & Risk**: one sentence per skill; no behavior change for hosts without the restriction.
- **Attempted**: in this Unit the rewrite of `plan.md`, a PADR and a moved source file each failed once with the
  read-first refusal and succeeded after a read.

## Diagnostic Details

- **Reproduction**: run `devkit spec proposal handoff <slug>`, then write `plan.md` with the host's whole-file write
  tool without reading it.
- **Expected / Actual**: expected the rewrite to succeed; the host refuses: the file has not been read yet.
- **Versions**: devkit-spec at this Unit's branch; Claude Code terminal CLI.
- **Conditions**: any skeleton or pre-existing file the agent did not read in the current context.
- **Workarounds Attempted**: read the file, then write; succeeded.
- **Related Assets**: `spec-specify`, `spec-plan`, `spec-tasks` skills; `devkit spec proposal padr`.

## Evidence

```text
spec-plan SKILL.md §3: "Rewrite specs/<YYYY-MM>/<YYYYMMDD>-<slug>/plan.md, keeping its id and spec frontmatter."
Host refusal on the first write of plan.md and of PADR-read-only-local-server-over-git-refs.md:
"File has not been read yet. Read it first before writing to it."
```
