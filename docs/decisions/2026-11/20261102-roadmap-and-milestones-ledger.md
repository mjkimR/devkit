---
id: ADR-roadmap-and-milestones-ledger
title: Repository-owned roadmap, milestone documents, merging and archive
summary: "For a plan above the Unit, we keep goals, MS milestones (live at the roadmap root, terminal ones in _archive/, mergeable into themes) and draft proposals in the repository, with typed unit prerequisites and two-confirmation closure, to orient agents offline, accepting a commit per roadmap change."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-roadmap-and-milestones
  - ADR-roadmap-in-repository
  - ADR-milestone-documents
  - ADR-separate-unit-prerequisites-from-milestone-themes
  - ADR-milestone-closure-confirmations
  - ADR-milestone-merging
  - ADR-archive-terminal-milestones-in-roadmap
  - ADR-retire-scheduled-roadmap-review
---

# [ADR-roadmap-and-milestones-ledger] Repository-owned roadmap, milestone documents, merging and archive

Superseded in part by `ADR-namespace-milestone-roots`: the clause "Milestones are global; per-namespace roadmaps are
deferred until a repository needs them" (ADR-milestone-documents) and the global-root wording "live milestones
remain at the global roadmap root `docs/roadmap/`" (ADR-archive-terminal-milestones-in-roadmap): a registered
namespace keeps its milestones under `docs/packages/<name>/roadmap/` with the same lifecycle placement. Every other
clause stands.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: @minjae, user, agent
- **Involved Components/Capabilities**: `ARCH-01-introduction-and-goals`, `CAP-DOCS-document-model`,
  `CAP-DOCS-document-lookup`, `CAP-GOV-spec-rules`, `CAP-DLV-proposal-planning`, `CAP-DLV-spec-bundles`,
  `CAP-HARN-agent-guidance`, `docs/roadmap/`

---

## 1. Context & Problem Statement

Three sources disagreed on where Backlog keeps its plan. The strategy layer's master flow (workbench
`docs/strategy-layer/01-master-flow.md`, §1, §5 and its glossary) made Backlog "manage GitHub issues and milestones",
defined a Phase as one GitHub milestone, and split a draft into drafts "or `session` · `spec` depth issues" (§5.2),
keeping the link to the original request in the issue's parent/child relation. autohub's Work Plan backlog contract
states that repository documents own long-term direction and that GitHub issues are outbound execution records, "not a
second backlog"; autohub syncs Work Plans to issues one way. devkit-spec had no plan above the Unit: `milestone` was
free text nothing read, and `ARCH-01-introduction-and-goals` listed goals no work referred to. Neither GitHub
milestones nor issues were in use in this repository (checked 2026-10-16), so the choice cost no migration.

With the roadmap in the repository, its form must be chosen: what a milestone is, how milestones are ordered, how a
Unit joins one, how the next work is chosen, and how the record stays true as work completes, given that Units in
progress live on `plan-` and `dev-` branches while the base shows only merged state (01 §4.7).

Restricting dependency edges to milestones encouraged milestones that duplicate a single delivery unit for
fine-grained sequencing; `CAP-DOCS-document-model` and `CAP-DLV-proposal-planning` already provide anchor identity
and handoff rewriting. Closure must fit direct PROP-only membership without retaining delivery lineage after handoff,
and proposal disappearance cannot certify completion.

Granularity and exit-condition guidance was worded as SHOULD and SHOULD NOT, and keeping every `done` and `dropped`
milestone as a separate historical document left small milestones created before the coarse-theme guidance as
separate files even when one broader theme owned their scope. The repository merged five of them into
`MS-maintenance-operations` (commit `e048c24f`) as a one-off: the theme lists their IDs in `aliases`, their files were
deleted and `devkit rules fix` moved current references.

Root-only storage mixes done themes with current work. The document index already supports nested Markdown;
validator, authoring and viewer path assumptions prevented a coherent archive.

