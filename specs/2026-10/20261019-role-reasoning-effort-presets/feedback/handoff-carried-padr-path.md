---
id: FB-handoff-carried-padr-path
title: Handoff leaves the proposal's PADR file path in the carried spec notes
scope: repo
kind: suggestion
category: docs-mismatch
target: devkit spec proposal handoff (carried proposal notes in spec.md)
skill: spec-specify
agent: claude-code
origin: agent
severity: noise
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-handoff-carried-padr-path] Handoff leaves the proposal's PADR file path in the carried spec notes

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `devkit spec proposal handoff` promotes each `decisions/PADR-<slug>.md` to an ADR and
  rewrites PADR IDs and links, but a file path written as a code span (`` `decisions/PADR-<slug>.md` ``) in the
  carried "Proposed Design & Impact" notes stays as it was. The spec bundle's `decisions/` then holds only gate
  records, so the carried line points at a file that does not exist.
- **Proposed Procedure**: rewrite a code-span `decisions/PADR-<slug>.md` of a promoted PADR to the ADR's full ID,
  as the ID rewrite already does for bare `PADR-<slug>` references.
- **Expected Benefit**: the drafting agent does not have to notice and correct the stale path by hand; a later
  reader of a skeleton never follows a dead path.
- **Cost & Risk**: one more pattern in the handoff's rewrite; a code span that names a PADR file on purpose (as
  history) would be rewritten too, which is acceptable because the ADR is the current record.
- **Attempted**: in this run the drafted `spec.md` dropped the carried notes and recorded the promotion as an
  assumption citing `ADR-orchestration-workers`.

## Diagnostic Details

- **Reproduction**: hand off a proposal whose `proposal.md` names its PADR as a code-span path; read the carried
  section 5 of the new `spec.md`.
- **Expected / Actual**: expected `ADR-orchestration-workers`; actual is the original PADR path.
- **Versions**: devkit 0.1.1, handoff commit of SPEC-role-reasoning-effort-presets.
- **Conditions**: proposal with one PADR promoted at handoff.
- **Workarounds Attempted**: manual rewrite while drafting; it worked.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/proposals/handoff.py` (`_PADR`, the comment "a file name
  (PADR-x.md in a link) is left to the link rewrite"), the `spec-specify` skill.

## Evidence

```text
spec.md (handoff skeleton), section 5 "Proposed Design & Impact":
- **Decisions**: `decisions/PADR-role-effort-presets.md`.

<unit>/decisions/: 01-gate-plan-intent.yaml, 02-gate-plan-accept.yaml (no PADR file)
docs/decisions/2026-10/20261019-role-effort-presets.md: id: ADR-role-effort-presets
  section 1 still cites the proposal-relative path `materials/host-effort-semantics.md`; the handoff moved the
  file to docs/materials/2026-10/20261019-role-reasoning-effort-presets/ (same pattern: a code-span path, not a link)
```

- **Disposition**: packages/devkit-spec/src/devkit_spec/proposals/rewrite.py: handoff rewrites code-span paths in the carried spec and promoted ADRs to the new ID or path (kind=path)
