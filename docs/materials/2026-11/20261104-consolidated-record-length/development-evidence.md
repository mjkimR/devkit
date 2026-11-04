# Same-head consolidated record budget comparison

Method: run `.devkit/transient/consolidated-record-length/compare.py` with `uv run python` against the same
Development worktree files through the existing `services.testing.check` evaluator. Read the repository's
RULE-file-length settings in memory, preserving the capability override. First omit only consolidated_max_lines,
then use the configured 600. No checkout, historical file substitution or policy mutation is involved.
The probe is retained in the ignored worktree directory. This comparison is the accepted same-head baseline.

| Finding identity | Disabled | Enabled |
| --- | --- | --- |
| `ADR-adaptive-development-and-research` | line 401 | passes |
| `ADR-document-system` | line 401 | line 601 |
| `ADR-local-and-pull-request-integration` | line 401 | passes |
| `ADR-orchestration-workers` | line 401 | passes |
| `ADR-package-ownership-and-release-version` | line 401 | passes |
| `ADR-roadmap-and-milestones-ledger` | line 401 | passes |
| `ADR-rules-run-workspace-cache` | line 401 | passes |
| `CAP-DIST-sync-and-transactions` | line 601 | line 601 |
| `CAP-DLV-delivery-workflows` | line 601 | line 601 |
| `CAP-DLV-proposal-planning` | line 601 | line 601 |
| `UC-drive-development-to-integration` | line 401 | line 401 |

The six known ADR identities disappear. ADR-document-system remains at selected limit plus one (601).
Every unrelated finding keeps its identity, limit, line and numeric message. No invariant total is required.
