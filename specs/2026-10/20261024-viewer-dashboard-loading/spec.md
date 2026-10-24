---
id: SPEC-viewer-dashboard-loading
title: Incremental dashboard loading
summary: "Load dashboard sections from relevant documents and reuse bounded caches across tab visits."
status: active
created: 2026-10-24
related_capabilities: [CAP-VIEW-repository-viewer]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-dashboard-loading] Incremental dashboard loading

## 1. Problem Statement & Motivation

The dashboard indexes all Markdown before rendering. Tab remounts repeat the index and fixed request batches wait for their slowest member.

## 2. User Stories

- As a viewer user, I want independent dashboard sections and fast tab revisits with an explicit refresh.

## 3. Non-Goals

- **Scope Excluded**: replacing the HTTP framework, filesystem watchers, persistent caches or changing feedback coverage.

## 4. Acceptance Criteria

### [AC-01] Selective reads

- **Given** milestone, proposal, nested feedback and unrelated documents
- **When** the dashboard loads
- **Then** blob requests read only docs/roadmap/MS-*.md, direct docs/proposals/PROP-*/proposal.md anchors and non-README Markdown below feedback directories within docs/ and specs/.

### [AC-02] Independent rendering

- **Given** pending feedback and completed milestones
- **When** milestone reads finish
- **Then** milestone cards and counts display independently while feedback shows loading. Errors stay local and cannot appear as successful empty results.

### [AC-03] Bounded cache

- **Given** successful section, full index or roadmap results
- **When** revisiting within 30 seconds
- **Then** parsed results are reused without content requests, isolated by source identity, branch and purpose, with at most eight entries per source.
- **Given** expired, failed or aborted work
- **When** revisiting
- **Then** requests retry and partial or aborted results are never cached.

### [AC-04] Refresh and disposal

- **Given** cached data or in-flight requests
- **When** Refresh is selected or the source changes
- **Then** refresh invalidates source caches and reloads saved files, and disposed requests cannot publish to another view.

### [AC-05] Continuous workers

- **Given** one slow request and queued work
- **When** another request finishes
- **Then** another queued job starts without waiting for the slow request, with at most six requests per scan.
