# Documentary verification

Baseline: `cf1c4fd4767131c2194bfccea618dc722f49108d`. Native checks ran synchronously in the assigned worktree.

| Check | Outcome |
| --- | --- |
| Exact normalized moved-block comparison | PASS roles, worker inspection, lifecycle; see relocated-sections.json |
| Workflow CAP / role CAP lines | 783 to 498 / 342 |
| Proposal CAP / lifecycle CAP lines | 784 to 352 / 518 |
| Distribution reference lines | 433 to 414; unique diagnostics and source subset retained |
| Cumulative rules against baseline | PASS no violations |
| Affected tests, tier all | PASS 17 tests; partial selection 8 paths, no fallback suppressed |
| E2E selection over baseline | PASS explicit mode=none, paths=0 |
| Sync start/final | PASS exit=0; no sync outputs |
| Whitespace | PASS cumulative git diff --check cf1c4fd4767131c2194bfccea618dc722f49108d; EOF fix verified |

Docs hygiene retains four justified warnings: sync capability 643/600, consolidated document-system ADR 621/600,
distribution reference 414/400, Development use case 415/400. The first two remain untouched; the reference keeps
unique indexes and the use case keeps every acceptance scenario. No line-budget override or line joining is used.
Runtime, lint/type/frontend behavior is unchanged and the Host supplied passing baseline evidence; no source tests
were added merely to reflect prose. No benchmark or runtime improvement is claimed.

Independent review P2 repair: every baseline H2/H3 heading remains in the original CAP as either contract text or
a redirect portal. New CAP entrypoints name three existing doorway files each; no broad shared directory is added.

Entrypoint derivation: PASS zero source-code candidates from documentary boundaries (53 excluded-tree boundaries,
8 non-entrypoint-bearing targets). No candidates applied. New manual doorway metadata is validated by rules and
docs list --file, which returns CAP-DLV-delivery-roles for worker CLI and CAP-DLV-proposal-lifecycle for handoff.

Independent reconciliation verified all20 targets, normalized block hashes, anchors, scenario bodies and backlinks.
It found the clean-worktree whitespace check did not cover committed changes. The extra roles EOF blank line was
removed, and the cumulative baseline diff is now checked explicitly. The change is whitespace-only.

Final document content at c46dfaca: cumulative committed-range whitespace, rules, sync and tier-all affected17
tests PASS. Only workflow evidence/status records follow this checked content.