A scheduled roadmap review (three `done` milestones or 2027-01-31, recorded as a roadmap-review ADR and reported by
`spec-next`'s idle step) is no longer carried by any shipped guidance or code: commit `e9f589c4` (2026-10-22) removed
the idle step and a later commit its test assertion, while five milestones are `done` in `docs/roadmap/_archive/`, so
the count trigger passed with no record.

---

## 2. Decision Drivers

- An agent orients from files it can read offline; `spec-next` must recommend work without network access.
- References are validated deterministically by rules that run offline, in the commit gate and in CI; reuse the
  document model: IDs, `RULE-document-reference`, `devkit spec list`, `resolve` and `refs`.
- Consumer projects need not host on GitHub: no request, and no link to its origin, may exist only in GitHub.
- One owner per fact: no second backlog beside autohub's Work Plans and the repository's proposals; membership is
  stated once, on one side.
- Proportionate cost: no new document kind without a reader that needs it; build for the use there is. No new
  command, field or rule without a demonstrated need.
- Order expresses a real prerequisite, not a ranking that must be renumbered.
- No temporary checklists in `docs/` (`living-spec-writing`).
- The roadmap never blocks work: the user may deliberately start out of order.
- Checks that read only the base never claim facts that live on branches.
- Keep milestones as long-term multi-unit themes and collaborative scope documents; express explicit unit ordering;
  preserve history resolution; avoid conflating scheduling with verified delivery.
- Milestones are loosely managed themes reviewed by user and agent together, not a ledger of delivery units or
  delivery commitments.
- Preserve the user's authority over pickup, scope and milestone transitions; a confirmed completion is never
  reopened silently: the user owns every status change.
- Confirm both decomposition and settlement without duplicating work records; make stale confirmations unusable
  without building an automatic evaluator.
- Every milestone ID ever referenced stays resolvable through the document model's `aliases`.
- Completed specs and Git already keep the delivery record; a milestone file adds no evidence of delivery.
- Separate current themes from history in filesystem browsing without changing identity or lifecycle meaning.
- Keep history lookup, aliases, incoming references, prerequisite readiness and existing viewer access intact.
- Retain simple Backlog file operations and concrete user authority; introduce no new runtime command or registry.
- Preserve existing contents and completion evidence when relocating old history.
- Accepted ADRs agree with the shipped guidance.
- A date-based reminder adds guidance that every idle `spec-next` run has to carry.

---

## 3. Considered Options

### Where the roadmap lives
- **GitHub issues and milestones own the roadmap** (rejected in ADR-roadmap-in-repository): the strategy layer's
  wording; familiar UI and natural intake for outside requests, but unreadable offline, references cannot be validated
  by rules, ties consumers to GitHub, contradicts autohub's contract and adds a third copy of the plan.
- **The repository owns goals and the roadmap** (selected in ADR-roadmap-in-repository): offline, validated by
  existing rules, reachable through `devkit spec list`, `resolve` and `refs`, history in Git, agrees with autohub. Cons:
  changing a milestone is a commit; no human-facing roadmap screen until a viewer renders it; small requests carry the
  weight of a draft proposal.
- **autohub Work Plans own the roadmap** (rejected in ADR-roadmap-in-repository): devkit-spec does not know autohub
  (one-way dependency); unavailable to local-only projects.

### Milestone form
- **One `docs/roadmap.md` with a milestone table** (rejected in ADR-milestone-documents): one file to read, but a
  milestone is an anchor, not an ID, so no rule validates a Unit's reference; every change touches the same file.
- **A milestone document kind, `MS-<slug>`** (selected in ADR-milestone-documents): references validated by the
  existing rule; membership through `refs --direction in`; one file per milestone. Cons: a new kind, its ID convention,
  format checks and a template.
- **Free-text `milestone` tags only** (rejected in ADR-milestone-documents): a typo creates a new milestone; nowhere
  to state a goal, an order or an exit condition.

### Milestone ordering
- **Numbers** (rejected in ADR-milestone-documents): renumbered on every insertion.
- **`after`** (rejected in ADR-milestone-documents): reads both ways.
- **`depends_on`, declared by the successor** (selected in ADR-milestone-documents): the prerequisite is a fact the
  successor owns; the reverse direction is a query; matches proposal `supersedes` and autohub Work Plan dependencies.

### Next-work ordering
- **`devkit spec list --sort`** (rejected in ADR-milestone-documents): reverses `CAP-DOCS-document-lookup`'s non-goal
  and would sort enum values as text.
- **In `spec-next` over `--where` queries** (selected in ADR-milestone-documents): no CLI change; the order is
  documented once in the skill.

### Unit ordering
- **Continue milestone-only ordering** (rejected in ADR-separate-unit-prerequisites-from-milestone-themes): no model
  changes, but single-unit milestones remain necessary for sequencing.
- **Typed unit edges with frontmatter authoring** (selected in ADR-separate-unit-prerequisites-from-milestone-themes):
  reuses indexing and handoff and separates grouping and order; requires mixed-unit graph validation and lifecycle
  guidance.
- **New scheduling CLI and automatic lineage resolution** (rejected in
  ADR-separate-unit-prerequisites-from-milestone-themes): centralized execution, but adds authority and provenance
  mechanisms beyond the requested ordering outcome.

### Milestone closure
- **Conversation only** (rejected in ADR-milestone-closure-confirmations): no new representation, but the milestone
  does not retain its closure assertions.
- **Two plain body assertions and a fresh Backlog decision** (selected in ADR-milestone-closure-confirmations): small
  durable record; semantic correctness remains a user/agent review.
- **Typed frontmatter plus close command and scope fingerprint** (excluded in ADR-milestone-closure-confirmations
  without demonstrated need): adds parsing, invalidation and command contracts; still cannot prove missing work
  delivered.

### Milestone merging
- **Recommendation wording and user-decided merging** (selected in ADR-milestone-merging): the roadmap shows themes;
  old IDs resolve; existing `aliases` and `devkit rules fix` do the mechanics. Cons: a merged `done` or `dropped`
  milestone file leaves the tree; its text remains only in Git.
- **Keep every done and dropped milestone as a historical document** (rejected in ADR-milestone-merging): only
  `planned` and `active` milestones could be folded together; legacy fragments stay in the roadmap indefinitely, and
  the theme cannot own the delivered part of its scope.
- **A merge command** (rejected in ADR-milestone-merging): a CLI that rewrites aliases, deletes files and moves
  references in one step; adds a command contract for an occasional Backlog edit that existing tools already cover.

### Terminal milestone storage
- **Keep terminal milestones at the root** (rejected in ADR-archive-terminal-milestones-in-roadmap): no reader work,
  but the requested filesystem separation is not delivered.
- **One flat `_archive` directory** (selected in ADR-archive-terminal-milestones-in-roadmap): one extra path pattern,
  preserves identity and existing status filters; all path-based consumers must agree before files move.
- **Year/status subdirectories** (rejected in ADR-archive-terminal-milestones-in-roadmap): more partitions and
  validation/discovery branches without a demonstrated browsing need.
- **A copied index, archive status or archive command** (rejected in ADR-archive-terminal-milestones-in-roadmap):
  centralizes moves but adds derived state or lifecycle machinery for an occasional user-owned Backlog edit.

### Scheduled roadmap review
- **Retire the scheduled review** (selected in ADR-retire-scheduled-roadmap-review): the ADR matches the shipped
  guidance; no reminder text returns. Cons: no fixed point forces a look at unused milestone machinery.
- **Restore the `spec-next` reminder** (rejected in ADR-retire-scheduled-roadmap-review): bring the idle step and its
  test back, then hold the review it reports; keeps the original evaluation plan, but reverses a deliberate guidance
  cut, and the count trigger has already fired.

---

## 4. Decision Outcome

### Roadmap in the repository

- **Goals** stay as prose in `ARCH-01-introduction-and-goals` §1.2. They get no IDs and no document kind; a milestone
  names the goal it advances by citing that document. Reopen condition: a repository needs goals per namespace, or more
  than one milestone must be traced to the same goal mechanically. (ADR-roadmap-in-repository)
- **Milestones are repository documents.** The strategy layer's glossary entry "Phase = one GitHub milestone" becomes
  "Phase = one milestone document". (ADR-roadmap-in-repository)
- **Requests not yet started are draft proposals**, whatever their eventual depth. A decomposition splits a draft into
  drafts only, each naming the original in `decomposed_from: PROP-<slug>` (a plain field like `supersedes`, not a
  validated reference, since the original is deleted in the same commit; `--decomposed-from` checks at creation that
  the original exists and is a draft). The handoff carries `decomposed_from` and `supersedes` to `spec.md` as
  provenance fields, like `proposal`, so a spec keeps the link to the request it came from.
  (ADR-roadmap-in-repository)
- **Follow-ups found during work** stay feedback; Backlog promotes a `repo`-scope feedback item it accepts into a draft
  placed in a milestone. (ADR-roadmap-in-repository)
- **External trackers are excluded.** No issue field, issue intake, issue closing, tracker synchronization or autohub
  record recognition is part of this design. Repository documents hold requests and their provenance.
  (ADR-roadmap-in-repository)
- **Backlog** classifies, adds drafts, decomposes requests and manages milestone placement and lifecycle.
  (ADR-roadmap-in-repository)

### Milestone documents and storage

- **Milestone document**: kind `milestone`, ID prefix `MS`, file `MS-<slug>.md` under `docs/roadmap/`. Frontmatter:
  `id`, `title`, English `summary`, `status`, `created_at`, optional `depends_on` (a list of `MS-` IDs). Body: the goal
  it advances (citing `ARCH-01-introduction-and-goals`), the exit condition, out of scope; no work items. The slug
  starts with a word: release-style names read MS-release-1-0, not MS-1-0. Milestones are global; per-namespace
  roadmaps are deferred until a repository needs them. (ADR-milestone-documents)
- **Flat archive**: live milestones remain at the global roadmap root `docs/roadmap/`; `done` and `dropped` files use
  `docs/roadmap/_archive/` with the same filename and identity. Both statuses already satisfy milestone prerequisites,
  and history stays derived from status rather than directory. Identity, membership, dependency and closure authority
  are unchanged by the archive. (ADR-archive-terminal-milestones-in-roadmap)
- **Placement**: placement validation belongs with existing document conventions. Close/drop/reopen guidance combines
  the existing user decisions, the applicable status/assertions/disposition and the file movement in one Backlog
  commit. Checks report invalid placement rather than automatically changing state. Merging historical themes and
  alias preservation remain. (ADR-archive-terminal-milestones-in-roadmap)
- **Relocation batch**: readers and tests land before the approved content-preserving batch. The four-file candidate
  manifest is review evidence, not a runtime protocol or authority. Changed candidate effects are refreshed before
  they are applied. (ADR-archive-terminal-milestones-in-roadmap)
- **Coarse milestones**: a milestone is a coarse grouping theme; a theme may initially have one member while
  describing broader scope. No milestone member-count rule is added. User and agent review milestone themes and
  decomposition together. (ADR-separate-unit-prerequisites-from-milestone-themes)
- **Tone**: granularity and exit-condition guidance in the roadmap README and the milestone template is a
  recommendation: a broader multi-unit theme is preferred over a milestone that only sequences one proposal, and
  phase-level exit conditions are recommended. (ADR-milestone-merging)

### Milestone lifecycle and ordering

- **Status**: `planned` → `active` → `done`, or `dropped` from `planned` or `active`. The user activates, closes and
  drops a milestone through Backlog (base commits, like drafts). Several may be `active` at once.
  (ADR-milestone-documents)
- **History**: a `done` or `dropped` milestone that is not merged stays a historical document (ADR-milestone-merging):
  `devkit spec list` hides such milestones by default as it hides completed spec bundles, and `refs --direction in`
  keeps their membership history. (ADR-milestone-documents)
- **Merging**: small milestones of any status (`planned`, `active`, `done`, `dropped`) MAY merge into a broader theme
  milestone, existing or new, on the user's Backlog decision on a concrete candidate. (ADR-milestone-merging)
  - The theme lists every merged ID in `aliases` and states the combined goal and exit condition.
    (ADR-milestone-merging)
  - The merged files are deleted in the same commit, and `devkit rules fix` moves current references; `depends_on`
    edges between the merged milestones are removed. (ADR-milestone-merging)
  - Completed specs and Git keep the delivery record. (ADR-milestone-merging)
  - Remaining scope moves to draft proposals in the theme. The theme is `planned` or `active` while scope remains and
    becomes `done` only through both Completion review confirmations. (ADR-milestone-merging)
  - A merge is not an in-place extension: extending a `done` milestone's own scope still needs the user's reopen to
    `active` with both assertions reset, or another milestone (Reopen below). (ADR-milestone-merging)
  - Merging through `aliases` keeps every ID resolvable and leaves delivery evidence where it already is, while the
    user's Backlog decision preserves authority over status changes. (ADR-milestone-merging)
- **Milestone `depends_on`** is a start condition: a milestone is *ready* when every milestone it depends on is `done`
  or `dropped`. Enforced at the decision points, never by refusal. (ADR-milestone-documents)
- **Activate**: the Host lists the dependencies not yet `done` or `dropped`; the user may activate anyway.
  (ADR-milestone-documents)
- **Drop**: each unsettled member is re-pointed, has its `milestone` cleared, or is rejected; each successor that
  depends on the milestone is shown, and the user keeps or edits its `depends_on`. (ADR-milestone-documents)

### Unit prerequisites and membership

- **Unit prerequisites**: proposal and spec anchors may declare typed direct PROP/SPEC anchor edges alongside the
  unchanged MS graph. Completed SPEC history is a terminal target, not a source of transitive readiness obligations. No
  decomposition/supersession graph is stored. Optional frontmatter is authored through existing document editing and
  templates, with no new CLI flag or evaluator. (ADR-separate-unit-prerequisites-from-milestone-themes)
- **Edges through the lifecycle**: handoff carries and rewrites edges after a projected-graph preflight. Other
  retirements require explicit incoming edge disposition; provenance never silently redirects an edge.
  (ADR-separate-unit-prerequisites-from-milestone-themes)
- **Unit readiness**: status completed on the selected local base satisfies a direct SPEC prerequisite for scheduling
  only. Unknown evidence blocks recommendation. Unit readiness filters critical drafts too, while existing milestone
  ranking exceptions remain intact. User-directed out-of-order starts remain available; structural validation remains
  mandatory. (ADR-separate-unit-prerequisites-from-milestone-themes)
- **Membership**: `milestone` in `proposal.md` is one `MS-` ID, validated by `RULE-document-reference`; milestone
  membership is direct PROP-only. Handoff does not carry milestone metadata into SPECs; legacy SPEC membership metadata
  is ignored without rewriting historical specs. The direct-spec creation `--milestone` flag and API parameter are
  removed with no compatibility shim; proposal milestone authoring (`devkit spec proposal new --milestone`) remains.
  (ADR-separate-unit-prerequisites-from-milestone-themes) A rejected proposal is not a member; `session` work has no
  Unit and is never a member; Units without a milestone stay valid. (ADR-milestone-documents)
- **No persistent milestone delivery lineage** is introduced; downstream status can be investigated from code/Git on
  demand. No milestone identity travels to SPEC. (ADR-separate-unit-prerequisites-from-milestone-themes,
  ADR-milestone-closure-confirmations)

### Milestone closure

- **Close**: the milestone body has a section `Completion review` with plain `Decomposition: pending` and
  `Direct proposal work: pending` statements. Both are recorded as `confirmed` with `status: done` in the same Backlog
  commit after the user confirms the concrete current close candidate. These are durable assertions rather than work
  items; no separate approval, per-item checklist, new schema, command or stored evidence ledger is introduced. Closure
  is allowed from `planned` or `active`. (ADR-milestone-closure-confirmations)
- **Closure assertions**: the first confirmation says the intended scope has been sufficiently decomposed; the second
  says directly associated work is delivered or explicitly removed from the agreed scope. Both depend on the
  milestone's exit condition being met for that scope. Focused implementation/Git inspection resolves uncertainty;
  unknown evidence remains open. A missing PROP, rejection, handoff or reassignment never proves implementation.
  (ADR-milestone-closure-confirmations)
- **Invalidation**: an actual semantic scope change (new required work, exclusion or moving scope elsewhere) clears
  both assertions. Normal PROP-to-SPEC handoff or mechanical identity relocation does not change scope/decomposition and
  requires no milestone review, reset or reconfirmation. Stored assertions are not standing authorization: every close
  requires a concrete approved candidate. If semantic scope or relevant completion evidence changes before writing,
  review and confirmation repeat. After interruption, establish the approved candidate and recheck those facts;
  unchanged authorization persists. Ask again only if facts changed or the approved candidate/evidence cannot be
  established. A pause or context compaction alone is not an invalidation event. Pure formatting changes do not
  invalidate; unchanged `done` is a no-op; existing `done` records need no migration.
  (ADR-milestone-closure-confirmations)
- **Reopen**: a scope extension to a `done` milestone requires a user-owned reopen to `active` with pending
  assertions, or a separate milestone. (ADR-milestone-closure-confirmations)

### Rules, warnings and next work

- **Rules**: `RULE-spec-format` covers `docs/roadmap/` (required keys, the status vocabulary); its fix fills
  `status: planned` and derives `MS-<stem>` for a milestone. `RULE-document-summary` requires a milestone `summary`; a
  `depends_on` cycle is a `RULE-document-reference` error. (ADR-milestone-documents)
- **Hygiene warnings**: two warnings, which read the base only and settle when the members are fixed: a `done` or
  `dropped` milestone with a member on the base that is neither settled nor rejected. Out-of-order activation raises no
  warning: the user decided it at activation. No "candidate to close" warning: membership on branches is invisible to
  the base; reconsider it once two or more milestones are `active` at once in practice. (ADR-milestone-documents)
- **Next work**: a Unit is *in progress* when it has a `plan-` or `dev-` branch, is a `reviewing` or `accepted`
  proposal, or is a spec not completed. While one is, `spec-next` follows the stage matrix for it. Queued drafts are
  not in progress: when nothing is, `spec-next` considers drafts whose displayed status is `draft`, that carry no
  `needs_decompose` and whose unit prerequisites are ready, in this order: (1) `critical` drafts, whatever their
  milestone; (2) drafts of `active` milestones, then of ready `planned` milestones, then drafts without a milestone,
  milestones of one rank by `created_at`, then ID; (3) within a group, `priority` (`critical`, `high`, `medium`,
  `low`), then `size` (`S`, `M`, `L`, `XL`), then `created_at`, then ID. A draft without `plan-intent` is recommended as
  "confirm the intent". Drafts in milestones that are not ready or are `done` or `dropped`, and `needs_decompose`
  drafts, are reported as Backlog actions. Open feedback adds a suggestion of a hygiene pass.
  (ADR-milestone-documents, ADR-separate-unit-prerequisites-from-milestone-themes)

### No scheduled review

- The scheduled roadmap review (three `done` milestones or 2027-01-31) is retired, and `spec-next` reports no review
  as due. (ADR-retire-scheduled-roadmap-review)
- The milestone machinery is reassessed through ordinary feedback when its use shows friction. A proposal to remove
  part of it follows the usual proposal path. (ADR-retire-scheduled-roadmap-review)
- Nothing is restated in a capability or architecture document for the retirement, because it removes an obligation
  and adds none. (ADR-retire-scheduled-roadmap-review)

---

## 5. Consequences

- **Positive**:
  - The roadmap converges on themes; the `MS-maintenance-operations` merge is the documented procedure.
    (ADR-milestone-merging)
  - Filesystem browsing, document tools and viewer history agree while old IDs and dependencies stay valid.
    (ADR-archive-terminal-milestones-in-roadmap)
  - The accepted ADRs no longer describe a review that no guidance runs. (ADR-retire-scheduled-roadmap-review)
- **Negative / Risks**:
  - Changing a milestone is a commit; no human-facing roadmap screen until a viewer renders it.
    (ADR-roadmap-in-repository)
  - Authors must maintain explicit dependency edges during lifecycle changes, for live incoming direct edges when a
    target is removed; completed history remains unchanged. No automatic selection of decomposed children or
    superseding proposals is safe. The base status signal can be weaker than verified completion; it intentionally
    grants no delivery certification. (ADR-separate-unit-prerequisites-from-milestone-themes)
  - There is no automatic delivery guarantee and no claim that body text validates implementation; semantic
    correctness remains a user/agent review. (ADR-milestone-closure-confirmations)
  - A merged milestone's text is read from Git, not from the tree. A merge reduces the number of `done` milestones
    that the roadmap review counted; its date trigger still applied (the review itself is retired above).
    (ADR-milestone-merging)
  - Docs/spec validators, agent guidance and Python/TypeScript viewer discovery need coordinated coverage. A
    root-only reader can hide history or make an edge unknown; the reader inventory and two loader-path tests address
    that concrete failure; ordinary file comparisons handle relocation collisions and content preservation. No package
    split, new archive screen, lifecycle evaluator or automatic data migration is required.
    (ADR-archive-terminal-milestones-in-roadmap)
  - Unused milestone machinery stays until someone files feedback about it. (ADR-retire-scheduled-roadmap-review)
- **Changes made**:
  - The strategy layer was updated by the Host after `plan-accept` and before `devkit spec proposal handoff`: 01 §1
    table, §5 (diagram, text and TODO), §5.1 (the policy exemption covers milestone documents: Backlog files that are
    not code), §5.2 (drafts only, `decomposed_from`), §7.4 (supersede link), §10 change list and the glossary; 02 adds
    the milestone kind to devkit-spec's responsibilities. (ADR-roadmap-in-repository)
  - `ARCH-01-introduction-and-goals` states where the roadmap lives. (ADR-roadmap-in-repository)
  - `CAP-DOCS-document-model` adds the kind, the `milestone` relation field and the `depends_on` field, and extends the
    historical-document rule to `done` and `dropped` milestones; `RULE-id-convention` adds the location; a milestone
    template joins the bundle's templates; the docs skeleton gains `docs/roadmap/`. (ADR-milestone-documents)
  - `devkit spec proposal new --milestone` takes an `MS-` ID. (ADR-milestone-documents)
  - The earlier free-text values needed no migration. No existing milestone instance is migrated or closed by the
    closure policy. (ADR-milestone-documents, ADR-milestone-closure-confirmations)
  - The hygiene warnings run through devkit-spec's `devkit.hygiene` extension, like the rejected-proposal warning.
    (ADR-milestone-documents)
  - The shipped milestone template, Backlog and orientation instructions and their contracts describe the closure
    procedure. (ADR-milestone-closure-confirmations)
- **Follow-ups**:
  - autohub may later map a Work Plan's `group_key` to a milestone ID and render milestones in the repository viewer;
    the Backlog subagents listed as TODO in 01 §5 (triage, decomposer) remain outside this decision.
    (ADR-roadmap-in-repository)
  - Optional future closure automation requires a demonstrated failure beyond this procedure.
    (ADR-milestone-closure-confirmations)

---

## 6. Confirmation

- `RULE-spec-format`, `RULE-document-summary` and `RULE-document-reference` (including `depends_on` cycles) check
  milestone documents and references. (ADR-milestone-documents)
- Development tests mixed cycles, history targets, handoff projection and conservative base recommendation.
  (ADR-separate-unit-prerequisites-from-milestone-themes)
- Guidance tests cover both positive and blocked closure cases. (ADR-milestone-closure-confirmations)
- `packages/devkit-spec/tests/integration/bundles/spec/test_milestone_completion_guidance.py` pins the recommendation
  wording, the merge procedure and the kept reopen rule in the shipped guidance; `RULE-document-reference` reports
  alias references and `depends_on` cycles left by a merge. (ADR-milestone-merging)
- Development checks AC-01 through AC-08: path/status and historical targeting, lookup/alias/refs/search, membership
  notice, both terminal dependency states, optimized/generic viewer loading and detail, close/drop/reopen and the exact
  byte-preserving batch. Run affected Python tests plus viewer lint/check/test/build and rebuild its committed page.
  Semantic transition correctness and concrete batch authority are review-only; a rule cannot certify user intent.
  (ADR-archive-terminal-milestones-in-roadmap)
- Review only for the retired review: `rg "2027-01-31|roadmap.review" packages/ .devkit/managed/` finds no guidance
  that reports the review. (ADR-retire-scheduled-roadmap-review)
