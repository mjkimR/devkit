# Design options compared (Planning round 1)

Inputs: `scout-01` (internal, `q2-internal-integration.md`), `scout-02` (external, `q1-review-criteria-research.md`).
The `user` direction for this turn adds that the playbook must cover consolidation and reduction explicitly:
merging duplicated logic into shared modules, folding repeated technical helpers into utilities, and removing
unneeded code, guidance, options and commands.

## O1. Run shape: one playbook or one per surface

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. One `review-refactor` playbook covering code, guidance and CLI, run in batches (chosen) | Milestone exit names one broad pass (`MS-maintenance-operations`); cross-surface findings exist, such as a CLI docstring against guidance (q1 RC-L4) | One asset, one capability, one use case | The playbook must stay within the skill size budget (12288 bytes) |
| B. Three playbooks, one per surface | Criteria sets are distinct (q1 §2) | Three assets, three capabilities, triple packaging edits | Duplicated intake, decision and report text; contradicts the proposal's single asset |

## O2. Bounding a run (spike Q2; user question)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. User-selected scope (surfaces and roots) at intake, split into batches of one surface each, with one decision round per batch; a cross-surface finding cites both sides and belongs to the batch of the surface where its change lands (recommended; chosen by `user`) | Proven drift-reconciliation pattern (drift-reconciliation.md:12-17) | Low; reuses the shared wording | Batch size is agent judgment |
| B. All three surfaces with a top-N candidate cap | weekly-report ranks by impact (weekly-report.md:51-52) | Medium; needs a ranking rule | Arbitrary cap; incomparable criteria; large mixed diffs |
| C. Diff-driven since the last run or a named ref | weekly-report snapshot capture | Low only with history | Misses accumulated debt; coupled to `PROP-maintenance-history` |

## O3. Removing commands, options and public interfaces (user direction 3; user question)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. The decision round may approve a contract removal, which is applied as a separate contract change through the repository's development workflow and kept apart from behavior-preserving changes (recommended; chosen by `user`) | q1 RC-L5 (contract change, never refactoring); `user` reduction direction | Medium; a second work item per contract removal | A larger run when many contract removals are approved |
| B. A contract removal is always a deferred follow-up | Proposal draft §3 | Low within the run | Reductions accumulate as unworked follow-ups, the failure the `user` direction names |
| C. A removal is in-run refactoring when no consumer is found | None | Lowest | A dynamic or external consumer the search misses breaks; mislabels a contract change |

## O4. Evidence that a removal or consolidation preserves behavior (user question)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. Evidence per change: reachability (static references plus the repository's dynamic reach: entry points, plugin registries, configuration, documentation, string dispatch); relevant verification before and after; a characterization test when no test exercises every merged caller; for guidance, a retained-constraint map (recommended; chosen by `user`) | vulture misses dynamic code (q1 §3.2); behavioral check for guidance (q1 §4, G8) | Medium | Characterization tests add test code, but only where coverage is missing |
| B. Characterization tests before every removal or merge | Fowler: refactoring rests on tests | High | Adds test volume, against the reduction goal |
| C. Existing relevant verification passing is enough | Repository verification policy | Low | Untested removed paths pass trivially |

## O5. Where consolidated helpers live (user directions 1 and 2; user question)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. Lowest common owner every caller may already depend on under the target repository's declared layering; a new cross-package or foundation module, or a repository with no declared layering, is a decision in the round (recommended; chosen by `user`). In devkit: feature-local, then a package-level `utils` (technical) or `base` (contracts), then `devkit_core` only for generic primitives with no application dependency (AGENTS.md architecture section) | AGENTS.md: package-level `utils` and `base` are created only when needed; `devkit_core` never imports application packages | Low | Judgment on what is "generic" |
| B. Always a common `utils` module in the nearest shared package | None | Low | Breaks layer direction; grows a catch-all module |
| C. Merge only into existing shared modules; a new shared module is a follow-up | Conservative | Lowest | Blocks most consolidations the `user` direction asks for |

## O6. Preset placement (user question)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. Add to `upkeep` and add a solo preset `refactoring` (recommended; chosen by `user`) | The proposal requires selection without the other playbooks; `upkeep` was the earlier accepted grouping (q2 packaging) | Low | Projects that already select `maintenance:upkeep` receive it on their next sync (no external consumers yet) |
| B. `upkeep` only | Earlier accepted design | Lowest | No preset deploys it alone |
| C. Solo preset only | Independence | Low | `upkeep` no longer means all upkeep work |
