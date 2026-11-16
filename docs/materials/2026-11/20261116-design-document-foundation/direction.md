# Foundation direction and evidence

## Evidence identity and limits

Planning base: `fab44e919c5d516adfa4666fff444096be14300c`; reviewing-status head:
`196af9770a513253f555c18436eb5f2bd99de6c8`. `SPEC-design-document-pilot` and its retained
[evidence](../20261116-design-document-pilot/evidence.md),
[reader trials](../20261116-design-document-pilot/reader-trials.md),
[reviewer trials](../20261116-design-document-pilot/reviewer-trials.md) and
[passage ledger](../20261116-design-document-pilot/statement-ledger.md)
are present at this base. The completed pilot still supplies the evidence; Planning performs no new reader trial.
No assumption about a newer base, timing or exhaustive corpus inspection is made.

The four real distribution drafts show supplied-entry usefulness. R1 and fresh V1 show a direct contract-to-detail
gap. Indexed owner search/resolve/refs succeeded. The gap does not establish that a new kind, relation, config or
UI is needed. Global owner-linked entry discovery, package-context navigation, domain/operations unsupplied
entry discovery, viewer behavior and actual recovery remain unverified. Paper operations include pending journal,
later edits, legacy journal and no-journal drift; preserve the last state's not-ready result.

## Options

| Option | Viable result and cost | Risk / reason not selected |
| --- | --- | --- |
| A. ID-free `docs/designs/` entry and optional details, selected ordinary owner link | Separate maintained mechanism home; two real design files plus one contract link; existing owner search gets the starting contract; no runtime changes | Entries/details invisible to document search/resolve/refs; broken ordinary links need review. Selected with F3/F4 validation, not a promise of universal discovery. |
| B. Existing ARCH entry in `docs/architecture/`, linked ID-free details | Indexed entry uses current kinds and existing lookup; useful for system responsibility/interaction deep dives; no model change | Makes implementation-only mechanisms architectural chapters or leaves their actual detail elsewhere. Retain for architecturally significant content, not the pilot's local transaction mechanism. |
| C. New design Kind and ID under `docs/designs/` | Independent indexed design identity, stable lookup and graph nodes for entries | At least an enum member and definition row; many consumers derive behavior dynamically. Kind-specific path/lifecycle support and actual affected consumers require verification, not presumed edits everywhere. No demonstrated required outcome that A cannot meet. Reconsider only after a required route cannot be satisfied with existing owner links. |
| D. Existing CAP/reference entry, linked ID-free mechanism detail | An indexed contract or existing reference offers direct question routing at low cost | Useful routing alternative, but making a capability the current-design explanation owner mixes observable contract and mechanism responsibility. A retains this entry route while separating content ownership. |

A is recommended for clean responsibility boundaries and the smallest evidenced change. B and D remain valid for
their own responsibilities; neither is forbidden by a blanket content-depth rule. No existing Kind can be declared
inside `docs/designs/` merely by configuration: `CAP-DOCS-document-model` §3.2 and `RULE-id-convention` retain
kind-specific placement. The index's permissive parsing is not permission to violate that convention.
Domain and operations home/Kind/tooling choices remain independent and explicitly deferred to their proposals.

## Scout coverage and incoming references

Read-only nested Scout ran before Challenger. `scout-01.yaml` records its return. Its incoming-ref inventory:

| Touched indexed owner / decision | Total incoming refs | Inspected scope |
| --- | --- | --- |
| `CAP-DOCS-document-model` | 122 | First 40 rows |
| `CAP-DOCS-document-lookup` | 46 | First 40 rows |
| `CAP-DOCS-document-search` | 26 | All rows |
| `CAP-DOCS-namespaces` | 32 | All rows |
| `ADR-document-system` | 67 | First 20 rows; decision inspected |
| `ADR-kind-definition-table-keyed-on-the-declared-kind-enum` | 67 | Alias resolves to `ADR-document-system`; same bounded result |
| `CAP-DIST-sync-and-transactions` | 87 | Supplemental Scout inventoried all rows; current capability, ARCH, use case, pilot, proposal and ordering-feedback consumers inspected; historical bodies not exhaustive |

The namespace steering decisions `ADR-namespace-steering-directories` and `ADR-namespace-steering-registers`
were inspected as adjacent context, not changed. Their constraints remain intact. No accepted decision is
superseded. This is bounded impact discovery, not proof all incoming consumers were read.
`uv run devkit docs list spec --limit 8 --format json` found zero active specs (247 historical hidden).
Ownership search found the milestone and existing domain/operations proposals. No duplicate foundation was added.

