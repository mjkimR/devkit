---
name: adr-consolidation
aliases:
  - adr-compaction
description: Consolidate related approved ADRs into replacement ADRs that keep the retired IDs as aliases, deleting the retired files, without changing any decision.
---

# ADR consolidation

Run this playbook only when the user invoked or confirmed it, for the whole ledger or named ADRs; that invocation
authorizes the run's ADR deletions. It runs at `session` depth from a clean working tree; record the base commit
(`git rev-parse HEAD`).

A consolidation never changes a decision. A decision that must change needs a new ADR with `supersedes`, outside this
run.

## Step 1: Group

Read every ADR in scope, superseded ones included (`uv run devkit docs list decision --history -n 0`).

- Group ADRs by topic: a group is one decision area a reader looks up, with two or more members.
- Put a wholly superseded ADR (`superseded_by` in frontmatter) in the group of its superseder.
- A partial supersession (`supersedes` with a "Superseded in part by" line) may cross groups. Note each crossing pair
  in the group map; Step 2 handles it.
- Leave out an ADR that contradicts another in-effect ADR or no longer matches the code or the Living Spec, and record
  it with the `spec-feedback` skill.
- Order members by `created_at`, then supersession order.
- If `RULE-file-length` configures `consolidated_max_lines`, use the larger of that budget and the resolved
  `max_lines` as a topic-breadth heuristic for each proposed replacement. Review an over-budget group by topic;
  preserve every driver, decision, rejected option and consequence. Never discard retained content to meet a budget.

Show the user the group map (replacement slug, members, one-line topic) before writing, unless the request named the
groups.

## Step 2: Write each replacement

Write `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`, dated today, from `.devkit/managed/docs/templates/decision.md`:

- Frontmatter: `status: accepted`, `created_at` today, `aliases:` every member ID and every alias a member declared;
  no `proposal`. Add `supersedes` only for an ADR kept outside the run that a member partially superseded; list the
  kept ADR there.
- Section 4 lists only statements in effect, each ending with its source ID in parentheses; a clause a "Superseded
  in part by" line names is not in effect.
- Considered options keep each option a member rejected, labelled by that member. No History section.
- For a crossing pair, the target's replacement leaves out the replaced clauses. The superseding replacement states
  what it replaced and cites the target's replacement ID.
- Add, drop or change the meaning of no driver, option, scope or consequence.

## Step 3: Apply and verify

1. `git rm` the member files, then run `uv run devkit rules fix` to rewrite alias references in current documents.
   If an ADR kept outside the run names a member in `supersedes`, name the member's replacement instead, and add the
   matching "Superseded in part by" line to that replacement. A kept ADR's own "Superseded in part by" line now names
   the member's replacement, which lists it in `supersedes` (Step 2).
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
