---
id: SPEC-viewer-dashboard-pagination
title: Dashboard cached lists and incremental pages
summary: "Cached section metadata preserves dashboard ordering and counts while only visible pages fetch full document bodies."
status: completed
created: 2026-10-24
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---


# [SPEC-viewer-dashboard-pagination] Dashboard cached lists and incremental pages

## Problem and User Story

The dashboard reads all matching bodies before rendering a subset. Users need incremental cards with stable order and cached tab revisits.

## Non-Goals

- **Scope Excluded**: persistent indexes, watchers, other tabs and live updates within a snapshot.

## Acceptance Criteria

### [AC-01] Selective bodies
- **Given** a local section with more entries than one page
- **When** it opens
- **Then** candidate frontmatter supplies ordering and exact counts, and only the first 6 milestones, 9 proposals or 6 feedback bodies are requested.

### [AC-02] Stable pages
- **Given** a sorted snapshot
- **When** Load more is selected
- **Then** at most one page is appended, preserving status/severity then ID order, with path tie-breakers and no duplicate paths.

### [AC-03] Cache freshness
- **Given** loaded pages
- **When** the same source and branch reopen within 30 seconds of list completion
- **Then** list and loaded bodies are reused; expiration or Refresh starts a fresh first page.

### [AC-04] Errors and disposal
- **Given** a page failure or disposed view
- **When** pending work finishes
- **Then** existing cards survive page errors with a retry control, and aborted or stale work cannot publish to a replacement view or refreshed cache.

### [AC-05] Optional host capability
- **Given** an injected source without dashboard metadata support
- **When** its dashboard opens
- **Then** selective full-scan fallback remains supported with paged rendering; cold fallback may read all matching bodies.
