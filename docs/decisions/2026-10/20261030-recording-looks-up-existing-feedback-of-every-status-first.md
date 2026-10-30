---
id: ADR-recording-looks-up-existing-feedback-of-every-status-first
title: Recording looks up existing feedback of every status first
summary: For feedback recording, we search existing feedback of every status with the observation's own words before writing a new item and act on the matched status, to stop duplicates that differently worded targets hide, accepting one search per observation and an agent's judgment of sameness.
proposal: SPEC-feedback-dedup-and-compaction
status: accepted
created_at: 2026-10-30
---

# [ADR-recording-looks-up-existing-feedback-of-every-status-first] Recording looks up existing feedback of every status first

- **Status**: Accepted
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

The `spec-feedback` sweep skips a candidate only when an open item has the same `target` and nature, and a direct
recording checks nothing. `target` is free text (paths, capability IDs, advisory codes, commands), so the same
observation recorded twice under differently worded targets passes both checks:
`FB-local-render-fix-ignores-worker-write-scope` duplicated `FB-render-stale-fix-ignores-worker-scope`. Terminal items
are never consulted, so a regression of a resolved item, a point already declined or routed work is recorded again as
new. `devkit docs search --kind feedback --history` already ranked both items of that pair in its top three.

## 2. Decision Drivers

- One file per observation across every status.
- No new command or index where the existing lookup suffices.
- The recorder keeps its judgment; a numeric score decides nothing.

## 3. Considered Options

- **Keep the equal-`target` check on open items**: no cost, but misses reworded targets and every terminal item.
- **A dedicated lookup command with a sameness threshold**: mechanical, but hybrid scores are rank fusions (about
  0.03) and lexical scores vary per query, so no fixed threshold separates "same" from "related".
- **Search every status with the existing document search, then judge the hits**: reuses `devkit docs search`, finds
  reworded and compacted items, costs one search per observation.

## 4. Decision Outcome

Chosen: search every status with the existing document search, then judge the hits.

- Before writing, the recorder (a direct recording and every sweep) runs `devkit docs search "<symptom and asset
  words>" --kind feedback --history -n 5`, adding `--all-namespaces` where the sweep covers all namespaces, and reads
  the hits. A hit is the same observation when it describes the same symptom of the same asset or behavior, whatever
  its `target` wording. For a compact record hit, the recorder reads only the entries that match the observation's
  words, and the matching entry decides.
- By the matched status:
  - `open`: record nothing; name the existing ID. New evidence goes into that file when it is inside the recorder's
    write scope, otherwise into the report that names the ID.
  - `dismissed`: record nothing unless there is evidence against the recorded reason; then record and cite the ID.
  - `resolved`: record a regression that cites the resolved ID, with `recurring: true`.
  - `promoted` or `forwarded`: record nothing while the destination is live (an open proposal, a spec not yet
    `completed`, an upstream report still open); name it. When the destination is completed, rejected, closed or no
    longer resolves, record a new item that cites the ID, as for `resolved`.
- This lookup replaces the sweep's equal-`target` deduplication. A sweep reports duplicate IDs as before.

## 5. Consequences

- **Positive**: reworded duplicates and regressions are caught where they are recorded; terminal items become a
  memory the recorder consults.
- **Negative / Risks**: sameness stays a judgment, so a near miss can still be recorded or wrongly skipped; a skipped
  observation names the existing ID, which keeps the decision visible.
- **Follow-ups**: none.

## 6. Confirmation

- Guidance tests under `packages/devkit-spec/tests/integration/bundles/spec/` pin the lookup command and the status
  table in the `spec-feedback` recording procedure and its sweep reference.
