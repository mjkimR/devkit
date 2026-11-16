# Pilot example selection and evidence protocol

## Baseline and status

Inspected repository content at `697a5da02e4fc8a50493aef650738f91c634a5a1`; the first Planning commit changes
only proposal status. These are source observations and a Development protocol, not completed reader trials.
There is no timing or corpus-size improvement claim. Development records its actual HEAD with each trial.

A lexical search for `bundle selection transaction recovery` returns existing distribution capability and
architecture owners. `devkit docs list spec --format json` reports no active spec at this baseline. These commands
establish available entry facilities, not successful discovery of the proposed draft entries.

## Selected examples and ownership

| Role and reader question | Existing authority | Added pilot contribution | Boundary |
| --- | --- | --- | --- |
| Domain: how does an available bundle become selected assets and projected paths, and what does a receipt record? | `CAP-DIST-content-packages`, `CAP-DIST-manifest-spec`, `CAP-DIST-agent-projections`, `CAP-DIST-sync-and-transactions` §§1–2; glossary | One relationship view from availability through selection to installed evidence, with a source link per relationship | Validity, presets, identity and receipt schema remain in their capability owners; no copied invariant |
| Design: how can one managed path become a directory or the reverse without losing rollback information? | `ARCH-05-4-distribution-components`, `ARCH-06-runtime-view`, `CAP-DIST-sync-and-transactions` §3; transaction implementation | A mechanism entry leading to one independently readable detail on ordering, before/after content and created directories | Architecture keeps component/runtime structure; capability keeps safety guarantees; source remains executable truth |
| Operations: what does `TRANSACTION_PENDING` mean and which recovery owner applies when a later edit causes `RECOVERY_BLOCKED`? | `CAP-DIST-sync-and-transactions` §3, [distribution reference](../../../development/reference/distribution.md) §3, distribution advisory errors | Symptom → evidence → owner selection → normal-state observation | Recovery commands, stop conditions and authority stay with existing owners; no second recovery procedure |

The glossary already defines devkit bundle and projections. The domain draft uses those terms and distinguishes
availability, requested selection and recorded installation state by citing their contracts. It registers no terms.

The design is real implementation detail: [transaction.py](../../../../packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/transaction.py)
implements `_ordered`, `missing_directories`, `require_writable`, `apply_changes` and `recover_locked`.
The detail follows their present behavior and links specific symbols. A datasheet has no demonstrated need here;
none is required. An authored diagram is optional only if this sequence cannot be read clearly from the entry.

Architecture's runtime view already covers sync at system-interaction granularity. The pilot checks whether
an entry plus detail makes the file/directory mechanism easier to locate without restating that architecture.
Any conflict encountered is recorded against its existing owner and is not silently repaired in pilot content.

## Draft package for Development

Create three role entries and one design detail under the retained pilot evidence directory. Keep each entry
readable independently: reader question, relationship or mechanism explanation, owner links, evidence boundary.
The design entry links its detail by an ordinary relative Markdown link. No ID or invented kind is assigned.
Include a source statement ledger: draft passage, current owner and section, quotation/paraphrase/link/composition,
added value, normative owner before and after. A paraphrase that changes a guarantee fails ownership review.
Any repeated normative statement is replaced with an owner reference before acceptance.

## Acceptance evidence protocol

- **AC-PILOT-01 ownership**: inspect all four drafts. Record each statement in the ledger and classify adjacent
  content: capability, architecture, use case, UX, ADR, historical materials, reference or executable guidance.
  Use case goals and UX interactions are linked only if this slice needs them; absence is explicit. Record
  unchanged ownership for every selected source; transfers are outside this pilot's selected scope.
- **AC-PILOT-02 navigation**: for domain and operations, give an independent reader only the question
  and the named draft entry.
  Record every opened document/link, the final answer with owner/section, and any missing or misleading hop.
  Run domain concept-to-contract and operations symptom-to-owner trials.
  Run a separate design discovery trial starting with only `CAP-DIST-sync-and-transactions` §3 and the reader
  question. Record how the reader finds the draft entry, or record the unavailable contract-to-entry hop as a
  gap. Then supply the design entry for a separate entry-to-detail-to-source trial; its success does not prove
  discovery. An evidence-report source-to-draft map may be evaluated separately as ordinary navigation, with
  its extra starting information recorded; it does not turn a failed contract-only discovery trial into a pass.
  For operations cover interrupted sync, later edited content, a legacy journal lacking `directories`,
  and no pending journal with remaining desired-state changes.
  Success requires the reader to identify the correct existing authority and its stop conditions without copying
  recovery steps into the draft. The reader also identifies `CAP-DIST-sync-and-transactions` Readiness Gate:
  `uv run devkit sync --check` exit `0` means ready; exits `1` and `2` mean not ready. The no-journal/drift
  scenario is not ready. These are documented-state conclusions, not executed recovery or readiness evidence.
  Record failures even if the owner is eventually found by manual corpus search.
- **AC-PILOT-02 discovery baseline**: separately record `devkit docs search` in explicit lexical mode for the
  selected owner IDs and `devkit docs resolve`/`refs` on those IDs. Check ordinary relative draft/detail links
  locally. These unindexed Markdown drafts are not promised as search hits. Record the difference between
  reaching an existing owner and discovering a draft. Inspect namespace selection contracts in
  `CAP-DOCS-namespaces`; this global pilot claims no executed package-context or viewer validation.
- **AC-PILOT-03 maintenance**: use a counterfactual change to deletion ordering, with safety guarantees held
  constant. Identify source-symbol and design-detail updates, the architecture review needed if system interaction
  changes, and why domain relations and recovery contracts stay unchanged when their facts remain true. Then
  trace a counterfactual recovery stop-condition change to the existing capability/advisory owner and the
  operations entry link. Do not apply either change or claim a successful runtime recovery.
- **AC-PILOT-04 recommendation**: produce one row per role with separate content-home, kind/ID and runtime/UI
  recommendations. Each extension cites a failed trial and the smallest missing behavior; a successful existing
  path can recommend reuse. Mark facts, hypothetical maintenance scenarios, illustrative artifacts and unverified
  claims separately. Give `PROP-design-document-foundation` the retained draft links and outstanding limits.

The Development reviewer repeats all reader trials with their specified starting information and audits the ledger.
Its evidence records the reader, revision, observed path, result and unresolved gap for each trial. No invented
completion percentage or mandatory document count beyond this bounded sample substitutes for those observations.

## Planning review closure

The medium nested Challenger identified two P2 protocol defects: supplied-entry navigation bypassed discovery,
and operations success lacked the existing readiness criterion. The protocol now separates contract-only
and supplied-entry trials and adds the desired-state-drift paper case with the capability's readiness owner.
The worker verified those exact text changes. The support role reported no outside-scope reads; before/after
worktree tree snapshots were identical at `7043eb7b53b93139e9a85bc95e32226189974c74`.
