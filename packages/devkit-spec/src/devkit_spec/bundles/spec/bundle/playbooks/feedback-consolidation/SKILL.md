---
name: feedback-consolidation
aliases:
  - feedback-compaction
description: Delete eligible resolved feedback and consolidate other closed feedback under specs/ into per-area outcome records with aliases.
---

# Feedback consolidation

Run this playbook only when the user invoked or confirmed it; that invocation authorizes the run's feedback
deletions. Run at `session` depth from a clean working tree and record the base commit (`git rev-parse HEAD`).

A consolidation never changes an outcome and never reopens an item: each entry keeps its terminal status and
disposition.

## Step 1: Collect

List terminal feedback with `uv run devkit docs list feedback --history --all-namespaces -n 0`. Eligible: an item
under `specs/` whose `status` is `resolved`, `promoted`, `dismissed` or `forwarded`, including existing resolved
`FB-consolidated-...` records and their aliases; existing consolidated records of other statuses stay in place for
Step 3 to extend. Leave each of these in place and record it with the reason for the report:

- an `open` item;
- an item of a spec bundle whose `spec.md` is not `completed`, or of a proposal that still exists under
  `docs/proposals/`;
- an item a current document outside this run's deletions references (`uv run devkit docs refs <ID> --direction in`;
  completed spec bundles are work history and do not count);
- an item an unmerged local branch references or changes: its ID or path appears in
  `git diff $(git merge-base HEAD <branch>) <branch>` for a branch
  `git branch --no-merged HEAD --format='%(refname:short)'` lists;
- a file that fails `uv run devkit rules check <file>` or has an unknown status.

Feedback under `docs/materials/` stays as written.

## Step 2: Group

- Separate eligible resolved items for deletion without a record or alias. Apply the same exclusion checks to
  existing resolved consolidated records and every alias they carry.
- Group each remaining eligible item by the capability area that covers its `target`, judged from the target, title
  and evidence: a `docs/capabilities/<area>/` directory, or `capabilities/<area>/` of a package namespace; an item no
  area covers goes to `other`. A misgrouped entry is accepted; to move it at a later run, move the entry and its
  alias to the record of the right area and the same status, and delete no file.
- Split each area into one group per area and status.
- Show the user the group map (record ID, member IDs, one-line topic) before writing, unless the request named the
  groups.

## Step 3: Write or extend each record

Write records only for `promoted`, `dismissed` and `forwarded` groups. Never create or extend a resolved
consolidated record.

The record of a group is `FB-consolidated-<area>-<status>`. For an area of a package namespace, `<area>` below
stands for `<namespace>-<area>` in the ID, title and file name alike (`FB-consolidated-<namespace>-<area>-<status>`).
If `uv run devkit docs resolve FB-consolidated-<area>-<status>` finds the record, append the new
entries and aliases to that file in place and update its `summary`. Otherwise create
`specs/<YYYY-MM>/feedback/<YYYYMMDD>-consolidated-<area>-<status>.md` with today's date from this template:

```markdown
---
id: FB-consolidated-<area>-<status>
title: <Area> feedback, <status>
summary: <One English sentence naming the area's recurring symptoms; the search ranks it.>
target: docs/capabilities/<area>/
status: <status>
created_at: <YYYY-MM-DD of the first run>
aliases:
  - FB-<retired-name>
---

# [FB-consolidated-<area>-<status>] <Area> feedback, <status>

## FB-<retired-name>

- **Symptom**: <the original title's words>
- **Response**: <the outcome with its spec, proposal, rule, ADR or report destination>
- **Reason**: <one line: why this outcome>
```

- Frontmatter holds only these seven fields. `target` is the area directory
  (`docs/packages/<namespace>/capabilities/<area>/` in a package namespace, `other` for the `other` group). `aliases`
  lists every retired ID and every alias a member declared. Write no observation field (`scope`, `kind`,
  `category`, `origin`, `severity`, `recurring`).
- Write one entry per retired ID, keyed by an H2 of that ID, with exactly the three lines and no dates or evidence.
  Take the Symptom from the original title, and the Response from the original's disposition line or section, its
  `disposition:` field or, when needed, its resolving `reconcile.md`.
- If `RULE-file-length` configures `consolidated_max_bytes`, use the larger of that budget and the resolved
  `max_bytes` to review an over-budget record by topic while preserving every retained outcome and disposition.
  Treat the warning as a signal for a separate authorized grouping decision; never split or discard entries to
  meet the budget during this run.

## Step 4: Apply and verify

1. `git rm` eligible resolved files, including existing resolved consolidated records, and the originals of other
   groups; then run `uv run devkit rules fix` to rewrite alias references in current documents.
2. Status check: for every deleted ID in a non-resolved group
   (`git diff --no-renames --name-only --diff-filter=D <base> -- specs/`), its `status` at the base
   (`git show <base>:<path>`) equals the `status` of the record that aliases it.
3. Fidelity review: compare each Response and Reason with the original's disposition or the resolving `reconcile.md`.
   If an entry is missing, altered or untraceable, return to Step 3 or restore the original
   (`git restore --source <base> --staged --worktree -- <path>`) and take it out of its group.

## Step 5: ADR candidates

List entries whose Reason reads as lasting policy (a reason repeated across entries, or a general rule of behavior)
that no accepted ADR states (`uv run devkit docs search "<reason>" --kind decision`). Give each candidate its entry
IDs and a one-line candidate decision for the user's decision. Write no ADR and no feedback for a candidate.

## Completion conditions

- `uv run devkit rules check` exits `0`.
- `uv run devkit docs resolve <ID>` prints a record with `alias=<ID>` for every deleted non-resolved feedback ID;
  resolved IDs need no alias.
- The status check and the fidelity review pass.
- One commit holds the records, deletions and rewrites; its body and the report to the user carry the group map,
  every item left out with its reason and the ADR candidates.
