# Bounded semantic exercises

This is execution evidence for `SPEC-incubation-discovery-teams`, not a statistical quality benchmark.
All product inputs and Vendor A/B pages in the matched fixture are fictional. No product, storage choice,
user interview, observed demand or production implementation is claimed.

## Method and identity

The isolated consumers were built with actual catalog/docs synchronization. Baseline used the pre-feature
`incubate` skill; candidate used the implemented user-invoked `incubate-research` skill. Inputs were the same
three raw files: ambiguous product request, architecture request and conflicting fictional source pack.
One initial research wave per variant was permitted, with at most four optional helpers and 1000 retained words.
Each evaluator was a fresh context with only its own consumer and raw inputs, not intended answers or peer output.

Host: Codex application. Agent calls used `fork_turns=none` and inherited model/effort; effective provider settings
were not surfaced. This is one matched composite fixture, not repeated or randomized trials. No quantitative
quality, cost or token-saving inference is supported.

`evidence/run-metadata.json` identifies baseline and pre-workspace candidate bundle digests and the input digest.
`evidence/workspace-metadata.json` identifies the refined scratch/promotion candidate and its Git baseline.
The input tree digest is `d0c017b50181f922eefa089cd0832a7462744a6441c4ac145b272e9f78fdf666`.
Source starting commit was `f22a533ade38d2675493d674638688226c15ea69`; bundle digests identify uncommitted guidance.

Snapshots in `evidence/` retain the raw inputs and selected product outputs, not whole temporary runs.
Machine-specific runtime/consumer prefixes in copied contexts are replaced by `<runtime>`/`<consumer>`.
The snapshot manifest records original and stored SHA256 values; these normalized copies are not byte-identical
to originals where a path was replaced.

## Observed cases

| Case | Actual execution | Observed result and limits |
| --- | --- | --- |
| Baseline | Existing skill, no helper calls or network; config/context/docs inspection and rules | 931 retained words; compared workaround/local/server, qualified Vendor A claims and proposed a conditional roadmap. It already handled the basic task well. |
| Candidate before scratch refinement | New skill; two independent generic/emulated direction-explorers and one generic/emulated critic | 962 words; critic challenged an unsupported local-file preference, which the coordinator removed. Compared burdens and preserved all three alternatives. Consumer had no Git; file hashes substituted for index/HEAD checks. |
| Fresh planner/resume | Fresh generic/emulated discovery-planner read candidate context, note and linked raw inputs | Recovered that no direction/storage was approved, identified unresolved overlap/value/burden assumptions, and drafted a next learning step with reopening conditions. Six inspected file hashes were unchanged. |
| Real primary-source research | Generic/emulated incubation-researcher; one contract read and two official page opens, no searches/writes | Official Zotero sync/groups pages distinguish personal WebDAV file sync from group attachment sync. The role reported this as a constraint, with actual offline/API/server behavior untested. This was separate from fictional product evidence. |
| SDD approach control | Installed pre-workspace research entry read its consumer; config returned effective SDD | Stopped product work without changing approach or creating retained notes. |
| Invalid approach control | Installed pre-workspace entry attempted context inspection | Exit 2, `DEVELOPMENT_CONFIG_INVALID`; stopped without repair, product work or helper calls. |
| Refined workspace/promotion | Workspace-refined guidance before the shell-example correction in a Git consumer; generic/emulated explorer and planner wrote separate assigned scratch files | 700 retained words; exact run/task paths ignored and untracked, no helper writes outside scratch, source/config/managed/projection hashes and HEAD/index unchanged. Master retained only research synthesis/current facts, with resolving non-scratch evidence links. |

All generic roles followed their installed effective contracts with explicit boundaries. They were not native
registered-role/sandbox enforcement tests. The primary-source-only role had no repository read scope for a
before/after Git comparison and performed no write operations; it does not establish a native confinement guarantee.

## Workspace refinement and checks

The refined run allocated a collision-free run under `.devkit/transient/incubation-research/` and separate explorer
and planner directories. The explorer wrote `notes.md`; planner wrote `roadmap-draft.md`. The coordinator retained
a run brief/comparison/check record in scratch and promoted only selected product research and current facts.
Scratch was preserved, not deleted or copied wholesale. No configuration or ignore rule was modified.

In the Git consumer the coordinator checked exact run/task paths with Git ignore/tracked queries and compared
actual source/configuration/managed/projection file hashes plus HEAD/index before and after helpers.
Final outside-scratch changes were exactly the retained research note and current-context file.
Retained links resolved independently of scratch. No real usage measurement, code experiment or publication ran.

Consumer rules checks reported 13 rules, zero errors/warnings in baseline, candidate and workspace runs.
Input identities were computed from actual files. The fresh planner confirmed raw-source identity
`660bfd64a9b4d1427a0a65d8f94f263eb84f06a05ce687d4d192c36819fa4899`.

## External source probe

Actual public sources accessed on 2026-10-29:

- [Zotero Syncing](https://www.zotero.org/support/sync): data/file sync and personal-library WebDAV support.
- [Zotero Groups](https://www.zotero.org/support/groups): group-library sharing/file-sync constraints.

The role found personal WebDAV attachment sync does not extend to group libraries. It kept offline completeness,
integration APIs, compatibility and actual conflict behavior unverified. Two sources do not constitute a market
survey, user validation or selection of a product direction.

## Interpretation and coverage

The observed benefit is deliberate research entry, independently scoped member work and a critic correction.
Baseline also produced useful alternatives and limits. These observations do not show general superiority,
escape from every local optimum, real-user usefulness, exact token cost or reproducible model-level performance.

Distribution/invocation/preservation are covered by catalog integration and built-wheel consumer tests; they
cannot prove research truth. Role absence, stop conditions, cross-candidate judgment and refusal behavior also
require contract review. The explicit workspace run checks positive allocation/promotion, not every filesystem
race, ignore-rule combination or native host permission configuration.

An ordinary small question remains permitted inline. The exercise budgets are fixture bounds, not mandatory
product defaults. The new skill adds no allocator registry, runtime scheduler or test-generated product code.

## Review regression: executable allocation example

Independent code review found an unmatched quote in the task-directory example. The installed-consumer e2e
was extended to extract the shipped shell block, syntax-check it and execute it twice, checking distinct run
paths, task containment, effective Git ignoring and no tracked scratch content. It failed on the old example
with a shell parse error. After the exact quote correction, zsh syntax validation and the affected suite passed
(99 tests), including the built-wheel consumer regression. Catalog lint/format/type checks passed.
The earlier live workspace exercise used ordinary filesystem operations and did not execute that literal
example; its observed results remain bounded to the recorded bundle digest. The regression tests the final
shipped example directly rather than claiming that earlier run covered its syntax.
