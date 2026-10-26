---
id: FB-workflow-exit-check-without-directive
title: Workflow exit checks cannot carry a directive
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit/src/devkit_agt/features/workflow/cli/render.py
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-26
---

# [FB-workflow-exit-check-without-directive] Workflow exit checks cannot carry a directive

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: An unmet disk check on a stage exit prints `[UNMET: <check>]` and `[CHECK: ... detail=...]`
  at exit 0; a gate request that never opened is refused by `devkit workflow answer` with the generic
  `REQUEST_UNKNOWN`. A bundle that needs the agent to act a specific way on an unmet check must say so in skill text.
- **Proposed Procedure**: Let a workflow definition give an exit check an optional `fix` or directive that `next`
  renders beside the unmet check and `answer` adds to the `REQUEST_UNKNOWN` details, without a bundle-specific hook.
- **Expected Benefit**: Agent-first output: the deterministic directive reaches the agent from the command itself, so an
  agent does not resolve an unmet `frontmatter(...)` exit by editing the field.
- **Cost & Risk**: A workflow schema field and CLI output contract change in devkit-agt, with tests; existing
  definitions are unaffected when the field is absent.
- **Attempted**: Hypothesis. Planning of the XL size gate in PROP-backlog-subagent-roles found no way for devkit-spec to
  attach a directive at `next` or `answer` (spike F7, challenger-02 finding 2); it is offered there as option b of `q5`.

## Diagnostic Details

- **Reproduction**: not run end to end; follows from the render and answer code paths.
- **Expected / Actual**: Expected: an unmet check can state what to do. Actual: only the check reference and detail.
- **Versions**: `<worktree>` head `9774e95a`.
- **Conditions**: any stage exit check a bundle defines.
- **Workarounds Attempted**: guidance text in the skill that names the directive.
- **Related Assets**: `devkit workflow next`, `devkit workflow answer`, `sdd-proposal`.

## Evidence

```text
packages/devkit/src/devkit_agt/features/workflow/cli/render.py:66-89 renders UNMET and CHECK only.
packages/devkit/src/devkit_agt/features/workflow/usecases/answers.py:113-119 refuses a closed request as REQUEST_UNKNOWN.
packages/devkit/src/devkit_agt/features/workflow/models/definition.py:234-254: declared checks are runner or human only.
```

## Disposition

Dismissed on the user's decision (2026-10-26). The user chose q5 option a for the XL size gate: the gate stays
devkit-spec only, and the skill text reads an unmet size check as "decompose first". A workflow exit check that
carries its own directive (option b) is not needed for it. Reopen it if an agent is observed editing `size` to pass
the gate.
