---
name: decompose-initiative
description: Decompose a large engineering goal into phased GitHub Milestones and Issues with the gh CLI.
aliases: [roadmap planning, milestone planning, initiative breakdown, split large feature]
---

# Initiative decomposition procedure

## Prerequisites

- The goal is estimated L or XL under the `github-milestones` instruction, or the user asks for phased milestones.
- `gh auth status` succeeds and `gh repo view --json nameWithOwner -q .nameWithOwner` names the target repository.
  Otherwise stop and ask the user to install or authenticate the GitHub CLI.

## Procedure

1. Shape the goal with the user: the problem it solves and its delivery boundaries (for example CLI, runtime,
   governance).
2. Propose 2 to 4 sequential phases: a foundation (data models, interfaces, minimal baseline), the main
   implementation, then hardening and integrations. Under each phase, list S or M work items.
3. Present the phases and work items and wait for the user's confirmation. Create nothing on GitHub before it.
4. List the existing milestones:
   `gh api repos/{owner}/{repo}/milestones --jq '.[] | {number, title, state}'`.
5. Create each confirmed milestone that does not exist yet:
   `gh api repos/{owner}/{repo}/milestones -f title="<title>" -f description="<phase description>"`.
6. Create one issue per work item under its milestone:
   `gh issue create --title "<title>" --milestone "<milestone title>" --body "<scope and acceptance criteria>"`.
7. When the project keeps a planning or design document for a work item, record the issue in it as the
   instruction describes.

## Completion conditions

Report the milestones and issues created, with their numbers and URLs, and name the first work item to start.
Remind the user that merging with `Closes #<number>` closes the issue and advances its milestone.
