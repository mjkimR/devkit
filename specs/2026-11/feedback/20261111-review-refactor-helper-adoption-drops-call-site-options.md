---
id: FB-review-refactor-helper-adoption-drops-call-site-options
title: Adopting a shared helper silently dropped a call site's extra hardening
scope: repo
kind: change-request
category: missing-capability
target: packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/references/criteria.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-11
---

# [FB-review-refactor-helper-adoption-drops-call-site-options] Adopting a shared helper silently dropped a call site's extra hardening

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `criteria.md` §4 asks for reachability, verification before and after, and differential
  comparison for parsers and similar enumerable functions. When a call site is moved onto a consolidated helper,
  nothing asks for the arguments that call site passed and the helper does not.
- **Proposed Procedure**: Add a preservation item for each consolidation that replaces call sites with a shared
  helper. List each call site's options that differ from the helper's defaults: environment, flags, scope, timeouts
  and error handling. For each one, record "kept through <parameter>", or route it to the decision round as a
  behavior change. Brief editing subagents with that list.
- **Expected Benefit**: A narrowed call, such as a `--local` scope or an isolated environment, survives the
  consolidation even where no test covers it.
- **Cost & Risk**: One table per consolidation, and some extra briefing text.
- **Attempted**: Tested in this session. The dropped option was found by diff review and restored by hand.

## Diagnostic Details

- **Reproduction**: A git-config helper was adopted across packages in the code-surface review-refactor run. In
  devkit-spec `scope/services/observation.py`, the call changed from a `config --local --get` read to the helper's
  default scope.
- **Expected / Actual**: Expected behavior preserved. Actually, the scope read lost `--local` and could read global
  or system config. The tests still passed.
- **Versions**: work item branch after 0a6ff65c.
- **Conditions**: An editing subagent worked in its own checkout from a brief that stated only the helper adoption.
- **Workarounds Attempted**: Restored `optional(root, "config", "--local", "--get", ...)` by hand. This worked.
- **Related Assets**: `criteria.md` §4 and `applying.md` §3 (editing subagent brief).

## Evidence

```text
before: optional(root, "config", "--local", "--get", key)
after adoption: git_config(root, key)   # default scope, no --local
unit and integration tests: passed in both states
```
