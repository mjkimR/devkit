# Target documentation and ownership routing

## Shared ownership contract

CAP-DOCS-documentation-ownership (planned) is the sole normative home for the common role boundary and selected
ID-free design representation. Existing runtime contracts retain their owners. The following table is an author
routing aid, not a required reading matrix or mandatory set of links on each document.

| Reader asks / statement concerns | Primary owner | Boundary and pilot treatment |
| --- | --- | --- |
| What behavior, validity, safety or externally observable limit is promised? | Capability | Transaction eligibility, recovery stop and readiness stay `CAP-DIST-sync-and-transactions`; design gives concise orientation and owner citation. |
| Which concepts exist, what identifies them and how do their relationships/lifecycles fit? | Domain model; glossary for term definitions | Availability/requested selection/applied receipt composition remains pilot evidence until the domain proposal chooses its maintained home. Existing validity invariants stay capabilities. |
| Which system boundaries, components, dependencies and constraints hold? | Architecture | Installation-service responsibility stays `ARCH-05-4-distribution-components`; no internal algorithm ownership is inferred from its component placement. |
| How does one implementation mechanism work? | Current design explanation; source executes it | Preflight, journal encoding and deletion/reverse ordering go to the maintained entry/detail; source remains executable truth and capability owns guarantees. |
| What user/actor goal and scenario is supported? | Use case | Runtime technical interactions may support that scenario without restating its goal or success contract. |
| What human interface element and interaction serves the scenario? | UX | Design may explain implementation but does not duplicate the UX interaction owner. |
| Why choose an enduring option and accept its tradeoff? | ADR | Architecture records the chosen strategy; ADR retains alternatives/rationale; current contracts restate relevant outcome clauses. |
| What historical experiment, assumption or measurement supports a choice? | Materials | Original four drafts/trials stay evidence, distinct from adapted current design files. |
| What exact command/API/config shape or error mapping applies? | Reference | Reference keeps syntax, advisory mapping and API detail; design links to it when useful. |
| How does a contributor carry out a development activity? | Development guide | Contributing/build/test steps do not become design mechanism explanations. |
| Given a symptom and evidence, which existing action owner applies, and how is normal state confirmed? | Operations composition | Domain/design reading is unnecessary; capability/advisory/reference/executable guidance retain action authority. No-journal drift remains not-ready. |
| Which executable steps/permissions perform the chosen operation? | Existing instruction/playbook/advisory executor | Operations routes to the owner; it creates no second recovery procedure or permission. |

One normative statement has one primary owner. A concise summary can repeat orientation while citing the exact
owner; it adds no independent obligation. The foundation transfers none of the pilot's normative statements.

## ARCH overlap cases

- Strategy states structural choices and constraints; ADR supplies alternatives and rationale.
- Building blocks identify responsibilities and dependencies; local preflight/journal algorithms belong in design
  unless they themselves define a system-wide responsibility or constraint.
- Runtime views show relevant system interactions; use cases retain actor goals, and design retains local
  mechanism explanation. A runtime view need not enumerate each local operation to become complete.
- Cross-cutting technical concepts span implementations; domain concepts explain meaning and relationships.
  Common externally observable contracts stay capabilities even when several components enforce them.
- Deployment explains topology and distribution; operations selects diagnosis/recovery owners and normal-state
  observations. Executable recovery instructions retain their current owner.
- Architectural quality scenarios and risk already belong to arc42. No added chapter tutorial or empty chapter is
  needed. A design's numbers, detail length or datasheets alone do not change responsibility.

Clarify these boundaries in the architecture overview and source `architecture-writing.md`; the shared capability
owns cross-role routing. No rewrite of `ARCH-06-runtime-view` or migration of unrelated documents is selected.

## Entry and optional template

The optional source `design-template.md` has question/purpose, overview and authority boundary, mechanism content
or links to useful details/source, and maintenance touchpoints when known. It bears no `id`, `status` or new metadata
schema. Its headings are authoring prompts, not validator requirements. Supporting structure exists only as used.

The retained example becomes `docs/designs/distribution-transactions.md` with
`docs/designs/distribution-transactions/file-directory-replacement.md`. The capability's local ordinary link is
`../../designs/distribution-transactions.md`; the entry's ordinary detail link is
`distribution-transactions/file-directory-replacement.md`. Source links are adjusted and opened during review.
An indexed owner is cited by full ID; ordinary Markdown links name ID-free files. No reverse link is mandatory.
A package may use the analogous `docs/packages/<name>/designs/` layout without changing namespaces or identity.
F4 validates this convention in a disposable package fixture; no package-specific maintained content is created.

## Exact lasting-rule restatement

The PADR's unique-owner, role-separation and linked ID-free entry clauses are restated in
CAP-DOCS-documentation-ownership (planned), Ownership and Representation rules (MUST/SHOULD as appropriate).
Architecture's retained boundary is restated in the same capability's ARCH boundary rule and surfaced by the
architecture overview. Source instructions state consumer-generic versions without repository IDs. Compliance is
review-only for semantic ownership and ordinary navigation, supported by document/source asset rules and the
independent F1–F5 walkthroughs; no invented semantic validator is promised.
