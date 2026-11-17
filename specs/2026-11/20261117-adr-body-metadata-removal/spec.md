---
id: SPEC-adr-body-metadata-removal
title: Remove the ADR body metadata block and trim the ADR template
summary: Drop the Status/Date/Deciders/Involved block from the ADR template, the proposal scaffold and the handoff acceptance rewrite, since the frontmatter already owns status, date and supersession, and shorten the option and separator scaffolding to what decision-writing asks for.
status: planned
created: 2026-11-17
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-adr-body-metadata-removal] Remove the ADR body metadata block and trim the ADR template

## 1. Problem Statement & Motivation

Handed off from proposal PROP-adr-body-metadata-removal on 2026-11-17.
- **Preserved Materials**: `docs/materials/2026-11/20261117-adr-body-metadata-removal`

### 1. Background & Hypothesis

The ADR template (`templates/decision.md`) puts a metadata list under the H1: `- **Status**`, `- **Date**`,
`- **Deciders**` and `- **Involved Components/Capabilities**`.

- Status and Date repeat the frontmatter `status` and `created_at`; the superseded form ("Superseded by" plus an ADR ID)
  repeats `superseded_by`. In the 71 of 94 ADRs that carry the block, both values agree with the frontmatter.
- Deciders appears in 27 of 94 ADRs and Involved Components in 45; nothing parses either line, but backticked IDs in
  Involved Components lines count as body references for `devkit docs refs` and the viewer's reference panel.
- No rule enforces the block, but code keeps the copy alive: the proposal scaffold (`scaffold.py`) writes it for PADRs,
  and handoff acceptance (`_accept_status` in `handoff.py`) rewrites the body Status line in step with the frontmatter.
  Tests pin both (`test_proposal_handoff.py`, `test_proposal_scaffold.py`).

The same template scaffolds per-option Overview/Pros/Cons although `decision-writing.md` asks for one or two lines per
option with its main trade-off, and separates every section with `---`.

Hypothesis: the frontmatter is the single owner of status, date and supersession; removing the body copy removes a
synchronization path in code and a field authors fill by rote.

Kept: the "Superseded in part by" body lines (they name replaced clauses, which the frontmatter cannot), Decision
Drivers, Confirmation and the outcome-trace comments (test-enforced).

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Remove the ADR body metadata block and trim the ADR template so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Existing ADRs: remove the block from all 71 in one mechanical pass, or leave them and only stop writing it?
  Leaving them means no code keeps them in step after `_accept_status` loses its body pass.
  - **Answer**: remove it, in one mechanical pass that Development runs at its own HEAD (after
    `SPEC-formal-doc-padding-trim` integrates, so any ADR promoted in between is covered). Cost: about 230 deleted
    lines across 71 files in one commit, no decision changed, no rule or reader affected; a wording and metadata repair
    the `docs/decisions/` ledger allows without a superseding ADR. Leaving them keeps 71 copies nothing updates (a later
    whole supersession leaves a stale `Accepted`) and two ADR layouts. `ADR-frontmatter-only-decision-status`.
- **Q2**: Does any reader (viewer, `devkit docs` index, search snippet, handbook generation, supersession tooling) parse
  the body Status line? Confirm nothing does before removing the rewrite.
  - **Answer**: no reader parses the Status, Date or Deciders lines. Every reader takes status from the frontmatter
    and supersession from `supersedes`, `superseded_by` and the partial pointer lines; the only code touching the
    block is the scaffold and the handoff body pass. One indirect reader exists: backticked IDs anywhere in the body,
    Involved Components lines included, are body references (`devkit docs refs`, the viewer reference panel). In about
    20 ADRs the Involved Components line is the only mention of some IDs; the Q1 pass keeps those edges
    (`docs/materials/2026-11/20261117-adr-body-metadata-removal/body-status-readers.md`).
- **Q3**: Where do "Superseded in part by" lines sit once the block is gone (directly under the H1)?
  - **Answer**: directly under the H1, each a paragraph of its own, as the handoff already writes them
    (`CAP-DLV-proposal-lifecycle` handoff step 4) and as existing ADRs already place them above the block. The
    template comment under the H1 stays as the authoring cue.
- **Q4**: Option scaffolding: `- **<Option>**: <trade-off against drivers>` lines, with the selected option marked;
  drop the `---` separators.
  - **Answer**: yes. The template's Considered Options becomes one list item per option,
    `- **<Option>** (selected): <main trade-off against the drivers>.` for the chosen one and
    `- **<Option>**: <main trade-off against the drivers>.` for the others, under a comment pointing to
    `decision-writing`; every `---` separator in the body goes. Existing ADRs keep their option layout and separators
    (out of scope: a per-ADR rewrite, not a mechanical one).

### 3. Proposed Design & Impact

- Docs bundle: the decision template loses the block, the per-option Overview/Pros/Cons sub-bullets and the `---`
  separators; Considered Options takes the Q4 lines. `decision-writing.md` gains one statement that status, date and
  whole supersession live only in the frontmatter, and asks to mark the selected option; its "one or two lines per
  option" rule stays. The H1 comment about "Superseded in part by" lines stays, as do Decision Drivers, Confirmation
  and the outcome-trace comments.
