# Domain Planning options and evidence

Planning source HEAD: `5ff227fbb6a903539ba842661de14b3bba2370b1`; Foundation is present in this tree.
Scout read-only at that clean HEAD reported no outside-worktree reads. Baseline incoming document counts were
ownership 2, Foundation ADR 4, lifecycle 19 and transactions 88. `incoming-references.txt` was captured after
draft authoring but before draft commit; it includes the new proposal/PADR references and totals 4, 5, 20 and 89
respectively. These two stages are distinct; no claim of
reading all incoming bodies is made. Read bodies were limited to the ownership CAP/ADR, relevant document-model,
lookup/search/namespace contracts, delivery relation/handoff sections, pilot and Foundation evidence, glossary,
Kind definitions and source authoring instructions. No whole-corpus modeling was attempted.

Challenger round 1 reviewed committed `6137fd5336bd35e9e15260ac6c8233006cc9a816` with no material findings.
Author writes and HEAD were frozen; full tracked plus nonignored-untracked byte snapshot before/after matched
`70f26b9913a21b590c917c56065667fa3d6d94e16c215e56d6896ea49f4b70cf`. The reviewer reported no outside-worktree
read or mutation. Only the stage labels above and EOF whitespace were corrected after the review; neither changes
a decision, contract or scope. Round 1 therefore ends under the no-finding rule, without a fresh round.

| Option | Why viable | Cost / limit | Decision |
| --- | --- | --- | --- |
| ID-free `docs/domain/` entries and selected owner links | Separates maintained relationships from contracts; uses ordinary Markdown and existing indexed owners | No direct domain node in search/resolve/refs; ordinary links and meaning need review | Recommended, conditional on D2–D4 independently proving domain routes |
| Existing ID-free steering topic | Existing context exposes title/summary globally or for selected package; suitable for short background | Whole topic body is the steering unit; context surfacing for every session adds load for question-specific domain detail, and directory caps apply | Viable for a short general domain overview; these two bounded relationship questions fit selected entry discovery better |
| Indexed domain Kind | Independent stable identity and direct query surface | At least Kind enum + definition row; exact remaining consumers/grammar/rules need separate inspection | No required indexed outcome demonstrated; not selected |

Location choice is `domain/` under global or registered package docs root. Identity choice is ID-free. Tooling
choice is existing owner lookup/search then ordinary links. No implication connects these choices automatically.
The existing ARCH/capability taxonomy can carry a link but does not become the conceptual entry's authority.

Evidence: `CAP-DOCS-documentation-ownership` §§3.1–3.3 retains the roles and defers domain home;
`ADR-documentation-ownership-and-linked-design-entries` §§3–5 selects DESIGN only and defers domain.
Pilot `domain-entry.md` lines 3–30 composes availability/selection/destinations/evidence;
`reader-trials.md` R3 supplies that filename, so unsupplied-entry discovery remains untested.
Foundation `development-evidence.md` F2–F4 demonstrates design global/package routes, not domain routes.

Actual minimum indexed-Kind cost: `packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py`
lines 25–42 and 64–82 define Kind and KindDefinition. Many consumers are data-driven; no broad hard-coded
consumer rewrite is asserted. Namespace configuration does not register a Kind. This turn does not inspect every
consumer because it selects no runtime change.

Authority samples: `CAP-DOCS-document-model` §3.3 lines 234–251 owns milestone membership, unit dependencies and
non-reference provenance; `CAP-DLV-spec-bundles` §3 rule 7 owns direct-spec membership omission;
`CAP-DLV-proposal-lifecycle` §4.1 lines 52–56 owns handoff transformations. Existing distribution owners listed
in the blueprint retain availability, asset/preset, projection and receipt contracts. The two entries combine
relationships; normative transfer is zero.

High Planning compares these alternatives and requires Scout before Challenger. PADR admission is met because
multiple viable representations were compared and a lasting authoring convention affects multiple document roles.
Content-only Development effort becomes medium; assigned high Planning remains unchanged. Independent domain
reader evidence is a Development condition, not claimed achieved by this Planning turn.
