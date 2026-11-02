---
id: ADR-feedback-lifecycle-ledger
title: Feedback lifecycle, recording lookup and compaction
summary: "For the feedback backlog, we close items at promotion or direct verified resolution, search every status before recording, compact closed items into per-area records with aliases and delete resolved ones, to avoid duplicates and stale noise, accepting that retired resolved IDs stop resolving."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-feedback-lifecycle
  - ADR-feedback-resolution-lifecycle
  - ADR-feedback-terminal-outcomes
  - ADR-closed-feedback-compacts-into-per-area-records-with-aliases
  - ADR-recording-looks-up-existing-feedback-of-every-status-first
  - ADR-resolved-feedback-retires-by-deletion
---

# [ADR-feedback-lifecycle-ledger] Feedback lifecycle, recording lookup and compaction

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: not recorded in the members
- **Involved Components/Capabilities**: not recorded in the members

---

## 1. Context & Problem Statement

Capture and hygiene kept direct fixes and routed work under the same promoted status, and an authorized fix outside a
hygiene session could leave its originating feedback open after verification. Task completion needs source
traceability without treating capture as permission to triage unrelated backlog items. Routing an observation to
follow-up work already transfers its tracking responsibility; requiring that work to revisit promoted feedback
duplicates tracking and confuses feedback closure with implementation completion.

Recording deduplicated weakly. The `spec-feedback` sweep skipped a candidate only when an open item had the same
`target` and nature, and a direct recording checked nothing. `target` is free text (paths, capability IDs, advisory
codes, commands), so the same observation recorded twice under differently worded targets passed both checks:
`FB-local-render-fix-ignores-worker-write-scope` duplicated `FB-render-stale-fix-ignores-worker-scope`. Terminal items
were never consulted, so a regression of a resolved item, a point already declined or routed work was recorded again
as new. `devkit docs search --kind feedback --history` already ranked both items of that pair in its top three.

Terminal feedback (`resolved`, `promoted`, `dismissed`, `forwarded`) stays as traceability, so the ledger only grows:
233 of 242 files were terminal. Browsing hides them, but every full file stays in repository searches, where agents
read settled observations as if they were current. ADR compaction (`ADR-decision-ledger`) already consolidates ADRs
into replacement records that keep retired IDs as aliases. The document model lets a `feedback` document declare
`FB-` aliases, `devkit docs resolve` answers a retired ID with the record, and `devkit rules fix` rewrites alias
references in current documents while leaving work history alone. Resolved feedback records verified fixes; keeping
their summaries and aliases indefinitely increases ledger maintenance, while tests and Git history retain regression
checks and evidence.

---

## 2. Decision Drivers

- Distinguish routing an observation from its verified repair.
- Source traceability for task completion without treating capture as permission to triage unrelated backlog items.
- No duplicate tracking: follow-up work tracks its own progress once it receives an observation.
- One file per observation across every status.
- No new command or index where the existing lookup suffices.
- The recorder keeps its judgment; a numeric score decides nothing.
- A settled observation stays findable by its ID and by its wording.
- An outcome is never changed or reopened by a change of form.
- No change to the feedback status vocabulary or the document model.
- Grouping that costs nothing to maintain, because only lookup depends on it and lookup goes through search.
- Reduce retained records without losing active work references.
- Keep rejected and routed outcomes discoverable.

---

## 3. Considered Options

### Terminal outcomes
- **Keep using promoted for fixes** (rejected in ADR-feedback-resolution-lifecycle): no extra status, but cannot
  distinguish routing from verified completion; using promotion for direct fixes would erase the distinction between
  routing and verified repair (ADR-feedback-terminal-outcomes).
- **Resolve at handoff** (rejected in ADR-feedback-resolution-lifecycle): the state update accompanies proposal
  retirement, but claims resolution before implementation and verification.
- **Resolve explicit sources at completion, promoted sources included** (chosen in
  ADR-feedback-resolution-lifecycle; rejected in ADR-feedback-terminal-outcomes): evidence and source status travel
  with the fix, but keeping promoted-to-resolved transitions duplicates follow-up lifecycle tracking.
- **Separate terminal routes: promotion and direct verified resolution** (chosen in ADR-feedback-terminal-outcomes):
  retains the distinction while limiting feedback review to open items.

### Recording lookup
- **Keep the equal-`target` check on open items** (rejected in
  ADR-recording-looks-up-existing-feedback-of-every-status-first): no cost, but misses reworded targets and every
  terminal item.
- **A dedicated lookup command with a sameness threshold** (rejected in
  ADR-recording-looks-up-existing-feedback-of-every-status-first): mechanical, but hybrid scores are rank fusions
  (about 0.03) and lexical scores vary per query, so no fixed threshold separates "same" from "related".
- **Search every status with the existing document search, then judge the hits** (chosen in
  ADR-recording-looks-up-existing-feedback-of-every-status-first): reuses `devkit docs search`, finds reworded and
  compacted items, costs one search per observation.

### Closed feedback retention
- **Keep every full file** (rejected in ADR-closed-feedback-compacts-into-per-area-records-with-aliases): no work, but
  the ledger keeps growing in every search.
