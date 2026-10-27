---
id: FB-auto-gate-satisfied-under-unmet-exit
title: An auto gate prints satisfied=yes while its stage exit is unmet
scope: repo
kind: suggestion
category: unclear-output
target: packages/devkit/src/devkit_agt/features/workflow/cli/render.py
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-auto-gate-satisfied-under-unmet-exit] An auto gate prints satisfied=yes while its stage exit is unmet

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: Under `plan-intent = "auto"`, `devkit workflow next` on an `XL` draft prints the unmet size
  check and then `[GATE: plan-intent policy=auto satisfied=yes source=policy]`, although the stage stays
  `intent-proposal` and the gate never passes.
- **Proposed Procedure**: Print `satisfied=no` (or a pending state) for a gate whose stage exit checks are unmet, or
  omit the `[GATE: ...]` line until the exit holds.
- **Expected Benefit**: An agent reading `satisfied=yes` does not conclude that `plan-intent` passed for a draft the
  size gate stopped.
- **Cost & Risk**: A rendering change in devkit-agt with its exit-code tests; outside SPEC-backlog-subagent-roles.
- **Attempted**: The size gate tests assert on `[GATE_PASSED: ...]` and `[REQUEST: ...]` instead of the `[GATE: ...]`
  line.

## Diagnostic Details

- **Reproduction**: a draft bound to `sdd-proposal` with `size: XL`, `[workflow.approvals] plan-intent = "auto"`,
  `devkit workflow next --unit docs/proposals/PROP-<slug>`.
- **Expected / Actual**: Expected: the gate line shows it not satisfied. Actual: `satisfied=yes source=policy` beside
  `[UNMET: frontmatter(proposal.md size S|M|L|)]`.
- **Versions**: devkit-agt at worktree head of `dev-backlog-subagent-roles`.
- **Conditions**: any `auto` gate on a stage with an unmet disk exit check.
- **Workarounds Attempted**: read `[STAGE: ...]` and `[GATE_PASSED: ...]` instead.
- **Related Assets**: `packages/devkit-spec/tests/integration/features/proposals/test_size_gate.py`.

## Evidence

```text
[STAGE: intent-proposal human_gate=plan-intent role=developer isolation=none]
[UNMET: frontmatter(proposal.md size S|M|L|)]
[CHECK: frontmatter(proposal.md size S|M|L|) class=disk evaluated=true detail="size=XL"]
[NEXT_SKILL: spec]
[GATE: plan-intent policy=auto satisfied=yes source=policy]
```

## Disposition

Resolved as a contract clarification, without an output change. `satisfied` on the `[GATE: ...]` line reports the
gate's approval, and `CAP-DLV-workflow-orchestration` already defines an `auto` gate as `satisfied=yes source=policy`
while its stage is current, so the line is correct for an XL draft whose size check is unmet. `CAP-DLV-cli-and-output`
now states that `satisfied` covers the approval only and that the stage passes only when `[UNMET]` is empty.
