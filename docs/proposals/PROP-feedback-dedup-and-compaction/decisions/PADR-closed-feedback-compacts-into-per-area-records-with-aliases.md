---
id: PADR-closed-feedback-compacts-into-per-area-records-with-aliases
title: Closed feedback compacts into per-area records with aliases
summary: For the terminal feedback ledger, we let a user-invoked playbook compact closed items into short per-area records that keep every retired ID as an alias, to keep the memory searchable without hundreds of full files, accepting that Git history alone keeps full originals.
proposal: PROP-feedback-dedup-and-compaction
status: draft
created_at: 2026-10-30
---

# [PADR-closed-feedback-compacts-into-per-area-records-with-aliases] Closed feedback compacts into per-area records with aliases

- **Status**: Draft
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

`ADR-feedback-lifecycle` keeps terminal feedback (`resolved`, `promoted`, `dismissed`, `forwarded`) as traceability,
so the ledger only grows: 233 of 242 files are terminal. Browsing hides them, but every full file stays in repository
searches, where agents read settled observations as if they were current. `ADR-adr-compaction` already consolidates
ADRs into replacement records that keep retired IDs as aliases; feedback has no such form. The document model lets a
`feedback` document declare `FB-` aliases, `devkit docs resolve` answers a retired ID with the record, and `devkit rules
fix` rewrites alias references in current documents while leaving work history alone.

## 2. Decision Drivers

- A settled observation stays findable by its ID and by its wording.
- An outcome is never changed or reopened by a change of form.
- No change to the feedback status vocabulary or the document model.
- Grouping that costs nothing to maintain, because only lookup depends on it and lookup goes through search.

## 3. Considered Options

- **Keep every full file**: no work, but the ledger keeps growing in every search.
- **Delete closed feedback**: smallest ledger, but retired IDs stop resolving and the memory of declined and routed
  points is lost.
- **Group by a topic taxonomy chosen at recording**: precise records, but every recorder must pick and keep a topic
  current, and a wrong choice misleads lookups.
- **Compact at a user-invoked run into one record per capability area and outcome, keeping retired IDs as aliases**:
  ADR-compaction's model; existing terminal statuses stay true; misgrouping is cheap.
- **One record per capability area with a new terminal status `compacted`**: fewer records, but changes the
  `feedback` kind's statuses in `devkit-docs` and `devkit-spec` and loses status filtering of past outcomes.

## 4. Decision Outcome

Chosen: compact at a user-invoked run into one record per capability area and outcome, keeping retired IDs as
aliases.

- Recording picks no topic; a feedback file stays where it was observed until a compaction run.
- The `feedback-compaction` playbook runs only when the user invokes or confirms it, at `session` depth from a clean
  tree; the invocation authorizes its deletions. It never changes an outcome or reopens an item.
- It compacts every terminal item under `specs/` except, each left in place and reported with the reason:
  - an item of a spec bundle whose `spec.md` is not `completed`, or of a live proposal;
  - an item a current document outside the run's own deletions references (`devkit docs refs <ID> --direction in`,
    work history excluded), so an ADR, a capability or a live `Source feedback` keeps citing the observation itself;
  - an item an unmerged local branch references or changes in its diff from its merge base, so the branch still
    merges and resolves its sources;
  - an item that fails `devkit rules check` or has an unknown status.
  Feedback under `docs/materials/` stays as written, like every material.
- It groups items by the capability area (`docs/capabilities/<area>/`, or a package namespace's
  `capabilities/<area>/`) that covers their target, judged by the run; an item no area covers goes to `other`. A
  misgrouped entry is accepted and may move at a later run. Lookup never depends on the grouping.
- Each group is one `feedback` record, `FB-compacted-<area>-<status>` (`FB-compacted-<namespace>-<area>-<status>` in a
  package namespace), at `specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md` on its first run. A later
  run appends its entries to the existing record of the same area and status in place.
- The record's frontmatter holds only `id`, `title`, `summary` (the area's recurring symptoms, which the search ranks),
  `target` (the area directory), the group's terminal `status`, `created_at` of the first run and `aliases:` listing
  every retired ID and every alias a member declared. It carries no observation fields (`scope`, `kind`, `category`,
  `origin`, `severity`, `recurring`), so `--where` filters never match a record by a member's values.
- Each entry is keyed by its retired ID and carries three short lines: **Symptom** (the original title's words),
  **Response** (the outcome with its spec, proposal, rule, ADR or report destination) and **Reason**.
- The run deletes the originals, then runs `devkit rules fix`; completed spec history keeps the retired IDs, which
  resolve through the aliases. Git history keeps the full originals. A branch that merges a compacted base runs
  `devkit rules fix` as after any base merge.
- Fidelity: for every deleted ID, its `status` at the base equals the `status` of the record that aliases it (a
  mechanical check), and a review compares each Response with the original's disposition or the resolving
  `reconcile.md`, as `adr-compaction` reviews its replacements.
- The run lists entries whose reason reads as lasting policy (a reason repeated across entries, or a general rule of
  behavior) that no accepted ADR states, for the user's decision only; it writes no ADR and no feedback for them.
- Terminal feedback stays traceability (`ADR-feedback-lifecycle`) through the record, its aliases and Git history.

## 5. Consequences

- **Positive**: the ledger shrinks to a few records per area; retired IDs still resolve; the recording lookup finds
  compacted observations.
- **Negative / Risks**: entries carry no dates or evidence, so a past week's dispositions are rebuilt from Git
  history; a record of a busy area grows with every run; cited items and items of unmerged branches wait for a later
  run.
- **Follow-ups**: if one area's record becomes too long to read, a later decision may split it.

## 6. Confirmation

- Guidance tests under `packages/devkit-spec/tests/integration/bundles/spec/` pin the playbook's invocation, scope,
  record shape and completion conditions.
- The run's own completion check: `devkit rules check` exits `0`; `devkit docs resolve <ID>` prints the record with
  `alias=<ID>` for every deleted feedback ID; the base status of every deleted ID equals its record's status.
