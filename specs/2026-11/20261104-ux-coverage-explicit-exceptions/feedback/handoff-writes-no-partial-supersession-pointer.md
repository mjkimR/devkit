---
id: FB-handoff-writes-no-partial-supersession-pointer
title: Handoff promotes a partially superseding PADR without writing the pointer its commit gate requires
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal handoff
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-handoff-writes-no-partial-supersession-pointer] Handoff promotes a partially superseding PADR without writing the pointer its commit gate requires

## 1. Friction / Question (friction, question)

- **Context**: `devkit spec proposal handoff <slug> --effort medium` on a proposal whose two PADRs carry
  `supersedes: [ADR-<existing>]` for a partial replacement (the existing ADR stays accepted).
- **Expectation**: the handoff transaction commits, since Planning passed `devkit rules check` on the PADRs and the
  acceptance was recorded.
- **Actual**: the handoff promoted the PADRs to ADRs and staged the move, then its own commit was refused
  (`SPEC_HANDOFF_COMMIT_REFUSED`, `GATE_RULES_FAILED`): `RULE-decision-supersession` reports each promoted ADR because
  the superseded ADR has neither `superseded` status nor a "Superseded in part by" pointer naming the new ID. PADRs
  are exempt from that rule, so nothing flagged it before the handoff; the rule first sees the pair at the handoff
  commit, when the writes are already staged in the new worktree (`status=needs_recovery`).
- **Workaround (or Interpretation Chosen)**: in the dev worktree, add the "Superseded in part by `ADR-<new>`:
  <clauses>" lines to the existing ADR by hand, stage them and run the commit the `[NEXT_ACTION]` names.
- **Suggestion**: either have the handoff write the pointer line for each partial `supersedes` target that stays
  accepted (naming the clauses from the PADR's Decision Outcome, or a placeholder the Development must fill), or run
  the supersession check on PADRs against their `supersedes` targets during Planning with a remediation that names the
  pointer the handoff will need. The planning reference could also tell the executor to add the pointer lines to the
  superseded ADR within the Planning branch when `supersedes` is partial.

## Diagnostic Details

- **Reproduction**: Planning with `devkit spec proposal padr` plus a hand-written supersedes entry naming ADR-x where
  ADR-x is replaced only in part; accept; `devkit spec proposal handoff <slug> --effort medium`.
- **Expected / Actual**: expected a committed handoff; observed `HANDOFF_STOPPED ... status=needs_recovery commit=-`
  with the two `RULE-decision-supersession` details.
- **Versions**: the repository at the handoff base commit (main, 2026-11-04).
- **Conditions**: any partial supersession recorded in a PADR; a whole supersession may behave the same when the
  target's status is not yet `superseded`.
- **Workarounds Attempted**: the pointer lines by hand, then the named commit; succeeded.
- **Related Assets**: `devkit spec proposal handoff`, `RULE-decision-supersession`, the `decision-writing`
  instruction's Supersession section, the spec skill's `references/planning.md`.

## Evidence

```text
[HANDOFF_STOPPED: PROP-<slug> status=needs_recovery spec=SPEC-<slug> ... commit=-]
[ERROR]  (SPEC_HANDOFF_COMMIT_REFUSED) git commit refused the handoff transaction ...; its writes are kept staged
[DETAIL] RULE-decision-supersession docs/decisions/<date>-<new>.md:6: supersedes target ADR-<existing> needs
         superseded status or a partial pointer naming ADR-<new>
```
