---
reconcile_id: REC-milestone-guidance-tone
status: resolved
targets:
  - file: docs/decisions/2026-10/20261022-milestone-merging.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-roadmap-and-milestones.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/roadmap/README.md
    resolution: modified
---

# Reconcile: `SPEC-milestone-guidance-tone`

- `ADR-milestone-merging` (new, accepted): records the recommendation tone, the merge procedure and the kept reopen
  rule; its outcome names the replaced Status clause of `ADR-roadmap-and-milestones`.
- `ADR-roadmap-and-milestones`: the Status outcome bullet gains the one-line partial-supersession pointer; the ADR
  stays `accepted` (`ADR-immutable-decisions-editable-records`, "Decision changes").
- `CAP-DOCS-document-model` rule 7 (historical documents): a user-decided merge MAY delete a done or dropped milestone,
  whose ID then resolves as an alias of the theme. The rest of the capability is unchanged; §3.5 already allows
  "previous or alternate IDs" in `aliases`.
- `CAP-HARN-agent-guidance` milestone paragraph: the done/dropped-history sentence states the merge exception and the
  procedure the shipped Backlog reference follows; the reopen sentence stays. Its SHOULD granularity sentence stays,
  because RFC 2119 SHOULD already means "recommended" (spec Non-Goal 4).
- `docs/roadmap/README.md`: recommendation wording, the merge paragraph citing `ADR-milestone-merging` with
  `MS-maintenance-operations` as the example, and the reworded done-extension sentence.
- Checked without change: `CAP-DOCS-document-lookup` (`--history` behavior holds for unmerged records),
  `CAP-GOV-spec-rules` (done/dropped history is still never rewritten by `devkit rules fix`; a merge is a user edit)
  and `ADR-immutable-decisions-editable-records` ("stay as written" applies to reference rewrites only).
- Outside `docs/`, kept in step: the shipped seed roadmap README, milestone template and the spec skill's Backlog and
  milestone completion references, pinned by
  `packages/devkit-spec/tests/integration/bundles/spec/test_milestone_completion_guidance.py`.

## Deferred Work

None.

## Entrypoints

`devkit spec entrypoints derive` proposed the bundle guidance files and the guidance test for both capabilities; none
is applied. `CAP-HARN-agent-guidance` already declares the seed README, the milestone template and both spec skill
references. `CAP-DOCS-document-model` changed one sentence of its historical-document rule; the guidance assets belong
to `CAP-HARN-agent-guidance`, and `.claude`, `.devkit/managed` and tests are no doorways.
