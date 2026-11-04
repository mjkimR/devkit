# Consolidated record budget evidence

Source baseline: `2cf7879a74b50b687867e2184188dee6c29a2fbc`; Planning work commit changes only this proposal.

## Current implementation

`FileLengthSettings` in `features/rules/services/builtins/file_length/rule.py` has `max_lines` and `extensions`.
`SettingsResolver` in `features/rules/models/settings.py` resolves a dataclass by path patterns and already
supports optional integers; changing it is unnecessary for a rule-owned option.
`WorkspaceCache.get_frontmatter` reads through the shared parser/cache and raises `FrontmatterError` on an invalid
header. Calling it only above the ordinary budget avoids parsing unaffected files.

The ADR consolidation playbook requires two member records, each preserved through aliases. A renamed ADR can
also accumulate aliases, so count is a heuristic. The feedback playbook has no two-member lower bound and its
scaffold shows one alias. ID-kind guards keep unrelated alias-bearing documents outside the alternative budget.

## Measured hygiene baseline

Command: `uv run devkit rules check --phase hygiene --format json`; exit 0, no errors, eleven warnings, all
`RULE-file-length`. `WORKTREE_STALE_SKIPPED` noted unavailable gh authentication; stale-branch inspection is
unrelated to the measured file-length findings.

| ID | Measured lines | Current limit | Proposed limit | Result with option |
| --- | ---: | ---: | ---: | --- |
| `ADR-adaptive-development-and-research` | 471 | 400 | 600 | passes |
| `ADR-document-system` | 619 | 400 | 600 | warning |
| `ADR-local-and-pull-request-integration` | 536 | 400 | 600 | passes |
| `ADR-orchestration-workers` | 529 | 400 | 600 | passes |
| `ADR-package-ownership-and-release-version` | 455 | 400 | 600 | passes |
| `ADR-roadmap-and-milestones-ledger` | 407 | 400 | 600 | passes |
| `ADR-rules-run-workspace-cache` | 425 | 400 | 600 | passes |
| `CAP-DLV-delivery-workflows` | 714 | 600 | 600 | warning |
| `CAP-DLV-proposal-planning` | 799 | 600 | 600 | warning |
| `CAP-DIST-sync-and-transactions` | 620 | 600 | 600 | warning |
| `UC-drive-development-to-integration` | 420 | 400 | 400 | warning |

Largest feedback record: `FB-consolidated-delivery-promoted`, 110 lines and fifteen aliases.
The initial draft's historical approximation is superseded by this measured baseline, not by a changed record.

## Development reproduction

Use the same final head's files twice through the existing evaluation/testing entrypoint, passing rule settings
in memory. First omit `consolidated_max_lines`, then pass 600, preserving every other configured setting and
path override. Compare warning identities; six ADRs above disappear and `ADR-document-system` remains. New
history or unrelated integrated edits can change the total, so total five is a prediction for this baseline,
not an invariant assertion against a moved branch. No checkout or project-config mutation is needed.

## Scope and cost

A generic matcher requires changes to config decoding, settings metadata, resolver dependencies and every
consumer's validation contract. The selected optional field reuses validation and per-path resolution, adds
no feature edge and changes no document kind. Parsing is bounded to targeted over-budget Markdown with the
option enabled. No runtime or latency claim has been measured.