## Emulated boundaries and verification provenance

Explicit absolute cwd, read-only role instructions, no role Git mutations and temporary-index tree snapshots
substitute for native isolation. Scout reported no outside-worktree read. Initial tree
`d50b529e00c4e141f3346012f8cca1b63c80421a` changed to
`77a6588859004412082b089505f913f41a84b46c` only because the worker committed the required draft→reviewing status
while the first Scout ran. The actual changed path is only this proposal's `proposal.md`; attribute that known
worker mutation explicitly rather than claiming equal snapshots. Scout follow-up pinned the reviewing head.
Later support runs receive stable committed artifacts and exact before/after snapshots.

Planning executes no package fixture, consumer sync, recovery, runtime regression or viewer check. F3–F5 are
required Development evidence. The documentation-only implementation has medium Development effort, with high
Planning review due to common ownership and distributed authoring consequences.

## Round 1 fold and alternative-cost precision

`challenger-01.yaml` found missing Scout incoming-reference coverage for the transaction capability selected for
the ordinary entry link. `scout-02.yaml` supplements that scope at `0adfa0169e05c4cd211b0cf0896ce9f1a5c5f3eb`.
The 87-row inventory and relevant current consumers show no changed guarantee, responsibility or recovery action
needed for the link. Existing `FB-runtime-journal-ordering` keeps its original owner. The Scout inspected source
and records, not a future navigation result. The original finding is resolved by this concrete coverage addition.

A new Kind is feasible. At minimum it adds a `Kind` enum member and a `KindDefinition` row:
`packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py:25-42,65-89`.
`CAP-DOCS-document-model` §3.2 says ID grammar derives from rows; many list/search/reference consumers already
read those rows. Kind-specific path grammar and lifecycle are code, but this Planning does not assert that every
consumer needs an edit. Namespace-only configuration cannot register kinds (`CAP-DOCS-namespaces` §3.1).
The new-kind option loses because no required indexed outcome is evidenced, not because generic lookup must be
rewritten. Exact grammar/rule/consumer edits would need inspection if that option is later authorized.

The source instructions implement the single shared ownership contract in consumer-generic form; they do not
establish a second normative matrix. The optional template is delivered by the existing `templates` document
asset (`bundle.toml` source `templates`), requiring no new manifest entry.

Challenger round 1 snapshots both equal `0c8e1a7d95c165b578f411a08c74e7f194632caa`. During the supplemental
Scout, the worker added only historical Git `6aaddb58a48aa81c6a0c23417801e9b4542f758a:docs/proposals/PROP-design-document-foundation/envelopes/challenger-01.yaml`; compare the snapshot diff rather than attributing that
known worker-authored record to the read-only role. No support role reported writes or outside-worktree reads.
The batch includes cost clarification outside the finding's section, so a fresh Challenger round 2 checks the
whole fold rather than invoking the high-effort minor-fix shortcut.

## Review closure and run coverage

Fresh Challenger round 2 at `ae1b222adc3494339581fab9dcc3f12049cd2739` returned no findings. It verified the
round-1 coverage fix, accurate new-Kind comparison and the single normative ownership contract. Before/after trees
both equal `208c20d810f0a04356b31013e7b1234afc8093dd`. No role reported outside-worktree reads. Round-1 finding
is resolved; no Decision needed finding or unresolved goal/scope question remains. Acceptance and handoff remain
Host-owned ask gates, with no conversational acceptance assumed.

Scoped proposal rules passed with 22 rules and zero errors/warnings after the fold. Whitespace checks passed.
Envelope checks report unblocked and no pending questions. `spec proposal check` returned the expected
`SPEC_PROPOSAL_IN_PLANNING` Backlog mutability refusal once; it was not retried or treated as a Planning pass.
The first local YAML wrap and root ID-free routing-file defects were fixed; scoped rules and the ordinary commit
gates then passed. These were ordinary authoring defects, not evidence for new governance.

The per-run feedback sweep covered repository and upstream tools/assets, including navigation evidence, source
asset conventions, support-role boundaries and scoped checks. No new reusable tool/asset defect was observed.
The existing runtime-ordering feedback remains untouched and is not a newly observed issue in this run.
No feedback file or follow-up proposal is added. Runtime tests, lint/type checks for product code and package/
viewer/recovery trials are SKIP because this turn changes only the Planning bundle; required Development checks
remain F1–F6 rather than claimed execution.
