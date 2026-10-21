---
id: US-inspect-weekly-repository-progress
title: Inspect Weekly Repository Progress
summary: "A developer or agent obtains a bounded weekly report of verified work, decisions, health gaps and next actions without implicitly publishing it or running maintenance."
area: governance
actor: Developer or AI agent
status: active
capabilities:
  - CAP-DLV-weekly-report
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/weekly-report.md
---

# [US-inspect-weekly-repository-progress] Inspect Weekly Repository Progress

## 1. User Story Narrative

As a developer or agent, I want a revision-bound report of repository progress so I can distinguish verified
delivery from incomplete evidence, understand health limitations and choose useful next actions.

## 2. Context

Explicitly invoke weekly-report from the opt-in maintenance bundle. Supply scope, timezone/interval and local
artifact location, with optional prior report. Generation remains useful without maintenance artifacts or an
external destination. `CAP-DLV-weekly-report` defines evidence, comparison and publication boundaries.

## 3. Acceptance Criteria

### Evidence-based progress

- **Given** completed and unintegrated work, changed decisions and available verification artifacts.
- **When** the weekly report is generated for a captured revision and half-open timezone-aware interval.
- **Then** completed claims have status, verification and reachability evidence; unknown integration times remain
  snapshot limitations, and actions link existing follow-ups without creating work.

### Incomplete or changing evidence

- **Given** dirty/changing state, missing or stale checks, or an incompatible prior report.
- **When** evidence is collected and compared.
- **Then** dirty observations are separated, changed evidence re-collected or marked unverified, health gaps stay
  explicit, and absence never implies clean or resolved.

### Rerun and publication

- **Given** a verified immutable report and a same-period rerun or publication attempt.
- **When** the new artifact or authorized publication is recorded.
- **Then** reruns preserve predecessors; a separate companion carries digest and outcome; no authority means
  pending, a verified receipt means published, confirmed failure means failed, and lost response stays unknown
  until destination inspection resolves it. No blind retry or implicit external mutation occurs.
