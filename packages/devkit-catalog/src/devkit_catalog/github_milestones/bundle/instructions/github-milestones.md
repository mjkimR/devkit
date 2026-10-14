---
name: github-milestones
description: Read when splitting a large initiative into phased GitHub Milestones and Issues, sizing work items, or linking commits and pull requests to them.
---

# GitHub Milestone Conventions

Apply these conventions when an initiative spans several deliveries and is tracked with GitHub Milestones and Issues.

## 1. Sizing and Phasing

Estimate every work item before planning it. Never fold a large initiative into one work item:

- **S** (one fix, one session): one issue; no milestone needed.
- **M** (one or two sessions, one bounded module): one issue.
- **L** (several components): split into two sequential issues, or a two-phase milestone.
- **XL** (major initiative or system overhaul): decompose into 2 to 4 sequential milestones before implementation
  starts; each milestone holds independently deliverable S or M issues.

## 2. Repository and Tracker Boundary

- The repository holds current-state documentation and the code. Do not keep roadmap tables, phase checklists or
  progress checkboxes in repository Markdown.
- GitHub Milestones hold the phases (`Phase 1: Storage foundation`, `v0.5.0`) and their progress.
- GitHub Issues hold one deliverable work item each and are the identifier for discussion and closure.

## 3. Linking Work to Issues

- When the project keeps a planning or design document for a work item, record the issue there as
  `**Tracker**: #<number> (<issue URL>)`.
- Name the issue in the pull request description, and in the final commit message when there is no pull request.

## 4. Completion

Do not update progress by hand in several places. Close issues through GitHub's closing keywords: put
`Closes #<number>` or `Fixes #<number>` in the pull request description or the final commit message. Merging closes
the issue and advances its milestone.
