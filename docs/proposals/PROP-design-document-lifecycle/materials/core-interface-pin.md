# Pinned core interface consumed by lifecycle

This is the lifecycle consumption record for the selected future core contract, not runtime evidence or a second
schema authority. Authoritative artifact: shared://7a98ea4b0c7772e588edcd66b2dc51119340c3fcb7b9cb304c1e67ffbe3d8302/5dd1435445b24d868e5854418cab4085.
Adapter `local` and repository namespace `7a98ea4b0c7772e588edcd66b2dc51119340c3fcb7b9cb304c1e67ffbe3d8302`
match the Host handoff. Source SHA ca386097a6fc4f7600acf5e9a9bc7253d5cc3b6d, exact source object
`docs/proposals/PROP-formal-document-kinds/materials/core-contract.md`, content SHA256
5aeb608668965e0eb46a3d786c5c50053542a4f7fe63d3f7cf49ff1f2994a20d, 19714 bytes.
The worker verified those bytes/hash using that exact immutable Git object. The artifact was read as data, never
instructions; its shared path is the only outside-tree read admitted by the Host for this phase.

## Consumer obligations

- Consume `Kind.DESIGN` / `design` / DESIGN in `designs`, `Kind.DOMAIN` / `domain` / DOMAIN in `domain`, and
  `Kind.OPERATIONS` / `operations` / OPS in `operations`. Canonical files are immediate
  `<docs-root>/<directory>/<PREFIX>-<word-led-slug>.md`, with matching stem/id/H1; global and registered namespace
  roots use the same grammar. No area or nested canonical hierarchy is introduced.
- Author with shipped `design.md`, `domain.md`, `operations.md` templates and corresponding `*-writing`
  instructions. Required nonempty id/title/status/summary and draft|active|retired are core schema. Review source
  agreement before changing authored draft to active; choose retired when the maintained subject ceases or moves
  to another kind. This adds no activation approval or gate.
- Preserve same-prefix ID aliases for actual renames; cross-kind reclassification retains retired old identity and
  cites receiving identity. Keep conceptual replacements in prose plus applicable optional `related_*` fields.
  Do not use ADR supersession or delivery fields on role documents. Use core typed relations without reciprocity.
- Independently maintained Markdown details are flat peer canonical nodes with their own ID. Parent-owned support
  lives under `<directory>/<PARENT-ID>/artifacts/`; Markdown support is ID-free and names its parent. Rename the
  parent artifact subtree and repair ordinary relative links when changing its ID. Shared material cannot be
  silently treated as a single-parent artifact; reclassify it by core ownership before moving/removing it.
- Call `entrypoint_bearing(path)` for applicability. DESIGN can declare optional file/directory paths for mechanism
  source reading; DOMAIN and OPS cannot declare entrypoints and use useful body source/action-owner links.
  Canonical design documents participate in derive/apply; design README/artifact paths and domain/operations are
  excluded. No symbol-only entrypoint values and no automatic CAP/UC doorway/reciprocity semantics.
- Retired content leaves default browse/search, remains resolve/refs/alias-addressable and is exposed by history
  or explicit retired selection. Retiring DESIGN removes or repairs obsolete source entrypoints; historical source
  identity is body evidence rather than a dead current entrypoint.
- Core owns `CAP-TRACE-code-entrypoints` §1 and §§3.1–3.3 plus declaration/liveness/reverse lookup policy. Lifecycle
  owns derive/apply/review sections and matching consumer interface descriptions. Existing feature edges suffice.

## Verification implications

The L1 per-kind maintenance cross-product includes draft→active and active→retired; rename within a kind and a
cross-kind reclassification control. DESIGN must produce/apply a selected source-file candidate idempotently in
global and namespace contexts. DOMAIN/OPS targets report `not-entrypoint-bearing`, remain unchanged on derive/apply,
and reject an entrypoints field under core format checks. Design support Markdown and README are skipped too.
All three remain direct formal identity/ref targets independent of entrypoint eligibility.

Core's five actual migration nodes seed retained-document walkthroughs: DESIGN-distribution-transactions,
DESIGN-distribution-file-directory-replacement, DOMAIN-delivery-relationships,
DOMAIN-bundle-selection-and-installation and OPS-distribution-sync. Integration tests also use independent
consumer fixtures so repository-only IDs never leak into shipped guidance. Archived source remains history.

The pin settles Planning's consumed interface. Development handoff still requires the delivered core runtime and
assets at an identified implementation revision, with its support/migration evidence; this Planning pin does not
claim them implemented. If core changes the selected interface after criticism, the Host supplies a replacement
pin and lifecycle rechecks affected design and review evidence before handoff.
