# Mandatory review: repeated reader trials and ownership audit

## Identity and limits

Reader/reviewer: nested Code Reviewer pilot_review. Reviewed source:
`3a1a21701faf9c827088204b586aaf7a25e77359`, base
`3d21622a44ccb9fdf1388a33b360bf39c71a79a1`. Verdict PASS, no findings.
The CLI review record is `envelopes/review-01.yaml` in the spec unit.
Before/after content snapshots were identical: `5fabe976c544a6fbcfe1efe1203572714c1f3751`.

The contract-only trial ran before the reviewer received draft names, unit or diff. The three supplied entries
were later fetched in one batch; their cross-role content was visible before follow-up. These repeats are not
three separately blinded sessions. Read boundaries were emulated through explicit cwd, read-only commands,
opened-path reports and unchanged snapshots, without a native enforcement claim.
The reviewer initially opened the base checkout's response-style skill for reply instructions; that outside-worktree
read was disclosed to the Host. All content evidence came from the assigned worktree. No probe, recovery,
file edit, staging or commit was performed. No package-context, viewer, timing or exhaustive-corpus test ran.

## V1: fresh contract-only design discovery

Starting inputs: the file/directory replacement question and `CAP-DIST-sync-and-transactions` §3 numbered items
1–6 only. The extract stopped before Post-Sync Extensions; only its heading appeared as a delimiter, without
subsection content or truncation.

| Opened document/section | Why |
| --- | --- |
| `CAP-DIST-sync-and-transactions` §3 items 1–6 | Given input; transaction/recovery guarantees |
| `CAP-DIST-workspace-ownership`, entire | Follow exact item-1 reference to check for detail routing; frontmatter/entrypoints and §2 useful; layout, overrides, preferences and snapshots unnecessary overread |

Answer: journal previous file evidence and created/replaced directories before mutation; delete owned blockers
before writing; restore prior contents and remove empty created directories on rollback. Foreign blockers fail
preflight and subsequent edits block recovery. The capability owns those guarantees.

Result: direct-reference discovery GAP. No design ID/link reaches the topology mechanism detail. The ownership
detour returns to the sync owner. The six-step overview and operational next actions are clear; the detailed-design
next step is absent. No whole-layer prerequisite was imposed. Ownership detour and broad extraction were unnecessary
work. No corpus search or known draft filename supplied the missing hop.

## V2: supplied design entry

Starting inputs: same question plus [design entry](design-entry.md).

| Opened document/section | Why |
| --- | --- |
| design-entry.md, all | Overview, owner map and detail link |
| replacement-detail.md, all | Independent mechanism explanation and symbols |
| transaction.py, all | Validate named eligibility/journal/application/recovery symbols, including atomic_write/replace_file; unrelated lock/JSON helpers were unnecessary surrounding code |
| `ARCH-05-4-distribution-components` §3 | Confirm installation-service ownership |

Result: useful entry → detail → source path. The detail matches preflight, before/after encoding, deletion-first
ordering, created/replaced directory recording, journal-before-application, directory removal, atomic delegation,
reverse application and empty-directory pruning. The entry overview/next step are explicit. No entry return or
runtime-view prerequisite was needed. Safety remains in `CAP-DIST-sync-and-transactions` §3. This success does not
repair V1's discovery gap.

## V3: domain concept to contract

Starting inputs: availability/selection/projected-path/receipt question plus [domain entry](domain-entry.md).

| Opened document/section | Why |
| --- | --- |
| domain-entry.md, all | Supplied relationship overview |
| `CAP-DIST-content-packages` §§1–3 | Availability/discovery/dependency boundary; packaging syntax/lifecycle examples unnecessary |
| `CAP-DIST-manifest-spec` §3 | Presets/default/auto-selection; earlier manifest syntax unnecessary |
| `CAP-DIST-agent-projections` §1 | Host/kind destinations |
| `CAP-DIST-sync-and-transactions` §1, §2 opening, Resolution Order through Unselected/Auto-Selected Bundles | Applied evidence and effective selection |

