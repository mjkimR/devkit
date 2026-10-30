---
reconcile_id: REC-scope-activity-write-evidence
status: pending
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/collaboration/UC-run-parallel-work-safely.md
    resolution: modified
---

# Reconcile: `SPEC-scope-activity-write-evidence`

## Reflected changes

- `CAP-COLL-work-scope-registry` 4.5: `collect` adds `horizon=`, `current=`/`future=` and `current_overlapping=`;
  `compare`, `query` and `update` do not (Non-Goal 5).
- `CAP-COLL-work-scope-registry` 4.9: the horizon rule (Planning activity = proposal unit on a `plan-*` source; entry
  `current` only when both sides are), the current-first evidence choice per path pair, the pair and summary counts,
  the Host reading, problem `inputs` with merged repeats and the detail format, the self-base guard (a base at the
  tip is a base; only the candidate's own full ref or a configured remote's whole-name tracking peer is discarded),
  the text field list and the new check file `test_collection_horizon.py`.
- `CAP-HARN-agent-guidance` (Host scope observation): current overlap serializes runs, future-only overlap does not
  serialize Planning runs but orders handoff and integration, partial coverage never proves independence.
- `UC-run-parallel-work-safely`: step 6 reads the horizon, extension 6a, the success guarantee names the horizon and
  Scenario 6 is GOP-04. Scenarios 1–5 keep their numbers.
- The source asset `spec-orchestrate/SKILL.md.jinja` states the same reading; `devkit sync` wrote only
  `.devkit/installation.json` among tracked files (the projected skill copies are ignored).

## No impact

- `docs/architecture/`: no component, layer or dependency changes; the change stays inside
  `devkit_spec.features.scope` services and its CLI renderer.
- `docs/steering/glossary.md`: no new domain term. `horizon`, `current` and `future` are output field values that
  `CAP-COLL-work-scope-registry` 4.9 defines; the "Work scope observation" entry still holds.
- `CAP-TRACE-code-entrypoints`: `_Boundary` entries under `docs/` stay `excluded-tree` (Non-Goal 4).
- Entrypoints (`devkit spec entrypoints derive`): every changed source is already declared or covered
  (`CAP-COLL-work-scope-registry` lists `features/scope/`, `CAP-HARN-agent-guidance` the `spec-orchestrate` skill
  source, `UC-run-parallel-work-safely` the collect command and use case). Rejected candidates: the sync receipt
  `.devkit/installation.json`, the test directory and the scope helpers as use case or guidance doorways. No change.

## Deferred work

None. Both review findings (P3) were fixed in this unit.
