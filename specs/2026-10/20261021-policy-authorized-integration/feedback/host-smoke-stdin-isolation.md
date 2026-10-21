---
id: FB-host-smoke-stdin-isolation
title: Close stdin when launching one-shot host smoke clients
scope: upstream
kind: suggestion
category: other
target: codex exec and claude -p smoke launchers
skill: spec
agent: codex
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-21
---

# [FB-host-smoke-stdin-isolation] Close stdin when launching one-shot host smoke clients

## Suggestion

This concerns subprocess input isolation during live host verification.

- **Current Procedure**: One-shot host clients were launched from a Python here-document with an explicit prompt but inherited stdin.
- **Proposed Procedure**: Set subprocess stdin to DEVNULL when the prompt is already an argument; use a deliberate pipe only for intended prompt content.
- **Expected Benefit**: Prevent launcher source from being appended to the intended smoke prompt and keep test evidence easier to interpret.
- **Cost & Risk**: Intentionally piped prompt workflows must retain their explicit input.
- **Attempted**: Both hosts completed the intended single integration call; the improved launcher input isolation was not rerun because the mutation evidence was already complete.

## Diagnostic Details

- **Reproduction**: Launch the explicit-prompt CLI as a subprocess from a Python here-document while inheriting stdin.
- **Expected / Actual**: Only the specified prompt was intended; Codex reported reading stdin, and Claude's result explicitly declined to execute Python text received after the prompt.
- **Versions**: Codex CLI 0.163.0; Claude Code 2.1.305.
- **Conditions**: Disposable local repositories, explicit MCP tool permission, no global configuration edits.
- **Workarounds Attempted**: Inspected resulting refs and filesystem independently; both matched the requested integration and cleanup.
- **Related Assets**: Live host-smoke material in this unit; CLI launch procedure, not integration service behavior.

## Evidence

Codex stderr: `Reading additional input from stdin...`.
Claude's result reported exactly one tool call and stated it did not run appended Python text.
