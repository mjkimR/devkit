# Pilot passage ownership ledger

## Audit method and comparison

Scope: every substantive passage in the four drafts below. Head and independent audit results are recorded in
[evidence](evidence.md). “Summary” means a concise non-normative orientation; the cited source still decides exact
conditions. No copied normative rule is admitted by relabeling it conceptual. No transfer is selected.

Before: the selected sources separately expose availability, deployment selection, projection and receipts;
architecture exposes components/runtime; source exposes file/directory ordering; capability/reference expose
recovery and readiness. After: those authorities are byte-unchanged, with question-specific composed entries and
one source-grounded detail. The added relationship, mechanism and symptom paths are evaluation content only.

| Draft passage | Existing source and section | Treatment and added value | Normative owner before → after |
| --- | --- | --- | --- |
| domain: question, opening distinction, relationship 1 | `CAP-DIST-content-packages` §§1–3; `CAP-DIST-sync-and-transactions` §§1–2 | Composition: availability/requested/applied perspectives | Same capabilities → same capabilities |
| domain: relationship 2 | `CAP-DIST-manifest-spec` §3 Presets; `CAP-DIST-sync-and-transactions` §2 | Summary and owner reference: selection sits between availability and destinations | Same capabilities → same capabilities |
| domain: relationship 3 and path next step | `CAP-DIST-agent-projections` §1 | One example plus owner reference: kinds differ in projection | Same capability → same capability |
| domain: relationship 4 and selection next step | `CAP-DIST-sync-and-transactions` §§1–2 | Summary: receipt is applied evidence, not requested input | Same capability → same capability |
| domain: evidence boundary and terminology | glossary, devkit bundle and projection rows; cited capabilities | Scope statement, existing terms only | Glossary and capabilities → unchanged |
| design: question and mechanism opening | transaction.py `_ordered`, `apply_changes`, `recover_locked` | Composition: deletion frees a path while rollback needs prior evidence | Safety: `CAP-DIST-sync-and-transactions` §3 → unchanged; executable behavior stays source |
| design: authority/context paragraph | `CAP-DIST-sync-and-transactions` §3; `ARCH-05-4-distribution-components` §3; `ARCH-06-runtime-view` §1 | Owner references: guarantee/component/runtime separation | Capability/architecture → unchanged |
| design: next step and evidence boundary | replacement-detail.md and inspected transaction.py | Ordinary link plus evaluation scope: readable depth without invented kind | No new normative owner |
| detail: question/opening and preflight | transaction.py `require_writable`, `_removed_owned`, `blocked_parent`, `_emptied`; capability §3 item 3 | Source explanation: admissibility before application | Capability §3 → unchanged; source remains executable truth |
| detail: notes shape examples | capability §3 item 3 and transaction.py | Illustrative path shape, not executed fixture or new guarantee | Same capability → same capability |
| detail: forward application paragraphs | transaction.py `apply_changes`, `_ordered`, `missing_directories`, `_remove_emptied`, `atomic_write`, `replace_file` | Source explanation: snapshots, directory evidence, journal-before-write order | Safety capability §3 → unchanged; code remains executable truth |
| detail: reverse application | transaction.py `recover_locked`, `_swapped_directory`, `_prune_created` | Source explanation and recovery-owner reference, no copied steps | Recovery capability §3 item 6 → unchanged |
| detail: maintenance seam | Counterfactual analysis of those symbols | Hypothesis: change-specific update set, conditional architecture impact | Existing source/capability/architecture owners → unchanged |
| operations: opening and four classification rows | `CAP-DIST-sync-and-transactions` §3 item 6 and Readiness Gate; distribution reference §3 Error codes | Symptom/evidence composition plus owner selection | Capability/advisory/reference → unchanged |
| operations: action boundary | Recovery item and actual error advisory | Owner reference: no parallel recovery procedure | Same capability/advisory → unchanged |
| operations: normal-state observation | Capability Readiness Gate; distribution reference §3 devkit status | Summary and owner link: journal absence is insufficient | Same capability → same capability |
| operations: evidence boundary | Pilot scope and protocol | Evaluation limitation: no runtime recovery claim | No normative owner introduced |

## Adjacent content classification

Capabilities own observable guarantees and validity; architecture owns system scope, components, interactions,
quality and risks. Reference owns CLI/library detail and advisory mapping; executable guidance/advisory owns
selected actions. The glossary owns terminology. These are retained, not competing domain/design/operations homes.
No use case goal or UX interaction changes in this slice, so no use case/UX link is necessary. No ADR decision is
changed. Historical Planning materials retain assumptions and protocol; these pilot drafts/evidence stay historical
materials rather than a new contract. Runtime and viewer support remain unverified. No normative transfer,
duplicate procedure or mandatory reciprocal link is selected.
