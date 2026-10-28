---
name: adr-compaction
description: Consolidate related approved ADRs into replacement ADRs that keep the retired IDs as aliases, deleting the retired files, without changing any decision.
---

# ADR compaction

Run this playbook only when the user invoked or confirmed it, for the whole ledger or named ADRs; that invocation
authorizes the run's ADR deletions. It runs at `session` depth from a clean working tree; record the base commit
(`git rev-parse HEAD`).

A compaction never changes a decision. A decision that must change needs a new ADR with `supersedes`, outside this
run.

## Step 1: Group

Read every ADR in scope, superseded ones included (`uv run devkit docs list decision --history -n 0`).

- A group holds the supersession closure of its members (`supersedes`, `superseded_by` in frontmatter; these are not
  in the reference graph) plus ADRs on the same topic. It has two or more members.
- Leave out an ADR that contradicts another in-effect ADR or no longer matches the code or the Living Spec, and record
  it with the `spec-feedback` skill.
- Order members by `created_at`, then supersession order.

Show the user the group map (replacement slug, members, one-line topic) before writing, unless the request named the
groups.

## Step 2: Write each replacement

Write `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`, dated today, from `.devkit/managed/docs/templates/decision.md`:

- Frontmatter: `status: accepted`, `created_at` today, `aliases:` every member ID and every alias a member declared;
  no `supersedes` or `proposal`.
- Section 4 lists only statements in effect, each ending with its source ID in parentheses. Considered options keep
  each option a member rejected, labelled by that member. No History section.
- Add, drop or change the meaning of no driver, option, scope or consequence.

## Step 3: Apply and verify

1. `git rm` the member files, then run `uv run devkit rules fix` to rewrite alias references in current documents.
2. Replace a retired ID in a `docs/steering/glossary.md` Owner by hand; `devkit rules fix` does not rewrite Owners.
3. Correct every path, test and rule ID in a replacement's Confirmation section that no longer exists; write "Review
   only" when no check exists.
4. Fidelity review: compare each replacement with its members (`git show <base>:<path>`) and their incoming references
   (`devkit docs refs <ID> --direction in`). If an in-effect statement is missing, altered or untraceable, return to
   Step 2 or take the member out of the group.

## Completion conditions

- `uv run devkit rules check` exits `0`.
- `uv run devkit docs resolve <ID>` prints the replacement with `alias=<ID>` for every deleted ID
  (`git diff --no-renames --name-only --diff-filter=D <base> -- docs/decisions/`), and no remaining `supersedes` or
  `superseded_by` names one.
- One commit holds the replacements, deletions and rewrites; its body and the report to the user carry the group map,
  the check and fidelity results and any ADR left out with the reason.