- **Delete closed feedback** (rejected in ADR-closed-feedback-compacts-into-per-area-records-with-aliases): smallest
  ledger, but retired IDs stop resolving and the memory of declined and routed points is lost.
- **Group by a topic taxonomy chosen at recording** (rejected in
  ADR-closed-feedback-compacts-into-per-area-records-with-aliases): precise records, but every recorder must pick and
  keep a topic current, and a wrong choice misleads lookups.
- **Compact at a user-invoked run into one record per capability area and outcome, keeping retired IDs as aliases**
  (chosen in ADR-closed-feedback-compacts-into-per-area-records-with-aliases): ADR compaction's model; existing
  terminal statuses stay true; misgrouping is cheap.
- **One record per capability area with a new terminal status `compacted`** (rejected in
  ADR-closed-feedback-compacts-into-per-area-records-with-aliases): fewer records, but changes the `feedback` kind's
  statuses in `devkit-docs` and `devkit-spec` and loses status filtering of past outcomes.

### Resolved feedback retention
- **Keep compact records and aliases for all outcomes** (rejected in ADR-resolved-feedback-retires-by-deletion):
  preserves lookup but retains resolved summaries indefinitely.
- **Delete eligible resolved records** (chosen in ADR-resolved-feedback-retires-by-deletion): reduces ledger size but
  retired IDs no longer resolve.

---

## 4. Decision Outcome

### Terminal outcomes

- Only `open` is actionable feedback backlog. `promoted` is terminal once identified follow-up work receives the
  observation; it does not claim that work is implemented. Progress belongs to the destination, and its completion
  MUST NOT change the source to `resolved` merely because the work finishes. (ADR-feedback-terminal-outcomes)
- `resolved` is terminal for an observation directly addressed and verified without promotion. An authorized session
  or spec task may resolve its explicitly linked open sources with outcome and concrete verification evidence.
  Partial, deferred or unverified direct fixes stay open. `dismissed` and `forwarded` retain their terminal meanings.
  (ADR-feedback-terminal-outcomes)
- Source FB IDs remain traceability. Terminal sources require no completion disposition, re-verification or write
  scope. Implicit worker source scope includes only committed open sources; explicit authorized task boundaries remain
  independent. The Host handles open-source dispositions outside a delegated worker's write scope.
  (ADR-feedback-terminal-outcomes)
- Capture and sweep create open observations and never change status. Source resolution of direct fixes does not
  depend on a hygiene invocation, capture settings or the sweep stage. A task rechecks its own new resolution if later
  changes invalidate its evidence before completion; this does not reopen pre-existing terminal sources.
  (ADR-feedback-terminal-outcomes)
- All existing statuses and handoff/archive handling are preserved. Historical feedback statuses are not migrated.
  (ADR-feedback-terminal-outcomes)

### Recording looks up existing feedback first

- Before writing, the recorder (a direct recording and every sweep) runs `devkit docs search "<symptom and asset
  words>" --kind feedback --history -n 5`, adding `--all-namespaces` where the sweep covers all namespaces, and reads
  the hits. A hit is the same observation when it describes the same symptom of the same asset or behavior, whatever
  its `target` wording. For a compact record hit, the recorder reads only the entries that match the observation's
  words, and the matching entry decides. (ADR-recording-looks-up-existing-feedback-of-every-status-first)
- By the matched status: (ADR-recording-looks-up-existing-feedback-of-every-status-first)
  - `open`: record nothing; name the existing ID. New evidence goes into that file when it is inside the recorder's
    write scope, otherwise into the report that names the ID.
  - `dismissed`: record nothing unless there is evidence against the recorded reason; then record and cite the ID.
  - `promoted` or `forwarded`: record nothing while the destination is live (an open proposal, a spec not yet
    `completed`, an upstream report still open); name it. When the destination is completed, rejected, closed or no
    longer resolves, record a new item that cites the ID.
- A recurrence of a resolved observation is a fresh observation; it cites an existing resolved record when one is
  available. (ADR-resolved-feedback-retires-by-deletion)
- This lookup replaces the sweep's equal-`target` deduplication. A sweep reports duplicate IDs as before.
  (ADR-recording-looks-up-existing-feedback-of-every-status-first)

### Compaction of closed feedback

- Recording picks no topic; a feedback file stays where it was observed until a compaction run.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- The `feedback-compaction` playbook runs only when the user invokes or confirms it, at `session` depth from a clean
  tree; the invocation authorizes its deletions. It never changes an outcome or reopens an item.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- Eligible resolved feedback is deleted during that user-invoked compaction without aliases, including existing
  resolved compact records and their aliases. The other terminal outcomes continue to be compacted with aliases.
  (ADR-resolved-feedback-retires-by-deletion)
