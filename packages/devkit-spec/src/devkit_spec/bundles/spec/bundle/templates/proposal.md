---
id: PROP-<slug>
title: Proposal Title (e.g., Pre-action Hook Context Advisor)
summary: "One or two English sentences: what this proposal changes and why"   # required, English; quote it, it may contain ": "
status: draft                         # draft | reviewing | accepted | rejected
created_at: YYYY-MM-DD
target_area: capabilities/<area>/      # Target capability area on graduation: an existing area, docs-root or repository path (e.g., governance/)
priority: high                        # critical | high | medium | low (estimated priority)
size: M                               # S | M | L | XL (estimated scope: S=single fix, M=1-2 sessions, L=complex module, XL=major overhaul)
# milestone: MS-<slug>                # direct PROP membership only; never carried to spec.md
# depends_on: [PROP-foundation, SPEC-parser] # exact prerequisite anchors; omit when empty
boundaries:                           # declared scope impact (owns) and excluded scope (excludes), carried to the spec
  owns:                               # existing paths (RULE-proposal-boundaries); a path to create: its nearest existing parent
    - capabilities/<area>/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
planning_effort: medium               # low | medium | high: Planning activity-effort hint
dev_effort: medium                    # low | medium | high: Development activity-effort hint
# supersedes: PROP-<old-slug>         # close by supersede: the accepted proposal this draft replaces
# needs_decompose: true               # Backlog splits this draft before Planning starts
---

# [PROP-<slug>] Proposal Title

## 1. Background & Hypothesis
<!-- Describe background, current challenges, and core hypothesis to address -->

## Source feedback (when this proposal receives feedback)
<!-- List full FB IDs and the scope this work receives; keep these references in the handed-off spec. Promotion
closes the feedback by handing it to follow-up work; the source stays promoted when that work finishes.
Resolution closes a verified direct fix without promotion. Omit this section when there is no source. -->

## 2. Technical Spike Questions
<!-- Define key uncertainties and technical questions to answer -->
- **Q1**: 
- **Q2**: 

## 3. Proposed Design & Impact
<!-- Describe expected architectural design, CLI commands, and structural impact -->

## 4. Lifecycle & Retirement Criteria
<!-- 
- On Acceptance: recorded with devkit spec proposal accept (after Planning, or --direct for an eligible draft in Backlog); handed off to a spec bundle on dev-<slug>; the proposal is deleted there and its decisions become ADRs
- On Rejection: status: rejected only, with the user's reason in the commit message; a later hygiene pass writes the rejection ADR and deletes the proposal
-->
