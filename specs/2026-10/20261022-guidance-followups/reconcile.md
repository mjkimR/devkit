---
reconcile_id: REC-guidance-followups
status: pending
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
---

# Reconcile: `SPEC-guidance-followups`

- `CAP-HARN-agent-guidance` milestone paragraph: the two SHOULD / SHOULD NOT granularity sentences become one
  preference ("Milestones are loosely managed themes: prefer ... over a milestone that only sequences one proposal"),
  matching `ADR-milestone-merging` (Tone outcome) and `docs/roadmap/README.md`. The obligation is unchanged; the rest
  of the paragraph, including the `MAY` merge clause, is untouched. `rg -n "SHOULD" docs | rg -i milestone` finds no
  other capability with the same sentence.
- `CAP-MCP-runtime-registration`: new `usecases` field listing `UC-drive-development-to-integration`.
- `UC-drive-development-to-integration`: `capabilities` gains `CAP-MCP-runtime-registration`, which extension 7g
  already cites for the `MCP_RUNTIME_STALE` recovery. `RULE-traceability-link` passes on both sides.
- Outside `docs/`, kept in step: the `spec-delegate` payload reference drops the stale "(it has no shell)" note from
  the `challenger` row (the `reconcile-reviewer` row made no shell claim), and `spec-sync` step 5 names the
  `reconcile-check` envelope command and links the `spec` skill's `references/envelope.md`; both are pinned by
  `packages/devkit-spec/tests/integration/bundles/spec/test_role_shell_guidance.py`. `CAP-HARN-agent-guidance` states
  neither the payload rows nor the spec-sync step text, so no capability sentence changes for them.

## Deferred Work

None.

## Source feedback

- `FB-capability-milestone-granularity-tone`: resolved (AC-01).
- `FB-payload-challenger-no-shell-note`: resolved (AC-02).
- `FB-runtime-registration-usecase-link`: resolved (AC-03).
- `FB-spec-sync-reconcile-check-command`: resolved (AC-04).

## Entrypoints

`devkit spec entrypoints derive` proposed the projections (`.claude`, `.devkit/managed`), the new guidance test and,
for `CAP-MCP-runtime-registration` and `UC-drive-development-to-integration`, the two spec bundle guidance files; none
is applied. `CAP-HARN-agent-guidance` already declares `payload.md` and the `spec-sync` skill; projections and tests
are no doorways; the MCP capability and the use case were touched for traceability metadata only and do not own the
spec bundle guidance.