- The run compacts every other terminal item under `specs/` except, each left in place and reported with the reason
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases); the same exceptions protect current references,
  incomplete work and unmerged branches from resolved deletion (ADR-resolved-feedback-retires-by-deletion):
  - an item of a spec bundle whose `spec.md` is not `completed`, or of a live proposal;
  - an item a current document outside the run's own deletions references (`devkit docs refs <ID> --direction in`,
    work history excluded), so an ADR, a capability or a live `Source feedback` keeps citing the observation itself;
  - an item an unmerged local branch references or changes in its diff from its merge base, so the branch still
    merges and resolves its sources;
  - an item that fails `devkit rules check` or has an unknown status.
  Feedback under `docs/materials/` stays as written, like every material.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- It groups items by the capability area (`docs/capabilities/<area>/`, or a package namespace's
  `capabilities/<area>/`) that covers their target, judged by the run; an item no area covers goes to `other`. A
  misgrouped entry is accepted and may move at a later run. Lookup never depends on the grouping.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- Each group is one `feedback` record, `FB-compacted-<area>-<status>` (`FB-compacted-<namespace>-<area>-<status>` in a
  package namespace), at `specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md`
  (`<YYYYMMDD>-compacted-<namespace>-<area>-<status>.md` in a package namespace) on its first run. A later run appends
  its entries to the existing record of the same area and status in place.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- The record's frontmatter holds only `id`, `title`, `summary` (the area's recurring symptoms, which the search ranks),
  `target` (the area directory), the group's terminal `status`, `created_at` of the first run and `aliases:` listing
  every retired ID and every alias a member declared. It carries no observation fields (`scope`, `kind`, `category`,
  `origin`, `severity`, `recurring`), so `--where` filters never match a record by a member's values.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- Each entry is keyed by its retired ID and carries three short lines: **Symptom** (the original title's words),
  **Response** (the outcome with its spec, proposal, rule, ADR or report destination) and **Reason**.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- The run deletes the originals, then runs `devkit rules fix`; completed spec history keeps the retired IDs.
  Compacted terminal feedback resolves through aliases; deleted resolved feedback stays in Git history, which keeps the
  full originals. A branch that merges a compacted base runs
  `devkit rules fix` as after any base merge. (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- Fidelity: for every compacted ID, its `status` at the base equals the `status` of the record that aliases it (a
  mechanical check), and a review compares each Response with the original's disposition or the resolving
  `reconcile.md`, as `adr-compaction` reviews its replacements.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- The run lists entries whose reason reads as lasting policy (a reason repeated across entries, or a general rule of
  behavior) that no accepted ADR states, for the user's decision only; it writes no ADR and no feedback for them.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- Compacted terminal feedback resolves through aliases; deleted resolved feedback stays in Git history.
  (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- Unresolved historical feedback references are permitted, while ambiguity errors and strict active reference
  validation are retained. (ADR-resolved-feedback-retires-by-deletion)

---

## 5. Consequences

- **Positive**:
  - Feedback review is limited to open items; routing and verified repair keep separate meanings.
    (ADR-feedback-lifecycle)
  - Reworded duplicates and regressions are caught where they are recorded; terminal items become a memory the
    recorder consults. (ADR-recording-looks-up-existing-feedback-of-every-status-first)
  - The ledger shrinks to a few records per area; compacted IDs still resolve; the recording lookup finds compacted
    observations. (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- **Negative / Risks**:
  - A promoted record cannot establish implementation success; read its destination for that evidence.
    (ADR-feedback-lifecycle)
  - Sameness stays a judgment, so a near miss can still be recorded or wrongly skipped; a skipped observation names
    the existing ID, which keeps the decision visible.
    (ADR-recording-looks-up-existing-feedback-of-every-status-first)
  - Entries carry no dates or evidence, so a past week's dispositions are rebuilt from Git history; a record of a busy
    area grows with every run; cited items and items of unmerged branches wait for a later run.
    (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
  - Historical missing feedback IDs, including typos, are no longer distinguished by reference validation. Git history
    retains deleted records; active references continue to block deletion. (ADR-resolved-feedback-retires-by-deletion)
- **Follow-ups**:
  - Existing status-filtered discovery remains available for all records. (ADR-feedback-lifecycle)
  - If one area's record becomes too long to read, a later decision may split it.
    (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)

---

## 6. Confirmation

- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_feedback.py` covers the feedback states
  (`open`, `promoted`, `resolved`, `dismissed`, `forwarded`) and that only `open` items are carried as actionable.
  (ADR-feedback-lifecycle)
- Review only for source-feedback resolution at completion; `RULE-document-reference` checks feedback ID resolution.
  (ADR-feedback-lifecycle)
- Guidance tests under `packages/devkit-spec/tests/integration/bundles/spec/` pin the lookup command and the status
  table in the `spec-feedback` recording procedure and its sweep reference
  (ADR-recording-looks-up-existing-feedback-of-every-status-first), and the compaction playbook's invocation, scope,
  record shape and completion conditions (ADR-closed-feedback-compacts-into-per-area-records-with-aliases).
- The compaction run's own completion check: `devkit rules check` exits `0`; `devkit docs resolve <ID>` prints the
  record with `alias=<ID>` for every compacted feedback ID; the base status of every compacted ID equals its record's
  status. (ADR-closed-feedback-compacts-into-per-area-records-with-aliases)
- Guidance integration tests cover compaction and recording; document reference rule tests cover historical and
  active references. (ADR-resolved-feedback-retires-by-deletion)
