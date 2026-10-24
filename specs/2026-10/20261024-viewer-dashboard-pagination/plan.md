---
id: PLAN-viewer-dashboard-pagination
spec: SPEC-viewer-dashboard-pagination
---
# Plan for `SPEC-viewer-dashboard-pagination`

## 1. Constitution & Invariant Review

None. Preserve browser parsing and working-tree guards from `CAP-VIEW-repository-viewer`.

## 2. Architecture Overview & Impact

Expose dashboard-list?path=milestones|proposals|feedback with UTF-8 frontmatter and per-file errors. Read only through the closing frontmatter delimiter; all candidate headers are necessary for global ordering and exact counts. Optional source.dashboardList supplies these entries. Other hosts retain selective scans.

## 3. Component & Interface Design

Parse headers in the browser, sort/filter through dashboard extraction and freeze eligible paths. Body workers fetch only requested 6/9/6-card pages with at most six concurrent requests. Keep loaded documents within the section snapshot. Key cards by path and append without resorting changed bodies. Retry failed pages without discarding cards.

## 4. Storage & State Management

Use source/ref/purpose cache entries. Expiry is fixed at list completion plus 30 seconds; page requests do not renew it. Commit only successful immutable snapshots through the original generation. Refresh invalidates source caches; disposal aborts publication. Sorted membership stays fixed until refresh even if files change.

## 5. Error Handling & Edge Cases

Missing roots are empty; read errors and invalid YAML remain visible. Invalid sections return 400 VIEWER_PATH_INVALID. Reuse symlink, .git and traversal guards. No server YAML parsing or new dependency.

## 6. Verification & Test Plan

Test header-only reader/HTTP responses, page body counts, stable order under delayed completion, cache/expiry, retry and disposal. Run just viewer lint/check/test/build/pack, just lint-check viewer, just check viewer, just test-affected and generated viewer-assets verification.
