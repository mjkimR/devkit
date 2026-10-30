---
id: SPEC-feedback-dedup-and-compaction
title: Feedback lookup before recording and compaction of closed feedback
summary: Search existing feedback of every status before recording a new item, and compact closed feedback into short symptom, response and reason records that keep the retired IDs as aliases, so the ledger stays searchable without hundreds of full files.
status: planned
created: 2026-10-30
related_capabilities: [CAP-HARN-agent-guidance, CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-dedup-and-compaction] Feedback lookup before recording and compaction of closed feedback

## 1. Problem Statement & Motivation

Handed off from proposal PROP-feedback-dedup-and-compaction on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-feedback-dedup-and-compaction`

The feedback ledger holds 242 files, 233 of them closed (130 `resolved`, 60 `promoted`, 41 `dismissed`, 2
`forwarded`). `ADR-feedback-lifecycle` and `CAP-DLV-weekly-report` keep terminal feedback as traceability, so nothing
ever leaves the ledger. Browsing hides closed items, but every full file stays in repository searches, where agents
read them as if they were current.

Recording does not look at that ledger first. The `spec-feedback` sweep deduplicates only against open items with an
equal `target` and nature, and a direct recording checks nothing. In the 2026-10-30 run,
`FB-local-render-fix-ignores-worker-write-scope` duplicated `FB-render-stale-fix-ignores-worker-scope` because their
`target` values were worded differently. `devkit docs search "<observation>" --kind feedback --history` returned both
in its top three hits (`docs/materials/2026-10/20261030-feedback-dedup-and-compaction/ledger-and-lookup-evidence.md`),
so the lookup already exists; the procedure does not use it.

The agreed design is fixed by two ADRs: `ADR-recording-looks-up-existing-feedback-of-every-status-first` (search every
status before recording and act on the matched status) and
`ADR-closed-feedback-compacts-into-per-area-records-with-aliases` (a user-invoked playbook compacts closed feedback
into one record per capability area and outcome that keeps every retired ID as an alias). Both refine
`ADR-feedback-lifecycle` without superseding it: statuses and their meanings are unchanged. Compaction mirrors the
`adr-compaction` playbook (`ADR-adr-compaction`): it never changes an outcome, only its form.

## 2. User Stories

- **US-1**: As an agent recording feedback, I want to search existing feedback of every status with the observation's
  own words before writing, so that a reworded duplicate, a regression of a resolved item, a point already declined or
  work already routed is not recorded again as new.
- **US-2**: As a maintainer, I want a playbook I invoke to compact closed feedback into short per-area records whose
  aliases keep every retired ID resolvable, so that the ledger stays a searchable memory at a fraction of its size.
- **US-3**: As a maintainer, I want the compaction run to list reasons that read as lasting policy for my decision, so
  that recurring declines can become ADRs without the run deciding for me.

## 3. Non-Goals

1. **Scope Excluded**: the first compaction run over the existing ledger. It is a separate, user-invoked run of the
   new playbook after integration; this spec edits and deletes no existing feedback file outside its own bundle.
2. **Scope Excluded**: automatic or scheduled compaction; the playbook runs only when the user invokes or confirms it.
3. **Scope Excluded**: any change to the feedback status vocabulary, the `feedback` document kind, the document model,
   the weekly report, `feedback-hygiene` triage itself or any command. No new lookup command and no sameness score.
4. **Scope Excluded**: writing ADRs or feedback for the policy candidates a compaction run finds; the run lists them
   for the user only.
5. **Scope Excluded**: a record-size limit or splitting a long area record (a follow-up of
   `ADR-closed-feedback-compacts-into-per-area-records-with-aliases`).

## 4. Acceptance Criteria & Behavioral Contracts

Guidance criteria are verified by guidance tests under `packages/devkit-spec/tests/integration/bundles/spec/` that
read the bundle source as an installed environment renders it.

### [AC-01] Direct recording looks up every status before writing
- **Given** the `spec-feedback` skill's recording procedure
- **When** an agent follows it to record one observation
- **Then** a step before writing the file runs `devkit docs search "<symptom and asset words>" --kind feedback --history -n 5`, reads the hits, judges a hit the same observation when it describes the same symptom of the same asset or behavior whatever its `target` wording, and on a compact record hit reads only the entries that match the observation's words, the matching entry deciding

### [AC-02] The matched status decides the action
- **Given** a lookup hit judged the same observation
- **When** the recorder acts on it
- **Then** the skill states, per matched status: `open` records nothing and names the existing ID, adding new evidence to that file inside the recorder's write scope or else to the report; `dismissed` records nothing unless there is evidence against the recorded reason, then records and cites the ID; `resolved` records a regression that cites the ID with `recurring: true`; `promoted` or `forwarded` records nothing while the destination is live and names it, and records a new item citing the ID once the destination is completed, rejected, closed or no longer resolves

### [AC-03] The sweep uses the same lookup instead of equal-target deduplication
- **Given** the sweep reference `spec-feedback/references/sweep.md`
- **When** a sweep deduplicates its candidates
- **Then** it runs the recording procedure's lookup for each candidate with `--all-namespaces` and reports the existing IDs as duplicates, and the reference no longer deduplicates against `devkit docs list feedback --status open` by an equal `target`

### [AC-04] The compaction playbook is a registered `spec` asset
- **Given** `bundle.toml` of the `spec` bundle and the repository's own `devkit sync`
- **When** the bundle is synchronized
- **Then** `feedback-compaction` is a `kind = "playbook"` asset with source `playbooks/feedback-compaction` in the `core` preset, `.devkit/managed/spec/playbooks/feedback-compaction/SKILL.md` exists, `devkit playbook get spec/feedback-compaction` exits `0`, and `devkit sync --check` exits `0`

### [AC-05] Invocation, authority and outcome preservation
- **Given** the `feedback-compaction` playbook
- **When** an agent reads its entry section
- **Then** it states that the playbook runs only when the user invoked or confirmed it, that the invocation authorizes the run's feedback deletions, that it runs at `session` depth from a clean working tree with the base commit recorded, and that it never changes an outcome or reopens an item

### [AC-06] Eligible items and exclusions
- **Given** the playbook's collection step
- **When** it selects items
- **Then** it compacts terminal feedback (`resolved`, `promoted`, `dismissed`, `forwarded`) under `specs/` and leaves in place, reported with the reason: `open` items; an item of a spec bundle whose `spec.md` is not `completed` or of a live proposal; an item a current document outside the run's own deletions references (`devkit docs refs <ID> --direction in`, work history excluded); an item an unmerged local branch references or changes in its diff from its merge base; a file that fails `devkit rules check` or has an unknown status; and feedback under `docs/materials/`

### [AC-07] Grouping and record shape
- **Given** the eligible items
- **When** the playbook groups them and writes records
- **Then** it groups by the capability area that covers each target (an item no area covers goes to `other`, misgrouping accepted), shows the group map, and writes one `feedback` record per area and status, `FB-compacted-<area>-<status>` (`FB-compacted-<namespace>-<area>-<status>` in a package namespace) at `specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md` on its first run, a later run appending to the existing record in place; the record's frontmatter holds only `id`, `title`, `summary`, `target`, `status`, `created_at` and `aliases` (every retired ID and every alias a member declared), and each entry is keyed by its retired ID with one-line **Symptom**, **Response** and **Reason**

### [AC-08] The playbook's record template is a valid feedback document whose aliases resolve
- **Given** the record template in the playbook, filled with example values and written at a record path, with a completed spec bundle that cites a retired ID
- **When** the document index loads the workspace and the document rules check it
- **Then** `resolve("<retired ID>")` returns the record (kind `feedback`, the group's status), and the `id-convention`, `spec-format` and `document-reference` rules report no violation

### [AC-09] Apply, fidelity and completion conditions
- **Given** the written records
- **When** the playbook applies and verifies the run
- **Then** it deletes the originals, runs `devkit rules fix`, checks that each deleted ID's `status` at the base equals the `status` of the record that aliases it, reviews each Response against the original's disposition or the resolving `reconcile.md`, and completes only when `devkit rules check` exits `0`, `devkit docs resolve <ID>` prints a record with `alias=<ID>` for every deleted ID, and one commit holds the records, deletions and rewrites with the group map, the items left out with their reason and the ADR candidates in its body and the report

### [AC-10] ADR candidates are listed only
- **Given** entries whose reason reads as lasting policy (a reason repeated across entries, or a general rule of behavior) that no accepted ADR states
- **When** the run reports
- **Then** the playbook lists each candidate with its entry IDs and a one-line candidate decision for the user's decision, and writes no ADR and no feedback for it

### [AC-11] Neighbouring guidance points to the new form
- **Given** `spec/references/source-feedback.md`, `spec/references/playbooks.md` and the `feedback-hygiene` playbook
- **When** an agent reads them
- **Then** source-feedback states that a terminal source may resolve to a compact record through its alias and stays traceability; `playbooks.md` states that confirming `spec/feedback-compaction` authorizes its deletions at `session` depth, as for `spec/adr-compaction`; `feedback-hygiene` names `feedback-compaction` as the separate procedure for terminal feedback

### [AC-12] Bundle constraints hold for the changed assets
- **Given** the changed and new bundle documents
- **When** the bundle guidance tests and `devkit rules check` run
- **Then** every skill and playbook document stays within 12288 bytes, the new playbook cites no authoring-repository document ID, the existing invoked-or-confirmed playbook test covers `feedback-compaction`, and `uv run devkit rules check` exits `0`

## 5. Living Spec Impact

`spec-sync` reflects the change at `living-spec-draft`: `CAP-HARN-agent-guidance` lists `feedback-compaction` in its
playbook asset row and playbook table and states the every-status lookup instead of open-backlog deduplication in its
feedback capture policy; `CAP-DLV-delivery-workflows` states the lookup before recording and the compaction of closed
feedback in its feedback lifecycle, citing both ADRs. `reconcile.md` records and the reconcile check verifies it.

## 6. Assumptions

- The lookup step goes into the recording procedure of `spec-feedback/SKILL.md` as a numbered step before writing,
  and the sweep reference reuses it by link rather than restating the status table, so one place owns the table.
- `--all-namespaces` is added only in the sweep, which already covered all namespaces; a direct recording searches
  the current namespace view, as `ADR-recording-looks-up-existing-feedback-of-every-status-first` states.
- The record template lives in the playbook body itself while the playbook stays within the 12288-byte budget; a
  `references/` file is added only if it does not.
- The carried open feedback `FB-feedback-lifecycle-confirmation-names-wrong-rule` targets `ADR-feedback-lifecycle`,
  which this spec's write scope excludes (`docs/decisions/`); it is not a source of this spec and stays open.
