---
id: PROP-viewer-decision-supersession
title: Show decision supersession in the Living Spec viewer
summary: "Show on a decision's viewer page which earlier ADRs it supersedes and which later ADRs supersede it, with the replaced scope from the partial-supersession statements, so a reader sees a partly replaced decision's state without running a command."
status: reviewing
created_at: 2026-11-10
target_area: capabilities/viewer/
namespace: global
priority: low                         # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
depends_on: [SPEC-partial-adr-supersession-statements]
boundaries:
  owns:
    - packages/devkit-viewer/
    - docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
  excludes:
    - packages/devkit-spec/
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-viewer-decision-supersession] Show decision supersession in the Living Spec viewer

## 1. Background & Hypothesis

`SPEC-partial-adr-supersession-statements` makes the replaced scope of a partial supersession a fixed statement in the
later ADR and adds `devkit docs supersession` for agents. Its Planning left the viewer out: the viewer change is a
separate package, capability and verification chain (`materials/planning-evidence.md` section 6 there).

The viewer's decision page shows `id`, `status`, `priority`, `milestone`, `target_area` and the title. It shows no
`supersedes`, and it has no list of the documents that reference the page. A reader of a partly replaced ADR sees the
"Superseded in part by" lines in its body and has to open each later ADR to see the rest.

### Hypothesis

A decision page that lists both directions (the earlier ADRs this decision supersedes, and the later ADRs that
supersede it, each with `whole` or `partial` and the statement text) lets a reader judge a decision's state on one
page.

## 2. Technical Spike Questions

- **Q1 Data source**: does the frontend build the reverse direction from the decision files it already loads, or does
  the viewer server gain an endpoint? An endpoint that reuses devkit-docs adds a package dependency the viewer does
  not have.
- **Q2 Placement**: where on the decision page do the relations appear, and do they apply to a PADR page?
- **Q3 Screens**: does `ADR-ux-screens` require a drafted screen for this change?

## 3. Proposed Design & Impact

To be settled in Planning. Expected touch points: `packages/devkit-viewer/frontend/`, the committed build under
`packages/devkit-viewer/src/devkit_viewer/static/` and `CAP-VIEW-repository-viewer` section 4.

## 4. Lifecycle & Retirement Criteria

Planning starts after `SPEC-partial-adr-supersession-statements` is delivered, because the page reads the statement
form that work defines. The draft is dropped if that work is rejected.
