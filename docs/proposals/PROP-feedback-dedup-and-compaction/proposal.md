---
id: PROP-feedback-dedup-and-compaction
title: Feedback lookup before recording and compaction of closed feedback
summary: Search existing feedback of every status before recording a new item, and compact closed feedback into short symptom, response and reason records that keep the retired IDs as aliases, so the ledger stays searchable without hundreds of full files.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-30
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/capabilities/delivery/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-feedback/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/
    - packages/devkit-spec/tests/
    - .devkit/installation.json
    - specs/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-feedback-dedup-and-compaction] Feedback lookup before recording and compaction of closed feedback

## 1. Background & Hypothesis

The feedback ledger holds 242 files, 233 of them closed (130 `resolved`, 60 `promoted`, 41 `dismissed`, 2
`forwarded`). `ADR-feedback-lifecycle` and `CAP-DLV-weekly-report` keep terminal feedback as traceability, so nothing
ever leaves the ledger. Browsing hides closed items, but every full file stays in repository searches, where agents
read them as if they were current.

Recording does not look at that ledger first. The `spec-feedback` sweep deduplicates only against open items with an
equal `target` string, and a direct recording checks nothing. In the 2026-10-30 run,
`FB-local-render-fix-ignores-worker-write-scope` duplicated `FB-render-stale-fix-ignores-worker-scope` because their
`target` values were worded differently. `devkit docs search "<observation>" --kind feedback --history` returned both
in its top three hits, so the lookup already exists; the procedure does not use it.

Hypothesis: if recording searches every status first, and closed feedback is periodically compacted into short
records that keep the retired IDs as aliases, the ledger stays a useful memory of what was fixed, routed or declined,
at a fraction of its size. Compaction mirrors the `adr-compaction` playbook: it never changes an outcome, only its
form.

## 2. Technical Spike Questions

Answered in Planning; evidence in `materials/ledger-and-lookup-evidence.md` and `envelopes/scout-01.yaml`.

- **Q1**: Compact record shape and location. **Answer**: a `feedback` document per capability area
  (`docs/capabilities/<area>/`, the user's decision: no topic chosen at recording, grouping only at compaction, lookup
  never through the partition) and per outcome, `FB-compacted-<area>-<status>`, so the record's own terminal status
  stays true without a status vocabulary change (pending the user's confirmation, question `q1`). It lives at
  `specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md`, a path the ID convention already accepts and
  that is no spec bundle's work history; later runs append to it in place. Its `aliases:` lists every retired ID. Each
  entry is keyed by the retired ID with **Symptom**, **Response** and **Reason**, one short line each.
- **Q2**: Which statuses compact and when. **Answer**: all four terminal statuses at once. `promoted` is terminal when
  the destination receives the item and `forwarded` after the submission (`ADR-feedback-lifecycle`), so neither waits;
  the Response names the destination. Excluded: `open` items, any feedback of a live proposal or of a spec bundle whose
  `spec.md` is not `completed`, and a file that fails `devkit rules check` or has an unknown status.
- **Q3**: Lookup. **Answer**: the existing `devkit docs search --kind feedback --history -n 5` suffices; after a
  simulated compaction the records ranked in the top five in hybrid and lexical modes, and an exact retired ID pins its
  record. No new command. No score decides sameness (hybrid scores are rank fusions); the recorder reads the hits and
  judges same symptom of the same asset or behavior, whatever the `target` wording.
- **Q4**: Traceability. **Answer**: `devkit docs resolve <retired ID>` returns the record with `alias=`; `devkit rules
  fix` rewrites alias references in current documents, ADRs and capabilities included, and leaves completed spec
  history, where alias references are accepted. A `Source feedback` naming a retired ID is always a terminal source
  and is rewritten. The weekly report is a playbook that matches feedback by ID with `--history` and reads committed
  content at its captured revision, so it needs no change; entries carry no dates, and Git history keeps the
  originals.
- **Q5**: ADR candidates. **Answer**: the run's report lists entries whose reason reads as lasting policy (a reason
  repeated across entries, or a general rule of behavior) that no accepted ADR states, each with its entry IDs and a
  one-line candidate decision, for the user's decision only; the run writes no ADR and no feedback for them.

## 3. Proposed Design & Impact

1. **Search before recording** (`PADR-recording-looks-up-existing-feedback-of-every-status-first`). The direct
   recording procedure and every sweep run `devkit docs search "<symptom and asset words>" --kind feedback --history
   -n 5` before writing and act on the matched status:
   - `open`: record nothing; name the existing ID. New evidence goes into that file when it is inside the recorder's
     write scope, otherwise into the report that names the ID.
   - `dismissed`: record nothing unless there is evidence against the recorded reason; then record and cite it.
   - `resolved`: record a regression that cites the resolved ID, with `recurring: true`.
   - `promoted` or `forwarded`: record nothing; name the destination.
   This replaces the sweep's equal-`target` deduplication.
2. **Compaction playbook** (`PADR-closed-feedback-compacts-into-per-area-records-with-aliases`). A new
   `feedback-compaction` playbook of the `spec` bundle, modelled on `adr-compaction`: user-invoked or confirmed only,
   `session` depth, clean tree, base commit recorded. Steps: collect the eligible terminal items (Q2); group them by
   capability area and outcome (an item no area covers goes to `other`; misgrouping is accepted and may move at a
   later run); show the group map; write or extend each record (Q1); delete the originals and run `devkit rules fix`;
   verify. It changes no outcome and reopens nothing.
3. **ADR candidates** (Q5): listed in the run's report for the user's decision only.
4. **Completion conditions of a run**: `devkit rules check` exits `0`; `devkit docs resolve <ID>` prints a record with
   `alias=<ID>` for every deleted feedback ID; one commit holds the records, deletions and rewrites; its body and the
   report carry the group map, items left out with the reason and the ADR candidates.
5. **Impact**: `spec-feedback` `SKILL.md` and `references/sweep.md` (the lookup); `skills/spec/references/source-feedback.md`
   (a terminal source may resolve to a compact record through its alias); `skills/spec/references/playbooks.md` and
   `feedback-hygiene` (point to the new playbook); the new `playbooks/feedback-compaction/SKILL.md` registered in
   `bundle.toml`; the playbook tables of `CAP-HARN-agent-guidance`; the feedback lifecycle of
   `CAP-DLV-delivery-workflows`; guidance tests under `packages/devkit-spec/tests/`; `.devkit/installation.json` from
   the repository's own sync. No change to the document model, the feedback statuses, the weekly report or any
   command.

### Planning decisions

- The user settled: compaction over deletion; each entry carries only symptom, response and reason; recording searches
  every status first; compaction is a user-invoked playbook that never changes an outcome, and ADR candidates go to the
  user. Grouping is by existing capability area at compaction time only, with misgrouping accepted.
- `CAP-DLV-weekly-report` and `CAP-DOCS-document-model` need no change (Q4, scout evidence), so they left the impact
  list and `docs/capabilities/documents/` left the boundaries.
- The two PADRs refine `ADR-feedback-lifecycle` without superseding it: statuses and their meanings are unchanged.

Out of scope: changing feedback statuses or the hygiene triage itself, automatic compaction, and the first compaction
run over the existing ledger.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-feedback-dedup-and-compaction`; the proposal is deleted there and its decisions become ADRs. The first
  compaction run over the existing 233 closed items is a separate, user-invoked run of the new playbook after
  integration.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes the
  rejection ADR and deletes the proposal.
