---
name: feedback-compaction
description: Compact closed feedback under specs/ into one short record per capability area and outcome that keeps every retired FB ID as an alias, deleting the originals, without changing any outcome.
---

# Feedback compaction

Run this playbook only when the user invoked or confirmed it; that invocation authorizes the run's feedback
deletions. It runs at `session` depth from a clean working tree; record the base commit (`git rev-parse HEAD`).

A compaction never changes an outcome and never reopens an item: each entry keeps its terminal status and
disposition. Git history keeps the full originals.

## Step 1: Collect

List terminal feedback with `uv run devkit docs list feedback --history --all-namespaces -n 0`. Eligible: an item
under `specs/` whose `status` is `resolved`, `promoted`, `dismissed` or `forwarded`. Leave each of these in place and
record it with the reason for the report:

- an `open` item;
- an item of a spec bundle whose `spec.md` is not `completed`, or of a proposal that still exists under
  `docs/proposals/`;
- an item a current document outside this run's deletions references (`uv run devkit docs refs <ID> --direction in`;
  completed spec bundles are work history and do not count), so that document keeps citing the observation itself;
- an item an unmerged local branch references or changes, so the branch still merges and resolves its sources: its ID
  or path appears in `git diff $(git merge-base HEAD <branch>) <branch>` for a branch
  `git branch --no-merged HEAD --format='%(refname:short)'` lists;
- a file that fails `uv run devkit rules check <file>` or has an unknown status.

Feedback under `docs/materials/` stays as written, like every material.

## Step 2: Group

- Group each eligible item by the capability area that covers its `target`: a `docs/capabilities/<area>/` directory,
  or `capabilities/<area>/` of a package namespace. Judge from the target, title and evidence; an item no area covers
  goes to `other`. A misgrouped entry is accepted and may move at a later run.
- Split each area by status: one group per area and status.
- Show the user the group map (record ID, member IDs, one-line topic) before writing, unless the request named the
  groups.

## Step 3: Write or extend each record

The record of a group is `FB-compacted-<area>-<status>` (`FB-compacted-<namespace>-<area>-<status>` in a package
namespace). If `uv run devkit docs resolve FB-compacted-<area>-<status>` finds it, append the new entries and aliases
to that file in place and update its `summary`. Otherwise create
`specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md` with today's date from this template:

```markdown
---
id: FB-compacted-<area>-<status>
title: <Area> feedback, <status>
summary: <One English sentence naming the area's recurring symptoms; the search ranks it.>
target: docs/capabilities/<area>/
status: <status>
created_at: <YYYY-MM-DD of the first run>
aliases:
  - FB-<retired-name>
---

# [FB-compacted-<area>-<status>] <Area> feedback, <status>

## FB-<retired-name>

- **Symptom**: <the original title's words>
- **Response**: <the outcome with its spec, proposal, rule, ADR or report destination>
- **Reason**: <one line: why this outcome>
```

- Frontmatter holds only these seven fields. `aliases` lists every retired ID and every alias a member declared.
  Write no observation field (`scope`, `kind`, `category`, `origin`, `severity`, `recurring`), so a `--where` filter
  never matches a record by a member's values.
- Write one entry per retired ID, keyed by an H2 of that ID, with exactly the three lines. Take the Symptom from the
  original title. Take the Response from the original's disposition line or section, its `disposition:` field or,
  for a resolved item without one, the resolving spec bundle's `reconcile.md`.
- Write no dates and no evidence in an entry.

## Step 4: Apply and verify

1. `git rm` the originals, then run `uv run devkit rules fix` to rewrite alias references in current documents.
2. Status check: for every deleted ID
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
- `uv run devkit docs resolve <ID>` prints a record with `alias=<ID>` for every deleted feedback ID.
- The status check and the fidelity review pass.
- One commit holds the records, deletions and rewrites; its body and the report to the user carry the group map,
  every item left out with its reason and the ADR candidates.
