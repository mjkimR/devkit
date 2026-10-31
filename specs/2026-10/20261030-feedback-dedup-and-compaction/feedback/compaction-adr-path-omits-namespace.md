---
id: FB-compaction-adr-path-omits-namespace
title: The feedback compaction ADR's record path omits the package namespace its record ID carries
scope: repo
kind: change-request
category: docs-mismatch
target: ADR-closed-feedback-compacts-into-per-area-records-with-aliases
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-compaction-adr-path-omits-namespace] The feedback compaction ADR's record path omits the package namespace its record ID carries

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `ADR-closed-feedback-compacts-into-per-area-records-with-aliases` names the record
  `FB-compacted-<namespace>-<area>-<status>` in a package namespace but its path always
  `specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md`. `RULE-id-convention` derives a month-level
  feedback ID from the file name, so the literal path gives the global ID.
- **Proposed Procedure**: a wording-only repair of the ADR's record bullet: in a package namespace the file name is
  `<YYYYMMDD>-compacted-<namespace>-<area>-<status>.md`, as the `feedback-compaction` playbook and
  `CAP-HARN-agent-guidance` already state (`SPEC-feedback-dedup-and-compaction`).
- **Expected Benefit**: the ADR, the playbook and the capability agree; a reader of the ADR cannot derive a colliding
  record ID.
- **Cost & Risk**: one sentence in an accepted ADR, an editable-record wording repair with no decision change.
- **Attempted**: the playbook and capability carry the namespaced file name; the ADR was outside this spec's write
  scope (`docs/decisions/` excluded).

## Diagnostic Details

- **Reproduction**: write a record with ID FB-compacted-pkg-delivery-resolved (an example ID) at
  `specs/2026-10/feedback/20261030-compacted-delivery-resolved.md` and run the `id-convention` rule.
- **Expected / Actual**: expected no violation; the rule reports that the path requires
  FB-compacted-delivery-resolved.
- **Versions**: branch `dev-feedback-dedup-and-compaction` at `5bc54069`.
- **Conditions**: a repository with a package namespace (`[[tool.docs.namespaces]]`).
- **Workarounds Attempted**: the playbook names the file with the namespace; verified by
  `test_feedback_compaction_guidance.py` (package-namespace case).
- **Related Assets**: `ADR-closed-feedback-compacts-into-per-area-records-with-aliases`, `RULE-id-convention`, the
  `feedback-compaction` playbook.

## Evidence

```text
review-01 finding 1 probe: 'Frontmatter id is "FB-compacted-pkg-delivery-resolved" but the path requires "FB-compacted-delivery-resolved"'
reconcile-check-01 finding 1 (P3): the ADR path omits the namespace segment
```

## Disposition

- **Disposition**: `docs/decisions/2026-10/20261030-closed-feedback-compacts-into-per-area-records-with-aliases.md`: resolved as a wording repair specifying the package-namespaced file name `<YYYYMMDD>-compacted-<namespace>-<area>-<status>.md`.
