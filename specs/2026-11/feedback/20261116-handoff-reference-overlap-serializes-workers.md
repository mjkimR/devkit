---
id: FB-handoff-reference-overlap-serializes-workers
title: Handoff reference rewrites serialize otherwise separate Development workers
scope: repo
kind: friction
category: redundant-step
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/SKILL.md
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-11-16
---

# [FB-handoff-reference-overlap-serializes-workers] Handoff reference rewrites serialize otherwise separate Development workers

## 1. Friction / Question

- **Context**: Two accepted documentation integration units consumed the same delivered core. Their worker payloads
  assigned separate packages and exact Living Spec targets.
- **Expectation**: Separate implementation ownership permits parallel Development, with serial integration and
  normal resolution of the handoff transactions' reference rewrites.
- **Actual**: Both native handoffs rewrote shared incoming references before their workers started. Scope collection
  classified eight inherited paths as current overlap. The orchestration instruction requires sequential work for
  current overlap, so the Viewer worker stopped authored writes after its three specification drafts.
- **Workaround**: Preserve the Viewer's clean specification checkpoint and continue only read-only preparation
  until the lifecycle unit lands. Preserve both handoff transactions and resolve their references during integration.
- **Suggestion**: Evaluate whether scheduling can distinguish a completed Host-owned handoff transaction from
  prospective worker writes. Keep the shared references in integration conflict detection and scope auditing.
  Do not exempt genuinely shared implementation or inferred broad boundaries.

## Diagnostic Details

- **Reproduction**: Hand off two accepted units from the same base whose incoming references share a capability,
  an ADR, a milestone and sibling proposal files. Run `uv run devkit spec scope collect` after both handoffs.
- **Expected / Actual**: Separate authored targets; eight current overlapping paths from the handoff commits.
- **Versions**: Core base `5d1cb2661871cd3fe12cf806b58ac2515a3ffaf4`; lifecycle handoff
  `7df4a63961e513f13a0ad092159ce945d670e955`; Viewer handoff `f32b831f7ca791566fad7934e13f537a40aaf787`.
- **Conditions**: Codex emulated local-orchestrated mode, required worktrees, two Development units after one core.
- **Workarounds Attempted**: Viewer specification-only checkpoint `0bd604352363054537a544ffea2da6659137b18d`
  retained clean; no Viewer production writes began before the hold. Parallel implementation was not tested.
- **Related Assets**: The `dev-design-document-lifecycle` and `dev-design-document-viewer` handoff revisions above,
  scope collection and the orchestration scheduling instruction. `FB-handoff-rewrite-edits-sibling-draft` resolved the existing sibling
  conflict procedure; this observation concerns its interaction with current-overlap scheduling.

## Evidence

```text
Lifecycle handoff: SPEC_PROPOSAL_REFS_REWRITTEN, 11 ID references.
Viewer handoff: SPEC_PROPOSAL_REFS_REWRITTEN, 9 ID references.
Scope collection: docs=0 code=8 current=8 future=0 for the two Development refs.
Shared paths include the documentation ownership capability, formal-role ADR, pilot evidence,
sibling proposal files and documentation-system milestone.
Orchestration: units whose horizon=current evidence overlaps run sequentially.
Viewer checkpoint: only spec.md, plan.md and tasks.md changed; worktree clean.
```

## Disposition

- **Disposition**: `PROP-handoff-rewrite-overlap-scheduling`: queued as a draft proposal that settles whether handoff-rewritten paths count as scheduling overlap.