- Spec package: `_padr` in `scaffold.py` stops writing `- **Status**`, `- **Date**` and the `---` after them; the
  handoff drops `_DRAFT_BODY_STATUS` and the body pass of `_accept_status`, which keeps only the frontmatter rewrite.
  Tests: `test_proposal_scaffold.py:222` asserts the lines are absent; `test_proposal_handoff.py:115-117` drops the
  body assertion; the three edge-case tests (fenced example, HTML comment, trailing comment) collapse into one test
  that a body `- **Status**: Draft` line, wherever it is, is left byte-identical while the frontmatter is accepted.
- Docs bundle test: a test under `packages/devkit-docs/tests/integration/bundles/docs/` asserts the template has no
  metadata block, no `---` body separator and no Overview/Pros/Cons scaffolding.
- Existing ADRs (Q1): one mechanical commit, run on every ADR under `docs/decisions/` at Development HEAD. In the
  first list after the H1 (before `## 1.`), it removes each item starting with `- **Status**:`, `- **Date**:`,
  `- **Deciders**:` or `- **Involved Components/Capabilities**:`, together with that item's indented continuation
  lines. Every other line stays where it is: "Superseded in part by" paragraphs and list items, other list items, and
  prose. When the list is left empty, its surrounding blank lines collapse to one, and a `---` that is the next
  non-blank line goes with it. When items remain, the list and its `---` stay. Handled by name, at this base:
  - `ADR-ux-screens`: its three "Superseded in part by" list items stay as the list.
  - `ADR-dual-source-of-truth-and-periodic-reconciliation`: its `- **Follow-up**` item stays as the list.
  - `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation`: its Deciders provenance becomes one sentence at the
    end of Context & Problem Statement: "Decided by the user on the rejection of ~~`PROP-direct-devkit-invocation`~~
    (Git `4672a101eec0`)."
  - `ADR-orchestration-workers`: prose follows the block before its `---`, so the `---` stays.
  - A `- **Status**:` item elsewhere in a body (the milestone lifecycle item of `ADR-roadmap-and-milestones-ledger`)
    is not in the first list and stays.
  - Reference edges: when an Involved Components line names a backticked ID that the rest of the body does not
    mention, one sentence at the end of Context & Problem Statement keeps it: "This decision involves `<ID>`, …."
    Plain path or skill names in those lines are dropped. Development lists the affected ADRs at its HEAD.
- Handoff compatibility: instead of rewriting a legacy body status, promotion deletes the exact block an earlier
  scaffold wrote, so a PADR scaffolded before the upgrade (in this repository or a consumer) reaches the ledger
  without a stale `Draft`. It deletes only the first visible `- **Status**: Draft` or `Proposed` line in the first list
  after the H1, a `- **Date**:` line directly after it, and a `---` that is the next non-blank line when that list is
  left empty; fenced, indented and commented lines stay. The existing edge-case tests (fenced example, HTML comment)
  become deletion tests.
- Living Spec: `CAP-DLV-proposal-planning` §4.4 states that the PADR body MUST carry no Status, Date, Deciders or
  Involved Components line, in place of "`- **Status**: Draft`, `- **Date**`"; `CAP-DLV-proposal-lifecycle` handoff
  step 4 replaces the body-line rewrite sentence with: promotion MUST change only the frontmatter status in place and
  MUST delete the legacy scaffold block as above; `DESIGN-proposal-handoff` line 156 (observed run) stops citing the body status.

#### Design, domain and operations assessment

- Design: `DESIGN-proposal-handoff` is affected. Changed statement: its observed ADR-promotion row claims the promoted
  ADR has `- **Status**: Accepted`. Source identity: `handoff.py` `_accept_status`. Statement owner:
  `CAP-DLV-proposal-lifecycle` handoff step 4; the design only illustrates it. Maintenance action: edit that row at
  Development HEAD, after `SPEC-formal-doc-padding-trim` (which owns `docs/designs/` and trims the same document)
  integrates. Verification: `devkit rules check` on the document and a review that the row matches the new handoff.
  No other design document cites the block (`rg` in `docs/designs/`).
- Domain: unaffected. No document under `docs/domain/` names the body block or the ADR status copy (`rg` over
  `docs/domain/`); ADR status as a domain concept stays in the frontmatter model.
- Operations: unaffected. No document under `docs/operations/` reads or repairs the block; the handoff recovery
  routes do not depend on the body status.

#### Planning decisions

- Q1-Q4 as answered in §2; the lasting choice is `ADR-frontmatter-only-decision-status`.
- Promotion keeps a deletion-only compatibility pass for the legacy scaffold block (challenger-01 finding 3; decided
  by the user at `plan-accept`). Dropping all body handling was rejected: a pre-upgrade PADR would reach the ledger
  with a stale `- **Status**: Draft`.
- The Q1 pass keeps reference edges by moving ADR-only IDs from Involved Components into one Context sentence
  (challenger-01 finding 2; decided by the user at `plan-accept`). Losing those edges in `devkit docs refs` and the
  viewer reference panel was rejected.
- Q4 is a template and guidance edit inside the existing `decision-writing` rule, not a new decision; it gets no PADR.
- `docs/designs/delivery/DESIGN-proposal-handoff/design.md` is in both this proposal's and
  `SPEC-formal-doc-padding-trim`'s boundaries; the overlap is sequenced (this unit integrates after it), and this unit
  edits only the one observed-run row.

### 4. Lifecycle & Retirement Criteria

- Planning settles Q1–Q4; acceptance hands off to Development and integrates locally under `dev-integration=auto`.
- Integrated after `SPEC-formal-doc-padding-trim`, which touches the same docs bundle.
- Retire when the template, scaffold and handoff changes land.

