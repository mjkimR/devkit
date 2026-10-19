---
id: FB-smoke-response-style-path
title: Consumer smoke reads a response-style instruction path the bundle no longer deploys
scope: repo
kind: friction
category: tool-error
target: scripts/smoke.sh
skill: none
agent: claude-code
origin: agent
severity: blocked
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-smoke-response-style-path] Consumer smoke reads a response-style instruction path the bundle no longer deploys

## 1. Friction / Question (friction, question)

- **Context**: running `just smoke` to verify this Unit's new viewer smoke section.
- **Expectation**: `just smoke` passes on the base branch, so a new section can be verified end to end.
- **Actual**: the "response templates" step asserts on `.devkit/managed/response-style/instructions/response-style.md`,
  which does not exist in the consumer project; the run stops there with `FileNotFoundError`, before the spec and
  viewer sections. The same failure occurs on the base branch at merge commit b942326, so it predates this Unit.
- **Workaround (or Interpretation Chosen)**: the viewer section was replayed in a fresh consumer project with the
  built wheels and passed; the full smoke stays unverified for this Unit.
- **Suggestion**: align the smoke assertion with where the templated response-style bundle now deploys its text
  (the recent templated skill deployment), or restore the instruction file if the move was unintended.

## Diagnostic Details

- **Reproduction**: `just smoke` on the base branch.
- **Expected / Actual**: expected `==> smoke passed`; got exit 1 at the response-templates step.
- **Versions**: base branch b942326.
- **Conditions**: macOS, uv-managed CPython 3.13 in the consumer project.
- **Workarounds Attempted**: replayed only the viewer section; passed.
- **Related Assets**: `scripts/smoke.sh` (response templates step), the `response-style` catalog bundle.

## Evidence

```text
--- response templates: lazy imports, configured language and final output
    assert "Use ko as the default" in path.read_text()
FileNotFoundError: [Errno 2] No such file or directory: '.devkit/managed/response-style/instructions/response-style.md'
```
