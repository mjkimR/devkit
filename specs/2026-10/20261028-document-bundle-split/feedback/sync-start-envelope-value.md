---
id: FB-sync-start-envelope-value
title: Worker sync_start exit conflicts with envelope check syntax
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/worker.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-28
---

# [FB-sync-start-envelope-value] Worker sync_start exit conflicts with envelope check syntax

## 1. Friction / Question

- **Context**: A Development worker recorded its initial successful sync check before returning committed evidence.
- **Expectation**: The worker contract says to record the exit as sync_start; Host validation says its check is 0.
- **Actual**: `workflow envelope worker --check sync_start=0` is rejected with `ENVELOPE_FLAG_INVALID` because every check value must begin PASS, FAIL or SKIP.
- **Workaround**: Record `sync_start=PASS exit=0`, retaining the observed exit in the supported check representation. This turn has no extra sync-output paths requiring the literal-zero acceptance check.
- **Suggestion**: Define one supported representation in both worker authoring and Host validation guidance.

## Diagnostic Details

- **Reproduction**: Run `devkit workflow envelope worker ... --check sync_start=0` after sync --check exits 0.
- **Expected / Actual**: Expected an exit-valued check; CLI refused it before writing an envelope.
- **Versions**: devkit-spec 0.1.4.
- **Conditions**: Codex emulated Development worker, initial sync clean, standard envelope CLI.
- **Workarounds Attempted**: PASS with an explicit exit detail preserves the result without editing YAML manually.
- **Related Assets**: Development worker step 5, spec-delegate worker validation, workflow envelope CLI check parsing.

## Evidence

```text
worker contract: record its exit as the sync_start check
Host reference: the worker's sync_start check is 0
ENVELOPE_FLAG_INVALID: --check 'sync_start=0': the value must start with PASS|FAIL|SKIP
```

## Disposition

Resolved by the session changes to the source Development worker instructions and
`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/worker.md`.
Both now use `sync_start=PASS exit=0` for a successful check and preserve the observed exit detail.
The regression in `test_delegation_sandbox_guidance.py` parses the documented flag with the actual envelope parser.

Verification: the focused Red run reproduced the failures before the fixes; both changed regression files passed
90 tests after the fixes. The cumulative affected selection passed 1,573 tests. Ruff, Pyright, governance rules,
and `devkit sync --check` passed. Independent code review of commit `2664c8c6c9d5d27e3fd247949b8f6d21d91ad9ab`
reported no findings; the Host verified the reviewed tree was unchanged.
