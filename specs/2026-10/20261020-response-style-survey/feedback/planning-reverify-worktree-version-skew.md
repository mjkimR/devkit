---
id: FB-planning-reverify-worktree-version-skew
title: Planning instructions can outpace the assigned worktree CLI
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/planning.md
skill: spec-delegate
agent: codex
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-planning-reverify-worktree-version-skew] Planning instructions can outpace the assigned worktree CLI

## 1. Friction / Question

- **Context**: Closing an independently reviewed Planning finding in an existing worktree.
- **Expectation**: The entry checkout's installed Planning instructions require a reverify envelope naming the
  challenger round.
- **Actual**: The assigned worktree CLI rejects a challenger as the source of reverify. Its local Planning
  instructions still specify a subsequent challenger envelope for the next result.
- **Workaround**: Use the assigned worktree's supported procedure: request a narrow independent recheck and record
  the returned challenger envelope. Preserve the original finding and state its disposition explicitly.
- **Suggestion**: Resolve operational skill instructions against the assigned worktree when resuming work. A
  newer entry-checkout instruction should not silently imply that an older worktree CLI supports its command.

## Diagnostic Details

- **Reproduction**: Load Planning instructions in the entry checkout, then run
  `devkit workflow envelope reverify --from envelopes/challenger-07.yaml` for the assigned proposal.
- **Expected / Actual**: Expected a closing record; received `ENVELOPE_FROM_INVALID` with exit code 2 and no
  reverify record. The preceding challenger record and document correction remain intact.
- **Versions**: Assigned worktree HEAD `ccec04fcbcd9cd75f1945a1b40d5ff3d7c21647a`; CLI package version unknown.
- **Conditions**: Codex continued an older Planning branch while the entry checkout had newer installed skills.
- **Workarounds Attempted**: Read the assigned worktree's Planning/envelope instructions and requested the narrow
  independent recheck; no source implementation or envelope YAML was manually altered.
- **Related Assets**: `spec/references/planning.md`, `spec/references/envelope.md`, and
  `devkit workflow envelope reverify`.

## Evidence

```text
Entry-checkout instruction: close a challenger round with reverify --from envelopes/challenger-NN.yaml.
Assigned-worktree CLI: ENVELOPE_FROM_INVALID --from must name a review or reverify envelope, not challenger.
Assigned-worktree envelope instruction: the highest sequence of a kind is current.
```

## Disposition

Directly resolved by `SPEC-feedback-planning-parser`. Planning instructions and CLI now resolve from the same assigned worktree. Required newer CLI features trigger Host refresh instead of mixed-version instructions or fabricated records.

Independent medium code review passed all four acceptance criteria without findings. The affected suite passed
1,113 tests, including parser default/order/error cases and existing consumer checks; lint, type checks and
cumulative governance checks passed. This disposition records verified branch work, not integration.
