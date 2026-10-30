---
reconcile_id: REC-feedback-dedup-and-compaction
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconcile: `SPEC-feedback-dedup-and-compaction`

## Living Spec changes

- `CAP-HARN-agent-guidance`: the playbook asset row and the 4.5 playbook table list `feedback-compaction` with its
  invocation, record shape, exclusions, fidelity checks and ADR candidates; the `spec-feedback` skill row names the
  lookup and `docs search`; the feedback capture policy states the every-status lookup and its per-status actions in
  place of open-backlog deduplication, and the Planning-return sweep sentence follows it.
- `CAP-DLV-delivery-workflows`: the source feedback lifecycle states that recording consults terminal feedback first
  and that closed feedback may be compacted into per-area records whose aliases keep retired IDs resolvable, so a
  terminal source reference may resolve to such a record.

## No impact

- Use cases: no use case goal changes; `UC-route-development-intent` already covers offering a playbook found at
  intake, and the new playbook is reached the same way.
- `CAP-DLV-weekly-report` and `CAP-DOCS-document-model`: no change (the weekly report matches feedback by ID with
  `--history`, and the document model already supports `feedback` aliases), as Planning concluded.
- `docs/decisions/`: the two ADRs are fixed by the handoff. In a package namespace the record's file name carries the
  namespace (`<YYYYMMDD>-compacted-<namespace>-<area>-<status>.md`) so `RULE-id-convention` derives the namespaced ID
  `ADR-closed-feedback-compacts-into-per-area-records-with-aliases` names; that ADR's path states the global case and
  its decision is unchanged. The wording repair of that path is deferred to the open feedback
  `FB-compaction-adr-path-omits-namespace` (`docs/decisions/` is outside this spec's write scope).

## Source feedback

None. The carried open `FB-feedback-lifecycle-confirmation-names-wrong-rule` is not a source of this spec and stays
open (its target `ADR-feedback-lifecycle` is outside the write scope).

## Entrypoints

`devkit spec entrypoints derive --spec` proposed pairs for both capabilities; none is applied.
`CAP-HARN-agent-guidance` already declares the bundle directory, which covers every changed asset, and the tests and
`.devkit/installation.json` are not entrypoints. `CAP-DLV-delivery-workflows` only states the lifecycle; the
playbook and the recording skill are owned by `CAP-HARN-agent-guidance`.
