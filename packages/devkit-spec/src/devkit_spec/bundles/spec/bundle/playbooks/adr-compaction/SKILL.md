---
name: adr-compaction
description: Consolidate related approved ADRs into replacement ADRs that keep the retired IDs as aliases, deleting the retired files, without changing any decision (ADR-immutable-decisions-editable-records).
---

# ADR compaction

Run this playbook only when the user asks for it; that request authorizes the run's ADR deletions
(`ADR-immutable-decisions-editable-records`). It runs at `session` depth: no spec unit, envelope or reconcile record.

A compaction reorganizes decisions and never changes one. Anything that needs a decision changed leaves the run.

## Prerequisites

- The user asked for this playbook, for the whole ledger or for named topics or ADRs.
- A clean working tree (`git status`). Record the base commit: `git rev-parse HEAD`.

## Step 1: Survey

```bash
uv run devkit spec list decision -n 0
rg -n '^(status|supersedes|superseded_by|aliases):' docs/decisions/
```

Read every ADR in scope. Build the supersession graph from frontmatter (`supersedes`, `superseded_by`); these fields
are outside the reference graph.

## Step 2: Group and order

- Start from supersession closure: a group holds every ADR a member's supersession field names, and every ADR whose
  supersession field names a member.
- Add ADRs on the same topic: shared components, the same capability, overlapping `devkit spec refs` targets.
- A group has two or more ADRs. An ADR that fits no group stays as it is.
- Leave out of every group an ADR that contradicts another in-effect ADR or no longer matches the code or the Living
  Spec; record the finding as feedback (`spec-feedback`).
- Order each group's members by decision date (`created_at`), then supersession order.

Show the user the group map (replacement slug, members, one-line topic) before writing, unless the request already
named the groups.

## Step 3: Write each replacement

Path `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md` dated today, from the decision template:

- Frontmatter: `id: ADR-<slug>`, `title`, an English Y-statement `summary`, `status: accepted`, `created_at` today,
  `aliases:` every member ID and every alias a member declared. No `supersedes`, no `proposal`.
- Sections 1 to 6: consolidated from the members. Section 4 lists only the statements in effect, one item per part,
  each ending with its source ID in parentheses; superseded parts are left out. Considered options keep the
  option a member rejected, labelled by that member. No History section: retired texts stay in Git.
- Keep wording faithful: no driver, option, scope or consequence is added, dropped or changed in meaning.

## Step 4: Apply

1. Delete the member files: `git rm <member paths>`.
2. Run `uv run devkit rules fix`: it rewrites alias references in current documents to the replacement ID and leaves
   history as written.
3. Run `uv run devkit sync` if a bundle source changed.

## Step 5: Verify

```bash
uv run devkit rules check
git diff --no-renames --name-only --diff-filter=D <base> -- docs/decisions/
```

- Every deleted ADR ID resolves: `uv run devkit spec resolve <ID>` prints the replacement with `alias=<ID>`.
- No remaining `supersedes` or `superseded_by` outside the replacements names a retired ID.
- Fidelity review: compare each replacement with its members (`git show <base>:<path>`), with each member's incoming
  references (`devkit spec refs <ID> --direction in`). Each in-effect statement must trace to a member, and no member's
  in-effect decision may be missing or altered. A change found here goes back to Step 3, or the member leaves the group.

## Step 6: Commit and report

Commit the replacements, the deletions and the rewrites together. The commit body carries the group map (replacement
and members), the check results and the fidelity review result. Report the same to the user, with any ADR left out
and why.
