---
id: SPEC-feedback-dedup-and-compaction
title: Feedback lookup before recording and compaction of closed feedback
summary: Search existing feedback of every status before recording a new item, and compact closed feedback into short symptom, response and reason records that keep the retired IDs as aliases, so the ledger stays searchable without hundreds of full files.
status: planned
created: 2026-10-30
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-feedback-dedup-and-compaction] Feedback lookup before recording and compaction of closed feedback

## 1. Problem Statement & Motivation

Handed off from proposal PROP-feedback-dedup-and-compaction on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-feedback-dedup-and-compaction`

### 1. Background & Hypothesis

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

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Feedback lookup before recording and compaction of closed feedback so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

Answered in Planning; evidence in `docs/materials/2026-10/20261030-feedback-dedup-and-compaction/ledger-and-lookup-evidence.md` and historical Git `eb4f48cb13e75d89d212baa4433f9feed721602d:docs/proposals/PROP-feedback-dedup-and-compaction/envelopes/scout-01.yaml`.

- **Q1**: Compact record shape and location. **Answer**: a `feedback` document per capability area
  (`docs/capabilities/<area>/`, the user's decision: no topic chosen at recording, grouping only at compaction, lookup
  never through the partition) and per outcome, `FB-compacted-<area>-<status>`, so the record's own terminal status
  stays true without a status vocabulary change (the user's decision over one record per area with a new `compacted`
  status). It lives at
  `specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md`, a path the ID convention already accepts and
  that is no spec bundle's work history; later runs append to it in place. Its frontmatter holds only `id`, `title`,
  `summary`, `target` (the area directory), `status`, `created_at` and `aliases:` (every retired ID), no observation
  fields. Each entry is keyed by the retired ID with **Symptom** (the original title's words), **Response** and
  **Reason**, one short line each. In a package namespace the ID adds the namespace.
- **Q2**: Which statuses compact and when. **Answer**: all four terminal statuses at once. `promoted` is terminal when
  the destination receives the item and `forwarded` after the submission (`ADR-feedback-lifecycle`), so neither waits;
  the Response names the destination. Left in place and reported: `open` items; feedback of a live proposal or of a
  spec bundle whose `spec.md` is not `completed`; an item a current document outside the run's deletions cites (an
  ADR, a capability or a live `Source feedback` keeps citing the observation itself); an item an unmerged local branch
  references or changes; a file that fails `devkit rules check` or has an unknown status. Feedback under
  `docs/materials/` stays as written, like every material.
- **Q3**: Lookup. **Answer**: the existing `devkit docs search --kind feedback --history -n 5` suffices. In a
  worst-case simulation (all 225 terminal items in one record per status, up to 125 entries) the record holding the
  related original ranked in the top three for 7 of 8 related pairs in both modes, the eighth being missed before
  compaction too; an exact retired ID pins its record. No new command and no record-size limit now. On a record hit
  the recorder reads only the entries matching its words. No score decides sameness (hybrid scores are rank fusions); the recorder reads the hits and
  judges same symptom of the same asset or behavior, whatever the `target` wording. A `promoted` or `forwarded` match
  suppresses recording only while its destination is live.
- **Q4**: Traceability. **Answer**: `devkit docs resolve <retired ID>` returns the record with `alias=`; `devkit rules
  fix` would rewrite alias references in current documents, so items those documents cite are left for a later run
  (Q2) and current citations keep naming the observation; completed spec history keeps the retired IDs, where alias
  references are accepted. A branch that merges a compacted base runs `devkit rules fix` as after any base merge. The weekly report is a playbook that matches feedback by ID with `--history` and reads committed
  content at its captured revision, so it needs no change; entries carry no dates, and Git history keeps the
  originals.
- **Q5**: ADR candidates. **Answer**: the run's report lists entries whose reason reads as lasting policy (a reason
  repeated across entries, or a general rule of behavior) that no accepted ADR states, each with its entry IDs and a
  one-line candidate decision, for the user's decision only; the run writes no ADR and no feedback for them.

### 3. Proposed Design & Impact

1. **Search before recording** (`ADR-recording-looks-up-existing-feedback-of-every-status-first`). The direct
   recording procedure and every sweep run `devkit docs search "<symptom and asset words>" --kind feedback --history
   -n 5` before writing and act on the matched status:
   - `open`: record nothing; name the existing ID. New evidence goes into that file when it is inside the recorder's
     write scope, otherwise into the report that names the ID.
   - `dismissed`: record nothing unless there is evidence against the recorded reason; then record and cite it.
   - `resolved`: record a regression that cites the resolved ID, with `recurring: true`.
   - `promoted` or `forwarded`: record nothing while the destination is live; name it. When it is completed,
     rejected, closed or unresolvable, record a new item that cites the ID.
   This replaces the sweep's equal-`target` deduplication.
2. **Compaction playbook** (`ADR-closed-feedback-compacts-into-per-area-records-with-aliases`). A new
   `feedback-compaction` playbook of the `spec` bundle, modelled on `adr-compaction`: user-invoked or confirmed only,
   `session` depth, clean tree, base commit recorded. Steps: collect the eligible terminal items (Q2); group them by
   capability area and outcome (an item no area covers goes to `other`; misgrouping is accepted and may move at a
   later run); show the group map; write or extend each record (Q1); delete the originals and run `devkit rules fix`;
   check fidelity: each deleted ID's base status equals its record's status, and a review compares each Response
   with the original disposition or the resolving `reconcile.md`. It changes no outcome and reopens nothing.
3. **ADR candidates** (Q5): listed in the run's report for the user's decision only.
4. **Completion conditions of a run**: `devkit rules check` exits `0`; `devkit docs resolve <ID>` prints a record with
   `alias=<ID>` for every deleted feedback ID; the status check and the fidelity review pass; one commit holds the records, deletions and rewrites; its body and the
   report carry the group map, items left out with the reason and the ADR candidates.
5. **Impact**: `spec-feedback` `SKILL.md` and `references/sweep.md` (the lookup); `skills/spec/references/source-feedback.md`
   (a terminal source may resolve to a compact record through its alias); `skills/spec/references/playbooks.md` and
   `feedback-hygiene` (point to the new playbook); the new `playbooks/feedback-compaction/SKILL.md` registered in
   `bundle.toml`; the playbook tables and the sweep deduplication clauses of `CAP-HARN-agent-guidance`; the feedback
   lifecycle of
   `CAP-DLV-delivery-workflows`; guidance tests under `packages/devkit-spec/tests/`; `.devkit/installation.json` from
   the repository's own sync. No change to the document model, the feedback statuses, the weekly report or any
   command.

#### Planning decisions

- The user settled: compaction over deletion; each entry carries only symptom, response and reason; recording searches
  every status first; compaction is a user-invoked playbook that never changes an outcome, and ADR candidates go to the
  user. Grouping is by existing capability area at compaction time only, with misgrouping accepted. Each area has one
  record per outcome, `FB-compacted-<area>-<status>`, with the existing statuses unchanged; one record per area with
  a new terminal status `compacted` was declined, because it would change the `feedback` kind in `devkit-docs`.
- `CAP-DLV-weekly-report` and `CAP-DOCS-document-model` need no change (Q4, scout evidence), so they left the impact
  list and `docs/capabilities/documents/` left the boundaries.
- The two PADRs refine `ADR-feedback-lifecycle` without superseding it: statuses and their meanings are unchanged.

Out of scope: changing feedback statuses or the hygiene triage itself, automatic compaction, and the first compaction
run over the existing ledger.

### 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-feedback-dedup-and-compaction`; the proposal is deleted there and its decisions become ADRs. The first
  compaction run over the existing 233 closed items is a separate, user-invoked run of the new playbook after
  integration.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes the
  rejection ADR and deletes the proposal.

