---
id: FB-integration-cli-runtime-version
title: Document an independent source-version runtime for CLI-changing integration
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/SKILL.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-25
---

# [FB-integration-cli-runtime-version] Document an independent source-version runtime for CLI-changing integration

## 1. Friction / Question

- **Context**: Integrating SPEC-automatic-scope-collection after source checks and independent reviews passed.
- **Expectation**: Preparation from the retained base checks the committed source and prospective result.
- **Actual**: RULE-cli-contract checks citations against the running CLI. The retained base's older CLI rejected
  three citations of the implemented collect command. Launching the source worktree runtime with an explicit base
  root then correctly refused cleanup of its active interpreter with INTEGRATION_RUNTIME_IN_WORKTREE.
- **Workaround (or Interpretation Chosen)**: Installed the verified source into a temporary environment outside
  the worktree using locked, non-editable workspace builds. The same local integration preparation from the retained
  base passed every readiness check, including CI_RULES. No rule, exclusion, authority or integration route changed.
- **Suggestion**: Explain this bootstrap procedure for changes to the CLI being used to integrate itself. Require a
  source-version runtime outside the cleanup target and retain all normal readiness checks.

## Diagnostic Details

- **Reproduction**: Add a mounted command and current capability citations; prepare through the retained base's
  older editable runtime, then through the source worktree's interpreter with an explicit retained base root.
- **Expected / Actual**: Source command citations validate; the old runtime reports unknown command and the source
  interpreter is inside the cleanup target.
- **Versions**: Source bb5036261a199c9fe10fc6026679c1ef61c8fcf9; base ad1f179a6a7d36ae4b951fb70cfed3ca1a3e9879.
- **Conditions**: Local auto integration deletes the source worktree and branch; CLI contract rule reads the active
  Click command tree rather than importing the committed snapshot's command implementation.
- **Workarounds Attempted**: Source interpreter with explicit base root refused safely; independent non-editable
  installation passed preparation.
- **Related Assets**: RULE-cli-contract; spec-integrate; integration usecases/service.py runtime-location guard.

## Evidence

```text
Retained base runtime: INTEGRATION_NOT_READY; RULE-cli-contract: Unknown command 'collect'.
Source worktree runtime: INTEGRATION_RUNTIME_IN_WORKTREE.
Independent source-version runtime: status=prepared, CI_RULES=pass, reasons=[], route=local, approval_policy=auto.
```

## Disposition

Resolved as a `spec-integrate` wording change (2026-10-27). The skill now states that a source changing the code
integration itself runs (a new rule's imports, `INTEGRATION_RULE_RUNTIME_MISMATCH`, or a CLI command the contract
rules cite) needs separately granted authority, then a runtime built from the source outside the worktree being
removed, run from the base checkout with every readiness check kept. `SPEC-integration-readiness-branch-code`
detects only the import case; a CLI citation mismatch still surfaces as `INTEGRATION_NOT_READY`.
