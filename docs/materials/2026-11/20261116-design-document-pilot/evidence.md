# Distribution documentation pilot: evidence and recommendations

## Result boundary

The retained [domain entry](domain-entry.md), [design entry](design-entry.md),
[replacement detail](replacement-detail.md) and [operations entry](operations-entry.md) demonstrate distinct
relationship, mechanism and symptom-selection contributions. The [passage ledger](statement-ledger.md) maps every
substantive draft passage to its unchanged owner. The [independent trials](reader-trials.md) record actual reader
paths. This is a four-draft sample, not evidence that every documentation role needs a new indexed kind.

Facts below are repository observations or attributed reader results. Maintenance scenarios are counterfactual.
The example path names in the detail are illustrative; there is no illustrative datasheet. Package-context and
viewer behavior, final content homes and runtime recovery are unverified.

## Baseline and before/after method

Agreed source baseline: `3d21622a44ccb9fdf1388a33b360bf39c71a79a1`.
Specify head: `a448f4ef5726039e7ddf61b72cef3bdc722dce19`.
The head-with-change-disabled comparison withholds the draft entries: R1 gives only the existing contract and
question before disclosing any draft filenames. R2 then supplies the entry explicitly. Existing contract/source
owners are byte-unchanged against the source baseline (`git diff --exit-code` on capabilities, architecture,
glossary, reference and transaction.py exits 0). No checkout of the base is used.

Before: the contract answers safety but the direct reference path to this pilot design detail is absent.
After: an explicitly supplied design entry reaches detail/source; domain and operations entries reach existing
authorities. The unavailable discovery hop remains unavailable. This is a qualitative navigation comparison,
not elapsed-time, corpus-size, accuracy-percentage or runtime improvement evidence. The initial reader's
extraction overreads/truncation are retained in its trial record, not counted as successful whole-corpus inspection.

## Independent review confirmation

The mandatory Code Reviewer repeated the protocol and audited all draft passages at
`3a1a21701faf9c827088204b586aaf7a25e77359`: PASS, no findings.
[Reviewer trials](reviewer-trials.md) preserve its fresh bounded contract-only result, supplied-entry paths,
separate allowed-search experiment, actual read ledger and limitations. Unlike the first reader's initial
extract, its numbered transaction extract did not truncate. Its ownership detour and other broad source reads
remain visible usability costs. Supplied-entry repeats shared cross-role visibility; they were not separately
blinded sessions. Native boundaries were emulated and one initial outside-worktree reply-skill read was disclosed.
No new content or tooling requirement was inferred from the repeated discovery gap.

## Existing discovery facilities

Executed at specify HEAD with unindexed draft working files. For each ID below, these exact command forms exited 0:
`uv run devkit docs search ID --mode lexical --limit 1 --format json`,
`uv run devkit docs resolve ID --format json`,
`uv run devkit docs refs ID --direction in --limit 1 --format json`.
Search pinned the named existing owner first; resolve returned its canonical path. Incoming refs totals were:

| ID | Incoming referencing documents |
| --- | --- |
| `CAP-DIST-content-packages` | 63 |
| `CAP-DIST-manifest-spec` | 42 |
| `CAP-DIST-agent-projections` | 43 |
| `CAP-DIST-sync-and-transactions` | 84 |

An earlier unbounded refs call used limit 0 and returned all rows; output truncation motivated the bounded repeat
above. The bounded commands are the reported measurement. A lexical query for `bundle selection transaction recovery`
returned `ARCH-05-4-distribution-components` first and `CAP-DIST-sync-and-transactions` second (limit 5).
That query reached existing owners; it did not discover a draft.

`CAP-DOCS-document-model` §3.1 excludes ID-free Markdown from the index, so these drafts are not promised search
hits or graph nodes. `CAP-DOCS-document-lookup` §3.3 already supports incoming/outgoing owner references;
no manual reciprocal-link registry is needed to query existing indexed references. `CAP-DOCS-namespaces` §3.3
keeps resolve/refs repository-wide while search/list narrow the selected namespace plus global documents.
That contract was inspected; no package-context execution or viewer validation is claimed.

## Ownership comparison and ambiguity

