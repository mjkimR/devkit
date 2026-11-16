# Foundation direction and evidence

## Evidence identity and limits

Planning base: `fab44e919c5d516adfa4666fff444096be14300c`; reviewing-status head:
`196af9770a513253f555c18436eb5f2bd99de6c8`. `SPEC-design-document-pilot` and its retained
[evidence](../../../materials/2026-11/20261116-design-document-pilot/evidence.md),
[reader trials](../../../materials/2026-11/20261116-design-document-pilot/reader-trials.md),
[reviewer trials](../../../materials/2026-11/20261116-design-document-pilot/reviewer-trials.md) and
[passage ledger](../../../materials/2026-11/20261116-design-document-pilot/statement-ledger.md)
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
| C. New design Kind and ID under `docs/designs/` | Independent indexed design identity, stable lookup and graph nodes for entries | Coordinated enum/table, grammar, governance, discovery and consumers; no demonstrated required outcome that A cannot meet. Reconsider only after a required route cannot be satisfied with existing owner links. |
| D. Existing CAP/reference entry, linked ID-free mechanism detail | Indexed contract/reference offers direct question routing at low cost | Useful routing alternative, but making a capability the current-design explanation owner mixes observable contract and mechanism responsibility. A retains this entry route while separating content ownership. |

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