Answer: Python installation supplies availability; explicit presets or auto-selection determine selected assets;
projected kinds map to host paths; receipt records applied selection, versions, asset paths and hashes/modes.
Receipt selection is audit evidence, not input. The cited capability sections remain owners.

Result: useful supplied concept-to-contract path, with clear distinctions and next steps. No design/source
prerequisite or unnecessary document return. A combined extraction truncated surrounding output; narrower
follow-ups recovered required passages. The repeat demonstrates useful routing, not perfect extraction efficiency.

## V4: operations four documented states

Starting inputs: four-state/readiness question plus [operations entry](operations-entry.md).

| Opened document/section | Why |
| --- | --- |
| operations-entry.md, all | Symptom/evidence/owner map |
| `CAP-DIST-sync-and-transactions` §3 item 6 | Recovery ownership for pending, edited and legacy cases |
| Same capability, Readiness Gate | Desired-state criterion and exit interpretation |
| Distribution reference heading/code search, devkit status lines 203–225, Error codes | Locate anchors and verify installed-state distinction/action rows; neighboring error rows unnecessary |

Conclusions: pending interruption is `TRANSACTION_PENDING` with the existing AUTO/recover mapping. Subsequent
edits and legacy journals without `directories` are `RECOVERY_BLOCKED`/HALT; existing owners retain content and
version-specific/manual recovery decisions. No-journal/desired-state drift is not ready. The readiness owner
requires sync --check exit 0; exits 1/2 are not ready.

Result: useful symptom-to-owner path for all four paper states. Overview, evidence discriminators and next owners
are clear. No domain/design prerequisite or entry return. No actual advisory, recovery or fixture was executed.

## V5: separate allowed-search trial

Extra starting information: permission to use lexical search/refs/resolve, the transaction question tokens and
known `CAP-DIST-sync-and-transactions` ID. This trial ran after supplied entries; only the stated tokens/ID entered
its query/lookup arguments. It is distinct from fresh contract-only V1.

All commands below used `uv run devkit` and exited 0:

- `docs search 'managed file directory rollback journal' --mode lexical --limit 5 --format json`
- `docs resolve CAP-DIST-sync-and-transactions --format json`
- `docs refs CAP-DIST-sync-and-transactions --direction out --limit 10 --format json`
- `docs refs CAP-DIST-sync-and-transactions --direction in --limit 5 --format json`

Workspace ownership ranked first and sync transactions second. Indexed runtime-ordering feedback appeared fourth.
Resolve returned the canonical owner; refs reported 20 outgoing and 85 incoming documents. Only bounded pages were
inspected. Existing facilities reach indexed owners; this neither promises ID-free draft discovery nor proves a
search-tool failure or need for a new kind. The incoming total differs from the earlier 84 because the build added
the indexed unit feedback referencing this owner.

## Ownership audit and additional review reads

The reviewer inspected unit spec/plan/tasks, actual diff, ledger, first-reader trials, evidence and preserved
example-selection protocol. It compared the glossary's existing devkit bundle/projection rows and the runtime-order
feedback against `ARCH-06-runtime-view` §1. It inspected `CAP-DOCS-document-model` §3.1, lookup §3.3 and namespaces
§3.3 for identity/discovery assertions. Document-model extraction unnecessarily included adjacent history/decision
material; lookup extraction included adjacent supersession text. Required effective role/skills, document-writing
instructions and spec/docs context were also opened. One guessed unit-local example-selection path did not exist
and opened no document; the retained materials path was then read.

Audit result: ledger covers substantive draft passages. Capability, architecture, glossary, reference/advisory and
source retain their existing distinct authority. Summaries introduce no competing procedure or selected transfer.
Both maintenance counterfactuals identify affected statements and symbols while qualifying unaffected facts.
Each role has separate home, kind/ID and tooling/UI recommendations. Actual committed diff stayed within the two
allowed directories (11 files); whitespace and unchanged owner checks passed. Caller-supplied tests/rules/link
results were explicitly SKIP for reviewer rerun, with exact source identity, rather than mislabeled reviewer PASS.
