---
id: FB-nested-role-skill-read-scope
title: Nested role loads startup skill outside assigned worktree
scope: repo
kind: friction
category: instruction-conflict
target: .devkit/managed/spec/skills/spec-delegate/references/payload.md
skill: spec-delegate
agent: codex
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-21
---

# [FB-nested-role-skill-read-scope] Nested role loads startup skill outside assigned worktree

## 1. Friction / Question

- **Context**: A read-only challenger received an absolute assigned worktree and explicit read boundary.
- **Expectation**: Operational instructions and evidence would all be read from that worktree.
- **Actual**: Its return disclosed an initial response-style skill read from the base checkout's catalog path.
  Proposal and contract evidence came from the assigned worktree; it reported no edits or Git mutations.
- **Workaround**: Disclosed the exception to the Host and checked the assigned worktree's HEAD, index and paths.
  The outside read supplied reply formatting, not design evidence.
- **Suggestion**: Supply the assigned response-style path explicitly in nested-role payloads, and clarify how
  absolute startup-skill catalog paths interact with worktree-specific read boundaries.

## Diagnostic Details

- **Reproduction**: One native challenger call with an emulated contract; the returned boundary exception named
  the base response-style read. No repeated invocation was performed.
- **Expected / Actual**: Worktree-local instruction loading versus one reported base skill read.
- **Versions**: Reviewed HEAD baf66e2c224449fe5f44de65a031be2dfbfc673c; host version unknown.
- **Conditions**: Local orchestration with a sibling worktree and absolute base skill catalog entries.
- **Workarounds Attempted**: Assigned-tree HEAD and index inspection found no reviewer mutation; Host informed.
- **Related Assets**: response-style skill; spec-delegate payload instructions; Codex challenger projection.

## Evidence

```text
Challenger return: initial required response-style skill read used the base checkout path,
outside the assigned worktree; all proposal and contract evidence used the assigned worktree.
Host inspection: HEAD unchanged; index empty; only worker-authored proposal, blueprint and material changes.
```