No normative transfer is selected. Capability retains validity, selection, receipt, transaction, recovery and
readiness; architecture retains system boundaries/interactions; reference/advisory retain command details and
actions; glossary retains terms; source retains executable behavior. The ledger distinguishes these owners from
the evaluation content. No affected use case, UX or ADR contract was identified.

`ARCH-06-runtime-view` §1 visually records journal entries inside its write loop, whereas the explicit capability
§3 item 3 and `apply_changes` write the journal before changed files. That is a coarse-view ordering ambiguity,
not a reason to copy a competing guarantee into design. Its needed architecture clarification is reported as
feedback in this unit; the architecture is outside this pilot's write scope.

## Counterfactual maintenance walkthrough

| Hypothetical change | Owned statements to inspect/update | Unaffected when their facts remain true |
| --- | --- | --- |
| Change deletion scheduling while keeping safety guarantees | Source `_ordered`, `apply_changes`, `recover_locked`; detail Forward/Reverse application and Maintenance seam. Review design entry's change-set overview for continued truth. | Domain availability/selection/projection/receipt relations; operations recovery selection and readiness; capability guarantee wording. Architecture review is needed only if component responsibilities or system interactions change. |
| Change recovery stop condition or accept another journal shape | Existing `CAP-DIST-sync-and-transactions` §3 Recovery plus advisory `RecoveryError`, transaction `recover_locked`/legacy-journal handling and reference Error codes. Update operations affected evidence discriminator/owner link, not a parallel procedure; detail only if its mechanism explanation changes. | Domain relationship view and projection matrix. Architecture only if responsibility/interaction changes; unrelated readiness and forward-write guarantees remain unchanged. |

These are statement-level impact analyses, not applied source edits or successful rollback experiments. No change
requires updating every layer. `PROP-design-document-lifecycle` owns eventual maintenance guidance after accepted
representation decisions; this pilot adds no new approval or completeness metric.

## Independent representation recommendations

Content location, indexed kind/ID and tooling/UI are separate choices. The roles remain retained regardless of
whether an extension is justified.

| Role | Content-location recommendation | Indexed kind/ID recommendation | Tooling/UI recommendation and minimal missing behavior |
| --- | --- | --- | --- |
| Domain | Keep this relationship composition as evidence; `PROP-domain-model-documents` chooses a maintained home after ownership review. Existing conceptual steering is a candidate, not a selected home. | Defer a separate kind. R3 reaches each existing contract from supplied content; it does not test unsupplied domain-entry discovery. | Reuse ID resolve and ordinary owner references. Need an agreed entry-discovery path before claiming end-to-end discoverability; no demonstrated UI extension. |
| Design | Retain entry plus one independently readable detail; `PROP-design-document-foundation` chooses a maintained representation alongside existing architecture. | No new kind is demonstrated necessary. R1 shows a direct contract-to-entry gap; R2 validates ordinary entry/detail/source links. | Smallest missing behavior is discoverable routing from the relevant contract/question to the mechanism entry. Test an ordinary link, existing indexed entry or source-to-entry map before adding runtime machinery. Such tests require later owner authority; R2 cannot substitute for them. Viewer remains unverified. |
| Operations | Retain the symptom/evidence composition; `PROP-operations-documents` selects maintained location while keeping capability/advisory recovery ownership. | Defer a separate kind; supplied-entry R4 reaches current recovery/readiness owners. Unsupplied symptom-to-entry discovery is untested. | Reuse codes, advisory mapping, ID resolution and reference anchors. No new recovery executor, checklist or UI is supported by this sample. Test discovery with unsupplied entry and later viewer context before claiming coverage. |

`PROP-design-document-foundation` consumes these drafts, ledger and trials, with source identity and limits above.
`PROP-domain-model-documents` owns domain representation; `PROP-operations-documents` owns operations representation;
`PROP-design-document-lifecycle` owns change-specific lifecycle integration; `PROP-design-document-viewer` owns actual
viewer verification after representation choices. All five existing IDs were resolved successfully. No follow-up
proposal was created or modified. Restart each deferred implementation only after its Planning accepts representation
and verifies the relevant missing discovery path; expected checks are owner uniqueness, useful question-specific
navigation and the proposal's actual runtime/package/viewer surfaces.
